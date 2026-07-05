import os
from app.orchestrator.prompts.scanner import SCANNER_SYSTEM_PROMPT


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

    try:
        entries = os.listdir(repo_path)
    except FileNotFoundError:
        await emit({"event": "agent_status", "agent": "scanner", "status": "done", "detail": "Repository path not found"})
        return analysis

    for entry in entries:
        full_path = os.path.join(repo_path, entry)
        if os.path.isfile(full_path):
            ext = os.path.splitext(entry)[1]
            if ext in (".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php"):
                entry_type = "test" if "test" in entry.lower() or "spec" in entry.lower() else "source"
                key = "test_files" if entry_type == "test" else "source_files"
                analysis[key].append({
                    "path": entry,
                    "language": ext.lstrip("."),
                    "size": os.path.getsize(full_path),
                })
        elif os.path.isdir(full_path) and entry not in (".git", "__pycache__", "node_modules", ".venv", "venv"):
            analysis["dependency_graph"][entry] = []

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

    await emit({"event": "agent_status", "agent": "scanner", "status": "done", "detail": f"Found {len(analysis['source_files'])} source files, {len(analysis['test_files'])} test files"})

    return analysis
