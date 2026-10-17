// 录屏式演示片（living screencast）的通用机制：挂词、打字节奏、录屏式镜头、吉祥物、光标、锚点、音效事件、HUD 状态。
// 机制改编自 lemo-opuscar styles/living-screencast/demo/film.js（MIT，见 LICENSE、NOTICE.md）；剧情、界面、角色全部不在这里。
// 与原版的三处改动（b2，2026-10-15）：
//   1. 挂词支持中文：按整句拼接后找子串，不再按英文单词逐个比对（原版的规范化会把汉字全部删掉）。
//   2. 锚点无状态：元素不在时返回兜底坐标或 null，不缓存「上一帧位置」，保证任意时刻单独渲染与顺序渲染一致。
//   3. 画幅不写死：镜头与锚点换算读 window.W / window.H（竖版 1080×1920 也能用）。
import { clamp, lerp, seg, ss, eio, eo, back, hash } from './core/lib.js';

// ───────── 音效 / 配乐事件：sound.py 读 events.json（由 toolkit/scripts/events.mjs 从页面导出）
export const EV = [];
export const ev = (t, type, o = {}) => EV.push({ t: +t.toFixed(3), type, ...o });

// ───────── 挂词：每个画面节拍挂在旁白（或字幕）的某个字词上
// words[id] = [[文本, 句内开始秒, 句内结束秒], ...]，来自 whisper 逐词/逐字时间戳；没有旁白时用 synthWords() 合成
let VO = {}, WORDS = {};
export function setVoice(vo, words) { VO = vo; WORDS = words; }
const norm = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}@]/gu, '');
function locate(id, word, n) {
  const ws = WORDS[id]; if (!ws) throw new Error(`no words for line ${id}`);
  let text = ''; const owner = [];                         // owner[字符序号] = 所属 token 序号
  ws.forEach(([w], i) => { for (const ch of norm(w)) { text += ch; owner.push(i); } });
  const target = norm(word); let pos = -1, from = 0;
  for (let k = 0; k <= n; k++) { pos = text.indexOf(target, from); if (pos < 0) throw new Error(`「${word}」 not in line ${id}`); from = pos + 1; }
  return [owner[pos], owner[pos + target.length - 1]];
}
export const W = (id, word, n = 0) => VO[id] + Math.max(0, WORDS[id][locate(id, word, n)[0]][1]);   // 该字词开始
export const WE = (id, word, n = 0) => VO[id] + WORDS[id][locate(id, word, n)[1]][2];              // 该字词结束
// 无旁白模式：按阅读速度给每句合成逐字时间（中文约 4.5 字/秒，DIRECTOR §7）；以后接 TTS + whisper 只换 words
export function synthWords(lines, cps = 4.5) {
  const words = {}, dur = {};
  for (const [id, text] of Object.entries(lines)) {
    let t = 0; const ws = [];
    for (const ch of text.replace(/[{}]/g, '')) { const d = /[\p{L}\p{N}]/u.test(ch) ? 1 / cps : .12; ws.push([ch, t, t + d]); t += d; }
    words[id] = ws; dur[id] = +t.toFixed(3);
  }
  return { words, dur };
}

// ───────── 打字：人手节奏（确定性抖动），返回第 i 个字出现的时刻
export function typing(t0, text, cps = 9, seed = 1, kind = 'key') {
  const T = []; let t = t0; const chars = [...text];
  chars.forEach((ch, i) => {
    const r = hash(seed * 31 + i * 7.3);
    t += (1 / cps) * (.55 + r * .9) + (ch === ' ' ? .03 : 0) + ('，。,.'.includes(chars[i - 1] || '') ? .12 : 0);
    T.push(t); ev(t, kind, { v: .6 + r * .4 });
  });
  return T;
}
export const typed = (T, text, t) => { let n = 0; while (n < T.length && T[n] <= t) n++; return [...text].slice(0, n).join(''); };

// ───────── 镜头：录屏软件式一镜到底；move 可重叠，后一段从前一段当前值出发（连续）
export const EASE = { eio, ss, eo, lin: (x) => clamp(x),
  whip: (x) => { x = clamp(x); return x < .5 ? 16 * x ** 5 : 1 - (-2 * x + 2) ** 5 / 2; } };
export function camera(init) {                              // init = [中心x, 中心y, 缩放]（世界坐标）
  const moves = [];
  return {
    move(t0, d, to, e = 'eio') { moves.push({ t0, d, to, e }); moves.sort((a, b) => a.t0 - b.t0); return this; },
    at(t) {
      let v = [init[0], init[1], Math.log(init[2])];
      for (const m of moves) { if (t <= m.t0) break; const p = EASE[m.e]((t - m.t0) / m.d);
        v = [lerp(v[0], m.to[0], p), lerp(v[1], m.to[1], p), lerp(v[2], Math.log(m.to[2]), p)]; }
      return [v[0] + Math.sin(t * .7) * 1.2, v[1] + Math.sin(t * .53 + 1) * .9, Math.exp(v[2])];   // 触控板微动
    },
  };
}

