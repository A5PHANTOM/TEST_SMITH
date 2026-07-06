import os, shutil, subprocess, tempfile, re
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.run import Run
from app.orchestrator.scanner import run_scanner
from app.orchestrator.reporter import run_reporter


GITHUB_URL_RE = re.compile(r"^https?://github\.com/[\w.-]+/[\w.-]+(/.*)?$")


def _validate_repo_path(repo_path: str, whitelist: list[str]) -> bool:
    if "*" in whitelist:
        return True
    resolved = os.path.abspath(os.path.normpath(repo_path))
    for allowed in whitelist:
        if resolved.startswith(os.path.abspath(allowed)):
            return True
    return False


def _is_github_url(value: str) -> bool:
    return bool(GITHUB_URL_RE.match(value.strip()))


def _clone_repo(url: str, dest: str) -> str:
    result = subprocess.run(
        ["git", "clone", "--depth=1", url.strip(), dest],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
    return dest


async def run_pipeline(run: Run, db: AsyncSession, emit):
    whitelist = os.getenv("REPO_ROOT_WHITELIST", "/tmp").split(",")

    if run.repo_url and _is_github_url(run.repo_url):
        await emit({"event": "agent_status", "agent": "clone", "status": "working", "detail": f"Cloning {run.repo_url}..."})
        run.status = "cloning"
        await db.commit()

        clone_dir = tempfile.mkdtemp(prefix="testsmith_clone_")
        run.clone_path = clone_dir
        await db.commit()
        try:
            _clone_repo(run.repo_url, clone_dir)
            run.repo_path = clone_dir
            await emit({"event": "agent_status", "agent": "clone", "status": "done", "detail": "Clone complete"})
        except RuntimeError as e:
            await emit({"event": "error", "detail": str(e)})
            run.status = "rejected"
            await db.commit()
            shutil.rmtree(clone_dir, ignore_errors=True)
            return
    else:
        if not _validate_repo_path(run.repo_path, whitelist):
            await emit({"event": "error", "detail": "Repository path not in whitelist"})
            run.status = "rejected"
            await db.commit()
            return

    run.status = "scanning"
    await db.commit()
    await emit({"event": "agent_status", "agent": "scanner", "status": "idle", "detail": ""})

    analysis = await run_scanner(run.repo_path, [], emit)
    run.analysis = analysis

    run.status = "analyzing"
    await db.commit()
    await emit({"event": "agent_status", "agent": "analyzer", "status": "idle", "detail": ""})

    report = await run_reporter(analysis, run.repo_path, emit)
    run.report = report

    run.status = "done"
    await db.commit()
    await emit({"event": "run_complete", "run_id": run.id})
