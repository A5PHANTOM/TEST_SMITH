import { useEffect, useRef } from "react";

export default function LiveFeed({ events }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  const working = events.some(
    (e) => e.event === "agent_status" && e.status === "working"
  );

  return (
    <div className="glass">
      <div className="px-4 py-2.5 border-b border-white/[0.06] text-xs text-slate-500 font-semibold flex items-center gap-2">
        <span>Event Log</span>
        {working && (
          <span className="inline-block w-2 h-2 rounded-full bg-blue-400 animate-ping" />
        )}
      </div>
      <div className="p-4 max-h-64 overflow-auto text-xs space-y-1.5">
        {events.length === 0 && (
          <div className="flex items-center gap-2 text-slate-600">
            <span className="inline-block w-3 h-3 border-2 border-slate-600 border-t-transparent rounded-full animate-spin" />
            Waiting for events...
          </div>
        )}
        {events.map((ev, i) => (
          <div key={i} className="text-slate-400">
            <span className="text-slate-600">
              {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ""}
            </span>{" "}
            <span className="text-teal-400">{ev.event}</span>{" "}
            {JSON.stringify(ev)}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
