from sqlalchemy.ext.asyncio import AsyncSession
from app.models.run import Run
from app.orchestrator.scanner import run_scanner
from app.orchestrator.reporter import run_reporter


def _validate_repo_path(repo_path: str, whitelist: list[str]) -> bool:
    import os
    if "*" in whitelist:
        return True
    resolved = os.path.abspath(os.path.normpath(repo_path))
    for allowed in whitelist:
        if resolved.startswith(os.path.abspath(allowed)):
            return True
    return False


async def run_pipeline(run: Run, db: AsyncSession, emit):
    import os
    whitelist = os.getenv("REPO_ROOT_WHITELIST", "/tmp").split(",")

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
