import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from app.db import async_session
from app.models.run import Run
from app.orchestrator.loop import run_pipeline

router = APIRouter()


@router.websocket("/ws/runs/{run_id}")
async def ws_run(ws: WebSocket, run_id: int):
    await ws.accept()

    async def emit(event: dict):
        await ws.send_text(json.dumps(event))

    try:
        async with async_session() as db:
            result = await db.execute(select(Run).where(Run.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                await emit({"event": "error", "detail": "Run not found"})
                return

            await run_pipeline(run, db, emit)
    except WebSocketDisconnect:
        pass
