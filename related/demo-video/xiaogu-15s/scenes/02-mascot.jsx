// 吉祥物小谷（共享元素，转折登场后一直在场，品牌段移到字标上方）
// 位置用世界坐标：中心 x、脚底 y、缩放（基准宽 480）。大位移用 tw，落地/表情切换用弹簧。
const MASCOT_W = 480;
const MASCOT_BLINKS = [4.7, 7.4, 9.9, 13.7];
const MASCOT_FACES = [[0, 'smile'], [3.75, 'surprise'], [5.0, 'think'], [11.0, 'wink'], [12.0, 'happy']];

function Mascot() {
  const { T, CUES } = useComposition();
  const sTurn = CUES.Turn, sProof = CUES.Proof, sCta = CUES.CTA;
  if (T < sTurn + 0.25) return null;

  const land = sTurn + 0.75;
  // 起跳入画 → 去右下角 → 品牌段回到中上
  const rise = tw(T, sTurn + 0.3, land, 1, 0, M.enter);
  const toCorner = tw(T, sProof, sProof + 0.6, 0, 1, M.draw);
  const toCta = tw(T, sCta, sCta + 0.5, 0, 1, M.draw);
  const lerp = (a, b, k) => a + (b - a) * k;
  let cx = lerp(540, 790, toCorner), foot = lerp(1560, 1600, toCorner), sc = lerp(1, 0.6, toCorner);
  cx = lerp(cx, 540, toCta); foot = lerp(foot, 1000, toCta); sc = lerp(sc, 0.75, toCta);
  foot += rise * 900;
  const bob = T > land ? Math.sin((T - land) * 2 * Math.PI / 2.1) * 6 : 0;   // 浮动
  // 落地压扁回弹 + 每次换表情的小弹跳
  const squash = T >= land ? spring(T, land, 0.86, 1, SPRING.pop) : 1;
  const face = MASCOT_FACES.filter(([t]) => T >= t).pop()[1];
  const tFace = MASCOT_FACES.filter(([t]) => T >= t).pop()[0];
  const popS = tFace > 0 ? spring(T, tFace, 1.07, 1, SPRING.pop) : 1;
  const blink = Math.max(0, ...MASCOT_BLINKS.map((b) => 1 - Math.abs(T - b) / 0.07));
  const look = face === 'think' ? [-7, -6] : [0, 0];
  // 芽：常态摆动；品牌段 12.5 与字标的芽同时一抖
  const sway = Math.sin(T * 2 * Math.PI / 3.2) * 5.5 + (T >= sCta + 0.5 ? spring(T, sCta + 0.5, 14, 0, SPRING.pop) : 0);
  const w = MASCOT_W * sc, h = w * 350 / 300;
  const glow = tw(T, sTurn + 0.3, land, 0, 1, M.enter);

  // 气泡：挂在小谷左上方，跟着它走；出场弹出，退场缩回尾巴
  const bIn = sTurn + 0.95, bOut = sProof + 1.2;
  const bubbleK = T < bIn ? 0 : spring(T, bIn, 0.6, 1, SPRING.pop) * (1 - tw(T, bOut, bOut + 0.2, 0, 1, M.draw));

  return (
    <>
      <div style={{ position: 'absolute', left: cx - w * 0.68, top: foot - h * 0.55 - w * 0.7 + bob, transform: `scale(${glow})` }}>
        <XgGlow size={w * 1.36} />
      </div>
      <div style={{ position: 'absolute', left: cx - w / 2, top: foot - h + bob, width: w, height: h,
        transformOrigin: '50% 100%', transform: `scale(${(2 - squash) * popS}, ${squash * popS})` }}>
        <XgMascot face={face} blink={blink} look={look} sway={sway} width={w} />
      </div>
      {bubbleK > 0.01 && (
        <div style={{ position: 'absolute', right: 1080 - (cx - w * 0.08), top: foot - h - 80 + bob, transformOrigin: '100% 100%', transform: `scale(${bubbleK})` }}>
          <div style={{ position: 'relative', background: XG.ink, color: XG.paper, fontFamily: XG.sans, fontWeight: 700, fontSize: 42,
            padding: '20px 30px', borderRadius: 18, whiteSpace: 'nowrap' }}>
            藏了不少信息
            <div style={{ position: 'absolute', right: 26, bottom: -9, width: 20, height: 20, background: XG.ink, transform: 'rotate(45deg)', borderRadius: 3 }} />
          </div>
        </div>
      )}
    </>
  );
}
