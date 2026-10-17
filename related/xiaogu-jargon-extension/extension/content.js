// 页面侧逻辑：扫描文本 → CSS Highlight API 高亮 → 点击弹浮窗。
// 不改页面 DOM（招聘站多是 SPA，拆文本节点会打断框架更新），
// 自身 UI 放在 Shadow DOM 里，扫描时整块跳过，不会扫到自己。
(function () {
  // 招聘站上 content script 已自动注入；点工具栏图标会再注入一次，这时只切换开关
  if (globalThis.__xgJargon) { globalThis.__xgJargon.toggle(); return; }

  const ENTRIES = globalThis.XG_JARGON || [];
  const PATTERNS = XGMatcher.compile(ENTRIES);
  const HIGHLIGHT = "xg-jargon";
  const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEXTAREA", "INPUT", "SELECT", "OPTION", "CODE", "PRE", "SVG"]);

  let enabled = true;
  let hitsByNode = new Map(); // Text 节点 → [{start, end, index, name}]
  let hitCount = 0;

  // ---------- 自身 UI ----------
  const host = document.createElement("xg-jargon-root");
  host.style.cssText = "all:initial;position:fixed;inset:auto;z-index:2147483647;";
  const shadow = host.attachShadow({ mode: "closed" });
  shadow.innerHTML = `<style>${STYLE()}</style>
    <button class="seal" part="seal" title="小谷黑话：点击开关高亮"><span class="mark">谷</span><span class="count">0</span></button>
    <div class="pop" hidden></div>`;
  const seal = shadow.querySelector(".seal");
  const countEl = shadow.querySelector(".count");
  const pop = shadow.querySelector(".pop");
  document.documentElement.appendChild(host);

  const pageStyle = document.createElement("style");
  pageStyle.textContent = `::highlight(${HIGHLIGHT}){background-color:rgba(196,140,60,.18);text-decoration:underline 1.5px rgba(178,74,48,.85);text-underline-offset:3px;}`;
  document.documentElement.appendChild(pageStyle);

  // ---------- 扫描 ----------
  function acceptable(node) {
    for (let el = node.parentElement; el; el = el.parentElement) {
      if (el === host) return false;
      if (SKIP_TAGS.has(el.tagName)) return false;
      if (el.isContentEditable) return false;
    }
    return true;
  }

  function scan() {
    hitsByNode = new Map();
    hitCount = 0;
    const ranges = [];
    if (enabled && document.body) {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode: (n) => (n.data.trim().length >= 2 && acceptable(n) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
      });
      for (let node; (node = walker.nextNode()); ) {
        const hits = XGMatcher.match(node.data, PATTERNS);
        if (!hits.length) continue;
        hitsByNode.set(node, hits);
        for (const h of hits) {
          const r = new Range();
          r.setStart(node, h.start);
          r.setEnd(node, h.end);
          ranges.push(r);
        }
        hitCount += hits.length;
      }
    }
    CSS.highlights.set(HIGHLIGHT, new Highlight(...ranges));
    countEl.textContent = enabled ? String(hitCount) : "关";
    seal.classList.toggle("off", !enabled);
  }

  let timer = 0;
  function scheduleScan() {
    clearTimeout(timer);
    timer = setTimeout(scan, 400);
  }

  new MutationObserver((records) => {
    // 只因自身 UI 变化触发的不重扫
    if (records.every((r) => r.target === host || host.contains(r.target))) return;
    scheduleScan();
  }).observe(document.body || document.documentElement, { childList: true, subtree: true, characterData: true });

  // ---------- 点击命中 ----------
  function hitAt(x, y) {
    const pos = document.caretPositionFromPoint
      ? document.caretPositionFromPoint(x, y)
      : document.caretRangeFromPoint && (() => { const r = document.caretRangeFromPoint(x, y); return r && { offsetNode: r.startContainer, offset: r.startOffset }; })();
    if (!pos || !hitsByNode.has(pos.offsetNode)) return null;
    const hit = hitsByNode.get(pos.offsetNode).find((h) => pos.offset >= h.start && pos.offset < h.end)
      // caret 落在词尾边界时取左侧词
      || hitsByNode.get(pos.offsetNode).find((h) => pos.offset === h.end);
    if (!hit) return null;
    const range = new Range();
    range.setStart(pos.offsetNode, hit.start);
    range.setEnd(pos.offsetNode, hit.end);
    // 确认点击确实落在这个词的矩形里，避免点到行尾空白也弹
    const inside = [...range.getClientRects()].some((b) => x >= b.left - 2 && x <= b.right + 2 && y >= b.top - 2 && y <= b.bottom + 2);
    return inside ? { hit, range, text: pos.offsetNode.data.slice(hit.start, hit.end) } : null;
  }

  document.addEventListener("click", (e) => {
    if (!enabled || e.composedPath().includes(host)) return;
    const found = hitAt(e.clientX, e.clientY);
    if (!found) { closePop(); return; }
    // 招聘站的整块卡片常常是链接，命中黑话时拦下跳转
    e.preventDefault();
    e.stopPropagation();
    openPop(found);
  }, true);

  // 悬停在黑话上时给手型光标，提示可点
  document.addEventListener("mousemove", (e) => {
    if (!enabled || !hitsByNode.size) return;
    const over = !!hitAt(e.clientX, e.clientY);
    document.documentElement.classList.toggle("xg-jargon-hover", over);
  }, { passive: true });
  pageStyle.textContent += `html.xg-jargon-hover, html.xg-jargon-hover *{cursor:pointer !important;}`;

  // ---------- 浮窗 ----------
  function esc(s) {
    return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function openPop({ hit, range, text }) {
    const e = ENTRIES[hit.index];
    const sameName = text.replace(/\s/g, "").toLowerCase() === e.term.replace(/\s/g, "").toLowerCase();
    const flags = (e.red_flags || []).map((f) => `<li>${esc(f)}</li>`).join("");
    pop.innerHTML = `
      <header>
        <h1>${esc(text)}</h1>
        ${sameName ? "" : `<p class="alias">词条　${esc(e.term)}</p>`}
        <button class="close" aria-label="关闭">×</button>
      </header>
      <section class="lead"><p>${esc(e.blunt)}</p></section>
      <section class="ask"><h2>可以这样问</h2><p>${esc(e.verify)}</p></section>
      <details>
        <summary>展开：字面意思 · 最坏情况 · 危险信号 · 合格回答</summary>
        <dl>
          <dt>字面意思</dt><dd>${esc(e.literal)}</dd>
          <dt>最坏情况</dt><dd>${esc(e.worst_case)}</dd>
          ${flags ? `<dt>危险信号</dt><dd><ul>${flags}</ul></dd>` : ""}
          <dt>合格回答</dt><dd>${esc(e.good_answer)}</dd>
        </dl>
      </details>
      <footer>${esc(e.evidence_boundary)}</footer>`;
    pop.hidden = false;
    pop.querySelector(".close").addEventListener("click", closePop);
    place(range.getBoundingClientRect());
  }

  function place(anchor) {
    const gap = 10;
    const w = pop.offsetWidth;
    const h = pop.offsetHeight;
    let left = Math.min(Math.max(12, anchor.left), innerWidth - w - 12);
    let top = anchor.bottom + gap;
    if (top + h > innerHeight - 12) top = Math.max(12, anchor.top - h - gap);
    pop.style.left = left + "px";
    pop.style.top = top + "px";
  }

  function closePop() { pop.hidden = true; }

  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closePop(); });
  addEventListener("scroll", closePop, { passive: true });

  // ---------- 开关 ----------
  function toggle() {
    enabled = !enabled;
    closePop();
    scan();
  }
  seal.addEventListener("click", toggle);

  globalThis.__xgJargon = { toggle, scan, stats: () => ({ enabled, hitCount }) };
  scan();

  // ---------- 样式（日式简约：纸白、墨色、朱印，一种强调色） ----------
  function STYLE() {
    return `
    :host{all:initial}
    *{box-sizing:border-box;margin:0;padding:0}
    .seal{position:fixed;right:20px;bottom:24px;display:flex;flex-direction:column;align-items:center;gap:2px;
      width:40px;padding:7px 0 6px;border:1px solid rgba(178,74,48,.9);border-radius:2px;background:#faf8f3;
      color:#b24a30;font:600 15px/1 "Songti SC","Noto Serif SC","Source Han Serif SC",serif;cursor:pointer;
      box-shadow:0 1px 0 rgba(40,30,20,.06);transition:transform .2s ease,opacity .2s ease}
    .seal:hover{transform:translateY(-2px)}
    .seal .count{font:500 10px/1 ui-monospace,"SF Mono",Menlo,monospace;color:#6b6358;letter-spacing:.04em}
    .seal.off{opacity:.45;border-color:#8a8378;color:#8a8378}
    .pop{position:fixed;width:min(360px,calc(100vw - 24px));max-height:min(70vh,520px);overflow:auto;
      background:#faf8f3;color:#2b2722;border:1px solid #d9d2c5;border-radius:2px;
      box-shadow:0 12px 32px -12px rgba(40,30,20,.28);padding:20px 22px 16px;
      font:14px/1.75 "Hiragino Sans GB","PingFang SC","Noto Sans SC",sans-serif;animation:rise .18s ease-out}
    @keyframes rise{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
    header{position:relative;padding-right:24px;margin-bottom:14px}
    h1{font:600 19px/1.4 "Songti SC","Noto Serif SC","Source Han Serif SC",serif;letter-spacing:.02em}
    .alias{margin-top:2px;font-size:12px;color:#8a8378}
    .close{position:absolute;top:-6px;right:-8px;width:28px;height:28px;border:0;background:none;color:#8a8378;font-size:18px;cursor:pointer}
    .close:hover{color:#2b2722}
    .lead p{font-size:15px;line-height:1.8}
    .ask{margin-top:14px;padding-left:12px;border-left:2px solid #b24a30}
    h2{font-size:11px;font-weight:600;letter-spacing:.16em;color:#b24a30;margin-bottom:2px}
    details{margin-top:16px;border-top:1px solid #e6e0d4;padding-top:10px}
    summary{cursor:pointer;font-size:12px;color:#6b6358;list-style:none}
    summary::-webkit-details-marker{display:none}
    summary::before{content:"＋";margin-right:6px;color:#b24a30}
    details[open] summary::before{content:"－"}
    dl{margin-top:8px}
    dt{margin-top:10px;font-size:11px;letter-spacing:.12em;color:#8a8378}
    dd{font-size:13.5px}
    ul{padding-left:1.1em}
    footer{margin-top:16px;padding-top:10px;border-top:1px solid #e6e0d4;font-size:11.5px;line-height:1.6;color:#8a8378}
    `;
  }
})();
