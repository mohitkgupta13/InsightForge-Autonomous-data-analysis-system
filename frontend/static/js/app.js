/* app.js — InsightForge Single-Page Application Logic */

/* ── State ─────────────────────────────────────────────────────── */
const state = {
  sessionId: null,
  currentStep: 1,
  maxUnlocked: 1,
};

/* ── DOM refs ──────────────────────────────────────────────────── */
const $  = (id) => document.getElementById(id);
const $$ = (sel) => document.querySelectorAll(sel);

/* ── Boot ──────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  initUpload();
  $("btn-preprocess").addEventListener("click", runPreprocess);
  $("btn-analyze").addEventListener("click", runAnalyze);
  $("btn-visualize").addEventListener("click", runVisualize);
  $("btn-query").addEventListener("click", runQuery);
  $("btn-report").addEventListener("click", downloadReport);
  $("nlp-input").addEventListener("keydown", (e) => { if (e.key === "Enter") runQuery(); });
  activateSection(1);
});

/* ══════════════════════════════════════════════════════════════════
   STEP 1 — Upload
══════════════════════════════════════════════════════════════════ */
function initUpload() {
  const zone = $("upload-zone");
  const input = $("file-input");

  zone.addEventListener("dragover", (e) => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  input.addEventListener("change", () => { if (input.files[0]) handleFile(input.files[0]); });
  zone.addEventListener("click", (e) => {
    if (e.target.id !== "upload-btn") input.click();
  });
}

async function handleFile(file) {
  showLoader("Uploading file…");
  try {
    const fd = new FormData();
    fd.append("file", file);
    const res = await API.upload(fd);
    state.sessionId = res.session_id;

    $("info-filename").textContent = res.data.filename;
    $("info-rows").textContent = res.data.rows.toLocaleString();
    $("info-cols").textContent = res.data.columns;
    $("info-session").textContent = state.sessionId.slice(0, 8) + "…";
    $("upload-info").style.display = "";

    setStatus("active", `Session: ${state.sessionId.slice(0,8)}`);
    toast("File uploaded successfully!", "success");

    unlockStep(2);
    await loadPreview();
    goToStep(2);
  } catch (err) {
    toast(`Upload failed: ${err.message}`, "error");
    setStatus("error", "Upload failed");
  } finally {
    hideLoader();
  }
}

/* ══════════════════════════════════════════════════════════════════
   STEP 2 — Preview
══════════════════════════════════════════════════════════════════ */
async function loadPreview() {
  if (!state.sessionId) return;
  showLoader("Loading preview…");
  try {
    const res = await API.preview(state.sessionId, 15);
    renderTable($("preview-table-wrapper"), res.data.rows, res.data.columns.map(c => c.name));
  } catch (err) {
    toast(`Preview error: ${err.message}`, "error");
  } finally {
    hideLoader();
  }
}

/* ══════════════════════════════════════════════════════════════════
   STEP 3 — Preprocessing
══════════════════════════════════════════════════════════════════ */
async function runPreprocess() {
  if (!state.sessionId) return toast("Upload a file first.", "error");
  showLoader("Running preprocessing pipeline…");
  setStatus("loading", "Preprocessing…");
  try {
    const res = await API.preprocess(state.sessionId, {
      missing_strategy: $("sel-missing").value,
      outlier_method:   $("sel-outlier").value,
      encoding_method:  $("sel-encoding").value,
      scaling_method:   $("sel-scaling").value,
    });
    renderPreprocessReport(res.data.report);
    toast("Preprocessing complete!", "success");
    setStatus("active", "Preprocessed");
    unlockStep(3);
    goToStep(3);
  } catch (err) {
    toast(`Preprocessing failed: ${err.message}`, "error");
    setStatus("error", "Preprocessing failed");
  } finally {
    hideLoader();
  }
}

function renderPreprocessReport(report) {
  const card = $("preprocess-report-card");
  const [origR, origC] = report.original_shape || [0, 0];
  const [cleanR, cleanC] = report.cleaned_shape || [0, 0];

  card.innerHTML = `
    <div class="report-grid">
      <div class="report-stat">
        <div class="report-stat-label">Original Shape</div>
        <div class="report-stat-val">${origR} × ${origC}</div>
      </div>
      <div class="report-stat">
        <div class="report-stat-label">Cleaned Shape</div>
        <div class="report-stat-val" style="color:var(--accent)">${cleanR} × ${cleanC}</div>
      </div>
      <div class="report-stat">
        <div class="report-stat-label">Duplicates Removed</div>
        <div class="report-stat-val">${report.duplicates_removed ?? 0}</div>
      </div>
      <div class="report-stat">
        <div class="report-stat-label">Outliers Removed</div>
        <div class="report-stat-val">${report.outliers?.rows_removed ?? 0}</div>
      </div>
    </div>
    <div class="report-pills-section">
      <p class="card-title">Steps Completed</p>
      <div class="report-pills">
        ${(report.steps || []).map(s => `<span class="pill green">✓ ${s.replace(/_/g,' ')}</span>`).join("")}
      </div>
    </div>
    ${report.missing_value_handling?.imputed_columns && Object.keys(report.missing_value_handling.imputed_columns).length ?
      `<div style="margin-top:1rem">
        <p class="card-title">Imputed Columns</p>
        <div class="report-pills">
          ${Object.entries(report.missing_value_handling.imputed_columns).map(([col, info]) =>
            `<span class="pill blue">${col} (${info.strategy}, ${info.n_imputed} cells)</span>`
          ).join("")}
        </div>
      </div>` : ""}
    <div style="margin-top:1rem;color:var(--text-secondary);font-size:.85rem">${report.summary || ""}</div>
  `;
}

/* ══════════════════════════════════════════════════════════════════
   STEP 4 — Analysis
══════════════════════════════════════════════════════════════════ */
async function runAnalyze() {
  if (!state.sessionId) return toast("Preprocess first.", "error");
  const targetCol = $("target-col-input").value.trim() || null;
  showLoader("Training models… this may take a moment ⏳");
  setStatus("loading", "Analyzing…");
  try {
    const res = await API.analyze(state.sessionId, targetCol);
    const d = res.data;

    $("banner-problem-val").textContent = d.problem_type.charAt(0).toUpperCase() + d.problem_type.slice(1);
    $("banner-best-val").textContent = d.best_model || "—";
    const metricLabel = d.problem_type === "classification" ? "Accuracy" : d.problem_type === "regression" ? "R²" : "Silhouette";
    $("banner-metric-val").textContent = d.best_metric != null ? `${(d.best_metric * 100).toFixed(2)}%` : "—";

    renderModelTable(d.all_metrics, d.best_model, d.problem_type);
    toast("Analysis complete!", "success");
    setStatus("active", `Best: ${d.best_model}`);
    unlockStep(4);
    unlockStep(5);
    unlockStep(6);
    unlockStep(7);
    goToStep(4);
  } catch (err) {
    toast(`Analysis failed: ${err.message}`, "error");
    setStatus("error", "Analysis failed");
  } finally {
    hideLoader();
  }
}

function renderModelTable(metrics, bestModel, problemType) {
  const wrapper = $("model-table-wrapper");
  if (!metrics || typeof metrics !== "object") {
    wrapper.innerHTML = "<p class='placeholder-text'>No model metrics available.</p>";
    return;
  }

  // For clustering, metrics is the clustering result object, not a model map
  if (problemType === "clustering") {
    wrapper.innerHTML = `<div class="nlp-text-response">
      Best K: ${metrics.best_k} &nbsp;|&nbsp; 
      Silhouette Score: ${metrics.silhouette_score} &nbsp;|&nbsp;
      Inertia (best K): ${metrics.inertia_curve?.[metrics.best_k] ?? '—'}
    </div>`;
    return;
  }

  const isClass = problemType === "classification";
  const headers = isClass
    ? ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "CV Acc"]
    : ["Model", "MAE", "MSE", "RMSE", "R²", "CV R²"];

  const rows = Object.entries(metrics)
    .filter(([, v]) => !v.error)
    .map(([name, v]) => {
      const isBest = name === bestModel;
      if (isClass) {
        return `<tr ${isBest ? 'style="background:rgba(233,69,96,.08)"' : ""}>
          <td><strong>${isBest ? "🏆 " : ""}${name}</strong></td>
          <td>${pct(v.accuracy)}</td>
          <td>${pct(v.precision)}</td>
          <td>${pct(v.recall)}</td>
          <td>${pct(v.f1)}</td>
          <td>${v.roc_auc != null ? pct(v.roc_auc) : "—"}</td>
          <td>${pct(v.cv_accuracy)}</td>
        </tr>`;
      } else {
        return `<tr ${isBest ? 'style="background:rgba(233,69,96,.08)"' : ""}>
          <td><strong>${isBest ? "🏆 " : ""}${name}</strong></td>
          <td>${v.mae}</td>
          <td>${v.mse}</td>
          <td>${v.rmse}</td>
          <td>${v.r2}</td>
          <td>${v.cv_r2}</td>
        </tr>`;
      }
    });

  wrapper.innerHTML = `
    <table>
      <thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead>
      <tbody>${rows.join("")}</tbody>
    </table>`;
}

