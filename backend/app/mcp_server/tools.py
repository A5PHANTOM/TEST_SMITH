import os, subprocess, tempfile, json


async def test_scaffold(repo_path: str, framework: str = "pytest") -> dict:
    """Scaffold a basic test directory structure in the target repo."""
    dirs_created = []
    test_dir = os.path.join(repo_path, "tests")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        dirs_created.append(test_dir)
    init_file = os.path.join(test_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")
        dirs_created.append(init_file)
    return {"dirs_created": dirs_created}


async def test_runner(repo_path: str, framework: str = "pytest", timeout: int = 300) -> dict:
    """Run the test suite in the repo and return results."""
    try:
        cmd = ["python", "-m", "pytest", repo_path, "-v", "--tb=short"] if framework == "pytest" else [framework, "test"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "Timeout exceeded"}
    except FileNotFoundError:
        return {"returncode": -1, "stdout": "", "stderr": f"Framework '{framework}' not found"}


async def coverage_report(repo_path: str, framework: str = "pytest") -> dict:
    """Generate a coverage report for the test suite."""
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", "--cov=" + repo_path, "--cov-report=term-missing", repo_path],
            capture_output=True, text=True, timeout=300,
        )
        return {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
    except Exception as e:
        return {"error": str(e)}
