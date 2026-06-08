const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const baseUrl = "http://127.0.0.1:5173";
const root = process.cwd();
const datasets = Array.from({ length: 12 }, (_, index) => {
  const number = String(index + 1).padStart(2, "0");
  const files = fs
    .readdirSync(path.join(root, "data", "practice", "class-12", "accountancy-syllabus-question-bank"))
    .filter((name) => name.startsWith(`${number}-`) && !name.includes("numerical-tables") && name.endsWith(".json"));
  if (files.length !== 1) throw new Error(`Expected one base Accountancy chapter file for chapter ${number}, found ${files.length}`);
  return `data/practice/class-12/accountancy-syllabus-question-bank/${files[0]}`;
});

function assertPayload(filePath) {
  const payload = JSON.parse(fs.readFileSync(path.join(root, filePath), "utf8"));
  const numericalTables = payload.activities.filter((activity) => activity.tableOnlyNumerical);
  if (payload.coverage.tablePracticeMode !== "continuous-table-drag-drop") {
    throw new Error(`${filePath} is not marked as continuous table drag/drop.`);
  }
  if (numericalTables.length < 3) throw new Error(`${filePath} has fewer than 3 merged numerical table activities.`);
  if (payload.activities.some((activity) => activity.tableOnlyNumerical && activity.type !== "data_chart_table")) {
    throw new Error(`${filePath} has numerical questions outside table type.`);
  }
  for (const activity of numericalTables) {
    if (activity.type !== "data_chart_table") throw new Error(`${filePath} contains a non-table activity.`);
    if (activity.tableData?.dropMode !== "table-cells") throw new Error(`${activity.id} is not table-cell drop mode.`);
    const blankCount = activity.tableData.rows.flat().filter((cell) => cell && typeof cell === "object" && cell.slotId).length;
    if (blankCount !== activity.answerSlots.length) throw new Error(`${activity.id} blank count does not match slots.`);
    const numericChip = [...activity.correctItems, ...activity.distractors].some((item) => /Rs|%|:|times|\d/.test(item.text));
    if (!numericChip) throw new Error(`${activity.id} does not include numerical chips.`);
  }
}

async function signIn(page, dataset) {
  await page.goto(`${baseUrl}/?dataset=${encodeURIComponent(dataset)}`, { waitUntil: "domcontentloaded" });
  if (!(await page.locator("#authForm").isVisible().catch(() => false))) return;
  const suffix = Date.now();
  await page.locator("#nameInput").fill("Accountancy Table Smoke");
  await page.locator("#emailInput").fill(`accountancy-table-smoke-${suffix}@learnify.test`);
  await page.locator("#passwordInput").fill("SmokeTest12");
  await page.locator("#classInput").selectOption("12");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/signup") && response.status() === 201),
    page.locator("#authSubmit").click(),
  ]);
  await page.waitForResponse((response) => response.url().includes("/api/datasets") && response.status() === 200, { timeout: 20000 }).catch(() => {});
}

async function checkUi(page, dataset) {
  const practiceResponse = page.waitForResponse((response) => response.url().includes("/api/practice-data") && response.url().includes(encodeURIComponent(dataset)) && response.status() === 200, { timeout: 20000 });
  await page.goto(`${baseUrl}/?dataset=${encodeURIComponent(dataset)}`, { waitUntil: "domcontentloaded" });
  await practiceResponse;
  await page.locator('[data-view="types"]').waitFor({ timeout: 15000 });
  const bookLabels = await page.locator("#datasetBookSelect option").allTextContents();
  if (bookLabels.some((label) => label.includes("Numerical Tables"))) {
    throw new Error("Separate Numerical Tables book is still visible in the Book dropdown.");
  }
  await page.locator('[data-view="types"]').click();
  await page.locator('#typeGrid [data-type-group="data_chart_table"]').click();
  if ((await page.locator(".continuous-table-card").count()) === 0) {
    await page.locator("#typeDetail [data-table-question]").first().waitFor({ timeout: 15000 });
    await page.evaluate(() => {
      const buttons = [...document.querySelectorAll("#typeDetail [data-table-question]")];
      const target = buttons[buttons.length - 1];
      if (!(target instanceof HTMLElement)) throw new Error("No table question button found");
      target.click();
    });
  }
  await page.locator(".continuous-table-card").first().waitFor({ timeout: 15000 }).catch(async (error) => {
    const summary = await page.locator("#typeSummary").textContent().catch(() => "");
    const detail = await page.locator("#typeDetail").textContent().catch(() => "");
    throw new Error(`${error.message}\nType summary: ${summary}\nDetail: ${detail.slice(0, 700)}`);
  });
  await page.locator(".continuous-table-card table").first().waitFor({ timeout: 15000 });
  const tableText = (await page.locator(".continuous-table-card table").first().textContent()) || "";
  if (!/Rs|%|ratio|times|\d/.test(tableText)) throw new Error(`Rendered table does not show numerical data. Table text: ${tableText.slice(0, 300)}`);
  const initialPlaced = await page.locator(".table-drop-cell .standard-chip").count();
  await page.locator(".continuous-table-card .standard-bank .standard-chip").first().click();
  const placed = await page.locator(".table-drop-cell .standard-chip").count();
  if (placed <= initialPlaced) throw new Error("Clicking a numerical chip did not place it into a table blank.");
}

async function main() {
  datasets.forEach(assertPayload);
  const browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  try {
    await signIn(page, datasets[0]);
    await checkUi(page, datasets[0]);
    await checkUi(page, datasets[11]);
    console.log("Class 12 Accountancy all-chapter numerical table smoke test passed.");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
