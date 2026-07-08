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

  const lastTestResult = events.filter((e) => e.event === "test_result").pop();
  const runnerEvent = lastAgentEvent("runner");
  const runnerWorking = runnerEvent?.status === "working";

  if (runError) {
    return <p className="text-red-400">Error: {runError}</p>;
  }

  if (!run) {
    return <p className="text-slate-500">Loading...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Run #{run.id}</h1>
        <span className={`text-xs px-2.5 py-1 rounded-full border ${
          connected
            ? "bg-teal-500/10 text-teal-300 border-teal-500/30"
            : "bg-red-500/10 text-red-300 border-red-500/30"
        }`}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </div>

      <div className="glass glass-hover p-3 text-xs text-slate-400">
        {run.repo_url ? (
          <><span className="text-slate-600">Repo:</span> {run.repo_url}</>
        ) : (
          <><span className="text-slate-600">Path:</span> {run.repo_path}</>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <AgentStatus name="Clone" data={lastAgentEvent("clone")} />
        <AgentStatus name="Scanner" data={lastAgentEvent("scanner")} />
        <AgentStatus name="Runner" data={lastAgentEvent("runner")} />
        <AgentStatus name="Analyzer" data={lastAgentEvent("analyzer")} />
      </div>

      {runnerWorking && !lastTestResult && (
        <div className="glass p-4 flex items-center gap-3">
          <span className="inline-block w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-slate-400">Running test suite...</span>
        </div>
      )}

      {lastTestResult && (
        <div className="glass p-4">
          <h3 className="text-sm font-semibold mb-3 text-slate-200">Test Results</h3>
          <div className="flex gap-4 text-sm">
            <span className="text-teal-400">{lastTestResult.pass_count} passed</span>
            {lastTestResult.fail_count > 0 && <span className="text-red-400">{lastTestResult.fail_count} failed</span>}
            {lastTestResult.error_count > 0 && <span className="text-amber-400">{lastTestResult.error_count} errors</span>}
            {lastTestResult.skip_count > 0 && <span className="text-slate-500">{lastTestResult.skip_count} skipped</span>}
            <span className="text-slate-500">
              {lastTestResult.pass_count + lastTestResult.fail_count + lastTestResult.error_count + lastTestResult.skip_count} total
            </span>
          </div>
        </div>
      )}

      {done && (
        <div className="glass-strong p-6 text-center space-y-4">
          <p className="text-lg font-semibold text-teal-400">Complete</p>
          <button
            onClick={() => navigate(`/runs/${id}/detail`)}
            className="bg-teal-500 hover:bg-teal-400 text-white rounded-lg px-5 py-2 text-sm transition-all shadow-[0_0_16px_-6px_rgba(20,184,166,0.4)]"
          >
            View Full Results
          </button>
        </div>
      )}

      <LiveFeed events={events} />
    </div>
  );
}
