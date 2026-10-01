// gen_boards.js — Gemini 批量概念板图生成（在 omp eval 内 %load 执行）
// 任务文件 /tmp/boards_job.json: { "prompts": ["...", "...", "..."], "outPrefix": "/tmp/xx_c", "lastRef": "/tmp/prev_c3.png" 可选 }
// 输出: <outPrefix>1.png .. 3.png；console 打印 saved/duplicate。
const job = JSON.parse(await Bun.file("/tmp/boards_job.json").text());
const crypto = require("crypto");
const tab = browser.tab("gemini-batch");
await tab.run(async function (ctx) { await ctx.page.bringToFront(); });

async function isIdle() {
  return await tab.evaluate(function () {
    return document.body.innerText.indexOf("正在创建您的图片") < 0;
  });
}

async function sendPrompt(text) {
  await Bun.write("/tmp/boards_prompt.txt", text);
  return await tab.run(async function (ctx) {
    const page = ctx.page;
    const t = (await Bun.file("/tmp/boards_prompt.txt").text()).trim();
    await page.bringToFront();
    await new Promise(function (res) { setTimeout(res, 800); });
    const box = await page.evaluate(function () {
      var el = document.querySelector("div[contenteditable='true'][role='textbox']");
      if (!el) return null;
      var rc = el.getBoundingClientRect();
      return { x: rc.x + 150, y: rc.y + Math.max(12, rc.height / 2) };
    });
    if (!box) return { error: "no composer" };
    await page.mouse.click(box.x, box.y);
    await new Promise(function (res) { setTimeout(res, 600); });
    await page.evaluate(function (tt) {
      var tb = document.querySelector("div[contenteditable='true'][role='textbox']");
      tb.focus();
      document.execCommand("insertText", false, tt);
    }, t);
    await new Promise(function (res) { setTimeout(res, 700); });
    const pos = await page.evaluate(function () {
      var btns = document.querySelectorAll("button");
      for (var k = 0; k < btns.length; k++) {
        if ((btns[k].getAttribute("aria-label") || "") === "发送") {
          var rc = btns[k].getBoundingClientRect();
          return { x: Math.round(rc.x + rc.width / 2), y: Math.round(rc.y + rc.height / 2) };
        }
      }
      return null;
    });
    if (pos) {
      await page.mouse.click(pos.x, pos.y);
    } else {
      // 回退：发送中按钮不可见时找可用的提交箭头
      const alt = await page.evaluate(function () {
        var btns = document.querySelectorAll("button[aria-label]");
        for (var k = 0; k < btns.length; k++) {
          var lb = btns[k].getAttribute("aria-label") || "";
          if (lb.indexOf("发送") >= 0 || lb.indexOf("Submit") >= 0 || lb.indexOf("Run") >= 0) {
            var rc = btns[k].getBoundingClientRect();
            if (rc.width > 0) return { x: Math.round(rc.x + rc.width / 2), y: Math.round(rc.y + rc.height / 2) };
          }
        }
        return null;
      });
      if (!alt) return { error: "no send button" };
      await page.mouse.click(alt.x, alt.y);
    }
    await new Promise(function (res) { setTimeout(res, 3000); });
    const cleared = await page.evaluate(function () {
      var tb = document.querySelector("div[contenteditable='true'][role='textbox']");
      return tb ? tb.innerText.trim().length : -1;
    });
    return { submitted: cleared === 0 };
  }, { timeout: 120 });
}

async function exportLast(path) {
  const b64 = await tab.evaluate(function () {
    var imgs = [];
    document.querySelectorAll("img").forEach(function (im) {
      if (im.src.indexOf("blob:") === 0 && im.naturalWidth > 400) imgs.push(im);
    });
    var im = imgs[imgs.length - 1];
    if (!im) return null;
    var c = document.createElement("canvas");
    c.width = im.naturalWidth; c.height = im.naturalHeight;
    c.getContext("2d").drawImage(im, 0, 0);
    return c.toDataURL("image/png").split(",")[1];
  });
  if (!b64) return null;
  const buf = Buffer.from(b64, "base64");
  await Bun.write(path, buf);
  return crypto.createHash("md5").update(buf).digest("hex");
}

let lastMd5 = job.lastRef
  ? crypto.createHash("md5").update(new Uint8Array(await Bun.file(job.lastRef).arrayBuffer())).digest("hex")
  : "";
const report = [];
for (let i = 1; i <= job.prompts.length; i++) {
  const prompt = job.prompts[i - 1].trim();
  const r = await sendPrompt(prompt);
  if (!r.submitted) { report.push({ i: i, error: JSON.stringify(r) }); break; }
  // 等待生成结束（文本残留以 blob 图数变化为准兜底）
  let idle = false;
  let lastCount = -1;
  for (let w = 0; w < 40; w++) {
    await new Promise(function (res) { setTimeout(res, 5000); });
    idle = await isIdle();
    if (idle) break;
  }
  if (!idle) {
    // 文本残留兜底：blob 图数量稳定即认为完成
    let stable = 0, prev = -1;
    for (let w = 0; w < 10 && stable < 3; w++) {
      await new Promise(function (res) { setTimeout(res, 5000); });
      const c = await tab.evaluate(function () {
        var n = 0;
        document.querySelectorAll("img").forEach(function (im) {
          if (im.src.indexOf("blob:") === 0 && im.naturalWidth > 400) n++;
        });
        return n;
      });
      if (c === prev) stable++; else stable = 0;
      prev = c;
    }
  }
  let saved = false;
  for (let attempt = 0; attempt < 5 && !saved; attempt++) {
    const md5 = await exportLast(job.outPrefix + i + ".png");
    if (md5 && md5 !== lastMd5) {
      console.log("c" + i + " saved:", md5.slice(0, 8));
      lastMd5 = md5;
      saved = true;
    } else {
      console.log("c" + i + " attempt " + attempt + ": " + (md5 ? "duplicate" : "no image"));
      await new Promise(function (res) { setTimeout(res, 10000); });
    }
  }
  report.push({ i: i, saved: saved });
}
console.log(JSON.stringify(report));
