const DATA_URL = "/api/practice-data";

const state = {
  dataset: null,
  activity: null,
  modes: [],
  answerGroups: [],
  questionIndex: 0,
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
    "feedbackPanel",
    "typeGrid",
    "typeGridPreview",
    "typeSummary",
    "progressSummary",
    "progressEvents",
    "librarySummary",
    "datasetList",
    "assignmentSummary",
    "assignmentList",
    "typeDetail",
    "adminSummary",
    "adminReviewList",
    "assignmentForm",
    "assignmentTitle",
    "assignmentDueDate",
    "teacherAnalytics",
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
  els.assignmentForm?.addEventListener("submit", createAssignment);
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
    const includeAll = ["teacher", "admin"].includes(state.user?.role) ? "?includeAll=1" : "";
    const result = await api(`/api/datasets${includeAll}`);
    state.datasets = result.datasets || [];
    state.selectedDataset = state.selectedDataset || state.datasets[0]?.id || state.datasets[0]?.jsonPath || null;
  } catch {
    state.datasets = [];
  }
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
    .map((event) => `<div><strong>${escapeHtml(event.activity_type)}</strong><span>${event.score}/${event.marks} · ${escapeHtml(event.difficulty)}</span></div>`)
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
  buildAnswerGroups();
  state.activity = getModeActivity(state.mode);
  resetActivity();
  renderTypeLibrary();
  renderDatasetSummary();
  renderAdminTools();
}

function shuffle(items) {
  return [...items].sort((a, b) => hashCode(`${a.id}-${a.text}`) - hashCode(`${b.id}-${b.text}`));
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
  els.optionTitle.textContent = activity.difficulty === "difficult" ? "Phrase Options" : "Sentence Options";
  renderStructure(activity);
  renderSlots(activity);
  renderBank();
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
    body.textContent = slot.label || "Drop item here";
    addDropHandlers(body);
    const placedItems = state.placements[slot.id] || [];
    if (placedItems.length > 0) {
      body.textContent = "";
      placedItems.forEach((itemId) => body.appendChild(createOptionCard(findItem(itemId), true, slot.id)));
    }
    wrapper.append(number, body);
    els.answerSlots.appendChild(wrapper);
  });
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
  card.innerHTML = `<span class="drag-handle">::</span><span class="item-text">${escapeHtml(item.text)}</span><span class="item-badge">${state.submitted ? (isCorrectAfterSubmit ? "✓" : "x") : ""}</span>`;
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
  const targetSlot =
    state.activity.difficulty === "difficult"
      ? slotIds.find((slotId) => (state.placements[slotId] || []).length < 4)
      : slotIds.find((slotId) => (state.placements[slotId] || []).length === 0);
  if (targetSlot) placeInSlot(itemId, targetSlot);
}

