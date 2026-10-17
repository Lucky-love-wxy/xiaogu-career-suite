// 《一个岗位，一次看懂》时间线（约 45 s，100 BPM，一拍 0.6 s）。剧本见 TREATMENT.md。
// 真相：JD 与回答取自 ref/jd.txt、ref/answer-2026-10-15.md；阶段时刻取自 ref/run-2026-10-15.json（发送后 0.02 理解问题、
// 0.17 查小谷数据库 / 生成回答、3.51 校验、3.54 返回）；逐字打出速度照 index.html 的 typeOut（每 16 ms 走 ceil(长度/400) 字）。
import { seg, back, eo } from './core/lib.js';
import { EV, ev, setVoice, synthWords, camera, Actor, Cursor, at, pt, hudState } from './engine.js';
import { VARIANT } from './variant.js';
// 路演版打开「运行记录」面板（主区中心 922）；用户版不开（主区中心 1092）：对话阶段的镜头横坐标统一右移 170
const TRACE = VARIANT === 'pitch';
const X = (x) => (TRACE ? x : x + 170);
export { EV };

export const SIZE = { W: 1920, H: 1080 };
export const BPM = 100, B = 60 / BPM;
export const DUR = 45;
const MESSAGE = `【产品运营实习生】
岗位职责：
1. 负责用户社群的日常运营，拉新促活，提升用户粘性；
2. 协助策划线上活动，跟进活动数据并复盘；
3. 对接设计、研发同学，推动需求落地；
任职要求：
1. 本科及以上在读，每周到岗 4 天以上，可实习 6 个月；
2. 抗压能力强，能适应快节奏，有 owner 意识；
3. 有自驱力，结果导向，拥抱变化。`;
const ANSWER = `**结论** 产品运营实习生，说白了就是帮公司把用户群管起来、把线上活动跑起来，再盯着数据看效果。招聘说明写清了：要管社群拉新促活、协助策划线上活动并复盘数据、对接设计和研发推动需求落地；也写清了门槛——本科及以上在读、每周到岗 4 天以上、能实习 6 个月。没写清的是：具体负责哪个产品、社群和活动的规模有多大、带不带人、有没有转正机会、薪资和补贴怎么算，以及“抗压能力强”“结果导向”“拥抱变化”这些词背后，压力到底来自工时、指标还是临时改需求。

**依据**
- JD 原文：“负责用户社群的日常运营，拉新促活，提升用户粘性；”
- JD 原文：“协助策划线上活动，跟进活动数据并复盘；”
- JD 原文：“对接设计、研发同学，推动需求落地；”
- JD 原文：“本科及以上在读，每周到岗 4 天以上，可实习 6 个月；”
- JD 原文：“抗压能力强，能适应快节奏，有 owner 意识；”
- JD 原文：“有自驱力，结果导向，拥抱变化。”
- 参考资料：“主人翁意识”在招聘话术里通常意味着：希望你主动补位，职责没写到的事也可能要你接。
- 参考资料：“抗压能力强”在招聘话术里通常意味着：这个岗位大概率有明确压力源，只是 JD 没直接说压力到底来自工时、指标还是冲突。
- 待核实推断：“有 owner 意识”可能意味着职责没写到的事也需要你主动补位，实际工作范围会比 JD 列的三条更宽。
- 待核实推断：“拥抱变化”可能意味着活动方案或目标会临时调整，你需要提前问清变更时有没有通知和重新排期。

**仍需确认**
- 具体负责哪个产品线或业务方向的社群和活动
- 社群规模、活动频次和考核指标是什么
- 实习薪资、补贴和是否有转正机会
- “抗压能力强”对应的主要压力源是工时、指标还是跨部门冲突

**下一步** 可以复制这句问招聘方：“请问这个实习岗日常在社群运营、活动策划、跨部门对接这三块的时间大概怎么分配？考核主要看哪些指标？”`;

// 字幕（只说画面上真实发生的事）：VO = 出现时刻
export const VO = { c1: 5.6, c2: 8.6, c3: 11.6, c4: 18.3, c5: 20.6, c6: 23.6, c7: 29.8 };
export const LINES = { c1: '把招聘说明整段贴进来。', c2: '小谷先查自己的数据库，再动笔。', c3: '整轮只用 {3.5 秒}。', c4: '先说这个岗位到底{做什么}。',
  c5: '没写清的，它也{说出来}。', c6: '每句判断，都标出{依据}。', c7: '要问招聘方的话，它替你{写好}。' };
