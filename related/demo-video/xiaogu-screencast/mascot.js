// 像素小谷：照小谷角色（codex/xiaogu-motion：黑色圆头套 + 白色内框 + 齐刘海 + 圆眼 + 腮红 + 头顶两片芽叶，
// 黑身体白肚皮，短手短脚）转成方像素。只用于小谷自己的推广片。
// 小谷 web 默认黑底白线：黑色头套在近黑界面上会消失，所以整个剪影外描一圈浅色像素描边（像素画常规做法）。
// 接口与模板 mascot.js 一致：PAL、GW、GH、WIPE_COLORS、grid、sprite、pixels、PROPS、dust。
export const PAL = { body: '#121211', hood: '#121211', ring: '#F4F2EC', skin: '#FBF6EF', hair: '#1A1A19', eye: '#121211',
  cheek: '#F0B6AC', leaf: '#232321', line: '#D9D6CE', mouth: '#5A3B33',
  wipe: ['#1F1F1D', '#262624', '#191918'], wipeInk: '#F2F2EE', shade: '#121211' };
export const GW = 22, GH = 24;                     // 含描边的网格宽高；脚底在第 GH 行下沿
export const WIPE_COLORS = null;                   // 擦除转场里照原色画（描边已经保证在深色块上可见）

// 类型：1 头套/身体 2 眼睛 3 芽叶 4 腮红 6 描边 7 白色内框/肚皮 8 脸 9 刘海 10 嘴
const T = { body: 1, eye: 2, leaf: 3, cheek: 4, line: 6, ring: 7, skin: 8, hair: 9, mouth: 10 };
const FILL = { 1: PAL.body, 2: PAL.eye, 3: PAL.leaf, 4: PAL.cheek, 6: PAL.line, 7: PAL.ring, 8: PAL.skin, 9: PAL.hair, 10: PAL.mouth };

// 左右对称：中轴在第 10.5 列，镜像列 = 21 - c。头套每行左边界（第 4–15 行）
const HOOD_L = { 4: 8, 5: 6, 6: 5, 7: 4, 8: 4, 9: 4, 10: 4, 11: 4, 12: 4, 13: 4, 14: 5, 15: 7 };
const LEAF_L = [[6, 0], [7, 0], [8, 0], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [9, 2]];   // 左叶（横向张开的椭圆，照原图）

export function grid({ eyes = 'n', arms = 'down', legs = 'stand' } = {}) {
  const P = new Map(), put = (c, r, v) => P.set(c + ',' + (r + 1), v);       // 整体下移 1 行，给描边留位
  const mir = (c, r, v) => { put(c, r, v); put(21 - c, r, v); };
  for (const [c, r] of LEAF_L) mir(c, r, T.leaf);
  put(10, 2, T.leaf); put(11, 2, T.leaf); put(10, 3, T.leaf); put(11, 3, T.leaf);   // 茎
  for (const [r, a] of Object.entries(HOOD_L)) for (let c = a; c <= 21 - a; c++) put(c, +r, T.body);
  // 白色内框（圆角矩形）
  for (let c = 7; c <= 14; c++) { put(c, 7, T.ring); put(c, 14, T.ring); }
  for (let r = 8; r <= 13; r++) mir(6, r, T.ring);
  // 脸：第 8 行齐刘海，第 9 行两侧鬓角，其余为皮肤
  for (let r = 8; r <= 13; r++) for (let c = 7; c <= 14; c++) put(c, r, T.skin);
  for (let c = 7; c <= 14; c++) put(c, 8, T.hair);
  mir(7, 9, T.hair);
  mir(8, 12, T.cheek);
  if (eyes !== 'wide') { put(10, 13, T.mouth); put(11, 13, T.mouth); }
  const E = { n: [[9, 10], [9, 11]], l: [[8, 10], [8, 11]], r: [[10, 10], [10, 11]], u: [[9, 10]], d: [[9, 11], [9, 12]],
    blink: [[9, 11]], happy: [[8, 11], [9, 10], [10, 11]], wide: [[9, 10], [9, 11], [9, 12]], shut: [[8, 11], [9, 11], [10, 11]] }[eyes] || [];
  const shift = eyes === 'l' ? -1 : eyes === 'r' ? 1 : 0;                       // 看左右时两只眼一起平移（不镜像）
  for (const [c, r] of E) {
    if (shift) { put(c, r, T.eye); put(c + 3, r, T.eye); }
    else mir(c, r, T.eye);
  }
  // 身体 + 白肚皮
  for (const [r, a] of [[16, 7], [17, 6], [18, 6], [19, 7]]) for (let c = a; c <= 21 - a; c++) put(c, r, T.body);
  for (const [c, r] of [[10, 17], [11, 17], [9, 18], [10, 18], [11, 18], [12, 18]]) put(c, r, T.ring);
  const AR = { down: [[5, 17], [5, 18], [16, 17], [16, 18]], up: [[5, 16], [4, 15], [16, 16], [17, 15]],
    wave: [[5, 17], [5, 18], [16, 16], [17, 15]], tuck: [] }[arms] || [];
  for (const [c, r] of AR) put(c, r, T.body);
  const LG = { stand: [[7, 20], [8, 20], [7, 21], [8, 21], [13, 20], [14, 20], [13, 21], [14, 21]],
    walkA: [[7, 20], [8, 20], [7, 21], [8, 21], [13, 20], [14, 20]], walkB: [[7, 20], [8, 20], [13, 20], [14, 20], [13, 21], [14, 21]],
    tuck: [[7, 20], [8, 20], [13, 20], [14, 20]] }[legs] || [];
  for (const [c, r] of LG) put(c, r, T.body);
  // 浅色描边：剪影外一圈（四邻），保证黑底上看得见
  const solid = new Set(P.keys());
  for (const k of solid) { const [c, r] = k.split(',').map(Number);
    for (const [dc, dr] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const n = (c + dc) + ',' + (r + dr); if (!solid.has(n) && !P.has(n)) P.set(n, T.line); } }
  return [...P].map(([k, v]) => { const [c, r] = k.split(',').map(Number); return [c, r, v]; });
}

