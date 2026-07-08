const statusConfig = {
  idle: {
    dot: "bg-slate-600",
    border: "border-white/[0.06]",
    bg: "bg-white/[0.03]",
    text: "text-slate-400",
  },
  working: {
    dot: "bg-blue-400 animate-ping",
    border: "border-blue-500/30",
    bg: "bg-blue-500/10",
    text: "text-blue-300",
  },
  done: {
    dot: "bg-teal-400",
    border: "border-teal-500/30",
    bg: "bg-teal-500/10",
    text: "text-teal-300",
  },
};

export default function AgentStatus({ name, data }) {
  const status = data?.status || "idle";
  const detail = data?.detail || "";
  const cfg = statusConfig[status] || statusConfig.idle;

  return (
    <div className={`rounded-xl p-3 text-sm border ${cfg.bg} ${cfg.border}`}>
      <div className="flex items-center gap-2">
        <span className={`inline-block w-2 h-2 rounded-full ${cfg.dot}`} />
        <div className="font-semibold text-slate-200">{name}</div>
      </div>
      <div className={`capitalize text-xs mt-1 ${cfg.text}`}>{status}</div>
      {detail && <div className="text-xs mt-1 text-slate-500">{detail}</div>}
    </div>
  );
}
