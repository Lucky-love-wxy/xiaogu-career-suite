// 黑话匹配器：纯函数，浏览器（content script）和 Node（单测）共用。
// 规则与 xiaogu-launch 的 search.py 对齐：忽略大小写、字符之间允许空白。
// 在此基础上加两条只对「页面内定位」有意义的规则：
//   1. 长词优先占位，短词不能落在已占位置里（「隔周双休」里不再单独亮「双休」）；
//   2. 否定跳过：否定词紧贴在命中前（同一小句内），且词条本身不含否定，就不算命中。
//      只认紧贴的否定，避免「非常有竞争力」「不断拥抱变化」「不定期团建」被误跳过。
(function (root) {
  const NEGATION = /不|无|非|没有|未/;
  const NEG_BEFORE = /(?:不是|没有|不提供|不含|非|无|不|未)\s*$/;
  const CLAUSE_BREAK = /[，。；;,.!！?？\n、：:]/;
  const NEG_WINDOW = 4;

  function escapeChar(ch) {
    return ch.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // 把词条及别名拍平成模式列表，按去空白后的长度降序
  function compile(entries) {
    const patterns = [];
    entries.forEach((entry, index) => {
      const names = [entry.term, ...(entry.aliases || [])];
      for (const name of names) {
        const bare = (name || "").replace(/ /g, "");
        if (!bare) continue;
        patterns.push({
          index,
          name,
          length: bare.length,
          negatable: !NEGATION.test(bare),
          regex: new RegExp([...bare].map(escapeChar).join("\\s*"), "gi"),
        });
      }
    });
    patterns.sort((a, b) => b.length - a.length);
    return patterns;
  }

  function negated(text, start) {
    let window = text.slice(Math.max(0, start - NEG_WINDOW), start);
    const cut = Math.max(...[...window].map((ch, i) => (CLAUSE_BREAK.test(ch) ? i : -1)));
    if (cut >= 0) window = window.slice(cut + 1);
    return NEG_BEFORE.test(window);
  }

  // 返回 [{start, end, index, name}]，按 start 升序，互不重叠
  function match(text, patterns) {
    const hits = [];
    const taken = new Uint8Array(text.length);
    for (const p of patterns) {
      p.regex.lastIndex = 0;
      let m;
      while ((m = p.regex.exec(text))) {
        const start = m.index;
        const end = start + m[0].length;
        if (m[0].length === 0) { p.regex.lastIndex++; continue; }
        let free = true;
        for (let i = start; i < end; i++) if (taken[i]) { free = false; break; }
        if (!free) continue;
        if (p.negatable && negated(text, start)) continue;
        taken.fill(1, start, end);
        hits.push({ start, end, index: p.index, name: p.name });
      }
    }
    return hits.sort((a, b) => a.start - b.start);
  }

  const api = { compile, match };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.XGMatcher = api;
})(globalThis);
