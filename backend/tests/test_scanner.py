import pytest
import os, tempfile
from app.orchestrator.scanner import run_scanner


@pytest.mark.asyncio
async def test_scanner_no_files():
    async def emit(msg):
        pass
    with tempfile.TemporaryDirectory() as tmpdir:
        result = await run_scanner(tmpdir, [], emit)
        assert result["source_files"] == []
        assert result["test_files"] == []


@pytest.mark.asyncio
async def test_scanner_python_project():
    async def emit(msg):
        pass
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "main.py"), "w") as f:
            f.write("def main(): pass")
        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("pytest\n")
        result = await run_scanner(tmpdir, [], emit)
        assert len(result["source_files"]) == 1
        assert result["source_files"][0]["path"] == "main.py"
        assert result["project_type"] == "python"
