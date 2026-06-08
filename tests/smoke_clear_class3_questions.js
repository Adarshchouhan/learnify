const { chromium } = require("playwright");

async function main() {
  const browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });
  const email = `smoke-class3-clear-${Date.now()}@learnify.local`;

  await page.goto("http://127.0.0.1:5173", { waitUntil: "domcontentloaded" });
  await page.fill("#nameInput", "Class Three Smoke");
  await page.fill("#emailInput", email);
  await page.fill("#passwordInput", "SmokeTest1");
  await page.selectOption("#classInput", "3");
  await page.click("#authSubmit");
  await page.waitForSelector("#dashboardView:not([hidden])", { timeout: 10000 });
  await page.waitForFunction(() => document.querySelectorAll("#datasetClassSelect option").length >= 12, null, { timeout: 10000 });

  await page.selectOption("#datasetClassSelect", "3");
  await page.waitForTimeout(400);
  await page.selectOption("#datasetSubjectSelect", { label: "English" });
  await page.waitForTimeout(400);
  await page.selectOption("#datasetBookSelect", { label: "English - Santoor" });
  await page.waitForTimeout(800);

  const summary = await page.textContent("#currentDatasetSummary");
  if (!summary.includes("Fun with Friends")) {
    throw new Error(`Expected clear chapter title, saw: ${summary}`);
  }

  const visibleText = await page.locator("#practiceView").innerText();
  const badPatterns = [
    /cesa101/i,
    /Define an important term from/i,
    /Note to the teacher/i,
    /Only one random word/i,
    /A\s+B\s+C\s+D\s+E\s+F/i,
  ];
  for (const pattern of badPatterns) {
    if (pattern.test(visibleText)) throw new Error(`Bad visible text remains: ${pattern}`);
  }

  const title = await page.textContent("#questionTitle");
  if (!/Fun with Friends/.test(title)) throw new Error(`Question title is not clear: ${title}`);

  await browser.close();
  console.log(`Smoke passed. ${summary}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
