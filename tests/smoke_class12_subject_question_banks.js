const { chromium } = require("playwright");

const baseUrl = "http://127.0.0.1:5173";
const datasets = [
  {
    subject: "English",
    path: "data/practice/class-12/english-board-question-bank/01-reading-comprehension.json",
  },
  {
    subject: "Business Studies",
    path: "data/practice/class-12/business-studies-board-question-bank/01-nature-and-principles-of-management.json",
  },
  {
    subject: "Economics",
    path: "data/practice/class-12/economics-board-question-bank/01-macroeconomics-and-national-income.json",
  },
];

function wordCount(text) {
  return String(text).trim().split(/\s+/).filter(Boolean).length;
}

async function signIn(page, dataset) {
  await page.goto(`${baseUrl}/?dataset=${encodeURIComponent(dataset)}&mode=easy`, { waitUntil: "domcontentloaded" });
  if (!(await page.locator("#authForm").isVisible().catch(() => false))) return;
  const suffix = Date.now();
  await page.locator("#nameInput").fill("Class 12 Subject Smoke");
  await page.locator("#emailInput").fill(`class12-subject-smoke-${suffix}@learnify.test`);
  await page.locator("#passwordInput").fill("SmokeTest12");
  await page.locator("#classInput").selectOption("12");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/signup") && response.status() === 201),
    page.locator("#authSubmit").click(),
  ]);
  await page.waitForResponse((response) => response.url().includes("/api/datasets") && response.status() === 200, { timeout: 20000 }).catch(() => {});
}

async function checkDataset(page, item) {
  await page.goto(`${baseUrl}/?dataset=${encodeURIComponent(item.path)}&mode=easy`, { waitUntil: "domcontentloaded" });
  await page.locator(".option-card").first().waitFor({ timeout: 15000 });
  const questionMeta = await page.locator("#questionMeta").textContent();
  if (!questionMeta.includes(item.subject)) throw new Error(`${item.subject} did not load in practice: ${questionMeta}`);
  const practiceTexts = await page.locator(".option-card .item-text").allTextContents();
  if (practiceTexts.filter((text) => wordCount(text) <= 7).length < 4) {
    throw new Error(`${item.subject} practice bank does not contain enough small answer parts.`);
  }

  await page.locator('[data-view="types"]').click();
  await page.locator('#typeGrid [data-type-group="formulate_question"]').click();
  await page.locator(".type-question-row").first().click();
  await page.locator(".standard-bank .standard-chip").first().waitFor({ timeout: 10000 });
  const typeTexts = await page.locator(".standard-bank .standard-chip").allTextContents();
  const smallCards = typeTexts.filter((text) => wordCount(text) <= 7);
  for (let index = 0; index < Math.min(3, smallCards.length); index += 1) {
    await page.locator(".standard-bank .standard-chip").filter({ hasText: smallCards[index] }).first().click();
  }
  const placedCount = await page.locator("#typesView .standard-slot-body .standard-chip").count();
  if (placedCount < 3) throw new Error(`${item.subject} Answer slot replaced cards instead of joining them.`);
  const joined = await page.locator("#typesView .joined-answer-preview").first().textContent();
  if (wordCount(joined) <= Math.max(...smallCards.slice(0, 3).map(wordCount))) {
    throw new Error(`${item.subject} joined preview did not combine selected parts.`);
  }
}

async function main() {
  const browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  try {
    await signIn(page, datasets[0].path);
    for (const item of datasets) await checkDataset(page, item);
    console.log("Class 12 subject question-bank smoke test passed.");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
