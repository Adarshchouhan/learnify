const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: false });
  const page = await browser.newPage({ viewport: { width: 1600, height: 950 } });
  await page.goto("https://theresanaiforthat.com/@taaft/image-generator/?ref=header", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.waitForTimeout(7000);
  const data = await page.evaluate(() => {
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && style.visibility !== "hidden" && style.display !== "none";
    };
    return {
      textareas: [...document.querySelectorAll("textarea")].map((el, index) => ({
        index,
        value: el.value,
        placeholder: el.placeholder,
        visible: visible(el),
        rect: (() => {
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })(),
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
      })),
      images: [...document.images].map((el, index) => ({
        index,
        src: el.currentSrc || el.src,
        alt: el.alt,
        visible: visible(el),
        naturalWidth: el.naturalWidth,
        naturalHeight: el.naturalHeight,
        rect: (() => {
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height };
        })(),
      })).filter((item) => item.visible && item.naturalWidth > 200),
    };
  });
  console.log(JSON.stringify(data, null, 2));
  await browser.close();
})();
