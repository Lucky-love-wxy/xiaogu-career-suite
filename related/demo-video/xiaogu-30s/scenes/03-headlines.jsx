// 顶部衬线标题（不受镜头缩放，屏幕空间）。主句先升起，末尾强调词随后升起并换强调色（参考片的语法）。
// 文案来源（事实表）：
//   「第一次找工作的 AI 伙伴」← home.html <title>「小谷求职 · 第一次找工作的 AI 伙伴」
//   「把招聘说明贴进来」← 对话页空状态「把招聘说明贴进来，或者直接问一个词。」
//   「写清了什么，没写清什么」← 本次回答「招聘说明写清了…；但没写清几点…」（rec/transcript.txt）
//   「每句都对着 JD 原文」← 回答「依据」一节逐条标「JD 原文」
//   「面试前，先问清这些」← 回答「仍需确认」一节（3 个待问问题）
const HEADS = [
  [3.3, 7.2, '第一次找工作的', 'AI 伙伴'],
  [7.6, 10.7, '把招聘说明', '贴进来'],
  [13.3, 16.9, '写清了什么，', '没写清什么'],
  [17.1, 20.6, '每句都对着', 'JD 原文'],
  [20.8, 24.0, '面试前，先问清', '这些'],
];

function Headlines() {
  const { T } = useComposition();
  const h = HEADS.find(([a, b]) => T >= a - 0.05 && T < b + 0.05);
  if (!h) return null;
  const [a, b, main, accent] = h;
  const out = tw(T, b - 0.3, b, 0, 1, M.draw);
  const p1 = spring(T, a, 0, 1, SPRING.pop), p2 = T >= a + 0.28 ? spring(T, a + 0.28, 0, 1, SPRING.pop) : 0;
  const card = tw(T, a - 0.05, a + 0.25, 0, 1, M.enter) * (1 - out);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 212, display: 'flex', justifyContent: 'center' }}>
      {/* 底卡：镜头推近时标题压在手机上方，用纸色底卡托住，保证可读 */}
      <div style={{ padding: '22px 40px', borderRadius: 28, background: `rgba(246,243,236,${0.94 * card})`, boxShadow: `0 10px 40px rgba(38,36,31,${0.08 * card})`,
        display: 'flex', alignItems: 'baseline', gap: 6, fontFamily: XG.serif, fontWeight: 700, fontSize: 66, lineHeight: 1.15, whiteSpace: 'nowrap' }}>
        <XgRise p={p1} q={out}><span style={{ color: XG.ink }}>{main}</span></XgRise>
        <XgRise p={p2} q={out}><span style={{ color: XG.shu }}>{accent}</span></XgRise>
      </div>
    </div>
  );
}

// 等待生成那段的加速标注：如实说明实际耗时（rec/events.json：发送 8.27s → 完成 64.14s）
function SpeedTag() {
  const { T } = useComposition();
  if (T < 10.85 || T > 13.0) return null;
  const k = tw(T, 10.85, 11.1, 0, 1, M.enter) * (1 - tw(T, 12.8, 13.0, 0, 1, M.draw));
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 230, display: 'flex', justifyContent: 'center' }}>
      <div style={{ transform: `scale(${0.85 + 0.15 * k})`, opacity: k, padding: '16px 30px', borderRadius: 999, background: XG.ink, color: XG.paper,
        fontFamily: XG.sans, fontWeight: 700, fontSize: 40, letterSpacing: '.04em' }}>▶▶ 已加速 · 实际约 56 秒</div>
    </div>
  );
}
