// 地址栏 ⇄ 手机（同一个元素形变，首尾呼应）+ 手机里的真实录屏 + 点击触点。
// 录屏来自 rec/record.mjs（本机 8781、真模型、手机视口 390×844@2x），帧时间戳在 rec/frames.js（window.REC_T，秒）。

// 视频时间 → 录屏时间（分段线性）。等待生成那段压缩播放，结论段略放慢给阅读时间。
const REC_MAP = [
  [3.0, 7.4, 0.4, 4.8],      // 主页：点小谷、点进入（1x）
  [7.4, 10.85, 4.85, 8.3],   // 对话页：点输入框、贴 JD、点发送（1x）
  [10.85, 13.0, 8.3, 64.1],  // 等待生成：实际约 56 秒，压到 2.15 秒（片中标注「已加速」）
  [13.0, 16.8, 64.1, 65.6],  // 回答出现，停在结论，与标题「写清了什么，没写清什么」同步
  [16.8, 21.5, 65.6, 70.6],  // 滚过依据，与标题「每句都对着 JD 原文」同步（约 1.06x）
  [21.5, 24.6, 70.6, 73.1],  // 停在「仍需确认」「下一步」
];
function recAt(T) {
  if (T <= REC_MAP[0][0]) return REC_MAP[0][2];
  for (const [a, b, ra, rb] of REC_MAP) if (T <= b) return ra + (rb - ra) * (T - a) / (b - a);
  return REC_MAP[REC_MAP.length - 1][3];
}
function recFrame(rt) {  // 二分：时间戳 ≤ rt 的最后一帧
  const A = window.REC_T; let lo = 0, hi = A.length - 1;
  while (lo < hi) { const m = (lo + hi + 1) >> 1; if (A[m] <= rt) lo = m; else hi = m - 1; }
  return lo;
}

// 几何（世界坐标）：开头地址栏、手机、结尾地址栏
const RECT_BAR1 = { x: 110, y: 896, w: 860, h: 128, r: 64 };
const RECT_PHONE = { x: 254, y: 434, w: 572, h: 1201, r: 72 };
const RECT_BAR2 = { x: 160, y: 1330, w: 760, h: 116, r: 58 };
const PHONE_PAD = 16, SCREEN_W = 540, CSS2WORLD = SCREEN_W / 390;
const lerpRect = (a, b, k) => ({ x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, w: a.w + (b.w - a.w) * k, h: a.h + (b.h - a.h) * k, r: a.r + (b.r - a.r) * k });
const mixHex = (a, b, k) => { const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)); const A = p(a), B = p(b);
  return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * k)).join(',')})`; };

// 点击触点：录制时记下的元素中心（CSS 像素）→ 世界坐标；时间 = 录屏时刻映射回视频时刻
const TAPS = [
  { t: 5.12, x: 195, y: 265 },   // 点小谷（rec 2.52）
  { t: 9.21, x: 195, y: 401 },   // 点输入框（rec 6.66）
  { t: 10.77, x: 351, y: 493 },  // 点发送（rec 8.22）
];

function phoneMorph(T) {
  const k1 = tw(T, 2.2, 3.0, 0, 1, M.draw);      // 地址栏 → 手机
  const k2 = tw(T, 24.0, 24.7, 0, 1, M.draw);    // 手机 → 地址栏
  return { k1, k2, rect: lerpRect(lerpRect(RECT_BAR1, RECT_PHONE, k1), RECT_BAR2, k2) };
}

function Phone() {
  const { T } = useComposition();
  const { k1, k2, rect } = phoneMorph(T);
  // 颜色非线性：尽快变成深色机身、到最后才变回白色地址栏，避免线性渐变途经的大块中灰
  const body = k2 > 0 ? mixHex('#141414', '#ffffff', k2 ** 3) : mixHex('#ffffff', '#141414', 1 - (1 - k1) ** 3);
  // 屏幕：形变到位后自上而下擦出；收回时自下而上擦掉
  const reveal = tw(T, 2.6, 3.1, 0, 1, M.enter) * (1 - tw(T, 24.0, 24.35, 0, 1, M.draw));
  const sx = rect.x + PHONE_PAD * k1 * (1 - k2), sy = rect.y + PHONE_PAD * k1 * (1 - k2);
  const sw = rect.w - 2 * PHONE_PAD * k1 * (1 - k2), sh = rect.h - 2 * PHONE_PAD * k1 * (1 - k2);
  const idx = recFrame(recAt(T));
  return (
    <>
      <div style={{ position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h, borderRadius: rect.r, background: body,
        boxShadow: `0 ${18 + 30 * k1}px ${50 + 50 * k1}px rgba(38,36,31,${0.12 + 0.1 * k1 * (1 - k2)})` }} />
      {reveal > 0.001 && (
        <div style={{ position: 'absolute', left: sx, top: sy, width: sw, height: sh, borderRadius: Math.max(0, rect.r - PHONE_PAD), overflow: 'hidden',
          clipPath: `inset(0 0 ${(1 - reveal) * 100}% 0)`, background: '#0a0a0a' }}>
          <img src={`rec/frames/${String(idx).padStart(5, '0')}.jpg`} style={{ width: SCREEN_W, height: SCREEN_W * 1688 / 780, display: 'block' }} />
        </div>
      )}
      {TAPS.map((p, i) => {
        if (T < p.t - 0.25 || T > p.t + 0.6) return null;
        const press = T < p.t ? tw(T, p.t - 0.25, p.t, 0, 1, M.enter) : 1 - tw(T, p.t, p.t + 0.3, 0, 1, M.draw);
        const ring = tw(T, p.t, p.t + 0.55, 0, 1, M.enter);
        const wx = RECT_PHONE.x + PHONE_PAD + p.x * CSS2WORLD, wy = RECT_PHONE.y + PHONE_PAD + p.y * CSS2WORLD;
        return (
          <div key={i} style={{ position: 'absolute', left: wx, top: wy }}>
            <div style={{ position: 'absolute', left: -36, top: -36, width: 72, height: 72, borderRadius: '50%', background: 'rgba(180,67,46,.35)',
              transform: `scale(${0.6 + 0.4 * press})`, opacity: press }} />
            {T >= p.t && <div style={{ position: 'absolute', left: -60, top: -60, width: 120, height: 120, borderRadius: '50%', border: `4px solid ${XG.shu}`,
              transform: `scale(${0.4 + 0.9 * ring})`, opacity: 1 - ring }} />}
          </div>
        );
      })}
    </>
  );
}
