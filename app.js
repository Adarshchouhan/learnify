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
  if (!state.dataset) {
    state.dataset = await api(DATA_URL);
    buildAnswerGroups();
    state.activity = getModeActivity(state.mode);
  }
  await refreshProgress();
  resetActivity();
  renderTypeLibrary();
  renderDatasetSummary();
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
  els.profileMeta.textContent = `Class ${state.user.classLevel}`;
  els.avatarText.textContent = state.user.name.slice(0, 1).toUpperCase();
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
  });
  return card;
}

function renderDatasetSummary() {
  const source = state.dataset.source;
  els.librarySummary.textContent = `${source.book}, Chapter ${source.chapterNumber}: ${source.chapter}. ${state.dataset.coverage.activityCount} activities generated from ${source.pdfPath}.`;
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
