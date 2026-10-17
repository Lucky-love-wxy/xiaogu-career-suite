// 渲染层：每帧 = film.frame(t) → 世界层（亮 / 暗两份，圆形展开切换）+ 精灵层（吉祥物、道具、光标）+ HUD。
// 改编自 lemo-opuscar styles/living-screencast/demo/main.js（MIT）。与原版的区别：
//   画幅读 film 的 SIZE（不写死 960/540）；精灵画法来自可替换的 mascot.js；道具由 film 声明的 props 驱动（不写剧情时间点）。
// 页面协议（toolkit/scripts/lib.mjs 的兼容层认这四个）：window.DUR / window.render(t) / window.READY / window.EV，另给 window.W / H。
import { seg, eo, hash } from './core/lib.js';
import * as UI from './ui.js';
import * as M from './mascot.js';
import * as FM from './film.js';

const { W, H } = FM.SIZE, CX = W / 2, CY = H / 2;
document.documentElement.style.setProperty('--W', W + 'px'); document.documentElement.style.setProperty('--H', H + 'px');
const Q = new URLSearchParams(location.search), NOSUBS = Q.has('nosubs');
const wL = document.getElementById('wL'), wD = document.getElementById('wD'), spr = document.getElementById('spr'), hudEl = document.getElementById('hud');
const mbg = document.getElementById('mbg'), mbw = document.getElementById('mbw');

// 有真实配音时 voices/words.json 存 whisper 逐字时间戳（{ id: [[字, 起, 止], …], __dur: { id: 秒 } }）；没有就走无旁白合成
let words = null;
try { const r = await fetch('voices/words.json'); if (r.ok) { const w = await r.json(); words = { words: w, dur: w.__dur }; } } catch (e) { /* 无旁白模式 */ }
FM.build(words);
Object.assign(window, { W, H, DUR: FM.DUR, EV: FM.EV.slice().sort((a, b) => a.t - b.t), SUBS: FM.SUBS.map((s) => ({ t0: s.t0, t1: s.t1, text: s.text.replace(/[{}]/g, '') })), T: FM.T });

const tf = ([cx, cy, z]) => `translate(${CX}px,${CY}px) scale(${z}) translate(${-cx}px,${-cy}px)`;
function render(t) {
  const F = FM.frame(t), [cx, cy, z] = F.cam;
  const html = UI.world(F.world);
  const D = F.dark, base = D.base === 'L' ? wL : wD, over = D.over ? (D.over === 'L' ? wL : wD) : null;
  base.innerHTML = html; base.style.display = ''; base.style.clipPath = ''; base.style.zIndex = 1;
  if (over) { over.innerHTML = html; over.style.display = ''; over.style.zIndex = 2; } else (base === wL ? wD : wL).style.display = 'none';
  for (const el of [wL, wD, spr]) el.style.transform = tf(F.cam);
  // 锚点：data-a 元素上一点的世界坐标（每帧现量 DOM，吉祥物永远站在真实元素上沿）
  const cache = {};
  const A = (key, fx = .5, fy = 0) => { const el = cache[key] !== undefined ? cache[key] : (cache[key] = base.querySelector(`[data-a="${key}"]`));
    if (!el) return null; const r = el.getBoundingClientRect(); if (!r.width && !r.height) return null;
    return { x: (r.left + r.width * fx - CX) / z + cx, y: (r.top + r.height * fy - CY) / z + cy, w: r.width / z, h: r.height / z }; };
  if (over) { const c = A(D.at, .5, .5) || { x: cx, y: cy }; over.style.clipPath = `circle(${D.r}px at ${c.x}px ${c.y}px)`; }
  // 动态模糊：只在甩镜时按镜头速度加各向异性模糊（加在未变换的外层，慢推保持清晰）
  const [px, py] = FM.camAt(t - 1 / 30), vx = (cx - px) * z, vy = (cy - py) * z;
  // 阈值 90 px/帧：只有甩镜才拖影；正常推移（S1 的大幅拉镜）保持清晰，文字始终可读
  const bx = Math.min(36, Math.max(0, Math.abs(vx) - 90) * .3), by = Math.min(36, Math.max(0, Math.abs(vy) - 90) * .3);
  mbg.setAttribute('stdDeviation', `${bx.toFixed(2)} ${by.toFixed(2)}`); mbw.style.filter = bx > .6 || by > .6 ? 'url(#mb)' : '';
  spr.innerHTML = sprites(F, t, A, z);
  hud(F, t, A, z, cx, cy);
}

