import os, shutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db import get_db
from app.models.run import Run

router = APIRouter(prefix="/runs", tags=["runs"])


class CreateRunRequest(BaseModel):
    repo_path: str = ""
    repo_url: str = ""


class RunResponse(BaseModel):
    id: int
    repo_path: str
    repo_url: str | None
    status: str
    created_at: str
    updated_at: str

    @classmethod
    def from_orm(cls, run: Run):
        return cls(
            id=run.id,
            repo_path=run.repo_path,
            repo_url=run.repo_url,
            status=run.status,
            created_at=run.created_at.isoformat(),
            updated_at=run.updated_at.isoformat(),
        )


@router.post("")
async def create_run(body: CreateRunRequest, db: AsyncSession = Depends(get_db)):
    if not body.repo_path and not body.repo_url:
        raise HTTPException(400, "Provide either repo_path or repo_url")
    run = Run(
        repo_path=body.repo_path or body.repo_url,
        repo_url=body.repo_url or None,
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return {"id": run.id, "status": run.status}


@router.get("")
async def list_runs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).order_by(Run.created_at.desc()))
    runs = result.scalars().all()
    return [RunResponse.from_orm(r) for r in runs]


@router.get("/{run_id}")
async def get_run(run_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(404, "Run not found")
    return {
        "id": run.id,
        "repo_path": run.repo_path,
        "repo_url": run.repo_url,
        "clone_path": run.clone_path,
        "status": run.status,
        "analysis": run.analysis,
        "execution_results": run.execution_results,
        "report": run.report,
        "transcript": run.transcript,
        "created_at": run.created_at.isoformat(),
        "updated_at": run.updated_at.isoformat(),
    }


@router.post("/{run_id}/dismiss")
async def dismiss_run(run_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(404, "Run not found")
    if run.clone_path:
        shutil.rmtree(run.clone_path, ignore_errors=True)
    run.status = "dismissed"
    await db.commit()
    return {"status": "dismissed"}
