import os, shutil, subprocess, tempfile, re
from app.orchestrator.prompts.runner import RUNNER_SYSTEM_PROMPT


async def run_runner(repo_path: str, analysis: dict, emit):
    test_files = analysis.get("test_files", [])
    if not test_files:
        await emit({"event": "agent_status", "agent": "runner", "status": "done", "detail": "No tests found to run"})
        return {"pass_count": 0, "fail_count": 0, "error_count": 0, "skip_count": 0, "failures": [], "output_log": "No test files found"}

    await emit({"event": "agent_status", "agent": "runner", "status": "working", "detail": f"Running {len(test_files)} test file(s)..."})

    sandbox = tempfile.mkdtemp(prefix="testsmith_runner_")
    result = {
        "pass_count": 0,
        "fail_count": 0,
        "error_count": 0,
        "skip_count": 0,
        "failures": [],
        "output_log": "",
    }

    try:
        _copy_to_sandbox(repo_path, sandbox)
        _install_deps(sandbox, analysis, result)

        cmd = _detect_test_command(sandbox, analysis)
        if not cmd:
            result["output_log"] = "No test framework detected"
            await emit({"event": "agent_status", "agent": "runner", "status": "done", "detail": "No tests found to run"})
            return result

        proc = subprocess.run(cmd, cwd=sandbox, capture_output=True, text=True, timeout=300)
        output = proc.stdout + "\n" + proc.stderr
        result["output_log"] = output

        _parse_output(result, output, cmd)

    except subprocess.TimeoutExpired:
        result["error_count"] = 1
        result["output_log"] = "Test execution timed out"
    except Exception as e:
        result["error_count"] = 1
        result["output_log"] = str(e)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    detail = f"Passed: {result['pass_count']}, Failed: {result['fail_count']}, Errors: {result['error_count']}"
    await emit({"event": "test_result", "pass_count": result["pass_count"],
                "fail_count": result["fail_count"], "error_count": result["error_count"],
                "skip_count": result["skip_count"]})
    await emit({"event": "agent_status", "agent": "runner", "status": "done", "detail": detail})

    return result


def _copy_to_sandbox(repo_path: str, sandbox: str):
    for item in os.listdir(repo_path):
        if item in (".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache"):
            continue
        src = os.path.join(repo_path, item)
        dst = os.path.join(sandbox, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules", ".venv", "venv"))
        else:
            shutil.copy2(src, dst)


def _install_deps(sandbox: str, analysis: dict, result: dict):
    try:
        if os.path.isfile(os.path.join(sandbox, "requirements.txt")):
            subprocess.run(["pip", "install", "-r", "requirements.txt"],
                           cwd=sandbox, capture_output=True, text=True, timeout=120)
        elif os.path.isfile(os.path.join(sandbox, "pyproject.toml")):
            subprocess.run(["pip", "install", "-e", "."],
                           cwd=sandbox, capture_output=True, text=True, timeout=120)
        if os.path.isfile(os.path.join(sandbox, "package.json")):
            subprocess.run(["npm", "install"], cwd=sandbox, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        result["output_log"] += "\n[Dependency installation timed out]"


def _detect_test_command(sandbox: str, analysis: dict) -> list[str] | None:
    for root, dirs, files in os.walk(sandbox):
        dirs[:] = [d for d in dirs if d in ("tests", "test", "__tests__", "spec") or d.startswith("tests")]
        for f in files:
            if re.search(r"test_.*\.py$|.*_test\.py$|.*test\.(js|jsx|ts|tsx)$", f):
                if f.endswith(".py"):
                    return ["python", "-m", "pytest", sandbox, "-v", "--tb=short"]
                else:
                    return ["npx", "vitest", "run", "--reporter=verbose"]
    return None


def _parse_output(result: dict, output: str, cmd: list[str]):
    if "pytest" in cmd:
        passed = re.findall(r"(\d+) passed", output)
        failed = re.findall(r"(\d+) failed", output)
        errors = re.findall(r"(\d+) errors", output)
        skipped = re.findall(r"(\d+) skipped", output)
        result["pass_count"] = int(passed[0]) if passed else 0
        result["fail_count"] = int(failed[0]) if failed else 0
        result["error_count"] = int(errors[0]) if errors else 0
        result["skip_count"] = int(skipped[0]) if skipped else 0
        for line in output.split("\n"):
            if "FAILED" in line:
                result["failures"].append(line.strip())
    elif any(fw in cmd for fw in ("vitest", "jest")):
        total = re.search(r"Tests\s+(\d+)", output)
        if total:
            result["pass_count"] = int(total.group(1))