const pct = (v) => v != null ? `${(v * 100).toFixed(2)}%` : "—";

/* ══════════════════════════════════════════════════════════════════
   STEP 5 — Visualize
══════════════════════════════════════════════════════════════════ */
async function runVisualize() {
  if (!state.sessionId) return;
  showLoader("Generating charts…");
  try {
    const res = await API.visualize(state.sessionId);
    const grid = $("chart-grid");
    if (!res.data.charts.length) {
      grid.innerHTML = "<p class='placeholder-text'>No charts generated.</p>";
    } else {
      grid.innerHTML = res.data.charts.map(c => `
        <div class="chart-card">
          <div class="chart-name">${c.name.replace(/_/g," ")}</div>
          <img src="data:image/png;base64,${c.base64}" alt="${c.name}" loading="lazy" />
        </div>
      `).join("");
    }
    toast(`${res.data.count} chart(s) generated!`, "success");
    goToStep(5);
  } catch (err) {
    toast(`Visualization failed: ${err.message}`, "error");
  } finally {
    hideLoader();
  }
}

/* ══════════════════════════════════════════════════════════════════
   STEP 6 — NLP Query
══════════════════════════════════════════════════════════════════ */
async function runQuery() {
  const q = $("nlp-input").value.trim();
  if (!q) return toast("Enter a query first.", "info");
  if (!state.sessionId) return toast("Upload a file first.", "error");

  showLoader("Thinking…");
  try {
    const res = await API.query(state.sessionId, q);
    const d = res.data;
    const resultDiv = $("nlp-result");

    if (d.response_type === "text") {
      resultDiv.innerHTML = `<div class="nlp-text-response">${escHtml(d.data)}</div>`;
    } else if (d.response_type === "table") {
      if (!Array.isArray(d.data) || !d.data.length) {
        resultDiv.innerHTML = `<div class="nlp-text-response">No results found.</div>`;
      } else {
        const cols = Object.keys(d.data[0]);
        resultDiv.innerHTML = `
          <div class="table-wrapper" style="max-height:360px;overflow:auto">
            <table>
              <thead><tr>${cols.map(c => `<th>${escHtml(c)}</th>`).join("")}</tr></thead>
              <tbody>${d.data.map(row =>
                `<tr>${cols.map(c => `<td>${escHtml(String(row[c] ?? ""))}</td>`).join("")}</tr>`
              ).join("")}</tbody>
            </table>
          </div>`;
      }
    } else if (d.response_type === "chart") {
      resultDiv.innerHTML = `<div class="chart-card"><img src="data:image/png;base64,${d.data}" alt="chart" /></div>`;
    }
  } catch (err) {
    toast(`Query failed: ${err.message}`, "error");
  } finally {
    hideLoader();
  }
}

