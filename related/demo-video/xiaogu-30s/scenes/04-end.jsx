// 品牌收尾：手机收回地址栏后，上方小谷跳出（开心脸）、字标显出、双芽在重拍长出，标语与内测说明升起，停住不淡出。
// 文案来源：标语 ← home.html 结尾「第一次找工作，从看懂一个岗位开始。」；说明 ← home.html「内测中，凭邀请码注册」。
function End() {
  const { T } = useComposition();
  if (T < 24.4) return null;
  const pop = T >= 24.8 ? spring(T, 24.8, 0, 1, SPRING.pop) : 0;
  const reveal = tw(T, 24.9, 25.3, 0, 1, M.enter);
  const sprout = T >= 25.2 ? spring(T, 25.2, 0, 1, SPRING.pop) : 0;
  const sway = Math.sin(T * 2 * Math.PI / 3.2) * 5;
  const blinkT = [27.4, 29.0].reduce((m, b) => Math.max(m, 1 - Math.abs(T - b) / 0.07), 0);
  return (
    <>
      <div style={{ position: 'absolute', left: 540 - 150, top: 440, width: 300, transformOrigin: '50% 100%', transform: `translateY(${(1 - pop) * 60}px) scale(${pop})` }}>
        <XgMascot face="happy" blink={blinkT} sway={sway} width={300} />
      </div>
      <div style={{ position: 'absolute', left: 540 - 210, top: 790 }}>
        <XgLogo width={420} reveal={reveal} sprout={sprout} sway={sway * 0.6} />
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1100, display: 'flex', justifyContent: 'center' }}>
        <XgRise p={T >= 25.7 ? spring(T, 25.7, 0, 1, SPRING.pop) : 0}>
          <div style={{ fontFamily: XG.serif, fontWeight: 600, fontSize: 46, color: XG.ink, letterSpacing: '.04em' }}>第一次找工作，从看懂一个岗位开始</div>
        </XgRise>
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1478, display: 'flex', justifyContent: 'center' }}>
        <XgRise p={T >= 26.1 ? spring(T, 26.1, 0, 1, SPRING.pop) : 0}>
          <div style={{ fontFamily: XG.sans, fontWeight: 500, fontSize: 34, color: XG.ink2 }}>内测中，凭邀请码注册</div>
        </XgRise>
      </div>
    </>
  );
}
