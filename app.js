const DATA_URL = "/api/practice-data";
const QUESTION_ART_VERSION = "no-question-art-v1";

const state = {
  dataset: null,
  activity: null,
  modes: [],
  answerGroups: [],
  questionIndex: 0,
  recentQuestionIndexes: [],
  mode: "easy",
  bank: [],
  placements: {},
  submitted: false,
  lastResult: null,
  score: 0,
  streak: 5,
  user: null,
  csrfToken: null,
  authMode: "signup",
  progress: { events: [], attempts: 0, averagePercent: 0 },
  datasets: [],
  selectedDataset: null,
  adminActivities: [],
  assignments: [],
  typeActivity: null,
  typePlacements: {},
  typeSubmitted: false,
  selectedTypeGroup: "",
  continuousTablePlacements: {},
  continuousTableSubmitted: {},
  continuousTableSelectedId: "",
  continuousTableView: "list",
  datasetFilters: {
    classLevel: "",
    subject: "",
    book: "",
  },
};

const typeLabels = {
  explain: "Explain",
  compare_contrast: "Compare / Contrast",
  cause_effect: "Cause / Effect",
  process_sequence: "Process / Sequence",
  pros_cons: "Pros / Cons",
  problem_solution: "Problem / Solution",
  fill_blanks: "Fill in the Blanks",
  true_false_not_given: "True / False / Not Given",
  short_answer_key_points: "Short Answer - Key Points",
  match_following: "Match the Following",
  data_chart_table: "Data / Chart / Table",
  paragraph_essay_structure: "Paragraph / Essay Structure",
  definition_term: "Definition / Term Based",
  timeline_chronological_order: "Timeline / Chronological Order",
  identify_main_idea: "Identify Main Idea",
  evidence_support_statement: "Evidence / Support",
  sequencing_steps_process: "Sequencing Steps",
  choose_correct_ending: "Choose Correct Ending",
  multiple_correct_answers: "Multiple Correct Answers",
  formulate_question: "Formulate a Question",
  assertion_reason: "Assertion / Reason",
};

const subjectOrder = [
  "Science",
  "Mathematics",
  "English",
  "Social Science",
  "Social",
  "Physical Education",
  "Arts",
  "Vocational Education",
];

const els = {};

function cacheElements() {
  [
    "landingView",
    "dashboardView",
    "authForm",
    "authMessage",
    "authSubmit",
    "nameField",
    "nameInput",
    "emailInput",
    "passwordInput",
    "classField",
    "classInput",
    "questionTitle",
    "builderQuestionText",
    "builderTaskText",
    "questionVisual",
    "questionMeta",
    "marksText",
    "progressText",
    "progressBar",
    "scoreText",
    "streakText",
    "instructionsText",
    "structureRail",
    "answerSlots",
    "optionBank",
    "optionTitle",
    "placedCount",
    "questionNavText",
    "prevQuestionButton",
    "nextQuestionButton",
    "randomQuestionButton",
    "feedbackPanel",
    "typeGrid",
    "typeGridPreview",
    "typeSummary",
    "progressSummary",
    "progressEvents",
    "librarySummary",
    "datasetList",
    "datasetClassSelect",
    "datasetSubjectSelect",
    "datasetBookSelect",
    "datasetChapterSelect",
    "currentDatasetSummary",
    "assignmentSummary",
    "assignmentList",
    "typeDetail",
    "adminSummary",
    "adminReviewList",
    "assignmentForm",
    "assignmentTitle",
    "assignmentDueDate",
    "teacherAnalytics",
    "imageStudioSummary",
    "imageGenerationForm",
    "imagePromptInput",
    "imageNegativeInput",
    "imageSizeInput",
    "imageStepsInput",
    "imageSeedInput",
    "imageGenerateButton",
    "imageGenerationStatus",
    "imageGenerationPreview",
    "imageGenerationPath",
    "profileName",
    "profileMeta",
    "avatarText",
    "goalPercent",
    "attemptCount",
  ].forEach((id) => {
    els[id] = document.getElementById(id);
  });
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  if (state.csrfToken && options.method && options.method !== "GET") {
    headers["X-CSRF-Token"] = state.csrfToken;
  }
  const response = await fetch(path, { credentials: "same-origin", ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || `Request failed with ${response.status}`);
    error.payload = data;
    throw error;
  }
  return data;
}

async function init() {
  cacheElements();
  bindLandingEvents();
  bindDashboardEvents();
  try {
    const session = await api("/api/session");
    if (session.authenticated) {
      state.user = session.user;
      state.csrfToken = session.csrfToken;
      await enterDashboard();
    } else {
      showLanding();
    }
  } catch (error) {
    showLanding();
    showAuthMessage(`Server is not ready: ${error.message}`, true);
  }
}

