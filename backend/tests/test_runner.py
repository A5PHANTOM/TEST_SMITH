import pytest
from app.orchestrator.runner import run_runner


@pytest.mark.asyncio
async def test_runner_no_project_type():
    async def emit(msg):
        pass
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await run_runner(tmpdir, {"source_files": [], "project_type": None}, emit)
        assert "pass_count" in result
        assert "fail_count" in result