function sprites(F, t, A, z) {
  let h = '';
  const cs = F.actors.map((act) => {
    const c = act && act.eval(t, A); if (!c) return null;
    h += M.sprite(c);
    for (const j of act.jumps) if (t >= j.t1 && t < j.t1 + .4) { const L = act.eval(j.t1 + .001, A); if (L) h += M.dust(L.x, L.y, seg(t, j.t1, j.t1 + .4), Math.max(3, L.px * .7), 6, j.t1 * 10); }
    return c;
  });
  // 出生：像素从锚点（logo 的芽）飞出，拼成吉祥物（STYLE §8 match-cut origin）
  if (F.birth && t >= F.birth.t0 && t < F.birth.t1) {
    const src = A(F.birth.from, .5, .5), dst = F.birth.to(A), k = seg(t, F.birth.t0, F.birth.t1);
    if (src && dst) for (const [i, q] of M.pixels({ x: dst.x, y: dst.y, px: F.birth.px }).entries()) {
      const e = Math.min(1, Math.max(0, (k - hash(i * 1.7) * .35) / .65)), ee = e * e * (3 - 2 * e);
      const ax = Math.sin(ee * Math.PI) * (hash(i * 3.1) - .5) * 80, ay = -Math.sin(ee * Math.PI) * 60 * hash(i * 5.3);
      const x = src.x + (q.x - src.x) * ee + ax, y = src.y + (q.y - src.y) * ee + ay, sz = 2 + (F.birth.px - 2) * ee;
      h += `<div style="position:absolute;left:${x - sz / 2}px;top:${y - sz / 2}px;width:${sz + .4}px;height:${sz + .4}px;background:${q.col}"></div>`;
    }
  }
  // 像素下划线：吉祥物落在某个词上时，在词下留一道像素线（表演层，不是界面功能）
  for (const u of F.ulines || []) {
    if (t < u.t0) continue; const p = A(u.key, 0, 1); if (!p) continue;
    const k = Math.min(1, (t - u.t0) / .25), n = Math.floor(p.w / 6);
    for (let i = 0; i < Math.ceil(n * k); i++) h += `<div class="uline" style="left:${p.x + i * 6}px;top:${p.y + 1}px;width:4px;height:4px;background:#f2f2ee"></div>`;
  }
  // 道具：film 声明 { kind, t0, t1, actor=0 }，画在吉祥物头顶
  for (const p of F.props || []) {
    const c = cs[p.actor || 0]; if (!c || t < p.t0 || t >= p.t1) continue;
    const k = seg(t, p.t0, p.t1), top = c.y - c.px * M.GH;
    if (p.kind === 'spark') for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + .3; h += M.PROPS.spark(c.x + Math.cos(a) * (30 + k * 70), c.y - 40 + Math.sin(a) * (20 + k * 50), 4, 1 - k); }
    else if (M.PROPS[p.kind]) h += M.PROPS[p.kind](c.x + 40, top - 40 - k * 10, 5, 1 - seg(t, p.t1 - .3, p.t1));
  }
  // 光标：屏幕尺寸恒定（录屏软件常用 1.6 倍），快速移动时带残影，点击有波纹
  const cu = F.cursor && F.cursor.eval(t, A);
  if (cu) {
    if (cu.sp > 900) for (let i = 1; i <= 4; i++) { const g = F.cursor.eval(t - i * .012, A); if (g) h += cursorSvg(g.x, g.y, 1, cu.op * .16 * (5 - i) / 4, z); }
    if (cu.ring > 0) h += `<div class="ring" style="left:${cu.x - 26 * cu.ring - 4}px;top:${cu.y - 26 * cu.ring - 4}px;width:${52 * cu.ring + 8}px;height:${52 * cu.ring + 8}px;opacity:${(1 - cu.ring) * .8};border-width:${3 / z}px"></div>`;
    h += cursorSvg(cu.x, cu.y, cu.sc, cu.op, z);
  }
  return h;
}
const cursorSvg = (x, y, sc, op, z) => { const s = 1.6 * sc / z;
  return `<svg style="position:absolute;left:${x - 2 * s}px;top:${y - 2 * s}px;opacity:${op};filter:drop-shadow(0 ${2 / z}px ${3 / z}px rgba(0,0,0,.3))" width="${22 * s}" height="${30 * s}" viewBox="0 0 22 30"><path d="M2 2 L2 24 L7.5 18.5 L11 27 L15 25.2 L11.6 17 L19 17 Z" fill="#000" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>`; };