function setQuery(el) {
  $("nlp-input").value = el.textContent;
  $("nlp-input").focus();
}

/* ══════════════════════════════════════════════════════════════════
   STEP 7 — Report
══════════════════════════════════════════════════════════════════ */
async function downloadReport() {
  if (!state.sessionId) return toast("No session found.", "error");
  showLoader("Generating report…");
  try {
    const res = await API.report(state.sessionId);
    const card = $("report-card");
    const d = res.data;
    card.innerHTML = `
      <div class="report-grid">
        <div class="report-stat"><div class="report-stat-label">Filename</div><div style="font-size:.9rem">${d.session?.filename ?? "—"}</div></div>
        <div class="report-stat"><div class="report-stat-label">Problem Type</div><div class="report-stat-val">${d.analysis?.problem_type ?? "—"}</div></div>
        <div class="report-stat"><div class="report-stat-label">Best Model</div><div class="report-stat-val" style="color:var(--accent)">${d.analysis?.best_model ?? "—"}</div></div>
        <div class="report-stat"><div class="report-stat-label">Queries Made</div><div class="report-stat-val">${d.query_history?.length ?? 0}</div></div>
      </div>`;

    // Download as JSON
    const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `insightforge_report_${state.sessionId.slice(0,8)}.json`;
    a.click();
    URL.revokeObjectURL(url);

    toast("Report downloaded!", "success");
    goToStep(7);
  } catch (err) {
    toast(`Report failed: ${err.message}`, "error");
  } finally {
    hideLoader();
  }
}

