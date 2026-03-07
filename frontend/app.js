// const API_URL = "http://localhost:8000/api/v1";
// const API_URL = "/api/v1";

// since the code is being pushed on render i am changing the backend api end point to the service's end poin
// if want to run locally then just have to comment the below const API_URL and uncomment the above one.

const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:8000/api/v1"        // local dev
  : "https://ai-resume-analyzer-backend-ks7b.onrender.com//api/v1";  // production



// --- File upload UI ---
const fileDrop = document.getElementById("file-drop");
const fileInput = document.getElementById("resume");
const fileLabel = document.getElementById("file-label");

fileDrop.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) {
    fileLabel.textContent = `✅ ${fileInput.files[0].name}`;
    fileDrop.classList.add("has-file");
  }
});

// Drag and drop support
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

// --- Main analyze function ---
async function analyzeResume() {
  const file = fileInput.files[0];
  const jd   = document.getElementById("jd").value.trim();

  // Validate inputs before hitting API
  if (!file) return showError("Please upload a PDF resume.");
  if (!jd)   return showError("Please paste a job description.");

  // UI state: show loading
  show("loading-section");
  hide("input-section");
  hide("results-section");
  hide("error-box");

  try {
    // FormData because we're sending file + text together
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jd);

    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData
      // DO NOT set Content-Type header manually
      // Browser sets it automatically with the correct boundary for multipart
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Something went wrong");
    }

    const data = await response.json();
    renderResults(data);

  } catch (err) {
    show("input-section");
    showError(err.message);
  } finally {
    hide("loading-section");
  }
}

// --- Render results ---
function renderResults(data) {
  // Fit score with color
  const scoreEl = document.getElementById("fit-score");
  const scoreCircle = document.querySelector(".score-circle");
  scoreEl.textContent = data.fit_score;
  scoreCircle.className = "score-circle";
  if (data.fit_score >= 70)      scoreCircle.classList.add("score-high");
  else if (data.fit_score >= 40) scoreCircle.classList.add("score-medium");
  else                           scoreCircle.classList.add("score-low");

  // Summary
  document.getElementById("summary-text").textContent = data.summary;

  // Strengths list
  const strengthsList = document.getElementById("strengths-list");
  strengthsList.innerHTML = data.strengths
    .map(s => `<li>${s}</li>`)
    .join("");

  // Improvements list
  const improvementsList = document.getElementById("improvements-list");
  improvementsList.innerHTML = data.improvements
    .map(i => `<li>${i}</li>`)
    .join("");

  // Cover letter
  document.getElementById("cover-letter-text").textContent = data.cover_letter;

  // Show results
  hide("input-section");
  show("results-section");
}

// --- Copy cover letter ---
function copyCoverLetter() {
  const text = document.getElementById("cover-letter-text").textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(".cover-header button");
    btn.textContent = "Copied!";
    setTimeout(() => btn.textContent = "Copy", 2000);
  });
}

// --- Reset ---
function resetForm() {
  fileInput.value = "";
  fileLabel.textContent = "Click to upload or drag & drop";
  fileDrop.classList.remove("has-file");
  document.getElementById("jd").value = "";
  show("input-section");
  hide("results-section");
  hide("error-box");
}

// --- Helpers ---
function show(id) { document.getElementById(id).classList.remove("hidden"); }
function hide(id) { document.getElementById(id).classList.add("hidden"); }
function showError(msg) {
  const box = document.getElementById("error-box");
  box.textContent = msg;
  box.classList.remove("hidden");
}