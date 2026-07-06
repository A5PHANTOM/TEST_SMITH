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

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            ext = os.path.splitext(f)[1]
            if ext not in SRC_EXTS:
                continue

            rel_path = os.path.relpath(os.path.join(root, f), repo_path)
            full_path = os.path.join(root, f)
            is_test = "test" in f.lower() or "spec" in f.lower()
            key = "test_files" if is_test else "source_files"

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

    if os.path.isfile(os.path.join(repo_path, "package.json")):
        analysis["project_type"] = "node"
    elif os.path.isfile(os.path.join(repo_path, "pyproject.toml")):
        analysis["project_type"] = "python"
    elif os.path.isfile(os.path.join(repo_path, "requirements.txt")):
        analysis["project_type"] = "python"
    elif os.path.isfile(os.path.join(repo_path, "Cargo.toml")):
        analysis["project_type"] = "rust"
    elif os.path.isfile(os.path.join(repo_path, "go.mod")):
        analysis["project_type"] = "go"

    await emit({"event": "agent_status", "agent": "scanner", "status": "done",
                "detail": f"Found {source_count} source files, {test_count} test files"})

    return analysis
