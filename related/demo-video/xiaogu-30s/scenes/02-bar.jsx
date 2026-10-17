// 地址栏里的内容：开头逐字打「xiaogu.icu」、点「前往」；结尾在收回的地址栏里再打一次（首尾呼应，也是可执行的入口）。
// 位置跟随 phoneMorph 的矩形，所以和形变是同一个元素。
const BAR_URL = 'xiaogu.icu';

function BarContent({ rect, typed, goPress, goOn, cursorOn, size }) {
  return (
    <div style={{ position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h, display: 'flex', alignItems: 'center',
      padding: `0 ${rect.h * 0.22}px 0 ${rect.h * 0.42}px`, boxSizing: 'border-box', gap: 18 }}>
      <svg width={size * 0.62} height={size * 0.62} viewBox="0 0 24 24" fill="none" stroke={XG.ink3} strokeWidth="2.4" strokeLinecap="round"><rect x="5" y="10" width="14" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
      <div style={{ flex: 1, fontFamily: XG.sans, fontWeight: 500, fontSize: size, color: XG.ink, letterSpacing: '.01em', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center' }}>
        {BAR_URL.slice(0, typed)}
        <span style={{ display: 'inline-block', width: size * 0.5, height: size * 1.05, marginLeft: 4, background: XG.ink, opacity: cursorOn ? 1 : 0 }} />
      </div>
      <div style={{ width: rect.h * 0.66, height: rect.h * 0.66, borderRadius: '50%', flex: 'none', display: 'grid', placeItems: 'center',
        background: goOn ? XG.shu : XG.rule, transform: `scale(${1 - 0.12 * goPress})` }}>
        <svg width={rect.h * 0.3} height={rect.h * 0.3} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
      </div>
    </div>
  );
}

function Bar() {
  const { T } = useComposition();
  const { k1, k2, rect } = phoneMorph(T);
  const blink = Math.floor(T * 2.2) % 2 === 0;
  // 开头：0.35–1.45 打字，1.85 点前往，2.2 起形变时内容收走
  if (k1 < 0.35) {
    const typed = Math.floor(tw(T, 0.35, 1.45, 0, BAR_URL.length, Easing.linear));
    const goPress = T > 1.7 && T < 2.2 ? 1 - Math.abs(T - 1.9) / 0.25 : 0;
    return <div style={{ opacity: 1 - k1 / 0.35 }}>
      <BarContent rect={rect} typed={typed} goPress={Math.max(0, goPress)} goOn={T > 1.8} cursorOn={typed < BAR_URL.length || blink} size={54} />
    </div>;
  }
  // 结尾：形变完成后再打一次网址，光标常亮闪烁，停住
  if (k2 > 0.85) {
    const typed = Math.floor(tw(T, 24.85, 25.55, 0, BAR_URL.length, Easing.linear));
    return <BarContent rect={rect} typed={typed} goPress={0} goOn={T > 25.6} cursorOn={typed < BAR_URL.length || blink} size={48} />;
  }
  return null;
}
