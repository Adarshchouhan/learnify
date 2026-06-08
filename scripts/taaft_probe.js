const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: false });
  const page = await browser.newPage({ viewport: { width: 1600, height: 950 } });
  await page.goto("https://theresanaiforthat.com/@taaft/image-generator/?ref=header", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.waitForTimeout(7000);
  console.log("URL", page.url());
  console.log("TITLE", await page.title());
  const textareas = await page.locator("textarea").count();
  const buttons = await page.locator("button").evaluateAll((items) =>
    items.slice(0, 30).map((button) => button.innerText || button.getAttribute("aria-label") || "")
  );
  console.log("TEXTAREAS", textareas);
  console.log("BUTTONS", JSON.stringify(buttons, null, 2));
  await page.screenshot({ path: "taaft-probe.png", fullPage: true });
  await browser.close();
})();
