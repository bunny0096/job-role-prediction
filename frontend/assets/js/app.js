const form = document.getElementById("resume-form");
const fileInput = document.getElementById("resume-input");
const dropzone = document.getElementById("dropzone");
const submitBtn = document.getElementById("submit-btn");
const statusText = document.getElementById("status-text");

const resultsSection = document.getElementById("results-section");
const predictedRoleEl = document.getElementById("predicted-role");
const confidenceEl = document.getElementById("confidence");
const processedTimeEl = document.getElementById("processed-time");
const topMatchesEl = document.getElementById("top-matches");
const skillCloudEl = document.getElementById("skill-cloud");
const resumeScoreValueEl = document.getElementById("resume-score-value");
const resumeScoreSummaryEl = document.getElementById("resume-score-summary");
const industryFitScoreEl = document.getElementById("industry-fit-score");
const comparisonRoleEl = document.getElementById("comparison-role");
const alignmentScoreEl = document.getElementById("alignment-score");
const requiredSkillsEl = document.getElementById("required-skills");
const matchedSkillsEl = document.getElementById("matched-skills");
const missingSkillsEl = document.getElementById("missing-skills");
const sectionBreakdownEl = document.getElementById("section-breakdown");
const improvementListEl = document.getElementById("improvement-list");
const interviewQuestionsEl = document.getElementById("interview-questions");
const historyEl = document.getElementById("history");
const networkInfoEl = document.getElementById("network-info");

const HISTORY_KEY = "rolescope_history_v1";

initialize();

function initialize() {
  bindDropzone();
  renderNetworkInfo();
  renderHistory();

  form.addEventListener("submit", onSubmit);
}

function bindDropzone() {
  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, () => {
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    if (!event.dataTransfer.files?.length) {
      return;
    }

    const file = event.dataTransfer.files[0];
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
  });
}

async function onSubmit(event) {
  event.preventDefault();

  if (!fileInput.files?.length) {
    updateStatus("Choose a resume file first.", true);
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("resume", file);

  submitBtn.disabled = true;
  updateStatus("Analyzing resume...", false);

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Prediction failed.");
    }

    renderResults(payload);
    addHistory(payload, file.name);
    updateStatus("Prediction complete.", false);
  } catch (error) {
    updateStatus(error.message || "Something went wrong.", true);
  } finally {
    submitBtn.disabled = false;
  }
}

function renderResults(payload) {
  resultsSection.classList.remove("hidden");

  predictedRoleEl.textContent = payload.predicted_role;
  confidenceEl.textContent = Number(payload.confidence).toFixed(2);

  const processedUtc = payload.processed_at_utc || new Date().toISOString();
  const localTime = formatDate(processedUtc);
  processedTimeEl.textContent = `Processed: ${localTime.local} | UTC: ${localTime.utc}`;

  topMatchesEl.innerHTML = payload.top_matches
    .map(
      (match) => `
      <article class="match-card">
        <div class="match-head">
          <h5 class="match-role">${escapeHtml(match.role)}</h5>
          <p class="match-score">${Number(match.confidence).toFixed(2)}%</p>
        </div>
        <div class="progress"><div class="progress-fill" style="width: ${Math.min(100, Math.max(0, match.confidence))}%"></div></div>
        <p class="match-desc">${escapeHtml(match.description)}</p>
      </article>
      `
    )
    .join("");

  if (payload.resume_skills?.length) {
    skillCloudEl.innerHTML = payload.resume_skills
      .slice(0, 30)
      .map((skill) => `<span class="skill-chip">${escapeHtml(skill)}</span>`)
      .join("");
  } else {
    skillCloudEl.innerHTML = '<span class="skill-chip">No recognized skills found</span>';
  }

  renderResumeScore(payload.resume_score);
  renderSkillComparison(payload.skill_comparison);
  renderSectionBreakdown(payload.resume_score?.section_breakdown || []);
  renderInsightList(
    improvementListEl,
    payload.improvement_suggestions || [],
    "No immediate suggestions."
  );
  renderQuestionList(
    interviewQuestionsEl,
    payload.interview_questions || [],
    "No interview questions generated."
  );
}

function renderNetworkInfo() {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "Unknown";
  const origin = window.location.origin;

  networkInfoEl.textContent = `Current URL: ${origin} | Your timezone: ${timezone}`;
}

function addHistory(payload, fileName) {
  const existing = getHistory();
  const item = {
    fileName,
    role: payload.predicted_role,
    confidence: Number(payload.confidence).toFixed(2),
    processedAtUtc: payload.processed_at_utc || new Date().toISOString(),
  };

  const updated = [item, ...existing].slice(0, 10);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  renderHistory();
}

