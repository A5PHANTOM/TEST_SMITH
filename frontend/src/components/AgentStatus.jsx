const statusColors = {
  idle: "bg-zinc-800 border-zinc-700 text-zinc-400",
  working: "bg-blue-900 border-blue-700 text-blue-200",
  done: "bg-green-900 border-green-700 text-green-200",
};

export default function AgentStatus({ name, data }) {
  const status = data?.status || "idle";
  const detail = data?.detail || "";
  const colors = statusColors[status] || statusColors.idle;

  return (
    <div className={`border rounded p-3 text-sm ${colors}`}>
      <div className="font-semibold mb-1">{name}</div>
      <div className="capitalize text-xs">{status}</div>
      {detail && <div className="text-xs mt-1 opacity-70">{detail}</div>}
    </div>
  );
}
