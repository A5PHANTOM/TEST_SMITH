import os, ast
from app.orchestrator.prompts.generator import ANALYZER_SYSTEM_PROMPT


async def run_reporter(analysis: dict, repo_path: str, emit):
    await emit({"event": "agent_status", "agent": "analyzer", "status": "working", "detail": "Analyzing codebase for diagnostic report..."})

    sections = []

    sections.append(_coverate_overview(analysis))
    sections.append(_file_detail_section(analysis, repo_path))
    sections.append(_dependency_analysis(analysis))
    sections.append(_testability_analysis(analysis, repo_path))
    sections.append(_recommendations(analysis))

    report = "\n\n".join(sections)

    await emit({"event": "agent_status", "agent": "analyzer", "status": "done", "detail": "Diagnostic report generated"})
    await emit({"event": "report_ready", "report": report})

    return report


def _coverate_overview(analysis: dict) -> str:
    source_files = analysis.get("source_files", [])
    test_files = analysis.get("test_files", [])
    test_names = {os.path.splitext(f["path"])[0].replace("test_", "").replace("_", "") for f in test_files}

    covered = []
    uncovered = []
    for sf in source_files:
        base = os.path.splitext(sf["path"])[0].replace("_", "")
        if any(base in tn or tn in base for tn in test_names):
            covered.append(sf["path"])
        else:
            uncovered.append(sf["path"])

    lines = [
        "## Coverage Overview\n",
        f"- **Source files**: {len(source_files)}",
        f"- **Existing test files**: {len(test_files)}",
        f"- **Covered**: {len(covered)} file(s)",
        f"- **Uncovered**: {len(uncovered)} file(s)\n",
    ]

    if covered:
        lines.append("### Covered Files\n")
        for f in covered:
            lines.append(f"- `{f}`")
        lines.append("")

    if uncovered:
        lines.append("### Uncovered Files\n")
        for f in uncovered:
            lines.append(f"- `{f}`")
        lines.append("")

    return "\n".join(lines)


def _file_detail_section(analysis: dict, repo_path: str) -> str:
    source_files = analysis.get("source_files", [])
    if not source_files:
        return "## File Analysis\n\n*No source files found.*"

    lines = ["## File Analysis\n"]
    for sf in source_files:
        fpath = sf["path"]
        full_path = os.path.join(repo_path, fpath)
        lang = sf.get("language", "?")

        funcs, classes, imports = _extract_python_info(full_path) if lang == "py" else ([], [], [])
        ext_deps = [imp for imp in imports if not imp.startswith("_") and "." not in imp]

        lines.append(f"### `{fpath}` ({sf.get('size', 0)} bytes, {lang})")
        if funcs:
            lines.append(f"- **Functions**: {', '.join(funcs[:10])}{'...' if len(funcs) > 10 else ''}")
        if classes:
            lines.append(f"- **Classes**: {', '.join(classes[:5])}{'...' if len(classes) > 5 else ''}")
        if ext_deps:
            lines.append(f"- **External imports**: {', '.join(sorted(set(ext_deps)))}")
        lines.append("")

    return "\n".join(lines)


def _dependency_analysis(analysis: dict) -> str:
    source_files = analysis.get("source_files", [])
    dep_graph = analysis.get("dependency_graph", {})
    project_type = analysis.get("project_type", "unknown")

    lines = ["## Dependency Analysis\n"]
    lines.append(f"- **Project type**: {project_type}")
    lines.append(f"- **Internal packages/modules**: {', '.join(dep_graph.keys()) if dep_graph else '*none detected*'}")
    lines.append(f"- **Source files**: {len(source_files)}\n")

    if dep_graph:
        lines.append("### Internal Dependencies\n")
        for pkg, deps in dep_graph.items():
            status = "has submodules" if deps else "leaf package (no submodules)"
            lines.append(f"- `{pkg}/` — {status}")

    return "\n".join(lines)


def _testability_analysis(analysis: dict, repo_path: str) -> str:
    source_files = analysis.get("source_files", [])
    concerns = []

    for sf in source_files:
        if sf.get("language") != "py":
            continue
        full_path = os.path.join(repo_path, sf["path"])
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path) as f:
                content = f.read()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if getattr(node.func, 'attr', '') in ('connect', 'request', 'run', 'start'):
                        concerns.append(f"- `{sf['path']}`: network call detected (`{node.func.attr}`) — may need mocking")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'open':
                        concerns.append(f"- `{sf['path']}`: file I/O (`open()`) — consider using tmp_path or mocks")

        except (SyntaxError, OSError):
            pass

    lines = ["## Testability Concerns\n"]
    if concerns:
        lines.extend(concerns)
    else:
        lines.append("*No significant testability concerns detected at the AST level.*")
    lines.append("")

    return "\n".join(lines)


def _recommendations(analysis: dict) -> str:
    source_files = analysis.get("source_files", [])
    test_files = analysis.get("test_files", [])

    lines = ["## Recommendations\n"]

    if not source_files:
        lines.append("No source files to analyze.")
        return "\n".join(lines)

    uncovered = 0
    test_names = {os.path.splitext(f["path"])[0].replace("test_", "").replace("_", "") for f in test_files}
    for sf in source_files:
        base = os.path.splitext(sf["path"])[0].replace("_", "")
        if not any(base in tn or tn in base for tn in test_names):
            uncovered += 1
            lines.append(f"- **High priority**: Write tests for `{sf['path']}`")

    if uncovered == 0:
        lines.append("- All source files appear to have test coverage.")

    project_type = analysis.get("project_type", "unknown")
    if project_type == "python":
        lines.append("- Use `pytest` with `pytest-cov` for coverage measurement.")
    elif project_type == "node":
        lines.append("- Use `vitest` or `jest` with `c8` for coverage measurement.")

    lines.append("- Consider adding CI integration to enforce minimum coverage thresholds.")
    lines.append("")

    return "\n".join(lines)


def _extract_python_info(filepath: str) -> tuple[list[str], list[str], list[str]]:
    funcs = []
    classes = []
    imports = []
    if not os.path.isfile(filepath):
        return funcs, classes, imports
    try:
        with open(filepath) as f:
            tree = ast.parse(f.read())
    except (SyntaxError, OSError):
        return funcs, classes, imports

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])

    return funcs, classes, list(set(imports))
