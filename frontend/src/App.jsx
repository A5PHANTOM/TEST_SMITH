import { Routes, Route, NavLink } from "react-router-dom";
import NewRun from "./pages/NewRun";
import LiveRun from "./pages/LiveRun";
import RunDetail from "./pages/RunDetail";
import History from "./pages/History";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="glass rounded-none border-x-0 border-t-0 mx-0 px-6 py-4">
        <nav className="max-w-6xl mx-auto flex items-center justify-between">
          <NavLink to="/" className="text-lg font-bold tracking-tight text-slate-100 no-underline hover:text-teal-400 transition-colors">
            TestSmith
          </NavLink>
          <div className="flex gap-6 text-sm">
            <NavLink to="/" end className={({ isActive }) => isActive ? "text-teal-400" : "text-slate-400 hover:text-slate-200 transition-colors"}>
              New Run
            </NavLink>
            <NavLink to="/history" className={({ isActive }) => isActive ? "text-teal-400" : "text-slate-400 hover:text-slate-200 transition-colors"}>
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
