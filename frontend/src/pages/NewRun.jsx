import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRun } from "../api/client";

export default function NewRun() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("local");
  const [repoPath, setRepoPath] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = mode === "local"
        ? { repo_path: repoPath }
        : { repo_url: repoUrl };
      const data = await createRun(payload);
      navigate(`/runs/${data.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-2 text-slate-100">New Diagnostic Run</h1>
      <p className="text-sm text-slate-500 mb-8">Scan a repository and generate a test readiness report.</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="glass p-1 w-fit flex">
          <button
            type="button"
            onClick={() => setMode("local")}
            className={`px-4 py-1.5 text-sm rounded-lg transition-all ${
              mode === "local"
                ? "bg-teal-500 text-white shadow-[0_0_12px_-4px_rgba(20,184,166,0.5)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Local Path
          </button>
          <button
            type="button"
            onClick={() => setMode("github")}
            className={`px-4 py-1.5 text-sm rounded-lg transition-all ${
              mode === "github"
                ? "bg-teal-500 text-white shadow-[0_0_12px_-4px_rgba(20,184,166,0.5)]"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            GitHub URL
          </button>
        </div>

        {mode === "local" ? (
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">Repository Path</label>
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="/path/to/project"
              className="input-glass w-full px-3 py-2.5 text-sm placeholder-slate-600"
              required={mode === "local"}
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">GitHub Repository URL</label>
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="input-glass w-full px-3 py-2.5 text-sm placeholder-slate-600"
              required={mode === "github"}
            />
          </div>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-teal-500 hover:bg-teal-400 text-white font-semibold rounded-lg px-4 py-2.5 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_-8px_rgba(20,184,166,0.4)] hover:shadow-[0_0_24px_-6px_rgba(20,184,166,0.6)]"
        >
          {loading ? "Starting..." : "Run Diagnostic"}
        </button>
      </form>
    </div>
  );
}
