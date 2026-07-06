import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import useRunSocket from "../hooks/useRunSocket";
import { getRun } from "../api/client";
import AgentStatus from "../components/AgentStatus";
import LiveFeed from "../components/LiveFeed";

export default function LiveRun() {
  const params = useParams();
  const { id } = params;
  const navigate = useNavigate();
  const [run, setRun] = useState(null);
  const [runError, setRunError] = useState(null);
  const { events, connected } = useRunSocket(id);
  const [done, setDone] = useState(false);

  useEffect(() => {
    getRun(id)
      .then(setRun)
      .catch((err) => setRunError(err.message));
  }, [id]);

  useEffect(() => {
    for (const ev of events) {
      if (ev.event === "run_complete") {
        setDone(true);
        getRun(id).then(setRun);
      }
    }
  }, [events, id]);

  const lastAgentEvent = (agent) =>
    events.filter((e) => e.event === "agent_status" && e.agent === agent).pop();

  if (runError) {
    return <p className="text-red-400">Error: {runError}</p>;
  }

  if (!run) {
    return <p className="text-zinc-500">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Run #{run.id}</h1>
        <span className={`text-xs px-2 py-1 rounded ${connected ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"}`}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </div>

      <div className="bg-zinc-900 border border-zinc-800 rounded p-3 text-xs text-zinc-400">
        {run.repo_url ? (
          <><span className="text-zinc-500">Repo:</span> {run.repo_url}</>
        ) : (
          <><span className="text-zinc-500">Path:</span> {run.repo_path}</>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AgentStatus name="Clone" data={lastAgentEvent("clone")} />
        <AgentStatus name="Scanner" data={lastAgentEvent("scanner")} />
        <AgentStatus name="Analyzer" data={lastAgentEvent("analyzer")} />
      </div>

      {done && (
        <div className="border border-zinc-700 rounded p-4 text-center space-y-3">
          <p className="text-lg font-semibold text-green-400">Diagnostic Complete</p>
          <button
            onClick={() => navigate(`/runs/${id}/detail`)}
            className="bg-zinc-800 hover:bg-zinc-700 text-zinc-100 rounded px-4 py-2 text-sm"
          >
            View Report
          </button>
        </div>
      )}

      <LiveFeed events={events} />
    </div>
  );
}
