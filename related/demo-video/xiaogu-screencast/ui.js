// 小谷 web 桌面端（默认「黑底白线」主题）的 2D 重绘：状态 → HTML（确定性）。
// 真相源：xiaogu-launch/platform/static/index.html（类名、CSS、图标 symbol、logo、文案、md() 渲染规则照搬），
// 内容取自 2026-10-15 本地真跑（ref/answer-2026-10-15.md、ref/run-2026-10-15.json）。不用截图，不加产品没有的界面效果。
// data-a = 镜头 / 光标 / 小谷要用到的锚点。
import { ICONS, LOGO } from './assets.js';

export const W = 1920, H = 1080;
export const SIDE = 264, TRACE = 340;

const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const ic = (id, cls = 'i') => `<svg class="${cls}"><use href="#${id}"/></svg>`;

// ───────── 回答渲染：照搬 index.html 的 inline / blockHtml / md（报告样式）
const KINDS = [['JD 原文', 'jd'], ['参考资料', 'ref'], ['从业者分享（未核实）', 'ext'], ['待核实推断', 'inf'], ['本人确认', 'me']];
function inline(s) {
  s = esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  for (const [label, cls] of KINDS) if (s.startsWith(esc(label) + '：')) { s = `<span class="k ${cls}">${esc(label)}</span>` + s.slice(esc(label).length + 1); break; }
  return s;
}
const SECTION = /^\*\*(依据|仍需确认|下一步|受阻原因)\*\*/;
function blockHtml(lines) {
  let html = '', list = null;
  const close = () => { if (list) { html += `</${list}>`; list = null; } };
  for (const line of lines) {
    if (!line.trim()) { close(); continue; }
    const ul = line.match(/^- (.*)/);
    if (ul) { if (list !== 'ul') { close(); html += '<ul>'; list = 'ul'; } html += `<li>${inline(ul[1])}</li>`; }
    else { close(); html += `<p>${inline(line)}</p>`; }
  }
  close(); return html;
}
function md(text) {
  const sections = [[]];
  for (const line of text.trim().split('\n')) { if (SECTION.test(line)) sections.push([]); sections[sections.length - 1].push(line); }
  return sections.map((lines, i) => `<div class="${i ? 'sec' : ''}" data-a="sec-${i}">${blockHtml(lines)}</div>`).join('');
}
// 给片子要用的字词与标签加锚点（只加 data-a，不改样式与文字）
function anchors(html) {
  let k = 0;
  for (const w of ['“抗压能力强”', '“结果导向”', '“拥抱变化”']) { const i = html.indexOf(w); if (i >= 0) { html = html.slice(0, i) + `<span data-a="w-${k}">${w}</span>` + html.slice(i + w.length); } k++; }
  for (const cls of ['jd', 'ref', 'inf']) html = html.replace(`<span class="k ${cls}">`, `<span class="k ${cls}" data-a="tag-${cls}">`);
  return html.replace(/(可以复制这句问招聘方：)(“[^”]*”)/, '$1<span data-a="nq">$2</span>');
}

