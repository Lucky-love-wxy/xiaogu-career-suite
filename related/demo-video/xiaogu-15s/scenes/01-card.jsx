// 引语卡片（共享元素，贯穿 钩子 → 转折 → 证明 → 屏息，品牌段被「刀切」收掉）
// 内容取自小谷黑话库「抗压能力强」条目（/Users/lucky_wang/Documents/codex/xiaogu-career-suite/database/jargon.json）：
//   blunt「大概率有明确压力源，只是 JD 没直接说压力到底来自…」→ 直白说
//   worst_case「长期人手不足、频繁救火…」→ 最坏是
//   verify「高峰期大约多久一次、持续多久？」→ 面试问
const CARD_QUOTE = ['「', '抗', '压', '能', '力', '强', '」'];
const CARD_ROWS = [
  { t: 5.0, label: '直白说', text: '大概率有压力，来源没写' },
  { t: 6.5, label: '最坏是', text: '人手不够，天天救火' },
  { t: 8.0, label: '面试问', text: '高峰多久一次？持续多久？' },
];
const CARD_X = 90, CARD_W = 900, CARD_TOP = 300, CARD_HEAD = 200, ROW_H = 170;

// 「抗压」的颤动：确定性伪随机（不用 Math.random），只在钩子后半段出现，暗示压力
const cardJitter = (T, i) => Math.sin(T * 61 + i * 1.7) * Math.sin(T * 23 + i) * 2.4;

function Card() {
  const { T, CUES } = useComposition();
  const sTurn = CUES.Turn, sCta = CUES.CTA, sBreath = CUES.Breath;
  if (T > sCta + 0.35) return null;

  // 钩子 → 卡片头：引语缩小上移（同一个元素，不卸载）
  const m = tw(T, sTurn, sTurn + 0.6, 0, 1, M.draw);
  const quoteY = 960 + (CARD_TOP + CARD_HEAD / 2 - 960) * m;
  const quoteS = 1 - 0.44 * m;
  // 卡片底板：从中心横向展开（不淡入），高度随行数用弹簧长高
  const cw = CARD_W * tw(T, sTurn + 0.05, sTurn + 0.5, 0, 1, M.enter);
  const rowsShown = CARD_ROWS.reduce((h, r) => h + spring(T, r.t - 0.35, 0, ROW_H, SPRING.snappy) * (T >= r.t - 0.35 ? 1 : 0), 0);
  const ch = CARD_HEAD + rowsShown + (T >= CARD_ROWS[0].t - 0.35 ? 30 : 0);
  // 品牌段：卡片沿中线被压扁收走（刀切）
  const knife = 1 - tw(T, sCta, sCta + 0.3, 0, 1, M.draw);
  const shake = T > 1.6 && T < sTurn ? 1 : 0;
  const dim = tw(T, sBreath, sBreath + 0.3, 0, 1, M.enter);       // 屏息：前两行退后
  const inv = tw(T, sBreath, sBreath + 0.35, 0, 1, M.enter);      // 屏息：第三行反白

  return (
    <div style={{ position: 'absolute', inset: 0, transformOrigin: `540px ${CARD_TOP + ch / 2}px`, transform: `scaleY(${knife})` }}>
      {/* 小标：JD 里写着 */}
      <div style={{ position: 'absolute', left: 0, right: 0, top: 790, display: 'flex', justifyContent: 'center' }}>
        <XgRise p={spring(T, -0.12, 0, 1, SPRING.pop)} q={tw(T, sTurn, sTurn + 0.3, 0, 1, M.draw)}>
          <div style={{ fontFamily: XG.sans, fontWeight: 500, fontSize: 46, color: XG.ink2, letterSpacing: '.2em' }}>JD 里写着</div>
        </XgRise>
      </div>
      {/* 卡片底板 */}
      {/* 底板跟着引语走（top 与引语同步），卡片和引语是同一个元素，不是两块 */}
      <div style={{ position: 'absolute', left: 540 - cw / 2, width: cw, top: quoteY - CARD_HEAD / 2, height: ch, background: XG.paper2,
        border: `1px solid ${XG.rule}`, borderRadius: 24, opacity: cw > 2 ? 1 : 0 }} />
      {/* 引语：逐字砸入，后半段颤动；转折时缩成卡片标题 */}
      <div style={{ position: 'absolute', left: 0, right: 0, top: quoteY - 80, height: 160, display: 'flex', justifyContent: 'center', alignItems: 'center',
        transform: `scale(${quoteS})` }}>
        {CARD_QUOTE.map((c, i) => {
          const ti = -0.5 + i * 0.075;   // 负起点：第 0 帧最后一个字正在落下，其余已落定；平台默认封面常取首帧
          const s = spring(T, ti, 1.4, 1, SPRING.pop);
          return (
            <span key={i} style={{ display: 'inline-block', fontFamily: XG.serif, fontWeight: 900, fontSize: 124, color: XG.ink, lineHeight: 1,
              visibility: T >= ti ? 'visible' : 'hidden', transform: `translate(${cardJitter(T, i) * shake}px, ${cardJitter(T + 1, i) * shake}px) scale(${s})` }}>{c}</span>
          );
        })}
      </div>
      {/* 钩子下划线：从左画出，转折时收回 */}
      <div style={{ position: 'absolute', left: 540 - 300, top: 1070, height: 8, borderRadius: 4, background: XG.ink,
        width: 600 * (tw(T, 0.7, 1.3, 0, 1, M.draw) - tw(T, sTurn, sTurn + 0.25, 0, 1, M.draw)) }} />
      {/* 三行翻译 */}
      {CARD_ROWS.map((r, i) => {
        const p = spring(T, r.t, 0, 1, SPRING.pop);
        const on = T >= r.t;
        const isKey = i === 2;
        const fade = isKey ? 1 : 1 - 0.65 * dim;
        return (
          <div key={i} style={{ position: 'absolute', left: CARD_X + 36, width: CARD_W - 72, top: CARD_TOP + CARD_HEAD + 10 + i * ROW_H, height: ROW_H - 24,
            visibility: on ? 'visible' : 'hidden', opacity: fade, borderRadius: 16, overflow: 'hidden' }}>
            {/* 第三行反白：底色从左扫过 */}
            {isKey && <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${inv * 100}%`, background: XG.ink }} />}
            <div style={{ position: 'relative', height: '100%', display: 'flex', alignItems: 'center', gap: 28, padding: '0 24px',
              transform: `translateY(${(1 - p) * 60}px)` }}>
              <div style={{ flex: 'none', fontFamily: XG.sans, fontWeight: 500, fontSize: 30, letterSpacing: '.1em', padding: '8px 16px', borderRadius: 10,
                color: isKey && inv > 0.5 ? XG.paper : XG.ink2, border: `1.5px solid ${isKey && inv > 0.5 ? XG.paper : XG.rule}` }}>{r.label}</div>
              <div style={{ fontFamily: XG.sans, fontWeight: 700, fontSize: 46, color: isKey && inv > 0.5 ? XG.paper : XG.ink, whiteSpace: 'nowrap' }}>{r.text}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
