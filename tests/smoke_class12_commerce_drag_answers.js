const { chromium } = require("playwright");

const baseUrl = "http://127.0.0.1:5173";
const dataset = "data/practice/class-12/commerce/chapter-1-leac101-88c964b2.json";

function wordCount(text) {
  return String(text).trim().split(/\s+/).filter(Boolean).length;
}

async function signIn(page) {
  await page.goto(`${baseUrl}/?dataset=${encodeURIComponent(dataset)}&mode=easy`, { waitUntil: "domcontentloaded" });
  if (!(await page.locator("#authForm").isVisible().catch(() => false))) return;
  const suffix = Date.now();
  await page.locator("#nameInput").fill("Class 12 Smoke Test");
  await page.locator("#emailInput").fill(`class12-smoke-${suffix}@learnify.test`);
  await page.locator("#passwordInput").fill("SmokeTest12");
  await page.locator("#classInput").selectOption("12");
  await page.locator("#authSubmit").click();
}

async function main() {
  const browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  const errors = [];

  try {
    await signIn(page);
    await page.locator(".option-card").first().waitFor({ timeout: 15000 });

    const practiceTexts = await page.locator(".option-card .item-text").allTextContents();
    const smallPracticeCards = practiceTexts.filter((text) => wordCount(text) <= 7);
    if (smallPracticeCards.length < 4) {
      errors.push(`Practice bank has too few small cards: ${smallPracticeCards.length}`);
    }

    for (let index = 0; index < Math.min(3, smallPracticeCards.length); index += 1) {
      await page.locator(".option-card").filter({ hasText: smallPracticeCards[index] }).first().click();
    }
    const placedPracticeCount = await page.locator(".drop-slot .option-card.placed").count();
    if (placedPracticeCount < 3) {
      errors.push(`Practice drag/click placement only placed ${placedPracticeCount} cards`);
    }

    await page.locator('[data-view="types"]').click();
    await page.locator('#typeGrid [data-type-group="explain"]').click();
    await page.locator(".type-question-row").first().click();
    await page.locator(".standard-bank .standard-chip").first().waitFor({ timeout: 10000 });

    const typeTexts = await page.locator(".standard-bank .standard-chip").allTextContents();
    const smallTypeCards = typeTexts.filter((text) => wordCount(text) <= 7);
    if (smallTypeCards.length < 4) {
      errors.push(`Question Types bank has too few small cards: ${smallTypeCards.length}`);
    }

    for (let index = 0; index < Math.min(3, smallTypeCards.length); index += 1) {
      await page.locator(".standard-bank .standard-chip").filter({ hasText: smallTypeCards[index] }).first().click();
    }
    await page.locator("#typesView .joined-answer-preview").first().waitFor({ timeout: 5000 });
    const joined = await page.locator("#typesView .joined-answer-preview").first().textContent();
    if (wordCount(joined) <= Math.max(...smallTypeCards.slice(0, 3).map(wordCount))) {
      errors.push("Joined answer preview did not combine selected parts.");
    }

    await page.locator('[data-type-back]').first().click();
    await page.locator('#typeGrid [data-type-group="formulate_question"]').click();
    await page.locator(".type-question-row").first().click();
    await page.locator(".standard-bank .standard-chip").first().waitFor({ timeout: 10000 });
    const formulateTexts = await page.locator(".standard-bank .standard-chip").allTextContents();
    const smallFormulateCards = formulateTexts.filter((text) => wordCount(text) <= 7);
    for (let index = 0; index < Math.min(3, smallFormulateCards.length); index += 1) {
      await page.locator(".standard-bank .standard-chip").filter({ hasText: smallFormulateCards[index] }).first().click();
    }
    const formulatePlacedCount = await page.locator("#typesView .standard-slot-body .standard-chip").count();
    if (formulatePlacedCount < 3) {
      errors.push(`Single Answer slot replaced cards instead of joining them; placed ${formulatePlacedCount}`);
    }
    const formulateJoined = await page.locator("#typesView .joined-answer-preview").first().textContent();
    if (wordCount(formulateJoined) <= Math.max(...smallFormulateCards.slice(0, 3).map(wordCount))) {
      errors.push("Formulate Question joined answer preview did not combine selected parts.");
    }

    if (errors.length) {
      throw new Error(errors.join("\n"));
    }
    console.log("Class 12 Commerce drag-answer smoke test passed.");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