// ───────── 吉祥物（软件的化身）：只站在真实界面元素的上沿；位置按像素网格步进
export class Actor {
  constructor(px = 7, beat = .5) { this.px = px; this.beat = beat; this.segs = []; this.jumps = []; }
  add(s) { this.segs.push(s); return this; }
  stand(t0, t1, at, o = {}) { return this.add({ k: 'stand', t0, t1, at, ...o }); }
  walk(t0, t1, from, to, o = {}) { for (let t = t0 + .06; t < t1; t += .11) ev(t, 'step', { v: .5 }); return this.add({ k: 'walk', t0, t1, from, to, ...o }); }
  jump(t0, t1, from, to, h = 120, o = {}) { this.jumps.push({ t0, t1 }); ev(t0 - .02, 'jump', { d: t1 - t0 }); ev(t1, 'land', { v: o.big ? 1 : .6 }); return this.add({ k: 'jump', t0, t1, from, to, h, ...o }); }
  hide(t0, t1) { return this.add({ k: 'hide', t0, t1 }); }
  seg(t) { let s = null; for (const x of this.segs) { if (x.t0 <= t && t < x.t1) return x; if (x.t0 <= t) s = x; } return s; }
  eval(t, A) {
    const s = this.seg(t); if (!s || s.k === 'hide') return null;
    const px = s.px || this.px, P = (f) => (typeof f === 'function' ? f(A, t) : f);
    let pos, legs = 'stand', flip = s.flip || false, sq = 0, rot = 0, arms = 'down', eyes = 'n';
    if (s.k === 'stand') pos = P(s.at);
    if (s.k === 'walk') { const a = P(s.from), b = P(s.to); if (!a || !b) return null; const p = (s.ease || ss)(seg(t, s.t0, s.t1));
      pos = { x: lerp(a.x, b.x, p), y: lerp(a.y, b.y, p) }; legs = Math.floor(t * 9) % 2 ? 'walkA' : 'walkB'; flip = b.x < a.x; }
    if (s.k === 'jump') { const a = P(s.from), b = P(s.to); if (!a || !b) return null; const p = seg(t, s.t0, s.t1);
      const top = Math.min(a.y, b.y) - s.h, cy = 2 * top - (a.y + b.y) / 2;           // 二次贝塞尔控制点：顶点约在 top
      pos = { x: lerp(a.x, b.x, p), y: (1 - p) ** 2 * a.y + 2 * (1 - p) * p * cy + p * p * b.y };
      legs = 'tuck'; flip = b.x < a.x - 2 ? true : b.x > a.x + 2 ? false : flip; arms = 'up';
      sq = p < .5 ? -.22 * (1 - p * 2) : -.12 * (p * 2 - 1); }
    if (!pos) return null;
    for (const j of this.jumps) {                                   // 起跳前蓄力、落地压扁回弹
      if (t >= j.t0 - .14 && t < j.t0) sq = Math.max(sq, .28 * ss(seg(t, j.t0 - .14, j.t0)));
      if (t >= j.t1 && t < j.t1 + .22) { const k = seg(t, j.t1, j.t1 + .22); sq = .34 * (1 - k) * Math.cos(k * 7); }
    }
    if (s.k === 'stand' && !s.still) { const bp = ((t % this.beat) + this.beat) % this.beat; if (bp < .12) sq += .07 * Math.sin(bp / .12 * Math.PI); }   // 随拍呼吸
    const bl = Math.floor(t / 2.9), bt = t - bl * 2.9 - hash(bl * 3.7 + px) * 2;
    if (bt > 0 && bt < .1) eyes = 'blink';
    if (s.eyes) { const e = typeof s.eyes === 'function' ? s.eyes(t) : s.eyes; if (e && !(eyes === 'blink' && 'nlr'.includes(e))) eyes = e; }
    if (s.arms) arms = typeof s.arms === 'function' ? s.arms(t) : s.arms;
    if (s.sq) sq += s.sq(t);
    return { x: Math.round(pos.x / (px / 2)) * (px / 2), y: pos.y, px, flip, sq, rot, legs, arms, eyes, op: s.op ? s.op(t) : 1, shadow: s.k === 'jump' ? 0 : 1 };
  }
}