function placeInSlot(itemId, slotId) {
  if (!slotId) return;
  state.submitted = false;
  state.lastResult = null;
  removeFromAllPlacements(itemId);
  state.bank = state.bank.filter((item) => item.id !== itemId);
  if (state.activity.difficulty === "difficult") {
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
  const result = activity.difficulty === "difficult" ? checkDifficult(activity) : checkSequenced(activity);
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
  const selectedBySlot = activity.answerSlots.map((slot, index) => {
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
    ${missing.length ? `<p class="feedback-note"><strong>Missing:</strong> ${missing.map(escapeHtml).join("; ")}</p>` : ""}
  `;
  els.progressSummary.textContent = result.isPerfect ? `Latest score: ${result.score}/${activity.marks}. Strong sequence and no distractors selected.` : `Latest score: ${result.score}/${activity.marks}. Put each sentence in its exact placeholder order and remove distractors.`;
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
  if (els.typeDetail) els.typeDetail.hidden = true;
  standardActivities.forEach((activity, index) => {
    els.typeGrid.appendChild(createTypeCard(activity, index));
    if (index < 8) els.typeGridPreview.appendChild(createTypeCard(activity, index, true));
  });
}

function createTypeCard(activity, index, compact = false) {
  const card = document.createElement("article");
  card.className = "type-card";
  const correctPreview = activity.correctItems.slice(0, compact ? 1 : 2);
  const wrongPreview = activity.distractors.slice(0, 1);
  card.innerHTML = `
    <div class="type-card-head"><span class="type-index">${index + 1}</span><h3>${escapeHtml(typeLabels[activity.type] || activity.type)}</h3></div>
    <p>${escapeHtml(activity.question)}</p>
    <div class="mini-answer">
      ${correctPreview.map((item) => `<span class="mini-chip correct">${escapeHtml(item.text)}</span>`).join("")}
      ${wrongPreview.map((item) => `<span class="mini-chip wrong">${escapeHtml(item.text)}</span>`).join("")}
    </div>
  `;
  card.addEventListener("click", () => {
    switchView("types");
    els.typeSummary.textContent = `${typeLabels[activity.type] || activity.type}: ${activity.modelAnswer}`;
    renderTypeDetail(activity);
  });
  return card;
}

function renderTypeDetail(activity) {
  if (!els.typeDetail) return;
  state.typeActivity = activity;
  state.typeSubmitted = false;
  state.typePlacements = {};
  activity.answerSlots.forEach((slot) => {
    state.typePlacements[slot.id] = [];
  });
  renderTypePractice();
}

function renderTypePractice() {
  const activity = state.typeActivity;
  if (!els.typeDetail || !activity) return;
  const renderer = layoutRenderer(activity);
  const placedIds = Object.values(state.typePlacements).flat();
  const available = getStandardItems(activity).filter((item) => !placedIds.includes(item.id));
  els.typeDetail.hidden = false;
  els.typeDetail.innerHTML = `
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
      <div class="standard-slots">
        ${activity.answerSlots
          .map(
            (slot) => `
              <div class="standard-slot">
                <strong>${escapeHtml(slot.label || slot.id)}</strong>
                <div class="standard-slot-body" data-type-slot="${escapeHtml(slot.id)}">
                  ${(state.typePlacements[slot.id] || []).map((itemId) => renderStandardChip(findStandardItem(activity, itemId), true, slot.id)).join("") || "<span>Click options to place them here</span>"}
                </div>
              </div>`
          )
          .join("")}
      </div>
      <div class="standard-bank">
        ${available.map((item) => renderStandardChip(item, false, "")).join("")}
      </div>
      <div class="builder-actions">
        <button class="secondary-button" id="typeResetButton" type="button">Reset Format</button>
        <button class="primary-button" id="typeCheckButton" type="button">Check Format</button>
      </div>
      <div id="typeCheckResult" class="format-result"></div>
    </div>
    <div class="model-answer"><strong>Model answer</strong><p>${escapeHtml(activity.modelAnswer)}</p></div>
  `;
  els.typeDetail.querySelectorAll("[data-type-item]").forEach((button) => {
    button.addEventListener("click", () => {
      const itemId = button.dataset.typeItem;
      const placed = button.dataset.placed === "1";
      if (placed) removeTypeItem(itemId);
      else placeTypeItem(itemId);
    });
  });
  els.typeDetail.querySelector("#typeResetButton")?.addEventListener("click", () => renderTypeDetail(activity));
  els.typeDetail.querySelector("#typeCheckButton")?.addEventListener("click", checkTypePractice);
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
  return `<button class="standard-chip ${className}" data-type-item="${escapeHtml(item.id)}" data-placed="${placed ? "1" : "0"}" type="button">${escapeHtml(item.text)}</button>`;
}

function placeTypeItem(itemId) {
  if (!state.typeActivity) return;
  const slot = state.typeActivity.answerSlots.find((candidate) => (state.typePlacements[candidate.id] || []).length === 0) || state.typeActivity.answerSlots[0];
  if (!slot) return;
  removeTypeItem(itemId, false);
  state.typePlacements[slot.id].push(itemId);
  state.typeSubmitted = false;
  renderTypePractice();
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
    resultNode.textContent = score === activity.marks ? `Correct: ${score}/${activity.marks}` : `Score: ${score}/${activity.marks}. Check order and remove distractors.`;
  }
}

function scoreStandardActivity(activity, selected) {
  const key = activity.answerKey || {};
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

function layoutRenderer(activity) {
  const correct = activity.correctItems || [];
  const wrong = activity.distractors || [];
  const chips = (items, className) => items.map((item) => `<span class="mini-chip ${className}">${escapeHtml(item.text)}</span>`).join("");
  if (activity.type === "compare_contrast") {
    return `<div class="special-layout two-col"><div><h4>Similarities</h4><div class="drop-preview">${chips(correct.slice(0, 2), "correct")}</div></div><div><h4>Differences</h4><div class="drop-preview">${chips(correct.slice(2), "correct")}${chips(wrong.slice(0, 1), "wrong")}</div></div></div>`;
  }
  if (activity.type === "cause_effect") {
    return `<div class="special-layout pair-layout">${correct.map((item, index) => `<div>${index + 1}</div><div class="mini-chip correct">${escapeHtml(item.text)}</div><div class="arrow-cell">-></div><div class="mini-chip ${wrong[index] ? "wrong" : "correct"}">${escapeHtml((wrong[index] || item).text)}</div>`).join("")}</div>`;
  }
  if (activity.type.includes("sequence") || activity.type.includes("timeline")) {
    return `<div class="special-layout sequence-preview">${correct.map((item, index) => `<div><span>${index + 1}</span>${escapeHtml(item.text)}</div>`).join("")}</div><div class="mini-answer">${chips(wrong, "wrong")}</div>`;
  }
  if (activity.type === "assertion_reason") {
    return `<div class="special-layout assertion-layout"><div><h4>Assertion</h4>${chips(correct.slice(0, 1), "correct")}</div><div><h4>Reason</h4>${chips(correct.slice(1, 2), "correct")}</div><div><h4>Options</h4>${chips(correct.slice(2), "correct")}${chips(wrong, "wrong")}</div></div>`;
  }
  if (activity.type === "data_chart_table") {
    return `<div class="special-layout data-layout"><table><tbody>${correct.slice(0, 4).map((item, index) => `<tr><th>Inference ${index + 1}</th><td>${escapeHtml(item.text)}</td></tr>`).join("")}</tbody></table><div>${chips(wrong, "wrong")}</div></div>`;
  }
  return `<div class="special-layout generic-layout"><div class="drop-preview">${chips(correct, "correct")}</div><div class="drop-preview">${chips(wrong, "wrong")}</div></div>`;
}

function renderDatasetSummary() {
  const source = state.dataset.source;
  els.librarySummary.textContent = `${source.book}, Chapter ${source.chapterNumber}: ${source.chapter}. ${state.dataset.coverage.activityCount} activities generated from ${source.pdfPath}.`;
  renderDatasetList();
}

function renderDatasetList() {
  if (!els.datasetList) return;
  if (!state.datasets.length) {
    els.datasetList.innerHTML = "<p>No generated datasets were discovered yet.</p>";
    return;
  }
  els.datasetList.innerHTML = state.datasets
    .map(
      (dataset) => `
        <button class="dataset-row ${state.selectedDataset === (dataset.id || dataset.jsonPath) ? "active" : ""}" data-dataset="${escapeHtml(dataset.id || dataset.jsonPath)}" type="button">
          <strong>Class ${escapeHtml(dataset.classLevel)} ${escapeHtml(dataset.subject)} <em>${escapeHtml(dataset.status || "generated")}</em></strong>
          <span>${escapeHtml(dataset.book)} - Chapter ${escapeHtml(dataset.chapterNumber)}: ${escapeHtml(dataset.chapter)}</span>
        </button>`
    )
    .join("");
  els.datasetList.querySelectorAll(".dataset-row").forEach((button) => {
    button.addEventListener("click", async () => {
      await openDataset(button.dataset.dataset);
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
