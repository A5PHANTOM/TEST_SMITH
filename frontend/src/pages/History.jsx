import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listRuns } from "../api/client";

const statusColors = {
  pending: "text-yellow-400",
  cloning: "text-blue-400",
  scanning: "text-blue-400",
  analyzing: "text-blue-400",
  done: "text-green-400",
  dismissed: "text-zinc-500",
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
      <h1 className="text-2xl font-bold mb-6">Past Runs</h1>

      {runs.length === 0 && (
        <p className="text-zinc-500">No runs yet. <Link to="/" className="text-[#8bff4a]">Start one.</Link></p>
      )}

      <div className="space-y-2">
        {runs.map((run) => (
          <Link
            key={run.id}
            to={`/runs/${run.id}/detail`}
            className="block bg-zinc-900 border border-zinc-800 rounded p-4 hover:border-zinc-600 transition-colors no-underline"
          >
            <div className="flex items-center justify-between">
              <span className="text-zinc-100 font-medium">Run #{run.id}</span>
              <span className={`text-xs ${statusColors[run.status] || "text-zinc-400"}`}>
                {run.status}
              </span>
            </div>
            <div className="text-xs text-zinc-500 mt-1">
              {run.repo_url || run.repo_path}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
