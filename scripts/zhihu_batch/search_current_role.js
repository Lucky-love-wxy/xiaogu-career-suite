/* Serial public Baidu discovery, current origin only. Offline research only.
 * Run via cdp.mjs eval --body-file after verifying a Baidu search page.
 * At most three searches, 5-9 seconds apart; caller owns rolling-hour ledger.
 * No Zhihu requests or account/profile capture. Stop on any denied/empty page.
 */
(async () => {
  const jobs = [{"role": "医疗器械注册", "query": "知乎 医疗器械注册 工作一年 日常 体验"}, {"role": "生物药研发", "query": "知乎 生物制药 研发 工作 体验"}, {"role": "医学写作", "query": "知乎 医学撰写 入职一年 medical writer"}];
  if (location.hostname !== 'www.baidu.com') throw new Error('Expected verified Baidu origin');
  const records = [];
  // Every attempt is checkpointed before sending. Read this checkpoint after
  // interruption; an unfinished attempt is UNKNOWN and must never be retried.
  const checkpoint = window.__xiaoguOfflineResearchSearchCheckpoint ||= [];
  if (checkpoint.some(record => record.state === 'UNKNOWN_IN_FLIGHT' || record.state.startsWith('STOP_'))) {
    throw new Error('Refuse: prior STOP/UNKNOWN checkpoint; reconcile durable journal first');
  }
  for (const job of jobs) {
    if (checkpoint.some(record => record.query === job.query)) continue;
    await new Promise(resolve => setTimeout(resolve, 5000 + Math.random() * 4000));
    const openedAt = new Date().toISOString();
    const attempt = { ...job, opened_at: openedAt, state: 'UNKNOWN_IN_FLIGHT' };
    checkpoint.push(attempt);
    let response, html;
    const controller = new AbortController();
    const deadline = setTimeout(() => controller.abort(), 5000);
    try {
      response = await fetch('/s?wd=' + encodeURIComponent(job.query), {
        credentials: 'include', signal: controller.signal
      });
      html = await response.text();
    } catch (error) {
      Object.assign(attempt, { checked_at: new Date().toISOString(),
        state: 'STOP_FETCH_ERROR', error: String(error) });
      records.push(attempt);
      break;
    } finally {
      clearTimeout(deadline);
    }
    const dom = new DOMParser().parseFromString(html, 'text/html');
    const text = dom.body?.textContent || '';
    const resultNodes = [...dom.querySelectorAll('#content_left .result,#content_left .c-container')];
    const state = response.status === 403 || response.status === 429 ? 'STOP_HTTP_DENIED'
      : /安全验证|操作频繁|访问过于频繁|验证码/.test(dom.title + text.slice(0, 1000)) ? 'STOP_VERIFICATION'
        : !text.trim() || !dom.title.includes('百度') ? 'STOP_EMPTY_REDIRECT' : 'SEARCH_LOADED';
    Object.assign(attempt, { checked_at: new Date().toISOString(),
      url: response.url, http_status: response.status, title: dom.title, state,
      results: resultNodes.filter(node => node.querySelector('h3') && /zhihu\.com/.test(node.getAttribute('mu') || ''))
        .map(node => ({ title: node.querySelector('h3').textContent.trim(),
          text: node.textContent.replace(/\s+/g, ' ').trim(), mu: node.getAttribute('mu') })) });
    records.push(attempt);
    if (state !== 'SEARCH_LOADED') break;
  }
  return JSON.stringify(records);
})()
