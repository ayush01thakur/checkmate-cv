// const API_URL = "http://localhost:8000/api/v1";

// since the code is being pushed on render i am changing the backend api end point to the service's end poin
// if want to run locally then just have to comment the below const API_URL and uncomment the above one.


const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:8000/api/v1"
  : "https://ai-resume-analyzer-backend-ks7b.onrender.com/api/v1";

// Global state — frontend holds this between steps
let currentAnalysis = null;

// ── Stats ──────────────────────────────────────────
async function fetchStats() {
  try {
    const base = API_URL.replace("/api/v1", "");
    const res = await fetch(`${base}/api/v1/stats`);
    const data = await res.json();
    document.getElementById("analyzed-count").textContent = data.analyzed;
    document.getElementById("updated-count").textContent  = data.updated;
  } catch (err) {
    // Fail silently — stats are non-critical
    console.warn("Could not fetch stats:", err);
  }
}

// Fetch stats on page load
fetchStats();

// ── File upload UI ─────────────────────────────────
const fileDrop  = document.getElementById("file-drop");
const fileInput = document.getElementById("resume");
const fileLabel = document.getElementById("file-label");

fileDrop.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) {
    fileLabel.textContent = `✅ ${fileInput.files[0].name}`;
    fileDrop.classList.add("has-file");
  }
});

fileDrop.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDrop.style.borderColor = "var(--primary)";
});
fileDrop.addEventListener("dragleave", () => {
  fileDrop.style.borderColor = "";
});
fileDrop.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file && file.type === "application/pdf") {
    fileInput.files = e.dataTransfer.files;
    fileLabel.textContent = `✅ ${file.name}`;
    fileDrop.classList.add("has-file");
  } else {
    showError("Please drop a PDF file.");
  }
});

// ── Analyze ────────────────────────────────────────
async function analyzeResume() {
  const file = fileInput.files[0];
  const jd   = document.getElementById("jd").value.trim();

  if (!file) return showError("Please upload a PDF resume.");
  if (!jd)   return showError("Please paste a job description.");

  show("loading-section");
  hide("input-section");
  hide("results-section");
  hide("error-box");

  try {
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

    const res = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData
      // DO NOT set Content-Type manually — browser handles multipart boundary
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Analysis failed");
    }

    const data = await res.json();

    // Store state for enhancement flow
    currentAnalysis = {
      resume_text:     data.resume_text,
      job_description: jd,
      improvements:    data.improvements,
      fit_score:       data.fit_score
    };

    renderResults(data);
    fetchStats(); // update count display

  } catch (err) {
    show("input-section");
    showError(err.message);
  } finally {
    hide("loading-section");
  }
}

// ── Render analysis results ────────────────────────
function renderResults(data) {
  // Score circle color
  const scoreEl     = document.getElementById("fit-score");
  const scoreCircle = document.querySelector(".score-circle");
  scoreEl.textContent   = data.fit_score;
  scoreCircle.className = "score-circle";
  if      (data.fit_score >= 70) scoreCircle.classList.add("score-high");
  else if (data.fit_score >= 40) scoreCircle.classList.add("score-medium");
  else                           scoreCircle.classList.add("score-low");

  document.getElementById("summary-text").textContent = data.summary;

  document.getElementById("strengths-list").innerHTML =
    data.strengths.map(s => `<li>${s}</li>`).join("");

  document.getElementById("improvements-list").innerHTML =
    data.improvements.map(i => `<li>${i}</li>`).join("");

  document.getElementById("cover-letter-text").textContent = data.cover_letter;

  hide("input-section");
  show("results-section");
}

// ── Enhancement flow ───────────────────────────────
async function showEnhanceForm() {
  if (!currentAnalysis) return showError("Please analyze a resume first.");

  show("loading-section");
  hide("results-section");
  hide("error-box");

  try {
    const res = await fetch(`${API_URL}/generate-form`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentAnalysis.improvements)
    });

    if (!res.ok) throw new Error("Could not generate form");

    const formDef = await res.json();
    renderDynamicForm(formDef.fields);

  } catch (err) {
    show("results-section");
    showError(err.message);
  } finally {
    hide("loading-section");
  }
}

function renderDynamicForm(fields) {
  const sectionLabels = {
    projects:     "🛠️ Projects",
    experience:   "💼 Work Experience",
    skills:       "⚡ Skills",
    achievements: "🏆 Achievements",
    education:    "🎓 Education",
    summary:      "👤 About You"
  };

  // Group fields by section
  const sections = {};
  fields.forEach(f => {
    if (!sections[f.section]) sections[f.section] = [];
    sections[f.section].push(f);
  });

  let html = `<div class="card" id="enhance-section">
    <h2 style="font-size:1.3rem;font-weight:800;color:var(--primary)">
      ✨ Update Your Resume
    </h2>
    <p style="color:var(--muted);font-size:14px">
      Fill in what you have. Fields marked
      <span class="required">*</span> are required.
      Everything else is optional.
    </p>`;

  Object.entries(sections).forEach(([section, sectionFields]) => {
    html += `<div class="form-section">
      <h3>${sectionLabels[section] || section}</h3>`;

    sectionFields.forEach(f => {
      const req = f.required
        ? `<span class="required">*</span>`
        : `<span class="optional">(optional)</span>`;

      if (f.type === "textarea") {
        html += `<div class="form-group">
          <label>${f.label} ${req}</label>
          <textarea id="${f.id}" placeholder="${f.placeholder}" rows="4"></textarea>
        </div>`;
      } else if (f.type === "select") {
        html += `<div class="form-group">
          <label>${f.label} ${req}</label>
          <select id="${f.id}">
            <option value="">Select...</option>
            <option value="yes">Yes, I have work experience</option>
            <option value="no">No, I'm a fresher</option>
          </select>
        </div>`;
      } else {
        html += `<div class="form-group">
          <label>${f.label} ${req}</label>
          <input type="${f.type}" id="${f.id}"
            placeholder="${f.placeholder}" />
        </div>`;
      }
    });

    html += `</div>`; // close form-section
  });

  html += `<div class="button-row">
    <button class="btn-secondary" onclick="goBackToResults()">← Back</button>
    <button class="btn-primary" onclick="submitEnhancement()">
      ✨ Generate My Resume
    </button>
  </div>
  </div>`; // close card

  document.getElementById("enhance-container").innerHTML = html;
  hide("results-section");
  show("enhance-container");
}