export const CHAPTERS = [{ t0: 17.4, no: '01', nm: '结论', hold: 5.1 }, { t0: 22.8, no: '02', nm: '依据', hold: 5.7 }, { t0: 28.8, no: '03', nm: '下一步', hold: 6.6 }];

export const SUBS = [], T = {};
let CAM, C, CUR, HUD, STEP;

export function build(words) {
  EV.length = 0;
  const voice = words || synthWords(LINES);
  setVoice(VO, voice.words);
  // 每句停留 = 阅读时长 + 1 s，但不压到下一句（字幕不重叠，DIRECTOR §7）
  const ids = Object.keys(VO);
  ids.forEach((id, i) => { const t = VO[id], next = ids[i + 1] ? VO[ids[i + 1]] - .15 : DUR; SUBS.push({ id, t0: t - .05, t1: Math.min(t + voice.dur[id] + 1.0, next), text: LINES[id] }); });
  CAM = camera([440, 250, 2.2]);
  C = new Actor(5, B); CUR = new Cursor();
  STEP = Math.ceil(ANSWER.length / 400);

  // ═ S1 片名：像素从 logo 的芽里飞出，拼成小谷，站上「新对话」；再跳到首页标语上（3.0 = 第 6 拍）
  T.birth0 = .6; T.birth1 = 1.4; ev(T.birth0, 'morph'); ev(T.birth1, 'land', { v: .6 });
  C.hide(0, T.birth1).stand(T.birth1, 1.9, at('newchat', .55, 0), { eyes: (t) => (t < 1.7 ? 'wide' : 'r') })
   .jump(1.9, 3.0, at('newchat', .55, 0), at('h2', .14, 0), 140, { big: true })
   .stand(3.0, 5.4, at('h2', .14, 0), { eyes: (t) => (t < 3.6 ? 'happy' : 'd') });
  CAM.move(1.6, 1.6, [1092, 470, 1.35], 'eio');

  // ═ S2 粘贴 + 发送
  T.click = 5.2; CUR.show(4.6, 8.4).move(4.6, 4.6, pt(1500, 900)).move(4.65, T.click - .03, at('ta', .25, .5), 40).click(T.click);
  T.paste = 6.2; ev(T.paste, 'paste');
  T.send = 7.8; ev(T.send - .02, 'key', { v: 1 }); ev(T.send + .02, 'send');
  C.jump(5.4, 5.85, at('h2', .14, 0), at('box', .96, 0), 70).stand(5.85, T.send + .1, at('box', .96, 0), { eyes: (t) => (t < T.paste ? 'd' : 'happy') });
  CAM.move(4.9, .9, [1092, 560, 1.55], 'eio');

  // ═ S3 对话：真实阶段 + 运行记录；小谷沿用户气泡上沿「读」过去
  T.final = T.send + 3.54; T.typeEnd = T.final + Math.ceil(ANSWER.length / STEP) * .016; ev(T.final, 'pane');
  T.traceClick = TRACE ? T.send + .55 : Infinity;
  if (TRACE) CUR.show(T.send + .1, T.traceClick + .5).move(T.send + .1, T.send + .1, at('send', .5, .5)).move(T.send + .15, T.traceClick - .03, at('tracebtn', .5, .5), 50).click(T.traceClick);
  CAM.move(T.send + .05, .45, [X(922), 360, 1.3], 'whip'); ev(T.send + .05, 'whoosh');
  C.jump(T.send + .1, T.send + .55, at('box', .96, 0), at('me', .08, 0), 120)
   .walk(T.send + .7, T.final - .3, at('me', .08, 0), at('me', .9, 0), { eyes: 'd' })
   .stand(T.final - .3, T.final + .1, at('me', .9, 0), { eyes: 'r' });
  if (TRACE) { CAM.move(T.final - .2, .45, [1484, 250, 2.2], 'whip'); ev(T.final - .2, 'whoosh'); }   // 路演版：甩到运行记录（3489 ms、第 1 次通过校验）
  else CAM.move(T.final - .4, .8, [X(922), 400, 1.4], 'eio');                                         // 用户版：推近状态行，看回答一出来就开始打字
  CAM.move(T.final + 1.9, .6, [X(922), 520, 1.2], 'eio');                                          // 回到正在打出的回答
  C.jump(T.final + .1, T.final + .6, at('me', .9, 0), at('sec-0', .5, 0, 0, 0, { x: X(922), y: 520 }), 90)
   .stand(T.final + .6, 17.6, at('sec-0', .5, 0, 0, 0, { x: X(922), y: 520 }), { eyes: 'd' });

  // ═ 01 结论：推近；小谷在三个黑话上逐拍跳（卡拉 OK 球），落脚处留像素下划线
  CAM.move(17.6, .1, [X(922), 470, 1.6], 'eio');
  T.hops = [18.6, 19.2, 19.8]; T.hops.forEach((x) => ev(x, 'pop'));
  let from = at('sec-0', .5, 0);
  T.hops.forEach((x, i) => { const to = at(`w-${i}`, .5, 0); C.jump(x - .35, x, from, to, i ? 30 : 70); C.stand(x, i < 2 ? T.hops[i + 1] - .35 : 23.2, to, { eyes: i < 2 ? 'd' : (t) => (t < 21.2 ? 'happy' : 'l') }); from = to; });
  CAM.move(18.2, 2.2, [X(960), 500, 1.6], 'ss');

  // ═ 02 依据：往下滚到依据；小谷依次踩三种标签
  T.scroll2 = 23.0; CAM.move(23.0, .1, [X(880), 420, 1.45], 'eio');
  T.tags = [24.0, 25.2, 26.4]; T.tags.forEach((x) => ev(x, 'pop'));
  from = at('w-2', .5, 0);
  ['jd', 'ref', 'inf'].forEach((k, i) => { const to = at(`tag-${k}`, .5, 0); C.jump(T.tags[i] - .4, T.tags[i], i ? from : pt(900, 300), to, 50); C.stand(T.tags[i], i < 2 ? T.tags[i + 1] - .4 : 29.0, to, { eyes: 'd' }); from = to; });
  CAM.move(24.0, 4.0, [X(880), 470, 1.45], 'ss');

  // ═ 03 下一步：滚到底；聚光冻结在那句可以直接复制的问话上；光标选中 + ⌘C
  T.scroll3 = 29.0; CAM.move(29.0, .1, [X(920), 560, 1.5], 'eio');
  T.spot0 = 30.6; T.spot1 = 34.0; ev(T.spot0, 'spot');
  C.jump(29.6, 30.1, pt(900, 360), at('nq', .15, 0), 60, { big: true }).stand(30.1, 36.4, at('nq', .15, 0), { eyes: (t) => (t < T.spot0 + .4 ? 'd' : 'happy'), arms: (t) => (t > T.spot0 + .3 && t < T.spot0 + 1.2 ? 'up' : 'down') });
  CAM.move(T.spot0 - .2, .9, [X(960), 600, 1.85], 'eio');
  T.sel0 = 34.4; T.sel1 = 35.2; T.copy = 35.7;
  CUR.show(34.0, 36.3).move(34.0, 34.0, pt(1300, 900)).move(34.05, T.sel0 - .03, at('nq', 0, .5), 30).move(T.sel0, T.sel1, at('nq', 1, .7), 0);
  ev(T.copy - .02, 'key', { v: 1 });

  // ═ 结尾：新对话回到首页，小谷在重拍落到「投」字上（39.6 = 第 66 拍）
  CAM.move(35.8, 1.2, [X(922), 540, 1.0], 'eio');
  T.newClick = 37.2; T.traceClose = TRACE ? 38.1 : Infinity;   // 路演版：新对话 → 再点「运行记录」收起面板（真实开关），标语回到正中
  CUR.show(36.3, TRACE ? 38.6 : 37.9).move(36.3, 36.3, pt(900, 700)).move(36.35, T.newClick - .03, at('newchat', .4, .5), 40).click(T.newClick);
  if (TRACE) CUR.move(T.newClick + .15, T.traceClose - .03, at('tracebtn', .5, .5), 60).click(T.traceClose);
  T.land = 39.6; ev(T.land, 'hit');
  C.jump(36.4, 36.9, at('nq', .15, 0, 0, 0, { x: 760, y: 700 }), at('newchat', .75, 0), 160)
   .stand(36.9, 38.85, at('newchat', .75, 0), { eyes: 'r' })
   .jump(38.85, T.land, at('newchat', .75, 0), at('tou', .5, 0), 180, { big: true })
   .stand(T.land, DUR, at('tou', .5, 0), { eyes: (t) => (t < T.land + .8 ? 'wide' : 'happy'), arms: (t) => (t > T.land + 1.0 && t < T.land + 2.2 ? 'wave' : 'down') });
  CAM.move(38.4, 1.0, [1092, 480, 1.45], 'eio');                  // 收起面板后推近标语，落「投」成为画面主体
  CAM.move(T.land + .2, DUR - T.land - .2, [1092, 470, 1.6], 'ss'); // 片尾极慢推近

  CHAPTERS.forEach((c) => ev(c.t0, 'wipe'));
  T.props = [{ kind: 'spark', t0: T.land, t1: T.land + .8 }, { kind: 'spark', t0: T.spot0 + .2, t1: T.spot0 + 1 }];
  T.ulines = T.hops.map((x, i) => ({ key: `w-${i}`, t0: x }));
  HUD = { subs: SUBS, chapters: CHAPTERS, spot: { key: 'nq', t0: T.spot0, t1: T.spot1 }, fadeOut: [DUR - 1.2, DUR], fadeIn: .4,
    keys: [{ t0: T.paste - .45, keys: ['⌘', 'V'], label: '粘贴', press: [T.paste] }, { t0: T.send - .45, keys: ['↵'], label: '发送', press: [T.send] },
      { t0: T.copy - .45, keys: ['⌘', 'C'], label: '复制', press: [T.copy] }] };
  return { C, CUR };
}

