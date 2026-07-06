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
      <h1 className="text-2xl font-bold mb-6">New Diagnostic Run</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="flex gap-2 bg-zinc-900 rounded p-1 border border-zinc-800 w-fit">
          <button
            type="button"
            onClick={() => setMode("local")}
            className={`px-4 py-1.5 text-sm rounded ${mode === "local" ? "bg-[#8bff4a] text-black" : "text-zinc-400 hover:text-zinc-200"}`}
          >
            Local Path
          </button>
          <button
            type="button"
            onClick={() => setMode("github")}
            className={`px-4 py-1.5 text-sm rounded ${mode === "github" ? "bg-[#8bff4a] text-black" : "text-zinc-400 hover:text-zinc-200"}`}
          >
            GitHub URL
          </button>
        </div>

        {mode === "local" ? (
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Repository Path</label>
            <input
              type="text"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              placeholder="/path/to/project"
              className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-[#8bff4a]"
              required={mode === "local"}
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm text-zinc-400 mb-1">GitHub Repository URL</label>
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-[#8bff4a]"
              required={mode === "github"}
            />
          </div>
        )}

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#8bff4a] text-black font-semibold rounded px-4 py-2 text-sm hover:bg-[#7ae63e] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Starting..." : "Run Diagnostic"}
        </button>
      </form>
    </div>
  );
}
