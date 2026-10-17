/* Offline research DOM reader. Run ONLY via the approved cdp.mjs eval --body-file.
 * Reads at most 10 answers already loaded on the current page.
 * No fetch, navigation, click, scroll, comments, or author profile access.
 * Returns a JSON string for saving in evidence/zhihu-batch-2026-10/.
 * Account verification and navigation ledger must precede content collection.
 */
(() => {
  const pageText = document.body?.innerText || '';
  const title = document.title;
  const url = location.href;
  const blocked = /安全验证|操作频繁|访问过于频繁|访问受限|请完成验证/.test(title)
    || /安全验证|操作频繁|访问过于频繁|请完成验证/.test(pageText.slice(0, 1000));
  const nodes = [...document.querySelectorAll('.AnswerItem')].slice(0, Math.min(10, window.__xiaoguOfflineAnswerLimit || 10));
  const excludedUrls = new Set(["https://www.zhihu.com/question/597894539/answer/126502285208", "https://www.zhihu.com/question/597894539/answer/3115268122", "https://www.zhihu.com/question/597894539/answer/30801381533", "https://www.zhihu.com/question/301742682/answer/49436158271", "https://www.zhihu.com/question/301742682/answer/1304055519", "https://www.zhihu.com/question/301742682/answer/728460034", "https://www.zhihu.com/question/50770074/answer/160962197", "https://www.zhihu.com/question/50770074/answer/123940480", "https://www.zhihu.com/question/50770074/answer/146942915", "https://www.zhihu.com/question/50770074/answer/122774731", "https://www.zhihu.com/question/50770074/answer/674383395", "https://www.zhihu.com/question/511536316/answer/2018002240619717108", "https://www.zhihu.com/question/511536316/answer/2517764426", "https://www.zhihu.com/question/511536316/answer/1967587276629452557", "https://www.zhihu.com/question/490150407/answer/2158935592", "https://www.zhihu.com/question/490150407/answer/2164415753", "https://www.zhihu.com/question/490150407/answer/2164598780", "https://www.zhihu.com/question/341517634/answer/2500794020", "https://www.zhihu.com/question/477517258/answer/2926204368", "https://www.zhihu.com/question/40603392/answer/2078071142095512602", "https://www.zhihu.com/question/339381703/answer/2897774054", "https://www.zhihu.com/question/299457070/answer/516243726", "https://www.zhihu.com/question/299457070/answer/1127859545", "https://www.zhihu.com/question/477517258/answer/2564190556", "https://www.zhihu.com/question/40603392/answer/2517958245", "https://www.zhihu.com/question/341517634/answer/11276023426", "https://www.zhihu.com/question/339381703/answer/2884647901", "https://www.zhihu.com/question/2060271953856950506/answer/2082417984132404512", "https://www.zhihu.com/question/477517258/answer/2028153748510229451", "https://www.zhihu.com/question/35251387/answer/2100528488", "https://www.zhihu.com/question/477517258/answer/2005667291547865830", "https://www.zhihu.com/question/35251387/answer/625808097", "https://www.zhihu.com/question/339381686/answer/2054890468027240800", "https://www.zhihu.com/question/2060271953856950506/answer/2072602664383276077", "https://www.zhihu.com/question/35251387/answer/1082993016", "https://www.zhihu.com/question/477517258/answer/1992971219218241460", "https://www.zhihu.com/question/31549004/answer/274462447", "https://www.zhihu.com/question/339381686/answer/784463006", "https://www.zhihu.com/question/2060271953856950506/answer/2070506953231677268", "https://www.zhihu.com/question/339381686/answer/2327467846", "https://www.zhihu.com/question/35251387/answer/2197056206", "https://www.zhihu.com/question/477517258/answer/1977168972207133145", "https://www.zhihu.com/question/339381703/answer/2050151533808039904", "https://www.zhihu.com/question/477517258/answer/1962821135705044384", "https://www.zhihu.com/question/35251387/answer/884016023", "https://www.zhihu.com/question/40603392/answer/2965039733", "https://www.zhihu.com/question/477517258/answer/112462074469", "https://www.zhihu.com/question/339381703/answer/784434981", "https://www.zhihu.com/question/299457070/answer/2354234269", "https://www.zhihu.com/question/339381703/answer/2845028792", "https://www.zhihu.com/question/341517634/answer/2595786507", "https://www.zhihu.com/question/339381703/answer/2023375971097519269"]);
  const answers = nodes.map((node, index) => {
    const loadedUrl = [...node.querySelectorAll('meta[itemprop=url]')].map(meta => meta.content).find(value => value.includes('/answer/')) || null;
    if (excludedUrls.has(loadedUrl)) return { index, answer_url: loadedUrl, excluded_previous_pilot: true };
    const body = node.querySelector('.RichContent-inner')?.innerText || '';
    const author = (node.querySelector('.AuthorInfo-name')?.innerText || '')
      .replace(/[\u200b\r\n]/g, '').trim();
    const dates = [...node.querySelectorAll('meta[itemprop*=date]')]
      .map(meta => ({ type: meta.getAttribute('itemprop'), value: meta.content }));
    const answerUrl = [...node.querySelectorAll('meta[itemprop=url]')]
      .map(meta => meta.content).find(value => value.includes('/answer/')) || null;
    return { index, author, body, dates, answer_url: answerUrl,
      date_label: node.querySelector('.ContentItem-time')?.innerText || null,
      unicode_without_whitespace: [...body.replace(/\s/gu, '')].length,
      visually_collapsed: Boolean(node.querySelector('.ContentItem-expandButton')) };
  });
  const targets = answers.filter(answer => !answer.excluded_previous_pilot);
  const state = blocked ? 'STOP_VERIFICATION_OR_RATE_LIMIT'
    : !nodes.length ? 'STOP_EMPTY_BODY_OR_LOGIN_REQUIRED'
      : !targets.length ? 'NO_NEW_ANSWERS'
        : targets.every(answer => !(answer.body || '').trim())
          ? 'STOP_EMPTY_BODY_OR_LOGIN_REQUIRED' : 'LOADED_ANSWERS';
  // Preserve stop text, never preserve the signed-in account name or profile.
  const stopText = state !== 'LOADED_ANSWERS'
    ? pageText.replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, '[email removed]').slice(0, 400)
    : null;
  const capture = { checked_at: new Date().toISOString(), title, url,
    state, stop_text: stopText, loaded_answer_count: nodes.length, answers };
  window.__xiaoguOfflineLoadedAnswerCapture = capture;
  return JSON.stringify({ ...capture, answers: answers.map(({body, ...meta}) => ({...meta, body_length: body?.length || 0})) });
})()
