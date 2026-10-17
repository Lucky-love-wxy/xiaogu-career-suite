// 品牌组件（不是场景）：吉祥物与字标，形状原样取自
// /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/home.html 与 brand/logo-lockup.svg。
// 网页版靠 CSS 动画和 data-face 切表情；视频里一切由 T 决定，所以表情、眨眼、芽摆动都改成参数。
// 本片舞台用对话页的浅色主题色（web/static/index.html:25-26），所以 XG 色板换成浅色版；吉祥物自身配色不变。

const XG = {
  paper: '#f6f3ec', paper2: '#efeadf', ink: '#26241f', ink2: '#5d5951', ink3: '#9a958a', rule: '#d9d2c3', shu: '#b4432e',
  serif: "'Noto Serif SC', serif", sans: "'Noto Sans SC', sans-serif",
};

// 吉祥物。face: smile | surprise | think | wink | happy；blink 0..1（1=闭眼）；look=[dx,dy] 眼睛朝向；sway 芽的角度（度）
function XgMascot({ face = 'smile', blink = 0, look = [0, 0], sway = 0, width = 480 }) {
  const on = (f) => (Array.isArray(f) ? f.includes(face) : f === face) ? 1 : 0;
  const eyeOpen = face === 'happy' ? 0 : 1;
  const eyeS = (face === 'surprise' ? 1.22 : 1) * Math.max(0.08, 1 - blink);
  const eye = (cx, hide) => (
    <g transform={`translate(${cx} 170) scale(${face === 'surprise' ? 1.22 : 1} ${eyeS}) translate(${-cx} -170)`} opacity={eyeOpen * (hide ? 0 : 1)}>
      <ellipse cx={cx} cy="170" rx="11.5" ry="16" fill="#111" />
      <circle cx={cx - 4} cy="163" r="3.6" fill="#fff" />
    </g>
  );
  return (
    <svg viewBox="0 0 300 350" width={width} height={width * 350 / 300} style={{ overflow: 'visible', display: 'block' }}>
      <ellipse cx="150" cy="276" rx="62" ry="46" fill="#131313" />
      <ellipse cx="116" cy="316" rx="30" ry="17" fill="#131313" />
      <ellipse cx="184" cy="316" rx="30" ry="17" fill="#131313" />
      <path d="M92 312 q24 -14 48 0" stroke="#f1f1ee" strokeWidth="6" fill="none" strokeLinecap="round" />
      <path d="M160 312 q24 -14 48 0" stroke="#f1f1ee" strokeWidth="6" fill="none" strokeLinecap="round" />
      <rect x="116" y="246" width="68" height="50" rx="8" fill="#e9e9e5" stroke="#cfcfca" />
      <path d="M150 283 v-10 M150 273 q-9 -9 -15 -2 q7 6 15 2 M150 273 q9 -10 16 -3 q-7 7 -16 3" stroke="#131313" strokeWidth="2.4" fill="none" strokeLinecap="round" />
      <ellipse cx="116" cy="272" rx="14" ry="13" fill="#1a1a1a" />
      <ellipse cx="184" cy="272" rx="14" ry="13" fill="#1a1a1a" />
      <g transform={`rotate(${sway} 150 64)`}>
        <path d="M150 64 q-1 -12 2 -22" stroke="#131313" strokeWidth="5" fill="none" strokeLinecap="round" />
        <ellipse cx="134" cy="38" rx="15" ry="8.5" transform="rotate(-28 134 38)" fill="#131313" />
        <ellipse cx="170" cy="33" rx="19" ry="9.5" transform="rotate(22 170 33)" fill="#131313" />
      </g>
      <ellipse cx="150" cy="150" rx="116" ry="104" fill="#131313" />
      <ellipse cx="150" cy="164" rx="94" ry="82" fill="#dcdcd7" />
      <ellipse cx="150" cy="168" rx="82" ry="70" fill="#f7f7f4" />
      <path d="M66 162 Q80 96 150 92 Q220 96 234 162 Q214 126 150 124 Q86 126 66 162 Z" fill="#131313" />
      <ellipse cx="104" cy="196" rx="11" ry="6.5" fill="#efb7b7" opacity=".5" />
      <ellipse cx="196" cy="196" rx="11" ry="6.5" fill="#efb7b7" opacity=".5" />
      <g transform={`translate(${look[0]} ${look[1]})`}>
        {eye(122, face === 'wink')}
        {eye(178, false)}
      </g>
      <path opacity={on('happy')} d="M110 172 q12 -14 24 0 M166 172 q12 -14 24 0" stroke="#111" strokeWidth="4.5" fill="none" strokeLinecap="round" />
      <path opacity={on('wink')} d="M110 172 q12 -12 24 0" stroke="#111" strokeWidth="4.5" fill="none" strokeLinecap="round" />
      <path opacity={on(['smile', 'wink'])} d="M139 197 q11 10 22 0" stroke="#111" strokeWidth="3.6" fill="none" strokeLinecap="round" />
      <path opacity={on('happy')} d="M136 193 q14 18 28 0 z" fill="#111" />
      <ellipse opacity={on('surprise')} cx="150" cy="201" rx="6" ry="7.5" fill="#111" />
      <path opacity={on('think')} d="M141 200 h18" stroke="#111" strokeWidth="3.6" strokeLinecap="round" />
      <g opacity={on('think')} fill="#131313"><circle cx="232" cy="52" r="5" /><circle cx="250" cy="40" r="6.5" /><circle cx="270" cy="26" r="8" /></g>
    </svg>
  );
}

