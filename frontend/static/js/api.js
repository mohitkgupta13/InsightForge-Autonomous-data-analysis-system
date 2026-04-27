/* api.js — All fetch() helpers for the InsightForge API */

// When served via Flask (http://127.0.0.1:5000) use relative URLs.
// If you ever serve frontend separately, set this to "http://127.0.0.1:5000"
const BASE = "";

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

  let res;
  try {
    res = await fetch(`${BASE}${path}`, opts);
  } catch (networkErr) {
    throw new Error(
      `Network error — cannot reach the API. ` +
      `Is the Flask server running at http://127.0.0.1:5000? (${networkErr.message})`
    );
  }

  let json;
  try {
    json = await res.json();
  } catch {
    throw new Error(`HTTP ${res.status} — server returned non-JSON response`);
  }

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${json.message || JSON.stringify(json)}`);
  }
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