function renderHistory() {
  const history = getHistory();
  if (!history.length) {
    historyEl.innerHTML = "<li>No submissions yet.</li>";
    return;
  }

  historyEl.innerHTML = history
    .map((entry) => {
      const dt = formatDate(entry.processedAtUtc);
      return `
        <li>
          <span><strong>${escapeHtml(entry.role)}</strong> (${escapeHtml(entry.confidence)}%) - ${escapeHtml(entry.fileName)}</span>
          <span>${escapeHtml(dt.local)}</span>
        </li>
      `;
    })
    .join("");
}

function getHistory() {
  try {
    const value = localStorage.getItem(HISTORY_KEY);
    if (!value) {
      return [];
    }

    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
}

function updateStatus(message, isError) {
  statusText.textContent = message;
  statusText.style.color = isError ? "#ff9b9b" : "#b8c9cf";
}

function renderResumeScore(scoreCard) {
  if (!scoreCard) {
    resumeScoreValueEl.textContent = "0";
    resumeScoreSummaryEl.textContent = "No score available.";
    industryFitScoreEl.textContent = "Industry fit: 0/20";
    return;
  }

  resumeScoreValueEl.textContent = escapeHtml(scoreCard.score);
  resumeScoreSummaryEl.textContent = scoreCard.summary || "No score summary available.";
  industryFitScoreEl.textContent = `Industry fit: ${Number(
    scoreCard.industry_fit_score || 0
  )}/${Number(scoreCard.industry_fit_max_score || 20)}`;
}

function renderSkillComparison(comparison) {
  if (!comparison) {
    comparisonRoleEl.textContent = "No role comparison available.";
    alignmentScoreEl.textContent = "0% aligned";
    requiredSkillsEl.innerHTML = '<span class="skill-chip">No role skills available</span>';
    matchedSkillsEl.innerHTML = '<span class="skill-chip">No matched skills</span>';
    missingSkillsEl.innerHTML = '<span class="skill-chip missing">No missing skills</span>';
    return;
  }

  comparisonRoleEl.textContent = `Target role: ${comparison.role}`;
  alignmentScoreEl.textContent = `${Number(comparison.alignment_percentage || 0)}% aligned`;
  renderSkillGroup(requiredSkillsEl, comparison.required_skills || [], false, "No role skills listed.");
  renderSkillGroup(matchedSkillsEl, comparison.matched_skills || [], false, "No matched skills found.");
  renderSkillGroup(missingSkillsEl, comparison.missing_skills || [], true, "No missing skills identified.");
}

function renderSkillGroup(container, skills, isMissing, emptyText) {
  if (!skills.length) {
    container.innerHTML = `<span class="skill-chip${isMissing ? " missing" : ""}">${escapeHtml(
      emptyText
    )}</span>`;
    return;
  }

  container.innerHTML = skills
    .map(
      (skill) =>
        `<span class="skill-chip${isMissing ? " missing" : ""}">${escapeHtml(skill)}</span>`
    )
    .join("");
}

function renderSectionBreakdown(sections) {
  if (!sections.length) {
    sectionBreakdownEl.innerHTML = '<article class="section-card">No section analysis available.</article>';
    return;
  }

  sectionBreakdownEl.innerHTML = sections
    .map((section) => {
      const ratio = Number(section.max_score)
        ? Math.min(100, Math.max(0, (Number(section.score) / Number(section.max_score)) * 100))
        : 0;
      return `
        <article class="section-card ${section.detected ? "detected" : "missing"}">
          <div class="section-head">
            <h5>${escapeHtml(section.name)}</h5>
            <span>${escapeHtml(section.score)}/${escapeHtml(section.max_score)}</span>
          </div>
          <div class="progress compact"><div class="progress-fill" style="width: ${ratio}%"></div></div>
          <p class="section-status">${section.detected ? "Detected" : "Missing"}</p>
          <p class="section-feedback">${escapeHtml(section.feedback)}</p>
        </article>
      `;
    })
    .join("");
}

function renderInsightList(container, items, emptyText) {
  if (!items.length) {
    container.innerHTML = `<li>${escapeHtml(emptyText)}</li>`;
    return;
  }

  container.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderQuestionList(container, items, emptyText) {
  if (!items.length) {
    container.innerHTML = `<li>${escapeHtml(emptyText)}</li>`;
    return;
  }

  container.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function formatDate(isoDate) {
  const date = new Date(isoDate);
  const local = date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });

  const utc = date.toLocaleString("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });

  return { local, utc };
}

function escapeHtml(text) {
  if (text === null || text === undefined) {
    return "";
  }

  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