async function submitEnhancement() {
  // Collect all filled form values
  const formData = {};
  document
    .querySelectorAll("#enhance-section input, #enhance-section textarea, #enhance-section select")
    .forEach(el => {
      if (el.value.trim()) formData[el.id] = el.value.trim();
    });

  show("loading-section");
  hide("enhance-container");
  hide("error-box");

  try {
    const res = await fetch(`${API_URL}/enhance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text:     currentAnalysis.resume_text,
        job_description: currentAnalysis.job_description,
        improvements:    currentAnalysis.improvements,
        form_data:       formData
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Enhancement failed");
    }

    const data = await res.json();
    renderEnhancedResults(data);
    fetchStats(); // update updated count

  } catch (err) {
    show("enhance-container");
    showError(err.message);
  } finally {
    hide("loading-section");
  }
}

// ── Render enhanced results ────────────────────────
function renderEnhancedResults(data) {
  const scoreClass = data.new_fit_score >= 70 ? "score-high"
    : data.new_fit_score >= 40 ? "score-medium" : "score-low";

  document.getElementById("enhanced-results").innerHTML = `
    <div class="card">

      <h2 style="font-size:1.3rem;font-weight:800;color:var(--primary)">
        ✅ Your Enhanced Resume
      </h2>

      <div class="score-row">
        <div class="score-circle ${scoreClass}">
          <span>${data.new_fit_score}</span>
          <small>New Score</small>
        </div>
        <p class="summary">
          Your resume has been optimized for this role.
          Download it below and use the cover letter and cold message to apply.
        </p>
      </div>

      <button class="btn-primary" onclick="downloadResume()">
        📄 Download Resume (Print → Save as PDF)
      </button>

      <div class="result-block cover-letter">
        <div class="cover-header">
          <h3>📄 Cover Letter</h3>
          <button onclick="copyText('enhanced-cover')">Copy</button>
        </div>
        <p id="enhanced-cover" style="font-size:14px;color:var(--muted);line-height:1.8;white-space:pre-wrap">
          ${data.cover_letter}
        </p>
      </div>

      <div class="cold-message-block">
        <div class="cover-header">
          <h3>💬 Cold Message Template</h3>
          <button onclick="copyText('cold-message-text')">Copy</button>
        </div>
        <p id="cold-message-text"
           style="font-size:14px;color:var(--muted);line-height:1.8;white-space:pre-wrap">
          ${data.cold_message}
        </p>
      </div>

      <div class="button-row">
        <button class="btn-secondary" onclick="resetForm()">
          🔄 Start Over
        </button>
      </div>

    </div>`;

  // Store HTML for PDF download
  window.resumeHTML = data.html;

  hide("enhance-container");
  show("enhanced-results");
}

// ── Download resume as PDF ─────────────────────────
function downloadResume() {
  const win = window.open("", "_blank");
  win.document.write(window.resumeHTML);
  win.document.close();
  // Small delay so content loads before print dialog
  setTimeout(() => win.print(), 500);
}

// ── Helpers ────────────────────────────────────────
function goBackToResults() {
  hide("enhance-container");
  show("results-section");
}

function resetForm() {
  fileInput.value = "";
  fileLabel.textContent = "Click to upload or drag & drop";
  fileDrop.classList.remove("has-file");
  document.getElementById("jd").value = "";
  currentAnalysis = null;
  document.getElementById("enhanced-results").innerHTML = "";
  document.getElementById("enhance-container").innerHTML = "";
  hide("results-section");
  hide("enhanced-results");
  hide("enhance-container");
  hide("error-box");
  show("input-section");
}

function show(id) { document.getElementById(id).classList.remove("hidden"); }
function hide(id) { document.getElementById(id).classList.add("hidden");    }

function showError(msg) {
  const box = document.getElementById("error-box");
  box.textContent = msg;
  box.classList.remove("hidden");
  setTimeout(() => box.classList.add("hidden"), 5000);
}

function copyText(id) {
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => {
    // Find the copy button nearest to this element and flash it
    const el  = document.getElementById(id);
    const btn = el.closest(".result-block, .cold-message-block")
                  ?.querySelector(".cover-header button");
    if (btn) {
      btn.textContent = "Copied!";
      setTimeout(() => btn.textContent = "Copy", 2000);
    }
  });
}