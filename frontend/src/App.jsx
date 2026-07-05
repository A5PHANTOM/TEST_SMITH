import { Routes, Route, NavLink } from "react-router-dom";
import NewRun from "./pages/NewRun";
import LiveRun from "./pages/LiveRun";
import RunDetail from "./pages/RunDetail";
import History from "./pages/History";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-zinc-800 px-6 py-4">
        <nav className="max-w-6xl mx-auto flex items-center justify-between">
          <NavLink to="/" className="text-lg font-bold tracking-tight text-zinc-100 no-underline">
            TestSmith
          </NavLink>
          <div className="flex gap-6 text-sm">
            <NavLink to="/" end className={({ isActive }) => isActive ? "text-[#8bff4a]" : "text-zinc-400 hover:text-zinc-200"}>
              New Run
            </NavLink>
            <NavLink to="/history" className={({ isActive }) => isActive ? "text-[#8bff4a]" : "text-zinc-400 hover:text-zinc-200"}>
              History
            </NavLink>
          </div>
        </nav>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        <Routes>
          <Route path="/" element={<NewRun />} />
          <Route path="/runs/:id" element={<LiveRun />} />
          <Route path="/runs/:id/detail" element={<RunDetail />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}