export function sprite({ x, y, px = 7, flip = false, sq = 0, rot = 0, op = 1, shadow = 0, colors = null, ...pose }) {
  let s = '';
  for (let [c, r, v] of grid(pose)) { if (flip) c = GW - 1 - c; s += `<rect x="${c}" y="${r}" width="1.04" height="1.04" fill="${(colors && colors[v]) || FILL[v]}"/>`; }
  const sy = 1 - sq, sx = 1 + sq * .7, w = GW * px * sx, h = GH * px * sy;
  const sh = shadow > 0 ? `<div style="position:absolute;left:${x - 6 * px}px;top:${y - px * .4}px;width:${12 * px}px;height:${px * .8}px;border-radius:50%;background:rgba(0,0,0,${.3 * shadow})"></div>` : '';
  return sh + `<svg class="px" viewBox="0 0 ${GW} ${GH}" width="${w}" height="${h}" style="left:${x - w / 2}px;top:${y - h}px;opacity:${op};transform:rotate(${rot}rad);transform-origin:50% 60%" shape-rendering="crispEdges">${s}</svg>`;
}
export function pixels(o) {
  const { x, y, px = 7, flip = false } = o;
  return grid(o).filter(([, , v]) => v !== T.line).map(([c, r, v]) => ({ x: x + ((flip ? GW - 1 - c : c) - GW / 2 + .5) * px, y: y + (r - GH + .5) * px, v, col: FILL[v] }));
}

// ───────── 像素道具（与小谷同一网格；黑底上用浅色）
export function pixart(rows, { x, y, px = 6, pal, op = 1 }) {
  let s = ''; rows.forEach((row, r) => [...row].forEach((ch, c) => { if (pal[ch]) s += `<rect x="${c}" y="${r}" width="1.04" height="1.04" fill="${pal[ch]}"/>`; }));
  const w = rows[0].length, h = rows.length;
  return `<svg class="px" viewBox="0 0 ${w} ${h}" width="${w * px}" height="${h * px}" style="left:${x}px;top:${y}px;opacity:${op}" shape-rendering="crispEdges">${s}</svg>`;
}
const GLOW = '#F2F2EE';
export const PROPS = {
  bang: (x, y, px = 6, op = 1) => pixart(['.kk.', 'kwwk', 'kwwk', 'kwwk', '.kk.', '....', '.kk.', '.kk.'], { x, y, px, op, pal: { w: '#121211', k: GLOW } }),
  check: (x, y, px = 6, op = 1) => pixart(['.....g', '....gg', 'g..gg.', 'gggg..', '.gg...'], { x, y, px, op, pal: { g: GLOW } }),
  spark: (x, y, px = 6, op = 1, col = GLOW) => pixart(['..y..', '..y..', 'yy.yy', '..y..', '..y..'], { x: x - 2.5 * px, y: y - 2.5 * px, px, op, pal: { y: col } }),
  heart: (x, y, px = 5, op = 1) => pixart(['.rr.rr.', 'rrrrrrr', 'rrrrrrr', '.rrrrr.', '..rrr..', '...r...'], { x: x - 3.5 * px, y: y - 3 * px, px, op, pal: { r: '#F0B6AC' } }),
  dots: (x, y, px = 6, op = 1, n = 3) => (n < 1 ? '' : pixart(['kk.kk.kk'.slice(0, n * 3 - 1), 'kk.kk.kk'.slice(0, n * 3 - 1)], { x, y, px, op, pal: { k: GLOW } })),
};
export function dust(x, y, t, px = 5, n = 6, seed = 1) {
  if (t <= 0 || t >= 1) return ''; let s = '';
  for (let i = 0; i < n; i++) {
    const side = i % 2 ? 1 : -1, k = (i >> 1) + 1, e = 1 - (1 - t) ** 2;
    const dx = side * (18 + k * 16 + ((seed * 7 + i * 13) % 9)) * e, dy = -(8 + k * 5) * Math.sin(Math.PI * t * .9), sz = px * (1 - t * .7);
    s += `<div style="position:absolute;left:${x + dx - sz / 2}px;top:${y + dy - sz}px;width:${sz}px;height:${sz}px;background:#6b6b67;opacity:${1 - t}"></div>`;
  }
  return s;
}
