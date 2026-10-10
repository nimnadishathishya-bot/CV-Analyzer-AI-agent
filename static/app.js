/**
 * HR CV Analyzer AI - Modern, User-Friendly Frontend Logic
 */

let selectedFile = null;
let currentReportData = null;

// Template options for 1-click test
const TEMPLATES = {
  python: `Role: Senior Backend Python Engineer
Experience: 4+ years of professional backend software development.
Key Requirements:
- Expert in Python, FastAPI or Django, and building RESTful microservices.
- Solid experience with PostgreSQL, SQLAlchemy, database indexing, and Redis caching.
- Familiar with Docker containerization, CI/CD pipelines, and AWS (EC2, S3).
- Strong understanding of asynchronous programming and API security.`,
  frontend: `Role: Senior Frontend React Developer
Experience: 3+ years modern frontend development.
Key Requirements:
- Strong mastery of JavaScript (ES6+), TypeScript, React, and Next.js.
- Deep expertise in responsive UI design, Tailwind CSS, HTML5, and CSS3.
- Experience with state management (Redux, Zustand) and client-side performance optimization.
- Familiar with REST APIs, GraphQL, and modern web testing frameworks (Jest, Playwright).`,
  hr: `Role: HR Talent Acquisition Specialist
Experience: 3+ years in technical recruitment and talent sourcing.
Key Requirements:
- Experience screening technical resumes and conducting competency-based behavioral interviews.
- Proficiency with modern ATS software (Greenhouse, Lever, or Workday).
- Strong relationship management, candidate pipeline tracking, and compensation negotiation skills.
- Excellent verbal and written communication skills.`
};

// Initialize app when DOM loads
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  checkBackendHealth();
  setupCharCounter();
});

// Theme Toggle
function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
    updateThemeIcon(true);
  } else {
    document.documentElement.classList.remove('dark');
    updateThemeIcon(false);
  }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.className = isDark ? "fa-solid fa-sun text-sm text-amber-400" : "fa-solid fa-moon text-sm text-slate-600";
  }
}

// Backend Health Check
async function checkBackendHealth() {
  const badge = document.getElementById('api-status-badge');
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      const data = await res.json();
      badge.className = "flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span>AI Ready (Groq)</span>`;
    } else {
      throw new Error();
    }
  } catch (err) {
    badge.className = "flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span><span>API Offline</span>`;
  }
}

// Character counter
function setupCharCounter() {
  const textarea = document.getElementById('job_description');
  const countDisplay = document.getElementById('jd-char-count');
  textarea.addEventListener('input', () => {
    countDisplay.textContent = `${textarea.value.length} characters`;
  });
}

// Quick Sample Templates
function loadSampleTemplate(type) {
  const textarea = document.getElementById('job_description');
  const text = TEMPLATES[type] || TEMPLATES.python;
  textarea.value = text;
  document.getElementById('jd-char-count').textContent = `${text.length} characters`;
  showToast("Template loaded into Job Description!");
}

// Load Demo Resume
async function loadDemoResume() {
  if (!document.getElementById('job_description').value.trim()) {
    loadSampleTemplate('python');
  }

  try {
    const res = await fetch('/static/sample_cv.pdf');
    if (res.ok) {
      const blob = await res.blob();
      const sampleFile = new File([blob], "Alex_Mercer_Senior_Engineer_CV.pdf", { type: 'application/pdf' });
      processFile(sampleFile);
      showToast("Sample candidate CV (PDF) loaded!");
      return;
    }
  } catch (err) {
    console.warn("Could not load /static/sample_cv.pdf directly, using fallback.", err);
  }

  const sampleCVText = `Alex Mercer - Senior Software Engineer
Email: alex.mercer@example.com | San Francisco, CA
Summary: 5+ years of experience engineering scalable Python web services, FastAPI microservices, PostgreSQL databases, Docker containers, and AWS.
Technical Skills: Python, FastAPI, Django, React, PostgreSQL, Docker, AWS, Redis.
Experience: Staff Backend Engineer at CloudScale Inc (2021 - Present). Built microservices handling 2M requests/day and cut DB latency by 45%.`;

  const blob = new Blob([sampleCVText], { type: 'application/pdf' });
  const sampleFile = new File([blob], "Alex_Mercer_Senior_Engineer_CV.pdf", { type: 'application/pdf' });
  processFile(sampleFile);
  showToast("Sample candidate CV loaded!");
}

// Drag & Drop
function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  document.getElementById('dropzone').classList.add('drag-over');
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  document.getElementById('dropzone').classList.remove('drag-over');
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  document.getElementById('dropzone').classList.remove('drag-over');
  const files = e.dataTransfer.files;
  if (files && files.length > 0) {
    processFile(files[0]);
  }
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files && files.length > 0) {
    processFile(files[0]);
  }
}

function processFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.txt')) {
    showError("Please upload a PDF file (.pdf).");
    return;
  }
  selectedFile = file;

  document.getElementById('dropzone-empty').classList.add('hidden');
  document.getElementById('dropzone-file-info').classList.remove('hidden');
  document.getElementById('dropzone-file-info').classList.add('flex');
  document.getElementById('file-name-display').textContent = file.name;

  const sizeKb = Math.round(file.size / 1024) || 1;
  document.getElementById('file-size-display').textContent = `${sizeKb} KB • Ready for analysis`;
  hideError();
}

function clearSelectedFile(e) {
  if (e) e.stopPropagation();
  selectedFile = null;
  document.getElementById('cv_file').value = '';
  document.getElementById('dropzone-empty').classList.remove('hidden');
  document.getElementById('dropzone-file-info').classList.add('hidden');
  document.getElementById('dropzone-file-info').classList.remove('flex');
}

// Form Submit
async function handleFormSubmit(e) {
  e.preventDefault();
  hideError();

  const jdText = document.getElementById('job_description').value.trim();
  if (!jdText || jdText.length < 15) {
    showError("Please enter a detailed Job Description with role requirements.");
    return;
  }

  if (!selectedFile) {
    showError("Please upload or choose a candidate CV (PDF file).");
    return;
  }

  setLoadingState(true);

  const formData = new FormData();
  formData.append('job_description', jdText);
  formData.append('cv_file', selectedFile);

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errJson.detail || `Server returned error (${response.status})`);
    }

    const data = await response.json();
    currentReportData = data;

    setTimeout(() => {
      setLoadingState(false);
      renderResults(data);
      showToast("CV screening analysis ready!");
    }, 300);

  } catch (err) {
    setLoadingState(false);
    showError(err.message || "Could not analyze CV. Please check your connection.");
  }
}

// UI State Toggles
function setLoadingState(isLoading) {
  const loadingEl = document.getElementById('loading-state');
  const resultsEl = document.getElementById('results-section');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('btn-text');

  if (isLoading) {
    loadingEl.classList.remove('hidden');
    loadingEl.classList.add('flex');
    resultsEl.classList.add('hidden');
    analyzeBtn.disabled = true;
    btnText.textContent = "Analyzing Candidate Fit...";
    loadingEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } else {
    loadingEl.classList.add('hidden');
    loadingEl.classList.remove('flex');
    analyzeBtn.disabled = false;
    btnText.textContent = "Analyze Candidate CV";
  }
}

function showError(msg) {
  const banner = document.getElementById('error-banner');
  document.getElementById('error-message-text').textContent = msg;
  banner.classList.remove('hidden');
  banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
  document.getElementById('error-banner').classList.add('hidden');
}