export const camAt = (t) => CAM.at(t);

// 状态行文字：照 setStatus（阶段名 + 已用整秒数），阶段时刻取自真跑
function status(t) {
  const d = t - T.send; if (d < .02 || t >= T.final) return null;
  const label = d < .17 ? '理解问题' : d < 3.51 ? '生成回答' : '校验', secs = Math.floor(d);
  return `正在处理 · ${label}${secs ? ' · ' + secs + ' 秒' : ''}`;
}

export function frame(t) {
  const F = { t, cam: CAM.at(t), actors: [C], cursor: CUR, props: T.props, ulines: T.ulines,
    birth: { t0: T.birth0, t1: T.birth1, from: 'sprout', to: (A) => at('newchat', .55, 0)(A), px: 5 } };
  const fresh = t < T.send || t >= T.newClick;
  const S = { t, fresh, message: MESSAGE, hist: [], newHot: t > T.newClick - .3 && t < T.newClick + .2, traceHot: (t > T.traceClick - .3 && t < T.traceClick + .25) || (t > T.traceClose - .3 && t < T.traceClose + .25) };
  if (t >= T.send) S.hist.push({ title: '【产品运营实习生】', active: t < T.newClick, p: seg(t, T.send, T.send + .28) });
  // 输入框：点击后聚焦；⌘V 一次贴入整段（textarea 自动滚到末尾）；发送后清空
  S.input = { focus: t > T.click && t < T.send, caret: t > T.click && t < T.send && (Math.floor(t * 2.2) % 2 === 0 || t > T.paste),
    text: t >= T.paste && t < T.send ? MESSAGE : '', scroll: t >= T.paste && t < T.send ? 70 : 0 };
  S.sendHot = t > T.send - .1 && t < T.send + .12;
  if (!fresh) {
    S.sent = back(seg(t, T.send, T.send + .3)); S.who = seg(t, T.send + .1, T.send + .4);
    S.status = status(t);
    if (t >= T.final) S.answer = { text: ANSWER, n: Math.min(ANSWER.length, Math.floor((t - T.final) / .016 + 1) * STEP) };
    // 用户往下滚动阅读（片中由镜头换段时一起完成；滚动量按版面实测）
    S.scroll = t < T.scroll2 ? 0 : t < T.scroll3 ? 200 * eo(seg(t, T.scroll2 - .3, T.scroll2)) : 200 + 580 * eo(seg(t, T.scroll3 - .3, T.scroll3));
    S.sel = t >= T.sel0 ? seg(t, T.sel0, T.sel1) : 0;
  }
  S.trace = { w: t < T.traceClick ? 0 : 340 * eo(seg(t, T.traceClick, T.traceClick + .3)) * (1 - eo(seg(t, T.traceClose, T.traceClose + .3))), item: t >= T.final ? seg(t, T.final, T.final + .25) : 0 };
  F.world = S;
  F.dark = { base: 'L' };
  F.hud = hudState(t, HUD); F.hud.dark = true;
  return F;
}