// 吉祥物身后的灰白光斑（网页 .stage::before 的同款），不让黑色角色融进黑底
function XgGlow({ size = 640, opacity = 1 }) {
  return <div style={{ width: size, height: size * 1.02, borderRadius: '50%', opacity,
    background: 'radial-gradient(closest-side, rgba(236,236,232,.92), rgba(190,190,186,.5) 55%, rgba(10,10,10,0) 100%)', filter: 'blur(4px)' }} />;
}

// 字标「小谷」+ 谷上双芽。reveal 0..1：字从下往上显出；sprout 0..1(+)：芽从茎根长出（允许弹簧过冲）
function XgLogo({ width = 600, reveal = 1, sprout = 1, sway = 0 }) {
  const clip = `inset(${(1 - reveal) * 100}% 0 0 0)`;
  return (
    <svg viewBox="0 0 152 100" width={width} height={width * 100 / 152} fill={XG.ink} style={{ display: 'block', overflow: 'visible' }}>
      <g style={{ clipPath: clip }}>
        <path transform="translate(0 25) scale(0.0739)" d="M661 286Q772 331 838.5 386.5Q905 442 935.5 498.0Q966 554 967.5 601.5Q969 649 949.0 679.0Q929 709 895.0 712.0Q861 715 820 682Q812 632 795.0 580.5Q778 529 755.5 478.5Q733 428 706.5 381.0Q680 334 651 292ZM204 270 398 347Q395 354 387.0 360.0Q379 366 360 366Q328 431 281.5 501.5Q235 572 171.5 636.0Q108 700 25 748L18 740Q56 690 86.5 630.5Q117 571 140.0 507.5Q163 444 179.0 383.0Q195 322 204 270ZM436 40 624 57Q623 68 614.5 75.5Q606 83 587 86V803Q587 853 573.5 888.0Q560 923 517.0 944.5Q474 966 386 974Q382 936 374.5 910.5Q367 885 349 867Q331 850 305.5 837.5Q280 825 227 815V803Q227 803 243.0 804.0Q259 805 283.0 806.0Q307 807 333.5 808.0Q360 809 381.5 810.0Q403 811 412 811Q426 811 431.0 806.5Q436 802 436 792Z" />
        <path transform="translate(76.86 25) scale(0.0739)" d="M549 294Q513 352 457.0 408.5Q401 465 330.5 514.5Q260 564 182.5 604.0Q105 644 25 670L19 659Q85 618 148.5 562.0Q212 506 265.0 443.5Q318 381 354.5 318.5Q391 256 404 203L618 257Q615 268 603.0 274.0Q591 280 564 282Q599 325 649.0 357.0Q699 389 757.5 411.0Q816 433 875.5 447.0Q935 461 988 470V486Q956 496 932.5 519.5Q909 543 895.0 573.0Q881 603 877 632Q802 597 737.5 550.0Q673 503 625.0 439.5Q577 376 549 294ZM572 43Q683 56 753.0 87.0Q823 118 859.0 156.5Q895 195 903.0 232.0Q911 269 897.0 296.5Q883 324 853.5 332.5Q824 341 785 321Q768 285 743.0 247.5Q718 210 688.0 174.5Q658 139 626.5 107.0Q595 75 564 50ZM429 110Q426 117 417.5 121.5Q409 126 391 125Q357 174 308.0 223.5Q259 273 197.5 315.5Q136 358 62 388L55 378Q105 331 145.0 269.5Q185 208 214.0 144.5Q243 81 258 27ZM732 856V884H281V856ZM626 574 693 500 830 605Q825 611 814.5 617.5Q804 624 787 628V937Q787 940 766.0 948.0Q745 956 716.0 963.0Q687 970 662 970H637V574ZM368 930Q368 937 349.5 947.5Q331 958 302.5 966.5Q274 975 244 975H223V574V516L375 574H726V602H368Z" />
      </g>
      <g transform="translate(76.86 25) scale(1.1197) translate(-17 -29.92)">
        <g transform={`translate(50 28) rotate(${sway}) scale(${Math.max(0, sprout)}) translate(-50 -28)`}>
          <path d="M50 28 q-1 -6 1.5 -11" stroke={XG.ink} strokeWidth="3.2" fill="none" strokeLinecap="round" />
          <ellipse cx="42" cy="17" rx="7" ry="4" transform="rotate(-28 42 17)" />
          <ellipse cx="60" cy="14.5" rx="8.6" ry="4.4" transform="rotate(22 60 14.5)" />
        </g>
      </g>
    </svg>
  );
}

// 遮罩升起的文字：p 0..1 从基线下升起，q 0..1 向上收走
function XgRise({ p, q = 0, children, style }) {
  return (
    <div style={{ overflow: 'hidden', ...style }}>
      <div style={{ transform: `translateY(${((1 - p) - q) * 110}%)` }}>{children}</div>
    </div>
  );
}
