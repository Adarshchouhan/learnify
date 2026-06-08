const { chromium } = require("playwright");

async function main() {
  const browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });
  const email = `smoke-all-classes-${Date.now()}@learnify.local`;

  await page.goto("http://127.0.0.1:5173", { waitUntil: "domcontentloaded" });
  await page.fill("#nameInput", "All Classes Smoke");
  await page.fill("#emailInput", email);
  await page.fill("#passwordInput", "SmokeTest1");
  await page.selectOption("#classInput", "10");
  await page.click("#authSubmit");
  await page.waitForSelector("#dashboardView:not([hidden])", { timeout: 10000 });
  await page.waitForFunction(() => document.querySelectorAll("#datasetClassSelect option").length >= 12, null, { timeout: 10000 });

  const classOptions = await page.$$eval("#datasetClassSelect option", (options) => options.map((option) => option.value));
  for (const klass of Array.from({ length: 12 }, (_, index) => String(index + 1))) {
    if (!classOptions.includes(klass)) throw new Error(`Missing Class ${klass} in class picker`);
  }

  await page.selectOption("#datasetClassSelect", "10");
  await page.waitForTimeout(500);
  const class10Subjects = await page.$$eval("#datasetSubjectSelect option", (options) => options.map((option) => option.textContent.trim()));
  if (class10Subjects.length < 20) throw new Error(`Expected many Class 10 subjects, saw ${class10Subjects.length}`);
  if (!class10Subjects.includes("Science")) throw new Error("Class 10 Science subject missing");
  if (!class10Subjects.includes("Mathematics")) throw new Error("Class 10 Mathematics subject missing");

  await page.selectOption("#datasetSubjectSelect", { label: "Mathematics" });
  await page.waitForTimeout(800);
  const current = await page.textContent("#currentDatasetSummary");
  if (!current.includes("Data Abstractor Question Bank")) {
    throw new Error(`Expected expanded Data Abstractor bank, saw: ${current}`);
  }

  await page.click('[data-view="types"]');
  await page.waitForFunction(() => document.querySelectorAll(".type-card").length > 0, null, { timeout: 10000 });
  const typeCounts = await page.$$eval(".type-card", (cards) =>
    cards.slice(0, 8).map((card) => {
      const text = card.textContent || "";
      const match = text.match(/(\d+)\s+question\(s\)/);
      return match ? Number(match[1]) : 0;
    })
  );
  if (!typeCounts.some((count) => count >= 20)) {
    throw new Error(`Expected expanded question counts, saw ${typeCounts.join(", ")}`);
  }

  await page.click('[data-view="practice"]');
  await page.waitForSelector(".question-card");
  const visualVisible = await page.locator("#questionVisual").evaluate((element) => {
    const style = window.getComputedStyle(element);
    return style.display !== "none" && element.getBoundingClientRect().width > 0;
  });
  if (visualVisible) throw new Error("Question visual placeholder is still visible");
  const questionArt = await page.locator(".question-card").evaluate((element) => window.getComputedStyle(element).getPropertyValue("--question-art"));
  if (questionArt.trim()) throw new Error(`Question art CSS still set: ${questionArt}`);
  const imageCount = await page.locator("#practiceView img:visible").count();
  if (imageCount !== 0) throw new Error(`Expected no visible practice images, saw ${imageCount}`);

  await page.selectOption("#datasetClassSelect", "1");
  await page.waitForTimeout(800);
  const class1ImageCount = await page.locator("#practiceView img:visible").count();
  if (class1ImageCount !== 0) throw new Error(`Expected no visible Class 1 practice images, saw ${class1ImageCount}`);
  const class1VisualVisible = await page.locator("#questionVisual").evaluate((element) => {
    const style = window.getComputedStyle(element);
    return style.display !== "none" && element.getBoundingClientRect().width > 0;
  });
  if (class1VisualVisible) throw new Error("Class 1 question visual placeholder is still visible");

  await browser.close();
  console.log(`Smoke passed. Class picker=${classOptions.length}, Class 10 subjects=${class10Subjects.length}, type counts=${typeCounts.join("/")}`);
}

main().catch(async (error) => {
  console.error(error);
  process.exit(1);
});
