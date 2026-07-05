import { useEffect, useRef } from "react";

export default function LiveFeed({ events }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  return (
    <div className="border border-zinc-800 rounded">
      <div className="px-4 py-2 border-b border-zinc-800 text-xs text-zinc-500 font-semibold">
        Event Log
      </div>
      <div className="p-4 max-h-64 overflow-auto text-xs space-y-1">
        {events.length === 0 && (
          <div className="text-zinc-600">Waiting for events...</div>
        )}
        {events.map((ev, i) => (
          <div key={i} className="text-zinc-400">
            <span className="text-zinc-600">{new Date(ev.timestamp).toLocaleTimeString()}</span>{" "}
            <span className="text-[#8bff4a]">{ev.event}</span>{" "}
            {JSON.stringify(ev)}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
