import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getRun, dismissRun } from "../api/client";

export default function RunDetail() {
  const { id } = useParams();
  const [run, setRun] = useState(null);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  useEffect(() => {
    getRun(id).then(setRun).catch((err) => setError(err.message));
  }, [id]);

  const handleDismiss = async () => {
    try {
      await dismissRun(id);
      setActionMsg("Run dismissed");
      setRun((prev) => ({ ...prev, status: "dismissed" }));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDownload = () => {
    if (!run?.report) return;
    const blob = new Blob([run.report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `testsmith-report-run-${run.id}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (error) return <p className="text-red-400">Error: {error}</p>;
  if (!run) return <p className="text-zinc-500">Loading...</p>;

  const exec = run.execution_results || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Run #{run.id}</h1>
        <span className="text-xs bg-zinc-800 text-zinc-300 px-2 py-1 rounded">
          Status: {run.status}
        </span>
      </div>

      <div className="space-y-1">
        {run.repo_url && (
          <div className="bg-zinc-900 border border-zinc-800 rounded p-3 text-sm">
            <span className="text-zinc-500">GitHub:</span>{" "}
            <a href={run.repo_url} target="_blank" rel="noreferrer" className="text-[#8bff4a] underline">
              {run.repo_url}
            </a>
          </div>
        )}
        {run.clone_path && (
          <div className="bg-zinc-900 border border-zinc-800 rounded p-3 text-sm">
            <span className="text-zinc-500">Cloned to:</span>{" "}
            <span className="text-zinc-300 font-mono text-xs">{run.clone_path}</span>
          </div>
        )}
        {!run.repo_url && (
          <div className="bg-zinc-900 border border-zinc-800 rounded p-3 text-sm">
            <span className="text-zinc-500">Path:</span> {run.repo_path}
          </div>
        )}
      </div>

      <div className="border border-zinc-800 rounded p-4">
        <h2 className="text-lg font-semibold mb-3">Test Results</h2>
        <div className="flex gap-4 text-sm mb-3">
          <span className="text-green-400">{exec.pass_count ?? 0} passed</span>
          {exec.fail_count > 0 && <span className="text-red-400">{exec.fail_count} failed</span>}
          {exec.error_count > 0 && <span className="text-yellow-400">{exec.error_count} errors</span>}
          {exec.skip_count > 0 && <span className="text-zinc-500">{exec.skip_count} skipped</span>}
          <span className="text-zinc-500">
            {(exec.pass_count || 0) + (exec.fail_count || 0) + (exec.error_count || 0) + (exec.skip_count || 0)} total
          </span>
        </div>
        {exec.failures?.length > 0 && (
          <div className="text-xs text-red-400 space-y-1 max-h-32 overflow-auto mb-3">
            {exec.failures.map((f, i) => <div key={i}>{f}</div>)}
          </div>
        )}
        {exec.output_log && (
          <details>
            <summary className="text-xs text-zinc-500 cursor-pointer">Output Log</summary>
            <pre className="bg-zinc-900 border border-zinc-800 rounded p-3 text-xs overflow-auto max-h-48 mt-2">
              {exec.output_log}
            </pre>
          </details>
        )}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-2">Analysis</h2>
        <pre className="bg-zinc-900 border border-zinc-800 rounded p-3 text-xs overflow-auto max-h-60">
          {JSON.stringify(run.analysis, null, 2)}
        </pre>
      </div>

      {run.report && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">Diagnostic Report</h2>
            <button
              onClick={handleDownload}
              className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded px-3 py-1 text-xs"
            >
              Download .md
            </button>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded p-4 text-sm leading-relaxed whitespace-pre-wrap font-mono">
            {run.report}
          </div>
        </div>
      )}

      {run.status === "done" && (
        <button
          onClick={handleDismiss}
          className="bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded px-4 py-2 text-sm"
        >
          Dismiss
        </button>
      )}

      {actionMsg && <p className="text-sm text-zinc-400">{actionMsg}</p>}
    </div>
  );
}
