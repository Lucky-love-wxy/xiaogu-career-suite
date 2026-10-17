// 品牌段：字标「小谷」从下往上显出，12.5 重拍上「谷」的双芽长出（招牌镜头），标语随后升起，停住不淡出。
// 标语取自主页结尾原文。
function Cta() {
  const { T, CUES } = useComposition();
  const s = CUES.CTA;
  if (T < s + 0.1) return null;
  const reveal = tw(T, s + 0.15, s + 0.55, 0, 1, M.enter);
  const sprout = T >= s + 0.5 ? spring(T, s + 0.5, 0, 1, SPRING.pop) : 0;
  const sway = Math.sin(T * 2 * Math.PI / 3.2) * 4;
  return (
    <>
      <div style={{ position: 'absolute', left: 540 - 300, top: 1040 }}>
        <XgLogo width={600} reveal={reveal} sprout={sprout} sway={sway} />
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1470, display: 'flex', justifyContent: 'center' }}>
        <XgRise p={T >= s + 0.8 ? spring(T, s + 0.8, 0, 1, SPRING.pop) : 0}>
          <div style={{ fontFamily: XG.serif, fontWeight: 600, fontSize: 44, color: XG.ink2, letterSpacing: '.06em' }}>第一次找工作，从看懂一个岗位开始</div>
        </XgRise>
      </div>
    </>
  );
}
