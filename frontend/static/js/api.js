/* api.js — All fetch() helpers for the InsightForge API */

const BASE = "http://127.0.0.1:5000";

async function apiRequest(method, path, body = null, isFormData = false) {
  const opts = { method };
  if (body) {
    if (isFormData) {
      opts.body = body;
    } else {
      opts.headers = { "Content-Type": "application/json" };
      opts.body = JSON.stringify(body);
    }
  }
  const res = await fetch(`${BASE}${path}`, opts);
  const json = await res.json();
  if (!res.ok) throw new Error(json.message || `HTTP ${res.status}`);
  return json;
}

const API = {
  upload: (formData) => apiRequest("POST", "/api/upload", formData, true),
  preview: (sid, rows = 10) => apiRequest("GET", `/api/preview/${sid}?rows=${rows}`),
  preprocess: (sid, opts) => apiRequest("POST", `/api/preprocess/${sid}`, opts),
  analyze: (sid, targetCol) => apiRequest("POST", `/api/analyze/${sid}`, { target_col: targetCol || null }),
  results: (sid) => apiRequest("GET", `/api/results/${sid}`),
  visualize: (sid) => apiRequest("GET", `/api/visualize/${sid}`),
  query: (sid, q) => apiRequest("POST", `/api/query/${sid}`, { query: q }),
  report: (sid) => apiRequest("GET", `/api/report/${sid}`),
};