function bindLandingEvents() {
  document.querySelectorAll("[data-auth-mode]").forEach((button) => {
    button.addEventListener("click", () => setAuthMode(button.dataset.authMode));
  });
  ["openSignupTop", "openSignupHero"].forEach((id) => {
    document.getElementById(id)?.addEventListener("click", () => {
      setAuthMode("signup");
      els.authForm.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
  ["openLoginTop", "openLoginHero"].forEach((id) => {
    document.getElementById(id)?.addEventListener("click", () => {
      setAuthMode("login");
      els.authForm.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
  els.authForm.addEventListener("submit", submitAuth);
}

function bindDashboardEvents() {
  document.querySelectorAll(".mode-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      state.activity = getModeActivity(state.mode);
      document.querySelectorAll(".mode-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
      resetActivity();
    });
  });
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  document.getElementById("clearButton").addEventListener("click", clearPlacements);
  document.getElementById("resetButton").addEventListener("click", resetActivity);
  document.getElementById("checkButton").addEventListener("click", checkAnswer);
  document.getElementById("hintButton").addEventListener("click", showHint);
  document.getElementById("jumpTypesButton").addEventListener("click", () => switchView("types"));
  document.getElementById("logoutButton").addEventListener("click", logout);
  document.getElementById("homeButton").addEventListener("click", () => switchView("practice"));
  els.prevQuestionButton.addEventListener("click", () => goToQuestion(state.questionIndex - 1));
  els.nextQuestionButton.addEventListener("click", () => goToQuestion(state.questionIndex + 1));
  els.randomQuestionButton.addEventListener("click", () => goToRandomQuestion());
  els.assignmentForm?.addEventListener("submit", createAssignment);
  els.imageGenerationForm?.addEventListener("submit", generateImageAsset);
  els.datasetClassSelect?.addEventListener("change", () => updateDatasetFilter("classLevel", els.datasetClassSelect.value));
  els.datasetSubjectSelect?.addEventListener("change", () => updateDatasetFilter("subject", els.datasetSubjectSelect.value));
  els.datasetBookSelect?.addEventListener("change", () => updateDatasetFilter("book", els.datasetBookSelect.value));
  els.datasetChapterSelect?.addEventListener("change", async () => {
    if (els.datasetChapterSelect.value) await openDataset(els.datasetChapterSelect.value);
  });
}

function setAuthMode(mode) {
  state.authMode = mode;
  document.querySelectorAll(".auth-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.authMode === mode));
  const isSignup = mode === "signup";
  els.nameField.hidden = !isSignup;
  els.classField.hidden = !isSignup;
  els.nameInput.required = isSignup;
  els.passwordInput.autocomplete = isSignup ? "new-password" : "current-password";
  els.authSubmit.textContent = isSignup ? "Create account" : "Log in";
  showAuthMessage("", false);
}

async function submitAuth(event) {
  event.preventDefault();
  const email = els.emailInput.value.trim();
  const password = els.passwordInput.value;
  const clientErrors = validateAuthForm(email, password);
  if (clientErrors.length) {
    showAuthMessage(clientErrors.join(" "), true);
    return;
  }
  const payload = { email, password };
  if (state.authMode === "signup") {
    payload.name = els.nameInput.value.trim();
    payload.classLevel = Number(els.classInput.value);
    if (payload.name.length < 2) {
      showAuthMessage("Enter your full name.", true);
      return;
    }
  }
  els.authSubmit.disabled = true;
  showAuthMessage("Checking your account...", false);
  try {
    const result = await api(state.authMode === "signup" ? "/api/signup" : "/api/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.user = result.user;
    state.csrfToken = result.csrfToken;
    await enterDashboard();
  } catch (error) {
    const fieldErrors = error.payload?.fields ? Object.values(error.payload.fields).flat().join(" ") : "";
    showAuthMessage(fieldErrors || error.message, true);
  } finally {
    els.authSubmit.disabled = false;
  }
}

function validateAuthForm(email, password) {
  const errors = [];
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errors.push("Enter a valid email.");
  if (password.length < 8) errors.push("Password needs at least 8 characters.");
  if (state.authMode === "signup" && !/[A-Z]/.test(password)) errors.push("Add one uppercase letter.");
  if (state.authMode === "signup" && !/[a-z]/.test(password)) errors.push("Add one lowercase letter.");
  if (state.authMode === "signup" && !/\d/.test(password)) errors.push("Add one number.");
  return errors;
}

function showAuthMessage(message, isError) {
  els.authMessage.textContent = message;
  els.authMessage.classList.toggle("error", isError);
}

async function enterDashboard() {
  showDashboard();
  renderUser();
  await loadDatasets();
  if (!state.dataset) {
    state.dataset = await loadPracticeData();
    buildAnswerGroups();
    state.activity = getModeActivity(state.mode);
  }
  await refreshProgress();
  await refreshAssignments();
  renderDatasetPicker();
  resetActivity();
  renderTypeLibrary();
  renderDatasetSummary();
  renderAdminTools();
}

function showLanding() {
  els.landingView.hidden = false;
  els.dashboardView.hidden = true;
}

function showDashboard() {
  els.landingView.hidden = true;
  els.dashboardView.hidden = false;
}

function renderUser() {
  if (!state.user) return;
  els.profileName.textContent = state.user.name;
  els.profileMeta.textContent = `Class ${state.user.classLevel} - ${state.user.role || "student"}`;
  els.avatarText.textContent = state.user.name.slice(0, 1).toUpperCase();
  document.querySelectorAll(".admin-only").forEach((element) => {
    element.hidden = !["teacher", "admin"].includes(state.user.role);
  });
}

async function loadDatasets() {
  try {
    const requestedDataset = getRequestedDatasetFromUrl();
    const requestedMode = getRequestedModeFromUrl();
    if (requestedMode) state.mode = requestedMode;
    const includeAll = ["teacher", "admin"].includes(state.user?.role) ? "?includeAll=1" : "";
    const result = await api(`/api/datasets${includeAll}`);
    state.datasets = sortDatasets(result.datasets || []);
    const classDatasets = state.datasets.filter((dataset) => Number(dataset.classLevel) === Number(state.user?.classLevel));
    const initial = classDatasets[0] || state.datasets[0];
    if (requestedDataset) state.selectedDataset = requestedDataset;
    state.selectedDataset = state.selectedDataset || datasetKey(initial) || null;
    syncFiltersFromDataset(findDataset(state.selectedDataset) || initial);
  } catch {
    state.datasets = [];
  }
}

function getRequestedDatasetFromUrl() {
  const value = new URLSearchParams(window.location.search).get("dataset");
  return value ? value.trim() : "";
}

function getRequestedModeFromUrl() {
  const value = new URLSearchParams(window.location.search).get("mode");
  return ["easy", "moderate", "difficult"].includes(value) ? value : "";
}

async function loadPracticeData() {
  const datasetQuery = state.selectedDataset ? `?dataset=${encodeURIComponent(state.selectedDataset)}` : "";
  return api(`${DATA_URL}${datasetQuery}`);
}

function buildAnswerGroups() {
  const builders = state.dataset.activities.filter((activity) => activity.type === "answer_builder");
  const groupMap = new Map();
  builders.forEach((activity) => {
    const groupId = activity.questionGroupId || activity.question;
    if (!groupMap.has(groupId)) {
      groupMap.set(groupId, {
        id: groupId,
        number: activity.chapterQuestionNumber ?? groupMap.size,
        question: activity.question,
        activities: [],
      });
    }
    groupMap.get(groupId).activities.push(activity);
  });
  state.answerGroups = [...groupMap.values()].sort((a, b) => a.number - b.number);
  if (state.answerGroups.length) {
    state.recentQuestionIndexes = [];
    state.questionIndex = randomQuestionIndex(-1);
    state.recentQuestionIndexes = [state.questionIndex];
  }
  state.modes = state.answerGroups[state.questionIndex]?.activities || builders.slice(0, 3);
}

async function logout() {
  await api("/api/logout", { method: "POST", body: "{}" }).catch(() => {});
  state.user = null;
  state.csrfToken = null;
  showLanding();
}

async function refreshProgress() {
  try {
    state.progress = await api("/api/progress");
  } catch {
    state.progress = { events: [], attempts: 0, averagePercent: 0 };
  }
  els.goalPercent.textContent = `${state.progress.averagePercent}%`;
  els.attemptCount.textContent = `${state.progress.attempts} attempts`;
  renderProgressEvents();
}

function renderProgressEvents() {
  if (!els.progressEvents) return;
  if (!state.progress.events.length) {
    els.progressEvents.innerHTML = "<p>No attempts saved yet.</p>";
    return;
  }
  els.progressEvents.innerHTML = state.progress.events
    .slice(0, 6)
    .map((event) => `<div><strong>${escapeHtml(event.activity_type)}</strong><span>${event.score}/${event.marks} Â· ${escapeHtml(event.difficulty)}</span></div>`)
    .join("");
}

function switchView(viewName) {
  document.querySelectorAll(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === viewName));
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active-view", view.id === `${viewName}View`));
  if (viewName === "assignments") refreshAssignments();
}

async function refreshAssignments() {
  if (!els.assignmentList) return;
  try {
    const result = await api("/api/student/assignments");
    state.assignments = result.assignments || [];
  } catch {
    state.assignments = [];
  }
  renderAssignments();
}

function renderAssignments() {
  if (!els.assignmentList) return;
  els.assignmentSummary.textContent = state.assignments.length
    ? `${state.assignments.length} assignment(s) for Class ${state.user?.classLevel || ""}.`
    : "No assignments yet. You can still practise from the Library.";
  if (!state.assignments.length) {
    els.assignmentList.innerHTML = `<div class="empty-state slim"><h3>No assigned work yet</h3><p>Use Practice or Library while your teacher prepares assignments.</p></div>`;
    return;
  }
  els.assignmentList.innerHTML = state.assignments
    .map((assignment) => {
      const due = assignment.due_at ? new Date(Number(assignment.due_at) * 1000).toLocaleDateString() : "No due date";
      return `
        <article class="assignment-card">
          <div>
            <strong>${escapeHtml(assignment.title)}</strong>
            <span>${escapeHtml(assignment.teacher_name || "Teacher")} - ${escapeHtml(due)}</span>
          </div>
          <button class="primary-button compact-button" data-assignment-dataset="${escapeHtml(assignment.dataset_path)}" type="button">Start</button>
        </article>`;
    })
    .join("");
  els.assignmentList.querySelectorAll("[data-assignment-dataset]").forEach((button) => {
    button.addEventListener("click", async () => {
      const datasetPath = button.dataset.assignmentDataset;
      await openDataset(datasetPath);
      switchView("practice");
    });
  });
}

async function openDataset(datasetIdOrPath) {
  state.selectedDataset = datasetIdOrPath;
  state.dataset = await loadPracticeData();
  state.questionIndex = 0;
  syncFiltersFromDataset(findDataset(datasetIdOrPath));
  buildAnswerGroups();
  state.activity = getModeActivity(state.mode);
  resetActivity();
  renderDatasetPicker();
  renderTypeLibrary();
  renderDatasetSummary();
  renderAdminTools();
}

function datasetKey(dataset) {
  return dataset ? dataset.id || dataset.jsonPath : "";
}

function findDataset(datasetIdOrPath) {
  return state.datasets.find((dataset) => datasetKey(dataset) === datasetIdOrPath || dataset.jsonPath === datasetIdOrPath);
}

function sortDatasets(datasets) {
  return [...datasets].sort((a, b) => {
    const leftSubject = subjectOrder.includes(a.subject) ? subjectOrder.indexOf(a.subject) : subjectOrder.length;
    const rightSubject = subjectOrder.includes(b.subject) ? subjectOrder.indexOf(b.subject) : subjectOrder.length;
    const left = [Number(a.classLevel) || 99, leftSubject, a.subject || "", bookPriority(a.book), a.book || "", Number(a.chapterNumber) || 999, a.chapter || ""];
    const right = [Number(b.classLevel) || 99, rightSubject, b.subject || "", bookPriority(b.book), b.book || "", Number(b.chapterNumber) || 999, b.chapter || ""];
    return left.join("|").localeCompare(right.join("|"), undefined, { numeric: true, sensitivity: "base" });
  });
}

function bookPriority(book) {
  const value = String(book || "").toLowerCase();
  if (value.includes("financial accounting - 1") || value.includes("financial accounting 1")) return 0;
  if (value.includes("financial accounting - 2") || value.includes("financial accounting 2")) return 1;
  return 2;
}

function syncFiltersFromDataset(dataset) {
  if (!dataset) return;
  state.datasetFilters = {
    classLevel: String(dataset.classLevel || state.user?.classLevel || ""),
    subject: dataset.subject || "",
    book: dataset.book || "",
  };
}

function uniqueValues(items, field) {
  return [...new Set(items.map((item) => item[field]).filter((value) => value !== undefined && value !== null && value !== ""))];
}

function sortSubjects(subjects) {
  return [...subjects].sort((a, b) => {
    const left = subjectOrder.includes(a) ? subjectOrder.indexOf(a) : subjectOrder.length;
    const right = subjectOrder.includes(b) ? subjectOrder.indexOf(b) : subjectOrder.length;
    return left - right || String(a).localeCompare(String(b));
  });
}

function setSelectOptions(select, values, selected, formatter = (value) => value) {
  if (!select) return;
  select.innerHTML = values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(formatter(value))}</option>`).join("");
  if (values.includes(selected)) select.value = selected;
}

async function updateDatasetFilter(field, value) {
  state.datasetFilters[field] = value;
  if (field === "classLevel") {
    const classDatasets = state.datasets.filter((dataset) => String(dataset.classLevel) === value);
    state.datasetFilters.subject = classDatasets[0]?.subject || "";
    state.datasetFilters.book = classDatasets.find((dataset) => dataset.subject === state.datasetFilters.subject)?.book || "";
  }
  if (field === "subject") {
    const subjectDatasets = state.datasets.filter((dataset) => String(dataset.classLevel) === state.datasetFilters.classLevel && dataset.subject === value);
    state.datasetFilters.book = subjectDatasets[0]?.book || "";
  }
  if (field === "book") {
    state.datasetFilters.book = value;
  }
  const next = filteredChapterDatasets()[0];
  renderDatasetPicker();
  if (next) await openDataset(datasetKey(next));
}

function filteredChapterDatasets() {
  return state.datasets.filter(
    (dataset) =>
      String(dataset.classLevel) === state.datasetFilters.classLevel &&
      dataset.subject === state.datasetFilters.subject &&
      dataset.book === state.datasetFilters.book
  );
}

function renderDatasetPicker() {
  if (!els.datasetClassSelect || !state.datasets.length) return;
  const classes = uniqueValues(state.datasets, "classLevel").map(String).sort((a, b) => Number(a) - Number(b));
  const selectedClass = state.datasetFilters.classLevel || String(state.user?.classLevel || classes[0] || "");
  setSelectOptions(els.datasetClassSelect, classes, selectedClass, (value) => `Class ${value}`);

  const classDatasets = state.datasets.filter((dataset) => String(dataset.classLevel) === selectedClass);
  const subjects = sortSubjects(uniqueValues(classDatasets, "subject"));
  if (!subjects.includes(state.datasetFilters.subject)) state.datasetFilters.subject = subjects[0] || "";
  setSelectOptions(els.datasetSubjectSelect, subjects, state.datasetFilters.subject);

  const subjectDatasets = classDatasets.filter((dataset) => dataset.subject === state.datasetFilters.subject);
  const books = uniqueValues(subjectDatasets, "book").sort((a, b) => bookPriority(a) - bookPriority(b) || String(a).localeCompare(String(b)));
  if (!books.includes(state.datasetFilters.book)) state.datasetFilters.book = books[0] || "";
  setSelectOptions(els.datasetBookSelect, books, state.datasetFilters.book);

  const chapters = filteredChapterDatasets();
  setSelectOptions(
    els.datasetChapterSelect,
    chapters.map(datasetKey),
    state.selectedDataset,
    (key) => {
      const dataset = findDataset(key);
      return dataset ? `Chapter ${dataset.chapterNumber}: ${dataset.chapter}` : key;
    }
  );

  const current = findDataset(state.selectedDataset);
  if (els.currentDatasetSummary && current) {
    els.currentDatasetSummary.textContent = `${current.subject} - ${current.book} - Chapter ${current.chapterNumber}: ${current.chapter}`;
  }
}

function shuffle(items) {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[swapIndex]] = [shuffled[swapIndex], shuffled[index]];
  }
  return shuffled;
}

function hashCode(value) {
  let hash = 0;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(index);
    hash |= 0;
  }
  return hash;
}

function getAllItems(activity) {
  return [...activity.correctItems.map((item) => ({ ...item, isCorrect: true })), ...activity.distractors.map((item) => ({ ...item, isCorrect: false }))];
}

function getPlacedIds() {
  return Object.values(state.placements).flat().filter(Boolean);
}

function getModeActivity(mode) {
  return state.modes.find((activity) => activity.difficulty === mode) || state.modes[0];
}

function goToQuestion(nextIndex) {
  if (!state.answerGroups.length) return;
  state.questionIndex = (nextIndex + state.answerGroups.length) % state.answerGroups.length;
  rememberQuestionIndex(state.questionIndex);
  state.modes = state.answerGroups[state.questionIndex].activities;
  state.activity = getModeActivity(state.mode);
  if (!state.activity) {
    state.mode = state.modes[0].difficulty;
    state.activity = state.modes[0];
  }
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    const isAvailable = state.modes.some((activity) => activity.difficulty === tab.dataset.mode);
    tab.disabled = !isAvailable;
    tab.classList.toggle("active", tab.dataset.mode === state.activity.difficulty);
  });
  resetActivity();
}

function randomQuestionIndex(previousIndex = state.questionIndex) {
  if (state.answerGroups.length <= 1) return 0;
  const allIndexes = state.answerGroups.map((_group, index) => index);
  const available = allIndexes.filter((index) => index !== previousIndex && !state.recentQuestionIndexes.includes(index));
  const pool = available.length ? available : allIndexes.filter((index) => index !== previousIndex);
  return pool[Math.floor(Math.random() * pool.length)] ?? 0;
}

function rememberQuestionIndex(index) {
  state.recentQuestionIndexes = [...state.recentQuestionIndexes.filter((item) => item !== index), index].slice(-Math.max(1, state.answerGroups.length - 1));
}

function goToRandomQuestion() {
  if (!state.answerGroups.length) return;
  const nextIndex = randomQuestionIndex();
  state.questionIndex = nextIndex;
  rememberQuestionIndex(nextIndex);
  state.modes = state.answerGroups[state.questionIndex].activities;
  state.activity = getModeActivity(state.mode);
  if (!state.activity) {
    state.mode = state.modes[0].difficulty;
    state.activity = state.modes[0];
  }
  document.querySelectorAll(".mode-tab").forEach((tab) => {
    const isAvailable = state.modes.some((activity) => activity.difficulty === tab.dataset.mode);
    tab.disabled = !isAvailable;
    tab.classList.toggle("active", tab.dataset.mode === state.activity.difficulty);
  });
  resetActivity();
}

function resetActivity() {
  if (!state.activity) return;
  state.submitted = false;
  state.lastResult = null;
  state.placements = {};
  state.activity.answerSlots.forEach((slot) => {
    state.placements[slot.id] = [];
  });
  state.bank = shuffle(getAllItems(state.activity));
  hideFeedback();
  renderPractice();
}

function clearPlacements() {
  state.submitted = false;
  state.lastResult = null;
  Object.keys(state.placements).forEach((slotId) => {
    state.placements[slotId] = [];
  });
  state.bank = shuffle(getAllItems(state.activity));
  hideFeedback();
  renderPractice();
}

function renderPractice() {
  const activity = state.activity;
  if (!activity) return;
  const modeNumber = state.modes.findIndex((item) => item.difficulty === activity.difficulty) + 1;
  const placedCount = getPlacedIds().length;
  const expectedCount = activity.difficulty === "difficult" ? activity.answerKey.requiredConceptIds.length : activity.answerKey.orderedItemIds.length;

  els.questionTitle.textContent = activity.question;
  els.builderQuestionText.textContent = activity.question;
  els.builderTaskText.textContent = getStudentTaskText(activity);
  renderQuestionScene(activity);
  els.questionMeta.textContent = `${activity.book} / Chapter ${activity.chapterNumber}: ${activity.chapter}`;
  els.marksText.textContent = activity.marks;
  els.instructionsText.textContent = activity.instructions;
  els.progressText.textContent = `${modeNumber} / ${state.modes.length}`;
  els.progressBar.style.width = `${(modeNumber / state.modes.length) * 100}%`;
  els.scoreText.textContent = `${state.score} / ${activity.marks}`;
  els.streakText.textContent = state.streak;
  els.placedCount.textContent = `${Math.min(placedCount, expectedCount)} / ${expectedCount} placed`;
  els.questionNavText.textContent = `Question ${state.questionIndex + 1} / ${state.answerGroups.length}`;
  els.prevQuestionButton.disabled = state.answerGroups.length <= 1;
  els.nextQuestionButton.disabled = state.answerGroups.length <= 1;
  els.randomQuestionButton.disabled = state.answerGroups.length <= 1;
  els.optionTitle.textContent = getOptionTitle(activity);
  renderStructure(activity);
  renderSlots(activity);
  renderBank();
}

function isYoungLearnerActivity(activity) {
  return Number(activity.classLevel) <= 2;
}

function renderQuestionScene(activity) {
  const subject = String(activity.subject || "").toLowerCase();
  const sceneClass = isYoungLearnerActivity(activity)
    ? "young"
    : subject.includes("science")
      ? "science"
      : subject.includes("math")
        ? "math"
        : subject.includes("english")
          ? "english"
          : "general";
  els.questionVisual.textContent = "";
  const questionScene = els.questionVisual.parentElement;
  questionScene.className = `builder-question ${sceneClass}-scene`;
  questionScene.style.removeProperty("--question-art");
  const questionCard = els.questionTitle.closest(".question-card");
  if (questionCard) {
    questionCard.className = "question-card";
    questionCard.style.removeProperty("--question-art");
  }
}

function versionedAssetUrl(path) {
  return `${path}${path.includes("?") ? "&" : "?"}v=${QUESTION_ART_VERSION}`;
}

function getQuestionArt(activity) {
  if (activity.visualArt) return activity.visualArt;
  const subject = String(activity.subject || "").toLowerCase();
  const classLevel = Number(activity.classLevel);
  const text = `${activity.question || ""} ${activity.chapter || ""} ${(activity.correctItems || []).map((item) => item.text).join(" ")}`.toLowerCase();
  const class1MathArt = getClass1MathArt(activity, text);
  if (class1MathArt) return class1MathArt;
  if (classLevel === 1 && subject.includes("english")) {
    const exactArt = getClass1EnglishArt(activity.question || "");
    if (exactArt) return exactArt;
  }
  if (classLevel <= 2 && (subject.includes("math") || subject.includes("english")) && hasPositionWordArtTrigger(text)) {
    return "assets/question-art/cat-position-4k-ui.png";
  }
  return "";
}

function hasPositionWordArtTrigger(text) {
  return /\b(cat|inside|outside|under|above)\b/.test(text);
}

function getClass1MathArt(activity, text) {
  if (Number(activity.classLevel) !== 1 || !String(activity.subject || "").toLowerCase().includes("math")) return "";
  const aiPath = "assets/question-art/class1-math-ai";
  const questionText = String(activity.question || "").toLowerCase();
  const chapterNumber = Number(activity.chapterNumber);
  if (chapterNumber === 2) {
    if (questionText.includes("sort shapes")) return `${aiPath}/shape-sort.png`;
    if (questionText.includes("know the shape") || questionText.includes("check")) return `${aiPath}/shape-check.png`;
    if (questionText.includes("round")) return `${aiPath}/round-things.png`;
    return `${aiPath}/long-things.png`;
  }
  const questionArt = getClass1MathQuestionArt(chapterNumber, questionText);
  if (questionArt) return `assets/question-art/class1-math-question-ai/${questionArt}`;
  if (hasPositionWordArtTrigger(text)) {
    if (text.includes("hidden") || text.includes("find")) return "assets/question-art/class1-math-ai/find-hidden-cat.png";
    if (text.includes("hopped") || text.includes("below") || text.includes("bottom") || text.includes("top")) return "assets/question-art/class1-math-ai/cat-movement.png";
    if (text.includes("position words") || text.includes("where the cat is")) return "assets/question-art/class1-math-ai/position-words.png";
    return "assets/question-art/class1-math-ai/cat-room-places.png";
  }
  return "";
}

function getClass1MathQuestionArt(chapterNumber, questionText) {
  const questionArtByChapter = {
    3: [
      ["count mangoes", "ch03-count-mangoes.png"],
      ["compare mangoes", "ch03-compare-mangoes.png"],
      ["share mangoes", "ch03-share-mangoes.png"],
      ["counting useful", "ch03-counting-useful.png"],
    ],
    4: [
      ["pairs make 10", "ch04-pairs-make-10.png"],
      ["learn making 10", "ch04-learn-making-10.png"],
      ["check 10", "ch04-check-10.png"],
      ["make 10", "ch04-make-10.png"],
    ],
    5: [
      ["know how many", "ch05-know-how-many.png"],
      ["while counting", "ch05-count-carefully.png"],
      ["compare two groups", "ch05-compare-groups.png"],
      ["count carefully", "ch05-count-carefully-why.png"],
    ],
    6: [
      ["vegetable farm", "ch06-farm-things.png"],
      ["count vegetables", "ch06-count-vegetables.png"],
      ["compare vegetables", "ch06-compare-vegetables.png"],
      ["farmers count", "ch06-farmers-count.png"],
    ],
    7: [
      ["lina's family", "ch07-family-members.png"],
      ["count family", "ch07-count-family.png"],
      ["families the same", "ch07-compare-families.png"],
      ["families do", "ch07-family-do.png"],
    ],
    8: [
      ["numbers help", "ch08-numbers-help.png"],
      ["see numbers", "ch08-see-numbers.png"],
      ["numbers in order", "ch08-number-order.png"],
      ["numbers fun", "ch08-numbers-fun.png"],
    ],
    9: [
      ["happens during utsav", "ch09-utsav-happens.png"],
      ["count during utsav", "ch09-count-utsav.png"],
      ["make groups", "ch09-make-groups.png"],
      ["utsav special", "ch09-utsav-special.png"],
    ],
    10: [
      ["morning", "ch10-morning.png"],
      ["in the day", "ch10-day.png"],
      ["night", "ch10-night.png"],
      ["follow time", "ch10-follow-time.png"],
    ],
    11: [
      ["know how many", "ch11-know-how-many.png"],
      ["while counting", "ch11-counting.png"],
      ["compare two groups", "ch11-compare-groups.png"],
      ["count carefully", "ch11-count-carefully.png"],
    ],
    12: [
      ["use money", "ch12-use-money.png"],
      ["before buying", "ch12-before-buying.png"],
      ["count money", "ch12-count-money.png"],
      ["spend less", "ch12-spend-less.png"],
    ],
    13: [
      ["count toys", "ch13-count-toys.png"],
      ["sort toys", "ch13-sort-toys.png"],
      ["compare toys", "ch13-compare-toys.png"],
      ["keep toys", "ch13-keep-toys.png"],
    ],
  };
  const matches = questionArtByChapter[chapterNumber] || [];
  const match = matches.find(([needle]) => questionText.includes(needle));
  return match ? match[1] : "";
}

function getClass1EnglishArt(question) {
  const map = {
    "What can my hands do?": "hands-clap",
    "What can my legs do?": "legs-walk",
    "What can my eyes and ears do?": "eyes-ears",
    "What are the parts of my body?": "body-parts",
    "What do we say when we meet?": "hello-meet",
    "What do we say in the morning?": "good-morning",
    "What do we say when someone helps us?": "thank-you",
    "What do we say when we leave?": "goodbye",
    "What living things do we see?": "living-things",
    "What do plants need?": "plants-need",
    "What do animals need?": "animals-need",
    "How should we care for living things?": "care-living",
    "What did the cap-seller carry?": "cap-seller-caps",
    "What did the monkeys do?": "monkeys-caps",
    "How did the cap-seller get his caps back?": "caps-back",
    "What do we learn from the story?": "story-learn",
    "What do we see on a farm?": "farm-see",
    "Who works on a farm?": "farmer-works",
    "What animals can live on a farm?": "farm-animals",
    "Why is a farm useful?": "farm-useful",
    "Why do we need food?": "need-food",
    "What food do we eat?": "eat-food",
    "How do we keep food clean?": "clean-food",
    "Why should we not waste food?": "not-waste-food",
    "Why do we eat food?": "why-eat-food",
    "Which foods are healthy?": "healthy-food",
    "When do we eat food?": "when-eat",
    "How should we eat?": "how-eat",
    "What happens in summer?": "summer",
    "What happens on rainy days?": "rainy-days",
    "What happens in winter?": "winter",
    "Why do seasons change our clothes?": "season-clothes",
    "What do we see in a rainbow?": "rainbow-see",
    "When can we see a rainbow?": "rainbow-when",
    "What colours can a rainbow have?": "rainbow-colours",
    "Why do children like a rainbow?": "rainbow-like",
  };
  const matchingQuestion = Object.keys(map).find((key) => question === key || question.includes(key));
  return matchingQuestion ? `assets/question-art/class1-english-ai/${map[matchingQuestion]}.png` : "";
}

function getQuestionSymbol(activity, sceneClass) {
  if (isYoungLearnerActivity(activity)) return "Q";
  if (sceneClass === "science") return "SCI";
  if (sceneClass === "math") return "123";
  if (sceneClass === "english") return "Aa";
  return "?";
}

function getStudentTaskText(activity) {
  if (isYoungLearnerActivity(activity)) {
    return isSequencedAnswer(activity) ? "Drag the answer parts in the correct order to build one full answer." : "Pick the small word cards that answer the question.";
  }
  return isSequencedAnswer(activity) ? "Arrange the answer parts in the correct order." : "Use the key phrases to build your answer.";
}

function getOptionTitle(activity) {
  if (isYoungLearnerActivity(activity)) return isSequencedAnswer(activity) ? "Answer Parts" : "Word Cards";
  return isSequencedAnswer(activity) ? "Answer Parts" : "Phrase Options";
}

function isSequencedAnswer(activity) {
  return Array.isArray(activity?.answerKey?.orderedItemIds);
}

function isSingleSlotJoinedSequence(activity) {
  return isSequencedAnswer(activity) && (activity?.answerSlots || []).length === 1;
}

function renderStructure(activity) {
  els.structureRail.innerHTML = "";
  activity.structureHelp.forEach((label, index) => {
    const chip = document.createElement("span");
    chip.className = "structure-chip";
    chip.textContent = `${index + 1}. ${label}`;
    els.structureRail.appendChild(chip);
  });
}

function renderSlots(activity) {
  els.answerSlots.innerHTML = "";
  activity.answerSlots.forEach((slot, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = `drop-slot ${activity.difficulty === "difficult" ? "bucket-slot" : ""}`;
    const number = document.createElement("div");
    number.className = "slot-number";
    number.textContent = index + 1;
    const body = document.createElement("div");
    body.className = "slot-body";
    body.dataset.slotId = slot.id;
    body.tabIndex = 0;
    body.textContent = isYoungLearnerActivity(activity) ? `Drop part ${index + 1} here` : slot.label || "Drop item here";
    addDropHandlers(body);
    const placedItems = state.placements[slot.id] || [];
    if (placedItems.length > 0) {
      body.textContent = "";
      if (isSingleSlotJoinedSequence(activity)) {
        const joined = placedItems
          .map((itemId) => findItem(itemId)?.text || "")
          .filter(Boolean)
          .join(" ");
        const preview = document.createElement("p");
        preview.className = "joined-answer-preview";
        preview.textContent = joined;
        body.appendChild(preview);
      }
      placedItems.forEach((itemId) => body.appendChild(createOptionCard(findItem(itemId), true, slot.id)));
    }
    wrapper.append(number, body);
    els.answerSlots.appendChild(wrapper);
  });
  const joined = getPracticeJoinedAnswer(activity);
  if (joined) {
    const preview = document.createElement("p");
    preview.className = "joined-answer-preview full-answer-preview";
    preview.textContent = joined;
    els.answerSlots.appendChild(preview);
  }
}

function getPracticeJoinedAnswer(activity) {
  const placed = activity.answerSlots
    .flatMap((slot) => state.placements[slot.id] || [])
    .map((itemId) => findItem(itemId)?.text || "")
    .filter(Boolean);
  return placed.length > 1 ? placed.join(" ") : "";
}

function renderBank() {
  els.optionBank.innerHTML = "";
  state.bank.forEach((item) => els.optionBank.appendChild(createOptionCard(item, false)));
  addDropHandlers(els.optionBank, true);
}

function createOptionCard(item, placed, slotId = null) {
  const card = document.createElement("button");
  card.type = "button";
  const isCorrectAfterSubmit = getCardCorrectness(item, placed, slotId);
  const revealClass = state.submitted ? (isCorrectAfterSubmit ? "correct-card" : "wrong-card") : "neutral-card";
  card.className = `option-card ${revealClass} ${placed ? "placed" : ""}`;
  card.draggable = true;
  card.dataset.itemId = item.id;
  card.innerHTML = `<span class="drag-handle">::</span><span class="item-text">${escapeHtml(item.text)}</span><span class="item-badge">${state.submitted ? (isCorrectAfterSubmit ? "âœ“" : "x") : ""}</span>`;
  card.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", item.id);
    event.dataTransfer.effectAllowed = "move";
  });
  card.addEventListener("click", () => (placed ? moveToBank(item.id) : placeInNextSlot(item.id)));
  return card;
}

function getCardCorrectness(item, placed, slotId) {
  if (!state.submitted) return false;
  if (!placed) return item.isCorrect;
  if (!item.isCorrect) return false;
  if (isSingleSlotJoinedSequence(state.activity)) {
    const placedItems = state.placements[slotId] || [];
    const selectedIndex = placedItems.findIndex((id) => id === item.id);
    return state.activity.answerKey.orderedItemIds[selectedIndex] === item.id;
  }
  if (state.activity.difficulty === "difficult") return true;
  const expectedForSlot = state.lastResult?.slotExpected?.[slotId];
  return expectedForSlot === item.id;
}

function addDropHandlers(element, isBank = false) {
  element.addEventListener("dragover", (event) => {
    event.preventDefault();
    element.classList.add("drag-over");
  });
  element.addEventListener("dragleave", () => element.classList.remove("drag-over"));
  element.addEventListener("drop", (event) => {
    event.preventDefault();
    element.classList.remove("drag-over");
    const itemId = event.dataTransfer.getData("text/plain");
    if (!itemId) return;
    if (isBank) moveToBank(itemId);
    else placeInSlot(itemId, element.dataset.slotId);
  });
}

function placeInNextSlot(itemId) {
  const slotIds = state.activity.answerSlots.map((slot) => slot.id);
  const maxJoinedParts = state.activity.answerKey?.orderedItemIds?.length || 4;
  const targetSlot =
    !isSequencedAnswer(state.activity) || isSingleSlotJoinedSequence(state.activity)
      ? slotIds.find((slotId) => (state.placements[slotId] || []).length < (isSingleSlotJoinedSequence(state.activity) ? maxJoinedParts : 4))
      : slotIds.find((slotId) => (state.placements[slotId] || []).length === 0);
  if (targetSlot) placeInSlot(itemId, targetSlot);
}

function placeInSlot(itemId, slotId) {
  if (!slotId) return;
  state.submitted = false;
  state.lastResult = null;
  removeFromAllPlacements(itemId);
  state.bank = state.bank.filter((item) => item.id !== itemId);
  if (!isSequencedAnswer(state.activity) || isSingleSlotJoinedSequence(state.activity)) {
    state.placements[slotId].push(itemId);
  } else {
    const existing = state.placements[slotId][0];
    if (existing) state.bank.push(findItem(existing));
    state.placements[slotId] = [itemId];
  }
  hideFeedback();
  renderPractice();
}

function moveToBank(itemId) {
  state.submitted = false;
  state.lastResult = null;
  removeFromAllPlacements(itemId);
  if (!state.bank.some((item) => item.id === itemId)) state.bank.push(findItem(itemId));
  state.bank = shuffle(state.bank);
  hideFeedback();
  renderPractice();
}

function removeFromAllPlacements(itemId) {
  Object.keys(state.placements).forEach((slotId) => {
    state.placements[slotId] = state.placements[slotId].filter((id) => id !== itemId);
  });
}

function findItem(itemId) {
  return getAllItems(state.activity).find((item) => item.id === itemId);
}

async function checkAnswer() {
  const activity = state.activity;
  const result = isSequencedAnswer(activity) ? checkSequenced(activity) : checkDifficult(activity);
  state.submitted = true;
  state.lastResult = result;
  state.score = result.score;
  if (result.score === activity.marks) state.streak += 1;
  renderPractice();
  renderFeedback(result);
  if (state.user) {
    await api("/api/progress", {
      method: "POST",
      body: JSON.stringify({
        activityId: activity.id,
        activityType: activity.type,
        difficulty: activity.difficulty,
        score: result.score,
        marks: activity.marks,
        selectedCount: getPlacedIds().length,
      }),
    }).catch(() => {});
    await refreshProgress();
  }
}

function checkSequenced(activity) {
  const expected = activity.answerKey.orderedItemIds;
  const slotExpected = {};
  const selectedBySlot = isSingleSlotJoinedSequence(activity)
    ? expected.map((expectedId, index) => {
        const slot = activity.answerSlots[0];
        slotExpected[slot.id] = expected[index];
        return { slotId: slot.id, itemId: state.placements[slot.id]?.[index], expectedId };
      })
    : activity.answerSlots.map((slot, index) => {
    slotExpected[slot.id] = expected[index];
    return { slotId: slot.id, itemId: state.placements[slot.id]?.[0], expectedId: expected[index] };
  });
  const selected = selectedBySlot.map((slot) => slot.itemId).filter(Boolean);
  const selectedSet = new Set(selected);
  const correctSelection = selected.filter((id) => expected.includes(id)).length;
  const wrongSelection = selected.filter((id) => !expected.includes(id)).length;
  const orderedMatches = selectedBySlot.filter((slot) => slot.itemId && slot.itemId === slot.expectedId).length;
  const completion = selected.length === expected.length;
  const raw = orderedMatches - wrongSelection;
  const score = Math.max(0, Math.round((raw / expected.length) * activity.marks));
  return { score, correctSelection, wrongSelection, orderedMatches, expectedCount: expected.length, completion, selectedSet, slotExpected, selectedBySlot, isPerfect: score === activity.marks && wrongSelection === 0 && completion };
}

function checkDifficult(activity) {
  const expected = activity.answerKey.requiredConceptIds;
  const selected = getPlacedIds();
  const correctSelection = selected.filter((id) => expected.includes(id)).length;
  const wrongSelection = selected.filter((id) => !expected.includes(id)).length;
  const selectedSet = new Set(selected);
  const completion = expected.every((id) => selectedSet.has(id));
  const raw = correctSelection - wrongSelection;
  const score = Math.max(0, Math.round((raw / expected.length) * activity.marks));
  return { score, correctSelection, wrongSelection, orderedMatches: correctSelection, expectedCount: expected.length, completion, selectedSet, slotExpected: {}, selectedBySlot: [], isPerfect: score === activity.marks && wrongSelection === 0 && completion };
}

function renderFeedback(result) {
  els.feedbackPanel.hidden = false;
  els.feedbackPanel.className = `feedback-panel ${result.isPerfect ? "good" : "needs-work"}`;
  const activity = state.activity;
  const missing = activity.correctItems.filter((item) => !result.selectedSet.has(item.id)).slice(0, 3).map((item) => item.text);
  els.feedbackPanel.innerHTML = `
    <div class="panel-heading">
      <div><h3>${result.isPerfect ? "Excellent answer" : "Sequence needs correction"}</h3><p>${escapeHtml(activity.modelAnswer)}</p></div>
      <span class="counter">${result.score} / ${activity.marks}</span>
    </div>
    <div class="feedback-grid">
      <div class="feedback-stat"><span>Correct items</span><strong>${result.correctSelection} / ${result.expectedCount}</strong></div>
      <div class="feedback-stat"><span>Exact slot order</span><strong>${result.orderedMatches} / ${result.expectedCount}</strong></div>
      <div class="feedback-stat"><span>Distractors used</span><strong>${result.wrongSelection}</strong></div>
      <div class="feedback-stat"><span>Completion</span><strong>${result.completion ? "Done" : "Pending"}</strong></div>
    </div>
    ${renderAnswerReview(activity, result)}
    ${missing.length ? `<p class="feedback-note"><strong>Missing:</strong> ${missing.map(escapeHtml).join("; ")}</p>` : ""}
  `;
  els.progressSummary.textContent = result.isPerfect ? `Latest score: ${result.score}/${activity.marks}. Strong sequence and no distractors selected.` : `Latest score: ${result.score}/${activity.marks}. Put each sentence in its exact placeholder order and remove distractors.`;
  els.feedbackPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAnswerReview(activity, result) {
  if (activity.difficulty === "difficult") {
    const expected = activity.answerKey.requiredConceptIds || [];
    const selected = getPlacedIds();
    return `
      <section class="answer-review">
        <div class="answer-review-head">
          <h4>Correct concepts to include</h4>
          <p>Use these ideas in your final answer and remove any unrelated option.</p>
        </div>
        <div class="correct-sequence-list">
          ${expected.map((itemId, index) => renderExpectedConceptRow(itemId, selected, index)).join("")}
        </div>
      </section>
    `;
  }

  return `
    <section class="answer-review">
      <div class="answer-review-head">
        <h4>Correct sequence</h4>
        <p>Compare each slot with what you placed to find the mistake.</p>
      </div>
      <div class="sequence-review-table">
        <div class="sequence-review-header">Slot</div>
        <div class="sequence-review-header">Correct answer</div>
        <div class="sequence-review-header">Your answer</div>
        <div class="sequence-review-header">Result</div>
        ${result.selectedBySlot.map((slot, index) => renderSequenceReviewRow(activity, slot, index)).join("")}
      </div>
    </section>
  `;
}

function renderExpectedConceptRow(itemId, selected, index) {
  const item = findItem(itemId);
  const hasConcept = selected.includes(itemId);
  return `
    <div class="correct-sequence-row ${hasConcept ? "row-correct" : "row-missing"}">
      <span>${index + 1}</span>
      <strong>${escapeHtml(item?.text || "Missing concept")}</strong>
      <em>${hasConcept ? "Included" : "Missing"}</em>
    </div>
  `;
}

function renderSequenceReviewRow(activity, slot, index) {
  const expectedItem = findItem(slot.expectedId);
  const selectedItem = slot.itemId ? findItem(slot.itemId) : null;
  const isCorrect = slot.itemId === slot.expectedId;
  const isMissing = !slot.itemId;
  const status = isCorrect ? "Correct" : isMissing ? "Empty" : "Fix order";
  const rowClass = isCorrect ? "row-correct" : "row-wrong";
  return `
    <div class="sequence-review-row ${rowClass}">
      <span>${escapeHtml(activity.answerSlots[index]?.label || `Slot ${index + 1}`)}</span>
      <strong>${escapeHtml(expectedItem?.text || "Expected answer unavailable")}</strong>
      <b>${escapeHtml(selectedItem?.text || "No answer placed")}</b>
      <em>${status}</em>
    </div>
  `;
}

function showHint() {
  els.feedbackPanel.hidden = false;
  els.feedbackPanel.className = "feedback-panel needs-work";
  els.feedbackPanel.innerHTML = `<div class="panel-heading"><div><h3>Hint</h3><p>${state.activity.hints.map(escapeHtml).join(" ")}</p></div><span class="counter">${state.activity.structureHelp.length} steps</span></div>`;
}

function hideFeedback() {
  els.feedbackPanel.hidden = true;
  els.feedbackPanel.innerHTML = "";
}

function renderTypeLibrary() {
  const standardActivities = state.dataset.activities.filter((activity) => activity.type !== "answer_builder");
  els.typeSummary.textContent = `${standardActivities.length} generated question formats from ${state.dataset.source.chapter}.`;
  els.typeGrid.innerHTML = "";
  els.typeGridPreview.innerHTML = "";
  els.typeGrid.classList.toggle("continuous-table-grid", false);
  if (els.typeDetail) els.typeDetail.hidden = true;
  renderTypeGroups(standardActivities);
}

function renderTypeGroups(activities) {
  const groups = groupActivitiesByType(activities);
  const selectedType = state.selectedTypeGroup && groups.has(state.selectedTypeGroup) ? state.selectedTypeGroup : groups.keys().next().value;
  state.selectedTypeGroup = selectedType || "";
  els.typeSummary.textContent = selectedType
    ? `${groups.get(selectedType).length} ${typeLabels[selectedType] || selectedType} question(s) from ${state.dataset.source.chapter}.`
    : `No generated question types found for ${state.dataset.source.chapter}.`;
  els.typeGrid.classList.add("type-group-grid");
  els.typeGrid.innerHTML = [...groups.entries()]
    .map(([type, items], index) => createTypeGroupButton(type, items, index, type === state.selectedTypeGroup))
    .join("");
  els.typeGridPreview.innerHTML = [...groups.entries()]
    .slice(0, 8)
    .map(([type, items], index) => createTypeGroupButton(type, items, index, type === state.selectedTypeGroup, true))
    .join("");
  els.typeGrid.querySelectorAll("[data-type-group]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedTypeGroup = button.dataset.typeGroup;
      state.continuousTableView = "list";
      renderTypeGroups(activities);
      scrollToTypeDetail();
    });
  });
  els.typeGridPreview.querySelectorAll("[data-type-group]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedTypeGroup = button.dataset.typeGroup;
      state.continuousTableView = "list";
      switchView("types");
      renderTypeGroups(activities);
      scrollToTypeDetail();
    });
  });
  renderTypeGroupQuestions(groups.get(state.selectedTypeGroup) || []);
}

function scrollToTypeDetail() {
  window.requestAnimationFrame(() => {
    if (!els.typeDetail || els.typeDetail.hidden) return;
    els.typeDetail.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function groupActivitiesByType(activities) {
  const grouped = new Map();
  activities.forEach((activity) => {
    if (!grouped.has(activity.type)) grouped.set(activity.type, []);
    grouped.get(activity.type).push(activity);
  });
  return new Map([...grouped.entries()].sort((a, b) => (typeLabels[a[0]] || a[0]).localeCompare(typeLabels[b[0]] || b[0])));
}

function createTypeGroupButton(type, items, index, active, compact = false) {
  const preview = items.slice(0, compact ? 1 : 2).map((activity) => `<span class="mini-chip neutral">${escapeHtml(activity.question)}</span>`).join("");
  return `
    <button class="type-card type-group-button ${active ? "active" : ""}" data-type-group="${escapeHtml(type)}" type="button">
      <div class="type-card-head"><span class="type-index">${index + 1}</span><h3>${escapeHtml(typeLabels[type] || type)}</h3></div>
      <p>${items.length} question(s)</p>
      <div class="mini-answer">${preview}</div>
    </button>`;
}

function renderTypeGroupQuestions(activities) {
  if (!els.typeDetail) return;
  if (!activities.length) {
    els.typeDetail.hidden = false;
    els.typeDetail.innerHTML = `<div class="empty-state slim"><h3>No questions in this type</h3></div>`;
    return;
  }
  if (state.dataset.coverage?.tablePracticeMode === "continuous-table-drag-drop" && state.selectedTypeGroup === "data_chart_table") {
    els.typeGrid.classList.add("continuous-table-grid");
    renderContinuousTablePractice(activities);
    return;
  }
  els.typeDetail.hidden = false;
  els.typeDetail.innerHTML = `
    <div class="panel-heading">
      <div>
        <span class="tag">${escapeHtml(typeLabels[state.selectedTypeGroup] || state.selectedTypeGroup)}</span>
        <h3>Questions</h3>
        <p>Select a question from this type to practise it.</p>
      </div>
      <span class="counter">${activities.length} questions</span>
    </div>
    <div class="type-question-list">
      ${activities.map((activity, index) => createTypeQuestionRow(activity, index)).join("")}
    </div>`;
  els.typeDetail.querySelectorAll("[data-type-question]").forEach((button) => {
    button.addEventListener("click", () => {
      const activity = activities.find((candidate) => candidate.id === button.dataset.typeQuestion);
      if (activity) renderTypeDetail(activity);
    });
  });
}

function createTypeQuestionRow(activity, index) {
  return `
    <button class="type-question-row" data-type-question="${escapeHtml(activity.id)}" type="button">
      <span>${index + 1}</span>
      <strong>${escapeHtml(activity.question)}</strong>
      <em>${escapeHtml(String(activity.marks || ""))} marks</em>
    </button>`;
}

function createTypeCard(activity, index, compact = false) {
  const card = document.createElement("article");
  card.className = "type-card";
  const previewItems = [...activity.correctItems, ...activity.distractors].slice(0, compact ? 2 : 3);
  card.innerHTML = `
    <div class="type-card-head"><span class="type-index">${index + 1}</span><h3>${escapeHtml(typeLabels[activity.type] || activity.type)}</h3></div>
    <p>${escapeHtml(activity.question)}</p>
    <div class="mini-answer">
      ${previewItems.map((item) => `<span class="mini-chip neutral">${escapeHtml(item.text)}</span>`).join("")}
    </div>
  `;
  card.addEventListener("click", () => {
    switchView("types");
    state.selectedTypeGroup = activity.type;
    if (activity.type === "data_chart_table" && state.dataset.coverage?.tablePracticeMode === "continuous-table-drag-drop") {
      state.continuousTableView = "list";
      renderTypeLibrary();
      scrollToTypeDetail();
      return;
    }
    els.typeSummary.textContent = `${typeLabels[activity.type] || activity.type}: ${activity.modelAnswer}`;
    renderTypeDetail(activity);
    scrollToTypeDetail();
  });
  return card;
}

function renderTypeDetail(activity) {
  if (!els.typeDetail) return;
  state.typeActivity = activity;
  state.typeSubmitted = false;
  state.typePlacements = {};
  getInteractiveTypeSlots(activity).forEach((slot) => {
    state.typePlacements[slot.id] = [];
  });
  renderTypePractice();
}

function renderTypePractice() {
  const activity = state.typeActivity;
  if (!els.typeDetail || !activity) return;
  if (activity.type === "cause_effect") {
    renderCauseEffectPractice(activity);
    return;
  }
  if (activity.type === "assertion_reason") {
    renderAssertionReasonPractice(activity);
    return;
  }
  const renderer = layoutRenderer(activity);
  getInteractiveTypeSlots(activity).forEach((slot) => {
    state.typePlacements[slot.id] = state.typePlacements[slot.id] || [];
  });
  const placedIds = Object.values(state.typePlacements).flat();
  const available = getStandardItems(activity).filter((item) => !placedIds.includes(item.id));
  const directTableDrop = activity.tableData?.dropMode === "table-cells" || hasTableBlankDrops(activity);
  els.typeDetail.hidden = false;
  els.typeDetail.innerHTML = `
    <div class="format-practice-toolbar">
      <button class="secondary-button compact-button" data-type-back type="button">Back to Questions</button>
      <span>${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
    </div>
    <div class="panel-heading">
      <div>
        <span class="tag">${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
        <h3>${escapeHtml(activity.question)}</h3>
        <p>${escapeHtml(activity.instructions)}</p>
      </div>
      <span class="counter">${activity.marks} marks</span>
    </div>
    ${renderer}
    <div class="standard-practice">
      ${
        directTableDrop
          ? ""
          : `<div class="standard-slots">
              ${activity.answerSlots
                .map(
                  (slot) => `
                    <div class="standard-slot">
                      <strong>${escapeHtml(slot.label || slot.id)}</strong>
                      <div class="standard-slot-body" data-type-slot="${escapeHtml(slot.id)}">
                        ${renderTypeSlotContent(activity, slot)}
                      </div>
                    </div>`
                )
                .join("")}
            </div>`
      }
      ${renderTypeJoinedAnswerPreview(activity)}
      ${hasTableInputDrops(activity) ? "" : `<div class="standard-bank">${available.map((item) => renderStandardChip(item, false, "")).join("")}</div>`}
      <div class="builder-actions">
        <button class="secondary-button" data-type-back type="button">Back to Questions</button>
        <button class="secondary-button" id="typeResetButton" type="button">Reset Format</button>
        <button class="primary-button" id="typeCheckButton" type="button">Check Format</button>
      </div>
      <div id="typeCheckResult" class="format-result"></div>
    </div>
    <div class="model-answer"><strong>Model answer</strong><p>${escapeHtml(activity.modelAnswer)}</p></div>
  `;
  els.typeDetail.querySelectorAll("[data-type-item]").forEach((button) => {
    button.addEventListener("dragstart", (event) => {
      event.dataTransfer.setData("text/plain", button.dataset.typeItem);
    });
    button.addEventListener("click", () => {
      const itemId = button.dataset.typeItem;
      const placed = button.dataset.placed === "1";
      if (placed) removeTypeItem(itemId);
      else placeTypeItem(itemId);
    });
  });
  els.typeDetail.querySelectorAll("[data-type-slot]").forEach((slot) => attachTypeDropZone(slot));
  els.typeDetail.querySelectorAll("[data-table-input-slot]").forEach((input) => {
    input.addEventListener("input", () => {
      state.typePlacements[input.dataset.tableInputSlot] = [input.value];
      state.typeSubmitted = false;
    });
  });
  els.typeDetail.querySelectorAll("[data-type-back]").forEach((button) => {
    button.addEventListener("click", () => {
      state.typeActivity = null;
      state.selectedTypeGroup = activity.type;
      const typeActivities = state.dataset.activities.filter((candidate) => candidate.type === activity.type);
      renderTypeGroupQuestions(typeActivities);
      els.typeDetail.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  els.typeDetail.querySelector("#typeResetButton")?.addEventListener("click", () => renderTypeDetail(activity));
  els.typeDetail.querySelector("#typeCheckButton")?.addEventListener("click", checkTypePractice);
}

function renderAssertionReasonPractice(activity) {
  const selected = state.typePlacements.answer?.[0] || "";
  const options = getAssertionReasonOptions(activity);
  els.typeDetail.hidden = false;
  els.typeDetail.innerHTML = `
    <div class="format-practice-toolbar">
      <button class="secondary-button compact-button" data-type-back type="button">Back to Questions</button>
      <span>${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
    </div>
    <div class="panel-heading">
      <div>
        <span class="tag">${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
        <h3>Assertion-Reason Question</h3>
        <p>Read the assertion and reason, then choose the correct option.</p>
      </div>
      <span class="counter">${activity.marks} marks</span>
    </div>
    <section class="assertion-question-card">
      <p class="assertion-instruction">In the question given below, there are two statements marked as Assertion [A] and Reason [R]. Read the statements and choose the correct option.</p>
      <div class="assertion-statement"><strong>Assertion [A]:</strong> ${escapeHtml(getAssertionText(activity))}</div>
      <div class="assertion-statement"><strong>Reason [R]:</strong> ${escapeHtml(getReasonText(activity))}</div>
      <div class="assertion-options">
        ${options
          .map(
            (option) => `
              <button class="assertion-option ${selected === option.id ? "selected" : ""}" data-assertion-option="${escapeHtml(option.id)}" type="button">
                <span>${escapeHtml(option.label)}</span>
                <strong>${escapeHtml(option.text)}</strong>
              </button>`
          )
          .join("")}
      </div>
    </section>
    <div class="builder-actions">
      <button class="secondary-button" data-type-back type="button">Back to Questions</button>
      <button class="secondary-button" id="typeResetButton" type="button">Reset Format</button>
      <button class="primary-button" id="typeCheckButton" type="button">Check Format</button>
    </div>
    <div id="typeCheckResult" class="format-result"></div>
    <div class="model-answer"><strong>Model answer</strong><p>${escapeHtml(activity.modelAnswer)}</p></div>
  `;
  els.typeDetail.querySelectorAll("[data-assertion-option]").forEach((button) => {
    button.addEventListener("click", () => {
      state.typePlacements.answer = [button.dataset.assertionOption];
      state.typeSubmitted = false;
      renderAssertionReasonPractice(activity);
    });
  });
  els.typeDetail.querySelectorAll("[data-type-back]").forEach((button) => {
    button.addEventListener("click", () => {
      state.typeActivity = null;
      state.selectedTypeGroup = activity.type;
      renderTypeGroupQuestions(state.dataset.activities.filter((candidate) => candidate.type === activity.type));
      els.typeDetail.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  els.typeDetail.querySelector("#typeResetButton")?.addEventListener("click", () => renderTypeDetail(activity));
  els.typeDetail.querySelector("#typeCheckButton")?.addEventListener("click", checkTypePractice);
}

function renderCauseEffectPractice(activity) {
  const pairs = getCauseEffectPairs(activity);
  pairs.forEach((pair) => {
    state.typePlacements[pair.cause.id] = state.typePlacements[pair.cause.id] || [];
  });
  const effects = getCauseEffectEffects(pairs);
  els.typeDetail.hidden = false;
  els.typeDetail.innerHTML = `
    <div class="format-practice-toolbar">
      <button class="secondary-button compact-button" data-type-back type="button">Back to Questions</button>
      <span>${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
    </div>
    <div class="panel-heading">
      <div>
        <span class="tag">${escapeHtml(typeLabels[activity.type] || activity.type)}</span>
        <h3>Cause and Effect Match</h3>
        <p>Match each cause on the left with the correct effect on the right.</p>
      </div>
      <span class="counter">${activity.marks} marks</span>
    </div>
    <section class="cause-effect-card">
      <div class="cause-effect-directions">Choose the effect letter for each cause.</div>
      <div class="cause-effect-grid">
        <div class="cause-effect-column">
          <h4>Cause</h4>
          ${pairs
            .map((pair, index) => {
              const selected = state.typePlacements[pair.cause.id]?.[0] || "";
              const correctness = state.typeSubmitted && selected ? selected === pair.effect.id : null;
              return `
                <label class="cause-match-row ${correctness === true ? "correct" : correctness === false ? "wrong" : ""}">
                  <span>${index + 1}.</span>
                  <strong>${escapeHtml(pair.cause.text)}</strong>
                  <select data-cause-id="${escapeHtml(pair.cause.id)}" aria-label="Effect for cause ${index + 1}">
                    <option value="">Choose</option>
                    ${effects.map((effect) => `<option value="${escapeHtml(effect.id)}" ${selected === effect.id ? "selected" : ""}>${escapeHtml(effect.letter)}</option>`).join("")}
                  </select>
                </label>`;
            })
            .join("")}
        </div>
        <div class="cause-effect-column effects">
          <h4>Effect</h4>
          ${effects.map((effect) => `<div class="effect-row"><span>${escapeHtml(effect.letter)}.</span><strong>${escapeHtml(effect.text)}</strong></div>`).join("")}
        </div>
      </div>
    </section>
    <div class="builder-actions">
      <button class="secondary-button" data-type-back type="button">Back to Questions</button>
      <button class="secondary-button" id="typeResetButton" type="button">Reset Match</button>
      <button class="primary-button" id="typeCheckButton" type="button">Check Match</button>
    </div>
    <div id="typeCheckResult" class="format-result"></div>
    <div class="model-answer"><strong>Model answer</strong><p>${escapeHtml(activity.modelAnswer)}</p></div>
  `;
  els.typeDetail.querySelectorAll("[data-cause-id]").forEach((select) => {
    select.addEventListener("change", () => {
      state.typePlacements[select.dataset.causeId] = select.value ? [select.value] : [];
      state.typeSubmitted = false;
      renderCauseEffectPractice(activity);
    });
  });
  els.typeDetail.querySelectorAll("[data-type-back]").forEach((button) => {
    button.addEventListener("click", () => {
      state.typeActivity = null;
      state.selectedTypeGroup = activity.type;
      renderTypeGroupQuestions(state.dataset.activities.filter((candidate) => candidate.type === activity.type));
      els.typeDetail.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  els.typeDetail.querySelector("#typeResetButton")?.addEventListener("click", () => renderTypeDetail(activity));
  els.typeDetail.querySelector("#typeCheckButton")?.addEventListener("click", checkTypePractice);
}

function getCauseEffectPairs(activity) {
  const pairs = activity.answerKey?.pairs || [];
  return pairs
    .map(([causeId, effectId]) => ({
      cause: findStandardItem(activity, causeId),
      effect: findStandardItem(activity, effectId),
    }))
    .filter((pair) => pair.cause && pair.effect);
}

function getCauseEffectEffects(pairs) {
  const letters = "abcdefghijklmnopqrstuvwxyz".split("");
  return pairs.map((pair, index) => ({ ...pair.effect, letter: letters[index] || String(index + 1) }));
}

function getAssertionText(activity) {
  return activity.assertion || activity.correctItems?.[0]?.text || activity.question;
}

function getReasonText(activity) {
  return activity.reason || activity.correctItems?.[1]?.text || activity.correctItems?.[0]?.text || activity.modelAnswer;
}

function getAssertionReasonOptions() {
  return [
    { id: "both_true", label: "(a)", text: "Both Assertion [A] and Reason [R] are true." },
    { id: "both_false", label: "(b)", text: "Both Assertion [A] and Reason [R] are false." },
    { id: "assertion_true_reason_false", label: "(c)", text: "Assertion [A] is true but Reason [R] is false." },
    { id: "assertion_false_reason_true", label: "(d)", text: "Assertion [A] is false but Reason [R] is true." },
  ];
}

function renderContinuousTablePractice(activities) {
  initializeContinuousTableState(activities);
  activities.forEach((activity) => {
    state.continuousTablePlacements[activity.id] = state.continuousTablePlacements[activity.id] || {};
    activity.answerSlots.forEach((slot) => {
      state.continuousTablePlacements[activity.id][slot.id] = state.continuousTablePlacements[activity.id][slot.id] || [];
    });
  });
  els.typeSummary.textContent = `${activities.length} table questions for ${state.dataset.source.chapter}. Choose a question to practise.`;
  if (els.typeDetail) els.typeDetail.hidden = false;
  renderContinuousTableList(activities);
}

function initializeContinuousTableState(activities) {
  const validIds = new Set(activities.map((activity) => activity.id));
  Object.keys(state.continuousTablePlacements).forEach((activityId) => {
    if (!validIds.has(activityId)) delete state.continuousTablePlacements[activityId];
  });
  Object.keys(state.continuousTableSubmitted).forEach((activityId) => {
    if (!validIds.has(activityId)) delete state.continuousTableSubmitted[activityId];
  });
  if (!validIds.has(state.continuousTableSelectedId)) state.continuousTableSelectedId = "";
}

function renderContinuousTableList(activities) {
  const container = els.typeDetail || els.typeGrid;
  const selected = activities.find((activity) => activity.id === state.continuousTableSelectedId) || activities[0];
  const questionButtons = activities
    .map(
      (activity, index) => `
        <button class="table-question-button ${activity.id === state.continuousTableSelectedId ? "active" : ""}" data-table-question="${escapeHtml(activity.id)}" type="button">
          <span>${index + 1}</span>
          <strong>${escapeHtml(activity.tableData?.title || activity.question)}</strong>
          <em>${escapeHtml(String(activity.marks || ""))} marks</em>
        </button>`
    )
    .join("");
  if (state.continuousTableView !== "detail" || !selected) {
    state.continuousTableView = "list";
    container.innerHTML = `
      <section class="table-list-shell">
        <div class="panel-heading">
          <div>
            <span class="tag">${escapeHtml(typeLabels.data_chart_table)}</span>
            <h3>Table Questions</h3>
            <p>Select a question to open the practice table.</p>
          </div>
          <span class="counter">${activities.length} questions</span>
        </div>
        <div class="table-question-list full" aria-label="Table questions">
          ${questionButtons}
        </div>
      </section>`;
  } else {
    state.continuousTableSelectedId = selected.id;
    container.innerHTML = `
      <section class="table-question-detail">
        ${renderContinuousTableActivity(selected, activities.indexOf(selected))}
      </section>`;
  }
  container.querySelectorAll("[data-table-question]").forEach((button) => {
    button.addEventListener("click", () => {
      state.continuousTableSelectedId = button.dataset.tableQuestion;
      state.continuousTableView = "detail";
      renderContinuousTableList(activities);
      container.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  container.querySelector("[data-table-back]")?.addEventListener("click", () => {
    state.continuousTableView = "list";
    renderContinuousTableList(activities);
    container.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  container.querySelectorAll("[data-cont-item]").forEach((button) => {
    button.addEventListener("dragstart", (event) => {
      event.dataTransfer.setData("text/plain", button.dataset.contItem);
      event.dataTransfer.setData("activity/id", button.dataset.activityId);
    });
    button.addEventListener("click", () => {
      const placed = button.dataset.placed === "1";
      if (placed) removeContinuousItem(button.dataset.activityId, button.dataset.contItem);
      else placeContinuousItem(button.dataset.activityId, button.dataset.contItem);
    });
  });
  container.querySelectorAll("[data-cont-slot]").forEach((slot) => {
    slot.addEventListener("dragover", (event) => {
      event.preventDefault();
      slot.classList.add("drag-over");
    });
    slot.addEventListener("dragleave", () => slot.classList.remove("drag-over"));
    slot.addEventListener("drop", (event) => {
      event.preventDefault();
      slot.classList.remove("drag-over");
      const itemId = event.dataTransfer.getData("text/plain");
      const activityId = event.dataTransfer.getData("activity/id") || slot.dataset.activityId;
      if (itemId && activityId === slot.dataset.activityId) placeContinuousItem(activityId, itemId, slot.dataset.contSlot);
    });
  });
  container.querySelectorAll("[data-cont-check]").forEach((button) => {
    button.addEventListener("click", () => {
      state.continuousTableSubmitted[button.dataset.contCheck] = true;
      renderContinuousTableList(activities);
    });
  });
  container.querySelectorAll("[data-cont-reset]").forEach((button) => {
    button.addEventListener("click", () => {
      const activity = activities.find((candidate) => candidate.id === button.dataset.contReset);
      state.continuousTablePlacements[activity.id] = {};
      activity.answerSlots.forEach((slot) => {
        state.continuousTablePlacements[activity.id][slot.id] = [];
      });
      state.continuousTableSubmitted[activity.id] = false;
      renderContinuousTableList(activities);
    });
  });
}

function renderContinuousTableActivity(activity, index) {
  const placedIds = Object.values(state.continuousTablePlacements[activity.id] || {}).flat();
  const available = getStandardItems(activity).filter((item) => !placedIds.includes(item.id));
  const result = scoreContinuousTable(activity);
  return `
    <article class="continuous-table-card">
      <div class="table-practice-toolbar">
        <button class="secondary-button compact-button" data-table-back type="button">Back to Questions</button>
        <span>${index + 1} / ${state.dataset.activities.filter((candidate) => candidate.type === "data_chart_table").length}</span>
      </div>
      <div class="type-card-head">
        <span class="type-index">${index + 1}</span>
        <div>
          <h3>${escapeHtml(activity.question)}</h3>
          <p>${escapeHtml(activity.instructions)}</p>
        </div>
      </div>
      ${renderContinuousTable(activity)}
      <div class="standard-bank">
        ${available.map((item) => renderContinuousChip(activity, item, false, "")).join("")}
      </div>
      <div class="builder-actions">
        <button class="secondary-button" data-cont-reset="${escapeHtml(activity.id)}" type="button">Reset Table</button>
        <button class="primary-button" data-cont-check="${escapeHtml(activity.id)}" type="button">Check Table</button>
      </div>
      <div class="format-result">${state.continuousTableSubmitted[activity.id] ? `Correct cells: ${result.correct} / ${result.expected}` : ""}</div>
    </article>`;
}

function renderContinuousTable(activity) {
  const table = activity.tableData;
  return `<div class="special-layout data-layout">
    <table>
      <thead><tr>${table.headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
      <tbody>${table.rows.map((row) => `<tr>${row.map((cell) => renderContinuousTableCell(activity, cell)).join("")}</tr>`).join("")}</tbody>
    </table>
  </div>`;
}

function renderContinuousTableCell(activity, cell) {
  if (!cell || typeof cell !== "object" || !cell.slotId) return `<td>${escapeHtml(cell)}</td>`;
  const placed = state.continuousTablePlacements[activity.id]?.[cell.slotId] || [];
  return `<td class="table-drop-td">
    <div class="table-drop-cell" data-activity-id="${escapeHtml(activity.id)}" data-cont-slot="${escapeHtml(cell.slotId)}">
      ${
        placed.length
          ? placed.map((itemId) => renderContinuousChip(activity, findStandardItem(activity, itemId), true, cell.slotId)).join("")
          : `<span>${escapeHtml(cell.label || "Drop calculated value")}</span>`
      }
    </div>
  </td>`;
}

function renderContinuousChip(activity, item, placed, slotId) {
  if (!item) return "";
  const submitted = state.continuousTableSubmitted[activity.id];
  const correctness = submitted ? getContinuousCorrectness(activity, item, placed, slotId) : null;
  const className = correctness === null ? "neutral" : correctness ? "correct" : "wrong";
  return `<button class="standard-chip ${className}" data-activity-id="${escapeHtml(activity.id)}" data-cont-item="${escapeHtml(item.id)}" data-placed="${placed ? "1" : "0"}" draggable="true" type="button">${escapeHtml(item.text)}</button>`;
}

function placeContinuousItem(activityId, itemId, targetSlotId = "") {
  const activity = state.dataset.activities.find((candidate) => candidate.id === activityId);
  if (!activity) return;
  const slot =
    activity.answerSlots.find((candidate) => candidate.id === targetSlotId) ||
    activity.answerSlots.find((candidate) => (state.continuousTablePlacements[activityId][candidate.id] || []).length === 0) ||
    activity.answerSlots[0];
  if (!slot) return;
  removeContinuousItem(activityId, itemId, false);
  state.continuousTablePlacements[activityId][slot.id] = [itemId];
  state.continuousTableSubmitted[activityId] = false;
  renderContinuousTableList(state.dataset.activities.filter((candidate) => candidate.type === "data_chart_table"));
}

function removeContinuousItem(activityId, itemId, rerender = true) {
  Object.keys(state.continuousTablePlacements[activityId] || {}).forEach((slotId) => {
    state.continuousTablePlacements[activityId][slotId] = state.continuousTablePlacements[activityId][slotId].filter((id) => id !== itemId);
  });
  state.continuousTableSubmitted[activityId] = false;
  if (rerender) renderContinuousTableList(state.dataset.activities.filter((candidate) => candidate.type === "data_chart_table"));
}

function getContinuousCorrectness(activity, item, placed, slotId) {
  if (!placed) return false;
  const accepted = new Set(asArray(activity.answerKey?.[slotId]));
  return accepted.has(item.id);
}

function scoreContinuousTable(activity) {
  let correct = 0;
  let wrong = 0;
  activity.answerSlots.forEach((slot) => {
    const accepted = new Set(asArray(activity.answerKey?.[slot.id]));
    const placed = state.continuousTablePlacements[activity.id]?.[slot.id] || [];
    placed.forEach((itemId) => (accepted.has(itemId) ? (correct += 1) : (wrong += 1)));
  });
  return { correct, wrong, expected: activity.answerSlots.length };
}

function getStandardItems(activity) {
  return [...activity.correctItems.map((item) => ({ ...item, isCorrect: true })), ...activity.distractors.map((item) => ({ ...item, isCorrect: false }))];
}

function findStandardItem(activity, itemId) {
  return getStandardItems(activity).find((item) => item.id === itemId);
}

function renderStandardChip(item, placed, slotId) {
  if (!item) return "";
  const correctness = state.typeSubmitted ? getStandardCorrectness(item, placed, slotId) : null;
  const className = correctness === null ? "neutral" : correctness ? "correct" : "wrong";
  return `<button class="standard-chip ${className}" data-type-item="${escapeHtml(item.id)}" data-placed="${placed ? "1" : "0"}" draggable="true" type="button">${escapeHtml(item.text)}</button>`;
}

function renderTypeJoinedAnswerPreview(activity) {
  if (isJoinedAnswerActivity(activity)) return "";
  const selected = getInteractiveTypeSlots(activity)
    .flatMap((slot) => state.typePlacements[slot.id] || [])
    .map((itemId) => findStandardItem(activity, itemId)?.text || "")
    .filter(Boolean);
  return selected.length > 1 ? `<p class="joined-answer-preview full-answer-preview">${escapeHtml(selected.join(" "))}</p>` : "";
}

function renderTypeSlotContent(activity, slot) {
  const placed = state.typePlacements[slot.id] || [];
  if (!placed.length) return "<span>Click options to place them here</span>";
  const chips = placed.map((itemId) => renderStandardChip(findStandardItem(activity, itemId), true, slot.id)).join("");
  if (!isJoinedAnswerActivity(activity, slot.id)) return chips;
  const joined = placed
    .map((itemId) => findStandardItem(activity, itemId)?.text || "")
    .filter(Boolean)
    .join(" ");
  return `<p class="joined-answer-preview">${escapeHtml(joined)}</p><div class="joined-answer-parts">${chips}</div>`;
}

function placeTypeItem(itemId, targetSlotId = "") {
  if (!state.typeActivity) return;
  const activity = state.typeActivity;
  const slots = getInteractiveTypeSlots(activity);
  const slot =
    slots.find((candidate) => candidate.id === targetSlotId) ||
    slots.find((candidate) => (state.typePlacements[candidate.id] || []).length === 0) ||
    slots[0];
  if (!slot) return;
  removeTypeItem(itemId, false);
  if (isJoinedAnswerActivity(activity, slot.id)) {
    state.typePlacements[slot.id] = [...(state.typePlacements[slot.id] || []), itemId];
  } else {
    state.typePlacements[slot.id] = [itemId];
  }
  state.typeSubmitted = false;
  renderTypePractice();
}

function attachTypeDropZone(element) {
  element.addEventListener("dragover", (event) => {
    event.preventDefault();
    element.classList.add("drag-over");
  });
  element.addEventListener("dragleave", () => element.classList.remove("drag-over"));
  element.addEventListener("drop", (event) => {
    event.preventDefault();
    element.classList.remove("drag-over");
    const itemId = event.dataTransfer.getData("text/plain");
    if (itemId) placeTypeItem(itemId, element.dataset.typeSlot);
  });
}

function removeTypeItem(itemId, rerender = true) {
  Object.keys(state.typePlacements).forEach((slotId) => {
    state.typePlacements[slotId] = state.typePlacements[slotId].filter((id) => id !== itemId);
  });
  state.typeSubmitted = false;
  if (rerender) renderTypePractice();
}

function getStandardCorrectness(item, placed, slotId) {
  if (!placed) return item.isCorrect;
  if (!item.isCorrect) return false;
  const activity = state.typeActivity;
  const key = activity?.answerKey || {};
  if (isJoinedAnswerActivity(activity, slotId)) {
    const expected = getJoinedAnswerExpectedIds(activity);
    const selected = state.typePlacements[slotId] || [];
    const selectedIndex = selected.findIndex((id) => id === item.id);
    return expected[selectedIndex] === item.id;
  }
  const ordered = activity?.answerKey?.orderedItemIds;
  if (ordered) {
    const slotIndex = activity.answerSlots.findIndex((slot) => slot.id === slotId);
    return ordered[slotIndex] === item.id;
  }
  if (key[slotId]) return asArray(key[slotId]).includes(item.id);
  if (key.pairs) return key.pairs.some((pair) => pair.includes(item.id));
  if (key.acceptedItemIds) return key.acceptedItemIds.includes(item.id);
  if (key.answers) return key.answers.includes(item.id);
  const required = key.requiredItemIds || activity?.correctItems?.map((correct) => correct.id) || [];
  return required.includes(item.id);
}

function checkTypePractice() {
  const activity = state.typeActivity;
  if (!activity) return;
  state.typeSubmitted = true;
  const selected = Object.values(state.typePlacements).flat();
  const result = scoreStandardActivity(activity, selected);
  const { correct, wrong, expected } = result;
  const score = Math.max(0, Math.round(((correct - wrong) / expected) * activity.marks));
  renderTypePractice();
  const resultNode = els.typeDetail.querySelector("#typeCheckResult");
  if (resultNode) {
    resultNode.textContent =
      activity.type === "cause_effect"
        ? correct === expected
          ? `Correct: ${activity.marks}/${activity.marks}`
          : `Matched ${correct} / ${expected}. Check the cause-effect letters.`
        : activity.type === "assertion_reason"
        ? correct === expected
          ? `Correct: ${activity.marks}/${activity.marks}`
          : "Choose the option that correctly matches Assertion [A] and Reason [R]."
        : score === activity.marks
          ? `Correct: ${score}/${activity.marks}`
          : `Score: ${score}/${activity.marks}. Check order and remove distractors.`;
  }
}

function scoreStandardActivity(activity, selected) {
  if (activity.type === "data_chart_table" && hasTableInputDrops(activity)) {
    return scoreTableInputActivity(activity);
  }
  if (activity.type === "cause_effect" && activity.answerKey?.pairs) {
    let correct = 0;
    let wrong = 0;
    activity.answerKey.pairs.forEach(([causeId, effectId]) => {
      const selectedEffect = state.typePlacements[causeId]?.[0];
      if (!selectedEffect) return;
      if (selectedEffect === effectId) correct += 1;
      else wrong += 1;
    });
    return { correct, wrong, expected: activity.answerKey.pairs.length };
  }
  if (activity.type === "assertion_reason") {
    const selectedOption = selected[0] || "";
    const correctOption = activity.answerKey?.assertionReasonOption || "both_true";
    return { correct: selectedOption === correctOption ? 1 : 0, wrong: selectedOption && selectedOption !== correctOption ? 1 : 0, expected: 1 };
  }
  const key = activity.answerKey || {};
  if (isJoinedAnswerActivity(activity)) {
    const slot = getJoinedAnswerSlot(activity);
    const selectedOrder = slot ? state.typePlacements[slot.id] || [] : selected;
    const expected = getJoinedAnswerExpectedIds(activity);
    let correct = 0;
    let wrong = 0;
    selectedOrder.forEach((id, index) => {
      if (id === expected[index]) correct += 1;
      else wrong += 1;
    });
    return { correct, wrong, expected: expected.length || 1 };
  }
  if (key.orderedItemIds) {
    let correct = 0;
    let wrong = 0;
    activity.answerSlots.forEach((slot, index) => {
      const id = state.typePlacements[slot.id]?.[0];
      if (!id) return;
      if (id === key.orderedItemIds[index]) correct += 1;
      else wrong += 1;
    });
    return { correct, wrong, expected: key.orderedItemIds.length };
  }
  if (key.pairs) {
    const accepted = new Set(key.pairs.flat());
    let correct = 0;
    let wrong = 0;
    selected.forEach((id) => (accepted.has(id) ? (correct += 1) : (wrong += 1)));
    return { correct, wrong, expected: accepted.size };
  }
  const groupedKeys = Object.keys(key).filter((name) => Array.isArray(key[name]));
  if (groupedKeys.length) {
    let correct = 0;
    let wrong = 0;
    let expected = 0;
    activity.answerSlots.forEach((slot) => {
      const accepted = new Set(asArray(key[slot.id]));
      if (accepted.size) expected += accepted.size;
      (state.typePlacements[slot.id] || []).forEach((id) => (accepted.has(id) ? (correct += 1) : (wrong += 1)));
    });
    return { correct, wrong, expected: expected || activity.correctItems.length };
  }
  const acceptedIds = key.acceptedItemIds || key.answers || key.requiredItemIds || activity.correctItems.map((item) => item.id);
  const accepted = new Set(acceptedIds);
  let correct = 0;
  let wrong = 0;
  selected.forEach((id) => (accepted.has(id) ? (correct += 1) : (wrong += 1)));
  return { correct, wrong, expected: key.minimumRequired || accepted.size || 1 };
}

function asArray(value) {
  return Array.isArray(value) ? value : value ? [value] : [];
}

function isJoinedAnswerActivity(activity, slotId = "") {
  if (!activity || ["assertion_reason", "cause_effect"].includes(activity.type)) return false;
  if (activity.type === "data_chart_table" && (activity.tableData?.dropMode === "table-cells" || hasTableBlankDrops(activity) || hasTableInputDrops(activity))) {
    return false;
  }
  const slots = activity.answerSlots || [];
  if (slots.length !== 1) return false;
  return !slotId || slots[0]?.id === slotId;
}

function getJoinedAnswerSlot(activity) {
  return (activity?.answerSlots || [])[0] || null;
}

function getJoinedAnswerExpectedIds(activity) {
  const key = activity?.answerKey || {};
  return key.orderedItemIds || key.requiredItemIds || (activity?.correctItems || []).map((item) => item.id);
}

function layoutRenderer(activity) {
  const correct = activity.correctItems || [];
  const wrong = activity.distractors || [];
  const options = [...correct, ...wrong];
  const chips = (items) => items.map((item) => `<span class="mini-chip neutral">${escapeHtml(item.text)}</span>`).join("");
  if (activity.type === "compare_contrast") {
    return `<div class="special-layout two-col"><div><h4>Group A</h4><div class="drop-preview">${chips(options.slice(0, 2))}</div></div><div><h4>Group B</h4><div class="drop-preview">${chips(options.slice(2, 5))}</div></div></div>`;
  }
  if (activity.type === "cause_effect") {
    return `<div class="special-layout pair-layout">${options.slice(0, 6).map((item, index) => `<div>${index + 1}</div><div class="mini-chip neutral">${escapeHtml(item.text)}</div><div class="arrow-cell">-></div><div class="mini-chip neutral">Choose matching effect</div>`).join("")}</div>`;
  }
  if (activity.type.includes("sequence") || activity.type.includes("timeline")) {
    return `<div class="special-layout sequence-preview">${options.slice(0, 6).map((item, index) => `<div><span>${index + 1}</span>${escapeHtml(item.text)}</div>`).join("")}</div>`;
  }
  if (activity.type === "assertion_reason") {
    return `<div class="special-layout assertion-layout"><div><h4>Assertion</h4>${chips(options.slice(0, 1))}</div><div><h4>Reason</h4>${chips(options.slice(1, 2))}</div><div><h4>Options</h4>${chips(options.slice(2, 6))}</div></div>`;
  }
  if (activity.type === "data_chart_table") {
    if (activity.tableData?.headers?.length && activity.tableData?.rows?.length) {
      const headers = activity.tableData.headers;
      const rows = activity.tableData.rows;
      return `<div class="special-layout data-layout">
        <table>
          <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows
              .map((row, rowIndex) => `<tr>${row.map((cell, cellIndex) => renderTableCell(activity, cell, rowIndex, cellIndex)).join("")}</tr>`)
              .join("")}
          </tbody>
        </table>
      </div>`;
    }
    return `<div class="special-layout data-layout"><table><tbody>${options.slice(0, 4).map((item, index) => `<tr><th>Option ${index + 1}</th><td>${escapeHtml(item.text)}</td></tr>`).join("")}</tbody></table></div>`;
  }
  return `<div class="special-layout generic-layout"><div class="drop-preview">${chips(options)}</div></div>`;
}

function renderTableCell(activity, cell, rowIndex = 0, cellIndex = 0) {
  if (!cell || typeof cell !== "object" || !cell.slotId) {
    if (isTableBlankCell(cell)) return renderTextTableBlankCell(activity, cell, rowIndex, cellIndex);
    return `<td>${escapeHtml(cell)}</td>`;
  }
  const placed = state.typePlacements[cell.slotId] || [];
  const slotLabel = cell.label || "Drop answer";
  return `<td class="table-drop-td">
    <div class="table-drop-cell" data-type-slot="${escapeHtml(cell.slotId)}">
      ${
        placed.length
          ? placed.map((itemId) => renderStandardChip(findStandardItem(activity, itemId), true, cell.slotId)).join("")
          : `<span>${escapeHtml(slotLabel)}</span>`
      }
    </div>
  </td>`;
}

function renderTextTableBlankCell(activity, cell, rowIndex, cellIndex) {
  const slotId = getTableBlankSlotId(rowIndex, cellIndex);
  if (isTableInputSlot(activity, slotId)) return renderTableInputCell(activity, cell, slotId);
  const placed = state.typePlacements[slotId] || [];
  const text = String(cell);
  const parts = text.split(/_{3,}/);
  const before = parts[0] || "";
  const after = parts.slice(1).join(" ");
  return `<td class="table-drop-td table-text-drop-td">
    <div class="table-text-drop-cell">
      ${before ? `<span>${escapeHtml(before.trim())}</span>` : ""}
      <div class="table-drop-cell inline-table-drop" data-type-slot="${escapeHtml(slotId)}">
        ${
          placed.length
            ? placed.map((itemId) => renderStandardChip(findStandardItem(activity, itemId), true, slotId)).join("")
            : "<span>Drop option here</span>"
        }
      </div>
      ${after ? `<span>${escapeHtml(after.trim())}</span>` : ""}
    </div>
  </td>`;
}

function renderTableInputCell(activity, cell, slotId) {
  const expected = getTableInputExpected(activity, slotId);
  const value = state.typePlacements[slotId]?.[0] || "";
  const submitted = state.typeSubmitted && value;
  const correct = submitted ? isTypedAnswerCorrect(value, expected) : null;
  const className = correct === null ? "" : correct ? " correct" : " wrong";
  const text = String(cell);
  const parts = text.split(/_{3,}/);
  const before = parts[0] || "";
  const after = parts.slice(1).join(" ");
  return `<td class="table-drop-td table-text-drop-td">
    <label class="table-input-wrap${className}">
      ${before ? `<span>${escapeHtml(before.trim())}</span>` : ""}
      <input class="table-answer-input" data-table-input-slot="${escapeHtml(slotId)}" value="${escapeHtml(value)}" inputmode="decimal" autocomplete="off" placeholder="Type answer" />
      ${after ? `<span>${escapeHtml(after.trim())}</span>` : ""}
    </label>
  </td>`;
}

function getInteractiveTypeSlots(activity) {
  if (hasTableInputDrops(activity)) return getTableInputSlots(activity);
  if (hasTableBlankDrops(activity) && activity.tableData?.dropMode !== "table-cells") return getTableBlankSlots(activity);
  return activity.answerSlots || [];
}

function hasTableInputDrops(activity) {
  return Boolean(activity?.type === "data_chart_table" && activity.tableData?.inputAnswers);
}

function getTableInputSlots(activity) {
  return Object.keys(activity.tableData?.inputAnswers || {}).map((id, index) => ({ id, label: `Input ${index + 1}` }));
}

function isTableInputSlot(activity, slotId) {
  return Boolean(activity?.tableData?.inputAnswers?.[slotId]);
}

function getTableInputExpected(activity, slotId) {
  return asArray(activity?.tableData?.inputAnswers?.[slotId]);
}

function scoreTableInputActivity(activity) {
  const entries = Object.entries(activity.tableData?.inputAnswers || {});
  let correct = 0;
  let wrong = 0;
  entries.forEach(([slotId, expected]) => {
    const value = state.typePlacements[slotId]?.[0] || "";
    if (!value) return;
    if (isTypedAnswerCorrect(value, asArray(expected))) correct += 1;
    else wrong += 1;
  });
  return { correct, wrong, expected: entries.length || 1 };
}

function isTypedAnswerCorrect(value, expectedValues) {
  const normalized = normalizeTypedAnswer(value);
  return expectedValues.some((expected) => normalizeTypedAnswer(expected) === normalized);
}

function normalizeTypedAnswer(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/rs\.?|â‚¹|,/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function hasTableBlankDrops(activity) {
  return Boolean(activity?.type === "data_chart_table" && activity.tableData?.rows?.some((row) => row.some(isTableBlankCell)));
}

function getTableBlankSlots(activity) {
  const slots = [];
  activity.tableData?.rows?.forEach((row, rowIndex) => {
    row.forEach((cell, cellIndex) => {
      if (isTableBlankCell(cell)) slots.push({ id: getTableBlankSlotId(rowIndex, cellIndex), label: `Table blank ${slots.length + 1}` });
    });
  });
  return slots;
}

function getTableBlankSlotId(rowIndex, cellIndex) {
  return `table-blank-${rowIndex}-${cellIndex}`;
}

function isTableBlankCell(cell) {
  return typeof cell === "string" && /_{3,}/.test(cell);
}

function renderDatasetSummary() {
  const source = state.dataset.source;
  const subjectCount = uniqueValues(state.datasets.filter((dataset) => Number(dataset.classLevel) === Number(source.classLevel)), "subject").length;
  els.librarySummary.textContent = `Class ${source.classLevel} has ${state.datasets.filter((dataset) => Number(dataset.classLevel) === Number(source.classLevel)).length} active chapter set(s) across ${subjectCount} subject area(s). Current: ${source.book}, Chapter ${source.chapterNumber}: ${source.chapter}.`;
  renderDatasetList();
}

function renderDatasetList() {
  if (!els.datasetList) return;
  if (!state.datasets.length) {
    els.datasetList.innerHTML = "<p>No generated datasets were discovered yet.</p>";
    return;
  }
  const classLevel = String(state.datasetFilters.classLevel || state.user?.classLevel || "");
  const visible = state.datasets.filter((dataset) => !classLevel || String(dataset.classLevel) === classLevel);
  const groups = new Map();
  visible.forEach((dataset) => {
    const groupName = `${dataset.subject} - ${dataset.book}`;
    if (!groups.has(groupName)) groups.set(groupName, []);
    groups.get(groupName).push(dataset);
  });
  els.datasetList.innerHTML = [...groups.entries()]
    .map(
      ([groupName, datasets]) => `
        <section class="dataset-group">
          <h3>${escapeHtml(groupName)} <span>${datasets.length} chapter(s)</span></h3>
          ${datasets
            .map(
              (dataset) => `
                <button class="dataset-row ${state.selectedDataset === datasetKey(dataset) ? "active" : ""}" data-dataset="${escapeHtml(datasetKey(dataset))}" type="button">
                  <strong>Class ${escapeHtml(dataset.classLevel)} ${escapeHtml(dataset.subject)} <em>${escapeHtml(dataset.status || "generated")}</em></strong>
                  <span>${escapeHtml(dataset.book)} - Chapter ${escapeHtml(dataset.chapterNumber)}: ${escapeHtml(dataset.chapter)}</span>
                </button>`
            )
            .join("")}
        </section>`
    )
    .join("");
  els.datasetList.querySelectorAll(".dataset-row").forEach((button) => {
    button.addEventListener("click", async () => {
      await openDataset(button.dataset.dataset);
      switchView("practice");
    });
  });
}

async function renderAdminTools() {
  if (!els.adminReviewList || !["teacher", "admin"].includes(state.user?.role)) return;
  try {
    const dataset = state.selectedDataset ? `?dataset=${encodeURIComponent(state.selectedDataset)}` : "";
    const result = await api(`/api/admin/activities${dataset}`);
    const analytics = await api("/api/teacher/analytics").catch(() => ({ rows: [], assignmentCount: 0 }));
    state.adminActivities = result.activities || [];
    els.adminSummary.textContent = `${state.adminActivities.length} activities ready for review from ${result.source?.chapter || "selected dataset"}. ${analytics.assignmentCount || 0} assignment(s) created.`;
    els.adminReviewList.innerHTML = state.adminActivities
      .slice(0, 24)
      .map(
        (activity) => `
          <article class="review-card">
            <div><strong>${escapeHtml(typeLabels[activity.type] || activity.type)}</strong><p>${escapeHtml(activity.question)}</p></div>
            <select data-activity="${escapeHtml(activity.id)}" aria-label="Review status for ${escapeHtml(activity.id)}">
              <option value="draft">Draft</option>
              <option value="approved">Approved</option>
              <option value="needs_revision">Needs revision</option>
              <option value="rejected">Rejected</option>
            </select>
          </article>`
      )
      .join("");
    els.adminReviewList.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", () => saveReview(select.dataset.activity, select.value));
    });
    renderTeacherAnalytics(analytics.rows || []);
  } catch (error) {
    els.adminReviewList.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
}

function renderTeacherAnalytics(rows) {
  if (!els.teacherAnalytics) return;
  if (!rows.length) {
    els.teacherAnalytics.innerHTML = "<p>No student attempts yet.</p>";
    return;
  }
  els.teacherAnalytics.innerHTML = rows
    .slice(0, 8)
    .map((row) => `<div class="analytics-row"><strong>${escapeHtml(typeLabels[row.activity_type] || row.activity_type)}</strong><span>${row.attempts} attempts - ${row.average_percent || 0}% avg</span></div>`)
    .join("");
}

async function createAssignment(event) {
  event.preventDefault();
  const title = els.assignmentTitle.value.trim() || `${state.dataset?.source?.chapter || "Practice"} assignment`;
  const dueAt = els.assignmentDueDate.value ? Math.floor(new Date(`${els.assignmentDueDate.value}T23:59:59`).getTime() / 1000) : null;
  const datasetPath = state.datasets.find((item) => (item.id || item.jsonPath) === state.selectedDataset)?.jsonPath || state.selectedDataset || "";
  await api("/api/teacher/assignments", {
    method: "POST",
    body: JSON.stringify({ title, datasetPath, classLevel: state.dataset?.source?.classLevel || 7, dueAt }),
  });
  els.assignmentTitle.value = "";
  els.assignmentDueDate.value = "";
  await renderAdminTools();
  await refreshAssignments();
}

async function generateImageAsset(event) {
  event.preventDefault();
  const prompt = els.imagePromptInput.value.trim();
  if (!prompt) {
    showImageGenerationStatus("Enter a prompt first.", true);
    return;
  }
  const [width, height] = els.imageSizeInput.value.split("x").map(Number);
  const seed = els.imageSeedInput.value.trim();
  els.imageGenerateButton.disabled = true;
  showImageGenerationStatus("Generating with SDXL-Lightning. First run may download model weights.", false);
  try {
    const result = await api("/api/admin/image-generation", {
      method: "POST",
      body: JSON.stringify({
        prompt,
        negativePrompt: els.imageNegativeInput.value.trim(),
        width,
        height,
        steps: Number(els.imageStepsInput.value),
        seed,
      }),
    });
    const image = result.image || {};
    els.imageGenerationPreview.src = `${image.path}?v=${Date.now()}`;
    els.imageGenerationPreview.hidden = false;
    els.imageGenerationPath.textContent = image.path || "";
    showImageGenerationStatus("Image generated and saved in the project assets folder.", false);
  } catch (error) {
    showImageGenerationStatus(error.message, true);
  } finally {
    els.imageGenerateButton.disabled = false;
  }
}

function showImageGenerationStatus(message, isError) {
  if (!els.imageGenerationStatus) return;
  els.imageGenerationStatus.textContent = message;
  els.imageGenerationStatus.classList.toggle("error", isError);
}

async function saveReview(activityId, status) {
  const datasetPath = state.datasets.find((item) => (item.id || item.jsonPath) === state.selectedDataset)?.jsonPath || state.selectedDataset || "";
  await api("/api/admin/reviews", {
    method: "POST",
    body: JSON.stringify({ datasetPath, activityId, status, notes: "" }),
  }).catch(() => {});
}


function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

init();

