import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRun } from "../api/client";

export default function NewRun() {
  const navigate = useNavigate();
  const [repoPath, setRepoPath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await createRun({ repo_path: repoPath });
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
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Repository Path</label>
          <input
            type="text"
            value={repoPath}
            onChange={(e) => setRepoPath(e.target.value)}
            placeholder="/path/to/project"
            className="w-full bg-zinc-900 border border-zinc-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-[#8bff4a]"
            required
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#8bff4a] text-black font-semibold rounded px-4 py-2 text-sm hover:bg-[#7ae63e] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Scanning..." : "Run Diagnostic"}
        </button>
      </form>
    </div>
  );
}
