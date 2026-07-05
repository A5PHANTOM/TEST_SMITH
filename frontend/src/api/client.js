const BASE = "/api";

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body}`);
  }
  return res.json();
}

export function createRun(data) {
  return request("/runs", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function listRuns() {
  return request("/runs");
}

export function getRun(id) {
  return request(`/runs/${id}`);
}

export function dismissRun(id) {
  return request(`/runs/${id}/dismiss`, { method: "POST" });
}
