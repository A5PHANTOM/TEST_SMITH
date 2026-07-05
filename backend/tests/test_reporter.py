import pytest
import os, tempfile
from app.orchestrator.reporter import run_reporter


@pytest.mark.asyncio
async def test_reporter_empty_analysis():
    async def emit(msg):
        pass
    report = await run_reporter({"source_files": [], "test_files": [], "dependency_graph": {}, "project_type": None}, "/tmp", emit)
    assert "Coverage Overview" in report
    assert "No source files found" in report


@pytest.mark.asyncio
async def test_reporter_with_files():
    async def emit(msg):
        pass
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "calc.py")
        with open(src_path, "w") as f:
            f.write("def add(a, b): return a + b\n")

        analysis = {
            "source_files": [{"path": "calc.py", "language": "py", "size": 30}],
            "test_files": [],
            "dependency_graph": {},
            "project_type": "python",
        }
        report = await run_reporter(analysis, tmpdir, emit)
        assert "calc.py" in report
        assert "Coverage Overview" in report
        assert "Uncovered" in report
