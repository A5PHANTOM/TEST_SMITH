import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listRuns } from "../api/client";

const statusColors = {
  pending: "text-amber-400",
  cloning: "text-blue-400",
  scanning: "text-blue-400",
  analyzing: "text-blue-400",
  done: "text-teal-400",
  dismissed: "text-slate-500",
  rejected: "text-red-400",
};

export default function History() {
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listRuns().then(setRuns).catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="text-red-400">Error: {error}</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 text-slate-100">Past Runs</h1>
      <p className="text-sm text-slate-500 mb-8">View or download reports from previous diagnostic runs.</p>

      {runs.length === 0 && (
        <p className="text-slate-500">No runs yet. <Link to="/" className="text-teal-400 hover:text-teal-300 transition-colors">Start one.</Link></p>
      )}

      <div className="space-y-3">
        {runs.map((run) => (
          <Link
            key={run.id}
            to={`/runs/${run.id}/detail`}
            className="glass glass-hover block p-4 no-underline transition-all"
          >
            <div className="flex items-center justify-between">
              <span className="text-slate-200 font-medium">Run #{run.id}</span>
              <span className={`text-xs ${statusColors[run.status] || "text-slate-400"}`}>
                {run.status}
              </span>
            </div>
            <div className="text-xs text-slate-500 mt-1.5 truncate">
              {run.repo_url || run.repo_path}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
