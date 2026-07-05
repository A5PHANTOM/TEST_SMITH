import { useEffect, useRef, useState, useCallback } from "react";

export default function useRunSocket(runId) {
  const ws = useRef(null);
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);

  const addEvent = useCallback((event) => {
    setEvents((prev) => [...prev, { ...event, timestamp: Date.now() }]);
  }, []);

  useEffect(() => {
    if (!runId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/runs/${runId}`;

    ws.current = new WebSocket(url);

    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);
    ws.current.onerror = () => setConnected(false);

    ws.current.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        addEvent(data);
      } catch {
        // ignore non-JSON messages
      }
    };

    return () => {
      ws.current?.close();
    };
  }, [runId, addEvent]);

  return { events, connected };
}