/* ══════════════════════════════════════════════════════════════════
   UI Helpers
══════════════════════════════════════════════════════════════════ */
function activateSection(step) {
  document.querySelectorAll(".section").forEach((s, i) => {
    s.classList.toggle("active", i + 1 === step);
  });
  document.querySelectorAll(".prog-step").forEach((s) => {
    const n = parseInt(s.dataset.step);
    s.classList.toggle("active", n === step);
    s.classList.toggle("done", n < step && n <= state.maxUnlocked);
  });
}

function unlockStep(n) {
  if (n > state.maxUnlocked) state.maxUnlocked = n;
  const stepEl = document.querySelector(`.prog-step[data-step="${n}"]`);
  if (stepEl) stepEl.style.pointerEvents = "auto";
}

function goToStep(n) {
  if (n > state.maxUnlocked) return;
  state.currentStep = n;
  activateSection(n);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderTable(wrapper, rows, cols) {
  if (!rows || !rows.length) {
    wrapper.innerHTML = "<p class='placeholder-text'>No data to display.</p>";
    return;
  }
  const headers = cols || Object.keys(rows[0]);
  wrapper.innerHTML = `
    <table>
      <thead><tr>${headers.map(h => `<th>${escHtml(h)}</th>`).join("")}</tr></thead>
      <tbody>${rows.map(row =>
        `<tr>${headers.map(h => `<td>${escHtml(String(row[h] ?? ""))}</td>`).join("")}</tr>`
      ).join("")}</tbody>
    </table>`;
}

function showLoader(msg = "Processing…") {
  $("loader-msg").textContent = msg;
  $("loader-overlay").classList.add("visible");
}

function hideLoader() {
  $("loader-overlay").classList.remove("visible");
}

function setStatus(type, text) {
  const dot = $("status-dot");
  dot.className = `status-dot ${type}`;
  $("status-text").textContent = text;
}

/* ── Toast (success / info only) ────────────────────────────── */
let _toastTimer;
function toast(msg, type = "info") {
  if (type === "error") {
    logError(msg);
    return;
  }
  const el = $("toast");
  el.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove("show"), 4000);
}

/* ── Persistent Error Console ────────────────────────────── */
function logError(msg) {
  const console_el = $("error-console");
  const body = $("error-console-body");
  console_el.style.display = "flex";

  const now = new Date().toLocaleTimeString();
  const line = document.createElement("div");
  line.className = "err-line";
  line.innerHTML = `<span class="err-time">[${now}]</span>${escHtml(msg)}`;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;

  // Also log to browser console
  console.error("[InsightForge]", msg);
}

function clearErrors() {
  $("error-console-body").innerHTML = "";
  $("error-console").style.display = "none";
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