// Render Results
function renderResults(data) {
  const resultsEl = document.getElementById('results-section');
  resultsEl.classList.remove('hidden');

  // Candidate Name & Initials
  const name = data.candidate_name || "Candidate";
  document.getElementById('res-candidate-name').textContent = name;
  const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || "CD";
  document.getElementById('res-initials').textContent = initials;

  // Recommendation Badge
  const recBadge = document.getElementById('res-recommendation-badge');
  const recText = data.recommendation || "Evaluated";
  recBadge.textContent = recText;

  if (recText.toLowerCase().includes('strong')) {
    recBadge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800";
  } else if (recText.toLowerCase().includes('moderate')) {
    recBadge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 border border-indigo-300 dark:border-indigo-800";
  } else if (recText.toLowerCase().includes('potential')) {
    recBadge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800";
  } else {
    recBadge.className = "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-300 dark:border-rose-800";
  }

  // Score Gauge
  const score = data.match_score || 0;
  document.getElementById('res-score-number').textContent = `${score}%`;

  let scoreColor = "#10b981"; // Emerald
  if (score < 50) scoreColor = "#f43f5e"; // Rose
  else if (score < 75) scoreColor = "#f59e0b"; // Amber

  const gaugeEl = document.getElementById('score-circle-element');
  gaugeEl.style.setProperty('--score-percent', score);
  gaugeEl.style.setProperty('--score-color', scoreColor);

  // Executive Summary
  document.getElementById('res-summary-text').textContent = data.candidate_summary || "No summary available.";

  // Matched Skills
  const matchedList = data.matched_skills || [];
  const matchedContainer = document.getElementById('res-matched-skills');
  document.getElementById('matched-count-badge').textContent = matchedList.length;
  matchedContainer.innerHTML = '';
  if (matchedList.length > 0) {
    matchedList.forEach(s => {
      const tag = document.createElement('span');
      tag.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100/80 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 border border-emerald-300/80 dark:border-emerald-700/60 flex items-center space-x-1.5";
      tag.innerHTML = `<i class="fa-solid fa-check text-[10px]"></i><span>${s}</span>`;
      matchedContainer.appendChild(tag);
    });
  } else {
    matchedContainer.innerHTML = `<p class="text-xs text-slate-500 italic">No direct matching skills found.</p>`;
  }

  // Missing Skills
  const missingList = data.missing_skills || [];
  const missingContainer = document.getElementById('res-missing-skills');
  document.getElementById('missing-count-badge').textContent = missingList.length;
  missingContainer.innerHTML = '';
  if (missingList.length > 0) {
    missingList.forEach(s => {
      const tag = document.createElement('span');
      tag.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-100/80 dark:bg-rose-900/40 text-rose-800 dark:text-rose-300 border border-rose-300/80 dark:border-rose-700/60 flex items-center space-x-1.5";
      tag.innerHTML = `<i class="fa-solid fa-xmark text-[10px]"></i><span>${s}</span>`;
      missingContainer.appendChild(tag);
    });
  } else {
    missingContainer.innerHTML = `<p class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">All required skills identified!</p>`;
  }

  // Red Flags
  const redFlags = data.red_flags || [];
  const redFlagsContainer = document.getElementById('res-red-flags');
  redFlagsContainer.innerHTML = '';
  if (redFlags.length > 0) {
    redFlags.forEach(flag => {
      const card = document.createElement('div');
      card.className = "p-3 rounded-xl bg-amber-100/60 dark:bg-amber-900/30 border border-amber-300/80 dark:border-amber-700/60 text-xs text-amber-900 dark:text-amber-200 flex items-start space-x-2.5";
      card.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-600 dark:text-amber-400 mt-0.5 shrink-0"></i><span>${flag}</span>`;
      redFlagsContainer.appendChild(card);
    });
  } else {
    redFlagsContainer.innerHTML = `
      <div class="p-3 rounded-xl bg-emerald-100/60 dark:bg-emerald-900/30 border border-emerald-300/80 dark:border-emerald-700/60 text-xs text-emerald-900 dark:text-emerald-200 flex items-center space-x-2">
        <i class="fa-solid fa-circle-check text-emerald-600 dark:text-emerald-400"></i>
        <span>No significant red flags detected.</span>
      </div>`;
  }

  // Interview Questions
  const questions = data.interview_questions || [];
  const questionsContainer = document.getElementById('res-questions-container');
  questionsContainer.innerHTML = '';
  if (questions.length > 0) {
    questions.forEach((q, idx) => {
      const qText = typeof q === 'string' ? q : q.question;
      const rationale = q.rationale || "Evaluates candidate experience.";
      const expected = q.expected_answer || "Look for clear examples and structured approach.";

      const card = document.createElement('div');
      card.className = "clean-card p-5 space-y-3";
      card.innerHTML = `
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start space-x-3">
            <span class="w-6 h-6 rounded-lg bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-400 text-xs font-black flex items-center justify-center shrink-0">
              ${idx + 1}
            </span>
            <h4 class="text-sm font-bold text-slate-900 dark:text-white leading-snug">${qText}</h4>
          </div>
          <button onclick="copyQuestion(this, \`${qText.replace(/`/g, '\\`')}\`)" class="text-xs text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-2.5 py-1 rounded-md border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition flex items-center space-x-1 shrink-0">
            <i class="fa-regular fa-copy"></i>
            <span>Copy</span>
          </button>
        </div>
        <div class="pl-9 space-y-1.5 text-xs">
          <p class="text-slate-600 dark:text-slate-400"><strong class="text-indigo-600 dark:text-indigo-400 font-bold">Why Ask:</strong> ${rationale}</p>
          <p class="text-slate-600 dark:text-slate-400"><strong class="text-emerald-600 dark:text-emerald-400 font-bold">Look For:</strong> ${expected}</p>
        </div>
      `;
      questionsContainer.appendChild(card);
    });
  } else {
    questionsContainer.innerHTML = `<p class="text-xs text-slate-500 italic">No interview questions generated.</p>`;
  }

  // Switch to summary tab by default and scroll
  switchTab('summary');
  resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Tab Switching
function switchTab(tabId) {
  const tabs = ['summary', 'skills', 'questions', 'redflags'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-btn-${t}`);
    const panel = document.getElementById(`tab-panel-${t}`);
    if (btn && panel) {
      if (t === tabId) {
        btn.classList.add('active');
        panel.classList.remove('hidden');
      } else {
        btn.classList.remove('active');
        panel.classList.add('hidden');
      }
    }
  });
}

// Copy Handlers
function copyQuestion(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const original = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-check text-emerald-500"></i><span class="text-emerald-500">Copied!</span>`;
    setTimeout(() => {
      btn.innerHTML = original;
    }, 2000);
  });
}

function copySummaryText() {
  if (currentReportData && currentReportData.candidate_summary) {
    navigator.clipboard.writeText(currentReportData.candidate_summary).then(() => {
      showToast("Candidate Summary copied to clipboard!");
    });
  }
}

// Reset for another candidate
function resetAnalysis() {
  clearSelectedFile();
  document.getElementById('results-section').classList.add('hidden');
  document.getElementById('analyzer-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast("Ready for next candidate analysis!");
}

// Toast notification helper
function showToast(msg) {
  const toast = document.getElementById('toast');
  const msgEl = document.getElementById('toast-message');
  msgEl.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}