// ───────── 光标（用户）：弹簧弧线移动，点击压一下 + 波纹；从不瞬移
export class Cursor {
  constructor() { this.moves = []; this.clicks = []; this.vis = []; }
  show(t0, t1) { this.vis.push([t0, t1]); return this; }
  move(t0, t1, to, arc = 40) { this.moves.push({ t0, t1, to, arc }); return this; }
  click(t) { this.clicks.push(t); ev(t, 'click'); return this; }
  eval(t, A) {
    let op = 0; for (const [a, b] of this.vis) op = Math.max(op, Math.min(seg(t, a, a + .15), 1 - seg(t, b - .2, b)));
    if (op <= 0) return null;
    let p = null, prev = null;
    for (const m of this.moves) {
      const to = m.to(A, t); if (!to) continue;
      if (t < m.t0) break;
      if (!prev) { p = to; prev = to; continue; }
      const k = seg(t, m.t0, m.t1), e = eio(k), from = prev, dx = to.x - from.x, dy = to.y - from.y, L = Math.hypot(dx, dy) || 1;
      p = { x: lerp(from.x, to.x, e) - dy / L * m.arc * Math.sin(Math.PI * e), y: lerp(from.y, to.y, e) + dx / L * m.arc * Math.sin(Math.PI * e), sp: Math.abs(Math.sin(Math.PI * k)) * L / (m.t1 - m.t0) };
      prev = k >= 1 ? to : from; if (k < 1) break;
    }
    if (!p) return null;
    let sc = 1, ring = 0; for (const c of this.clicks) { if (t >= c && t < c + .1) sc = .82; if (t >= c && t < c + .45) ring = seg(t, c, c + .45); }
    return { ...p, op, sc, ring };
  }
}

// ───────── 锚点：按 data-a 量真实 DOM（无状态）。元素暂时不在时用 fallback（世界坐标）或返回 null
export const at = (key, fx = .5, fy = 0, dx = 0, dy = 0, fallback = null) => (A) => {
  const p = A(key, fx, fy); return p ? { x: p.x + dx, y: p.y + dy } : fallback;
};
export const pt = (x, y) => () => ({ x, y });

// ───────── HUD 状态：字幕胶囊、章节签与像素擦除、按键提示、快进标签、聚光冻结、截图闪光、提示条、淡入淡出
// 参数都是剧情数据（film.js 提供），这里只算每帧的显隐与动画量
export function hudState(t, o) {
  const H = {};
  const s = (o.subs || []).find((x) => t >= x.t0 && t < x.t1);
  if (s) H.cap = { text: s.text, op: Math.min(seg(t, s.t0, s.t0 + .12), 1 - seg(t, s.t1 - .15, s.t1)), y: (1 - eo(seg(t, s.t0, s.t0 + .2))) * 10 };
  for (const c of o.chapters || []) {                           // c = { t0, no, nm, hold }
    if (t >= c.t0 && t < c.t0 + .85) H.wipe = { p: (t - c.t0) / .85, no: c.no, nm: c.nm };
    const end = c.t0 + (c.hold || 7.8);
    if (t >= c.t0 + .6 && t < end) H.chap = { no: c.no, nm: c.nm, op: Math.min(seg(t, c.t0 + .6, c.t0 + .9), 1 - seg(t, end - .3, end)) };
  }
  for (const k of o.keys || []) {                               // k = { t0, keys:[…], label, press:[t…] }
    if (t >= k.t0 && t < k.t0 + 1.5) H.keys = { keys: k.keys, label: k.label, op: Math.min(seg(t, k.t0, k.t0 + .15), 1 - seg(t, k.t0 + 1.25, k.t0 + 1.5)),
      dn: (k.press || []).some((p) => t >= p && t < p + .18), y: (1 - back(seg(t, k.t0, k.t0 + .3))) * 20 };
  }
  if (o.ramp && t > o.ramp.t0 - .1 && t < o.ramp.t1 + .1) H.ramp = { x: o.ramp.x || '4×', op: Math.min(seg(t, o.ramp.t0 - .1, o.ramp.t0), 1 - seg(t, o.ramp.t1 - .1, o.ramp.t1 + .1)), blink: Math.floor(t * 4) % 2 };
  if (o.spot && t > o.spot.t0 - .1 && t < o.spot.t1 + .3) H.spot = { key: o.spot.key, op: Math.min(seg(t, o.spot.t0 - .1, o.spot.t0 + .2), 1 - seg(t, o.spot.t1, o.spot.t1 + .3)) };
  if (o.flash && t > o.flash && t < o.flash + .3) H.flash = .5 * (1 - seg(t, o.flash, o.flash + .3));
  if (o.toast && t > o.toast.t0 && t < o.toast.t0 + 1.8) H.toast = { key: o.toast.key, text: o.toast.text, op: Math.min(seg(t, o.toast.t0, o.toast.t0 + .15), 1 - seg(t, o.toast.t0 + 1.5, o.toast.t0 + 1.8)) };
  if (o.fadeOut && t > o.fadeOut[0]) H.fade = seg(t, o.fadeOut[0], o.fadeOut[1]);
  if (t < (o.fadeIn ?? .5)) H.fadeIn = 1 - eo(t / (o.fadeIn ?? .5));
  return H;
}
