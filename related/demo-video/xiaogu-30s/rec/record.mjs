#!/usr/bin/env node
// 真机录屏：无头 Chrome 以手机视口打开本机小谷（127.0.0.1:8781，真模型），按脚本操作，
// 用 CDP screencast 抓每一帧（带时间戳），同时记下每次点击的位置和时刻，供合成时画触点。
// 不占用户屏幕（headless）。登录用开发环境接口预先完成，视频里不出现登录页。
// 产物：frames/NNNNN.jpg、frames.json（每帧时间戳）、events.json（操作时间线）
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire("/Users/lucky_wang/Documents/Claude/projects/product-demo-video/toolkit/package.json");
const { chromium } = require("playwright-core");

const ORIGIN = "http://127.0.0.1:8781";
const HERE = path.dirname(new URL(import.meta.url).pathname);
const OUT = path.join(HERE, "frames");
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
const JD = fs.readFileSync(path.join(HERE, "jd.txt"), "utf8").trim();

const browser = await chromium.launch({ channel: "chrome", headless: true });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: "zh-CN" });
// 开发环境才有的「测试环境 / 运行记录」标记：生产环境由 index.html:733 自动隐藏，这里按生产外观隐藏，不改产品界面
await ctx.addInitScript(() => document.addEventListener("DOMContentLoaded", () => {
  const st = document.createElement("style");
  st.textContent = "#envTag,#toggle{display:none!important}";
  document.head.appendChild(st);
}));
const page = await ctx.newPage();

// 1. 预登录：后台口令 → 生成邀请码 → 取开发验证码 → 注册（cookie 留在同一 context）
const api = ctx.request;
await api.post(`${ORIGIN}/api/admin/login`, { data: { token: "dev-admin" } });
const inv = await (await api.post(`${ORIGIN}/api/admin/invites`, { data: { count: 1, credits: 500, note: "demo-video" } })).json();
const invite = (inv.codes || inv.invites || [])[0];
const contact = `demo${Date.now() % 100000}@example.com`;
const code = (await (await api.post(`${ORIGIN}/api/auth/code`, { data: { contact } })).json()).dev_code;
const v = await api.post(`${ORIGIN}/api/auth/verify`, { data: { contact, code, invite: typeof invite === "string" ? invite : invite?.code, consent: true } });
if (!v.ok()) throw new Error(`login failed: ${v.status()} ${await v.text()}`);

// 2. screencast：每帧落盘并记时间戳（秒，epoch）
const cdp = await ctx.newCDPSession(page);
const frames = [];
cdp.on("Page.screencastFrame", async ({ data, metadata, sessionId }) => {
  const i = frames.length;
  fs.writeFileSync(path.join(OUT, `${String(i).padStart(5, "0")}.jpg`), Buffer.from(data, "base64"));
  frames.push(metadata.timestamp);
  await cdp.send("Page.screencastFrameAck", { sessionId }).catch(() => {});
});
const events = [];
const now = () => Date.now() / 1000;
const mark = (type, extra = {}) => { events.push({ t: now(), type, ...extra }); console.log(type, JSON.stringify(extra).slice(0, 80)); };
// 点击：先记录元素中心（CSS 像素），停一下让合成有时间画光标移动，再真实点击
async function tap(sel, label) {
  const box = await page.locator(sel).first().boundingBox();
  mark("tap", { label, x: box.x + box.width / 2, y: box.y + box.height / 2 });
  await page.locator(sel).first().tap();
}
const wait = (ms) => page.waitForTimeout(ms);

await page.goto(`${ORIGIN}/`, { waitUntil: "load" });
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92, maxWidth: 780, maxHeight: 1688, everyNthFrame: 1 });
mark("home");
await wait(2500);
await tap("#tilt", "mascot");          // 点一下小谷：换表情 + 冒气泡
await wait(2200);
await tap("#cta", "start");            // 开始使用 → 对话页
await page.waitForURL(/\/app/);
await page.waitForSelector("#input");
mark("chat");
await wait(1800);
await tap("#input", "input");
await page.fill("#input", JD);         // 真实用户是粘贴 JD，不逐字打
mark("pasted");
await wait(1500);
await tap("#send", "send-jd");
mark("jd-sent");
await page.waitForFunction(() => !document.querySelector("#send").disabled, null, { timeout: 180000 });
mark("jd-done");
await wait(1500);
// 慢慢往下滚对话容器 #log（滚轮落在顶栏上不会滚，所以直接滚容器），把评析全文录下来
const scrollMax = await page.evaluate(() => { const l = document.querySelector("#log"); return l.scrollHeight - l.clientHeight - l.scrollTop; });
mark("scroll-start", { px: scrollMax });
for (let k = 0; k < 24; k++) { await page.evaluate(() => document.querySelector("#log").scrollBy(0, 60)); await wait(120); }
mark("scroll-end");
await wait(2500);
mark("end");
await cdp.send("Page.stopScreencast");
await wait(300);

fs.writeFileSync(path.join(HERE, "frames.json"), JSON.stringify(frames));
fs.writeFileSync(path.join(HERE, "events.json"), JSON.stringify(events, null, 1));
// 回答原文留档，用于事实表
const texts = await page.evaluate(() => [...document.querySelectorAll("#log > *")].map((n) => n.innerText));
fs.writeFileSync(path.join(HERE, "transcript.txt"), texts.join("\n\n-----\n\n"));
console.log(`${frames.length} frames, ${(frames.at(-1) - frames[0]).toFixed(1)}s`);
await browser.close();
