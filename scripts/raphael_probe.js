const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: false });
  const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
  await page.goto("https://raphael.app/", { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForTimeout(7000);
  const data = await page.evaluate(() => {
    const visible = (el) => {
      const rect = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden";
    };
    return {
      url: location.href,
      title: document.title,
      textareas: [...document.querySelectorAll("textarea")].map((el, index) => ({
        index,
        placeholder: el.placeholder,
        value: el.value,
        visible: visible(el),
        rect: (() => {
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })(),
      })),
      inputs: [...document.querySelectorAll("input")].map((el, index) => ({
        index,
        type: el.type,
        placeholder: el.placeholder,
        value: el.value,
        visible: visible(el),
      })),
      buttons: [...document.querySelectorAll("button")].map((el, index) => ({
        index,
        text: el.innerText,
        aria: el.getAttribute("aria-label"),
        visible: visible(el),
        rect: (() => {
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })(),
      })).filter((button) => button.visible),
      images: [...document.images].map((el, index) => ({
        index,
        src: el.currentSrc || el.src,
        alt: el.alt,
        visible: visible(el),
        naturalWidth: el.naturalWidth,
        naturalHeight: el.naturalHeight,
      })).filter((image) => image.visible && image.naturalWidth > 200),
    };
  });
  console.log(JSON.stringify(data, null, 2));
  await page.screenshot({ path: "raphael-probe.png", fullPage: true });
  await browser.close();
})();
