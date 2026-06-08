const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const prompt = `Create a single polished children's textbook AI-art contact sheet with exactly six separate rectangular scenes in a 3 by 2 grid. Warm Indian primary school style, expressive children, soft painterly realism, high quality like a modern English textbook illustration. No text, no labels, no numerals, no badges, no circles, no worksheet graphics, no UI, no watermark.

Six scenes in order:
1. A playful orange cat sitting in different places inside a cozy classroom, showing room positions naturally.
2. A cat above a low table while another cat peeks from under a chair, showing position words naturally.
3. A cat jumping from a low blue stool to a higher yellow stool in a playground, showing up and down movement.
4. Children searching for a hidden cat partly visible behind a curtain and under a mat in a classroom.
5. Children comparing long objects: rope, pencil, stick, and ribbon laid on a classroom floor.
6. Children exploring round objects: ball, plate, wheel, coin-like toy, and round fruit on a table.

Use thin clean gutters between the six cells. Each cell should work as its own 16:9 image crop.`;

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: false });
  const page = await browser.newPage({ viewport: { width: 1600, height: 950 } });
  await page.goto("https://theresanaiforthat.com/@taaft/image-generator/?ref=header", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.waitForTimeout(6000);

  const before = new Set(
    await page.locator('img[src*="media.theresanaiforthat.com/g/image-generator"]').evaluateAll((imgs) =>
      imgs.map((img) => img.currentSrc || img.src)
    )
  );

  const textarea = page.locator('textarea[placeholder="Enter your prompt here"]').first();
  await textarea.fill(prompt);
  const generateButton = page.locator("button").filter({ hasText: "Generate" }).first();
  await generateButton.scrollIntoViewIfNeeded();
  await generateButton.click({ timeout: 60000 });
  console.log("Submitted prompt to TAAFT");

  let newSrc = "";
  for (let i = 0; i < 90; i += 1) {
    await page.waitForTimeout(4000);
    const candidates = await page.locator('img[src*="media.theresanaiforthat.com/g/image-generator"]').evaluateAll((imgs) =>
      imgs
        .map((img) => img.currentSrc || img.src)
        .filter(Boolean)
    );
    newSrc = candidates.find((src) => !before.has(src)) || "";
    if (newSrc) break;
    console.log(`Waiting for generated image... ${i + 1}`);
  }

  await page.screenshot({ path: "taaft-after-generate.png", fullPage: false });
  if (!newSrc) {
    console.log("NO_NEW_IMAGE");
    await browser.close();
    process.exit(2);
  }

  console.log("NEW_IMAGE", newSrc);
  const response = await page.request.get(newSrc.replace(/width=\d+/, "width=1600"));
  if (!response.ok()) {
    console.log("DOWNLOAD_FAILED", response.status());
    await browser.close();
    process.exit(3);
  }
  const outDir = path.join("assets", "question-art", "class1-math-taaft-sheets");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "sheet-01.png"), await response.body());
  console.log("SAVED", path.join(outDir, "sheet-01.png"));
  await browser.close();
})();