function hud(F, t, A, z, cx, cy) {
  const Hs = F.hud; let h = '';
  const scr = (p) => ({ x: (p.x - cx) * z + CX, y: (p.y - cy) * z + CY });
  if (Hs.spot) { const p = A(Hs.spot.key, .5, .5); if (p) { const s = scr(p), r = Math.max(p.w, p.h) * z * .75 + 40;
    h += `<div class="spot" style="opacity:${Hs.spot.op};background:radial-gradient(ellipse ${r * 1.6}px ${r}px at ${s.x}px ${s.y}px, transparent 60%, rgba(20,24,22,.55) 100%)"></div>`; } }
  if (Hs.toast) { const p = A(Hs.toast.key, .5, .72); if (p) { const s = scr(p); h += `<div class="toast" style="left:${s.x - 150}px;top:${s.y}px;opacity:${Hs.toast.op}">${Hs.toast.text}</div>`; } }
  if (Hs.flash) h += `<div class="flash" style="opacity:${Hs.flash}"></div>`;
  if (Hs.chap && !Hs.wipe) h += `<div class="chap ${Hs.dark ? 'dk' : ''}" style="opacity:${Hs.chap.op}"><b>${Hs.chap.no}</b>${Hs.chap.nm}</div>`;
  if (Hs.ramp) h += `<div class="ramp" style="opacity:${Hs.ramp.op}">${Hs.ramp.blink ? '▶▶' : '▷▷'} ${Hs.ramp.x}</div>`;
  if (Hs.keys) h += `<div class="keys" style="opacity:${Hs.keys.op};transform:translateY(${Hs.keys.y}px)">${Hs.keys.keys.map((k) => `<i class="${Hs.keys.dn ? 'dn' : ''}">${k}</i>`).join('')}<span>${Hs.keys.label}</span></div>`;
  if (Hs.cap && !NOSUBS) h += `<div class="cap ${Hs.dark ? 'dk' : ''}" style="opacity:${Hs.cap.op};transform:translate(-50%,${Hs.cap.y}px)">${Hs.cap.text.replace(/\{([^}]*)\}/g, '<em>$1</em>')}</div>`;
  if (Hs.wipe) h += wipe(Hs.wipe, t);
  if (Hs.fade) h += `<div class="fade" style="opacity:${Hs.fade}"></div>`;
  if (Hs.fadeIn) h += `<div class="fade" style="opacity:${Hs.fadeIn}"></div>`;
  hudEl.innerHTML = h;
}
// 章节转场：像素块从左下扫到右上盖满 → 章节名 → 同向揭开；中间一只浅色吉祥物跑过（配色取 mascot.PAL）
function wipe(Wp, t) {
  const S = 60, cols = Math.ceil(W / S), rows = Math.ceil(H / S), p = Wp.p; let s = '<div class="wipe">';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const d = (c / cols) * .55 + ((rows - r) / rows) * .2 + hash(c * 13.1 + r * 7.7) * .12;
    const a = Math.max(0, Math.min(1, (p / .42 - d) / .18)), b = Math.max(0, Math.min(1, ((p - .55) / .42 - d) / .18)), k = a * (1 - b);
    if (k <= 0) continue; const sz = S * k;
    s += `<b style="left:${c * S + (S - sz) / 2}px;top:${r * S + (S - sz) / 2}px;width:${sz + .5}px;height:${sz + .5}px;background:${M.PAL.wipe[Math.floor(hash(c * 3.7 + r * 11.3) * 3)]}"></b>`;
  }
  const lo = Math.max(0, Math.min(1, Math.min((p - .3) / .12, (.82 - p) / .1)));
  if (lo > 0) {
    s += `<div class="wlabel" style="opacity:${lo};transform:translateY(calc(-50% + ${(1 - lo) * 16}px))"><div class="no">${Wp.no}</div><div class="nm">${Wp.nm}</div></div>`;
    // 擦除转场里跑过的吉祥物配色由 mascot.js 决定（WIPE_COLORS：类型 → 颜色；null = 原色）
    s += M.sprite({ x: W * .15 + p * W * .7, y: H * .73, px: 6, legs: Math.floor(t * 12) % 2 ? 'walkA' : 'walkB', op: lo, colors: M.WIPE_COLORS || null });
  }
  return s + '</div>';
}

window.render = render;
await document.fonts.ready;
for (const f of ['400 16px "Noto Sans SC"', '500 16px "Noto Sans SC"', '700 30px "Noto Serif SC"', '400 12px "JetBrains Mono"']) { try { await document.fonts.load(f, '示例'); } catch (e) { /* 字体缺失时退回系统字体 */ } }
render(+(Q.get('t') || 0));
window.READY = true;