// S = { fresh, input:{text,focus,caret,scroll}, sent, who, status, answer:{text,n}, scroll, trace:{w,item}, hist:[…], sel, cursorBtn }
export function world(S) {
  const tw = S.trace ? S.trace.w : 0;
  let h = ICONS;
  h += `<div class="app ${S.fresh ? 'fresh' : ''}" style="grid-template-columns:${SIDE}px minmax(0,1fr) ${tw}px">`;
  // 左侧栏
  h += `<aside class="side"><div class="side-top"><span class="brand" data-a="logo">${LOGO}</span><span class="tb icon">${ic('i-side')}</span></div>`
    + `<div class="actions"><div class="item ${S.newHot ? 'hot' : ''}" data-a="newchat">${ic('i-new')}<span class="t">新对话</span></div>`
    + `<div class="search">${ic('i-search')}<span class="ph">搜索对话</span></div></div>`
    + `<div class="side-scroll"><div class="hist">${(S.hist || []).map((x, i) => `<div class="item ${x.active ? 'active' : ''}" data-a="hist-${i}" style="opacity:${x.p ?? 1}"><span class="t">${esc(x.title)}</span></div>`).join('')}</div></div>`
    + `<div class="account"><div class="me-btn"><span class="avatar">谷</span><span class="meta"></span>${ic('i-chev', 'i chev')}</div></div></aside>`;
  // 中间
  h += `<main><div class="bar"><span class="title">小谷</span><span class="spacer"></span><span class="tb trace-btn ${S.traceHot ? 'hot' : ''}" data-a="tracebtn">运行记录</span></div>`;
  h += `<div class="log"><div class="col" style="transform:translateY(${-(S.scroll || 0)}px)">`;
  if (S.fresh) h += `<section class="empty"><h2 data-a="h2">先看懂一个岗位，再决定要不要<span data-a="tou">投</span>。</h2><p>把招聘说明贴进来，或者直接问一个词。</p></section>`;
  else {
    h += `<div class="turn"><div class="me long" data-a="me" style="opacity:${Math.min(1, (S.sent ?? 1) * 3)};transform:scale(${.96 + .04 * (S.sent ?? 1)})">${esc(S.message)}</div>`;
    h += `<p class="who" style="opacity:${S.who ?? 1}">小谷 · AI 生成</p><div class="xg">`;
    if (S.status) h += `<p class="status" data-a="status"><span class="dots">${[0, 1, 2].map((i) => `<i style="transform:translateY(${(-4 * Math.max(0, Math.sin((S.t * 2 * Math.PI) - i * .9))).toFixed(1)}px)"></i>`).join('')}</span><span class="txt">${esc(S.status)}</span></p>`;
    if (S.answer && S.answer.n > 0) {
      let body = anchors(md(S.answer.text.slice(0, S.answer.n)));
      // 光标拖选：浏览器原生的选中高亮，从左往右长出来
      if (S.sel > 0) body = body.replace('<span data-a="nq">', `<span data-a="nq" style="background:linear-gradient(90deg,rgba(242,242,238,.3) ${(S.sel * 100).toFixed(1)}%,transparent ${(S.sel * 100).toFixed(1)}%)">`);
      h += `<div class="body">${body}</div>`;
    }
    h += `</div></div>`;
  }
  h += `</div></div>`;
  const inp = S.input || {};
  h += `<div class="compose"><div class="box ${inp.focus ? 'focus' : ''}" data-a="box">${ic('i-plus', 'i plus')}`
    + `<div class="ta" data-a="ta"><div class="ta-in" style="transform:translateY(${-(inp.scroll || 0)}px)">${inp.text ? esc(inp.text) : ''}${inp.caret ? '<span class="caret" data-a="caret"></span>' : '<span data-a="caret"></span>'}</div></div>`
    + `<span class="send ${inp.text ? '' : 'dim'} ${S.sendHot ? 'hot' : ''}" data-a="send">${ic('i-up')}</span></div>`;
  if (S.fresh) h += `<div class="chips"><span>${ic('i-job')}看懂岗位</span><span>${ic('i-target')}按岗位改简历</span><span>${ic('i-search')}问一个黑话</span></div>`;
  h += `<p class="foot-note">小谷的回答由 AI 生成，可能出错，重要信息请自己核实。</p></div></main>`;
  // 右侧运行记录（真实界面只在开发 / 测试环境出现）
  h += `<aside class="trace"><div class="in"><h3>运行记录</h3><div id="traceItems">`;
  h += S.trace && S.trace.item ? `<div class="t-item" data-a="titem" style="opacity:${S.trace.item}">${TRACE_ITEM}</div>` : `<div class="t-item">发送消息后，这里显示路由、检索、来源和校验次数。</div>`;
  h += `</div></div></aside></div>`;
  return h;
}

// 运行记录：字段照 index.html 的 trace()，数值取自 ref/run-2026-10-15.json
const TRACE_ITEM = `<div><b>结果</b> complete · 3489 ms · deepseek/deepseek-flash</div>
<div><b>路由</b> xiaogu-career-suite</div><div><b>判断</b> 规则</div><div><b>存入会话</b> job</div>
<div><b>本地检索</b> 黑话 4 条 · 职业 未命中</div><div class="ok" data-a="tcheck">第 1 次：通过校验</div>`;
