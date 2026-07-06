import os
from app.orchestrator.prompts.scanner import SCANNER_SYSTEM_PROMPT

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".egg-info"}
SRC_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php"}


async def run_scanner(repo_path: str, target_files: list[str], emit):
    await emit({"event": "agent_status", "agent": "scanner", "status": "working", "detail": "Analyzing repository structure..."})

    analysis = {
        "source_files": [],
        "test_files": [],
        "dependency_graph": {},
        "entry_points": [],
        "notable_patterns": [],
        "project_type": None,
    }

    if not os.path.isdir(repo_path):
        await emit({"event": "agent_status", "agent": "scanner", "status": "done", "detail": "Repository path not found"})
        return analysis

    source_count = 0
    test_count = 0
    has_py_tests = False
    has_js_tests = False

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        if os.path.basename(root) == "tests":
            has_py_tests = any(f.endswith(".py") for f in files)

        for f in files:
            ext = os.path.splitext(f)[1]
            if ext not in SRC_EXTS:
                continue

            rel_path = os.path.relpath(os.path.join(root, f), repo_path)
            full_path = os.path.join(root, f)
            is_test = "test" in f.lower() or "spec" in f.lower()
            key = "test_files" if is_test else "source_files"

            if is_test and ext == ".py":
                has_py_tests = True
            if is_test and ext in (".js", ".jsx", ".ts", ".tsx"):
                has_js_tests = True

            analysis[key].append({
                "path": rel_path,
                "language": ext.lstrip("."),
                "size": os.path.getsize(full_path),
            })
            if is_test:
                test_count += 1
            else:
                source_count += 1

    for root, dirs, _ in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for d in dirs:
            pkg_rel = os.path.relpath(os.path.join(root, d), repo_path)
            if pkg_rel not in analysis["dependency_graph"]:
                analysis["dependency_graph"][pkg_rel] = []

    if has_py_tests:
        analysis["project_type"] = "python"
    elif has_js_tests:
        analysis["project_type"] = "node"
    else:
        for root, dirs, files in os.walk(repo_path):
            if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
                analysis["project_type"] = "python"
                break
            if "package.json" in files:
                analysis["project_type"] = "node"
                break

    await emit({"event": "agent_status", "agent": "scanner", "status": "done",
                "detail": f"Found {source_count} source files, {test_count} test files"})

    return analysis
