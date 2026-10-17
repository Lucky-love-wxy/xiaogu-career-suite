"""录屏式演示片的声音：读 events.json（node toolkit/scripts/events.mjs <目录> 从页面导出），生成
assets/audio/music.wav（配乐）与 assets/audio/foley.wav（拟音 + 吉祥物芯片音）。运行：sh toolkit/audio/run.sh <目录>

STYLE §7「两种分辨率的音乐」：高保真层（采样器的真乐器）是界面世界，芯片方波是吉祥物；
拟音跟着用户动作（按键、点击、面板、弹出），吉祥物的跳跃、落地、脚步是 8-bit 音。
做具体产品时：改 BPM / 和弦 / 配器（避免泛滥的钢琴 + 弦乐），事件到音色的映射照用。
"""
import json
import numpy as np
from audiokit import S, F, SR, write, foley, credits

E = json.load(open('events.json', encoding='utf-8'))
DUR, EV = float(E['dur']), E['ev']
BPM = 100; BEAT = 60 / BPM                  # 与 film.js 一致：一拍 0.6 s，章节与落点都在拍上

# ───────── 配乐：颤音琴和弦铺底 + 马林巴固定音型 + 电贝斯 + 轻鼓；章节转场处加一记镲
CHORDS = [['F3', 'A3', 'C4', 'E4'], ['D3', 'F3', 'A3', 'C4'], ['B2', 'D3', 'F3', 'A3'], ['C3', 'E3', 'G3', 'B3']]
ROOT = ['F2', 'D2', 'B1', 'C2']
RIFF = ['C5', 'A4', 'F4', 'A4', 'G4', 'A4', 'C5', 'E5']
wipes = [e['t'] for e in EV if e['type'] == 'wipe']
spot = [e['t'] for e in EV if e['type'] == 'spot']
ev = []
bar = 0; t = 0.0
while t < DUR - .5:
    ch = bar % 4
    for p in CHORDS[ch]: ev.append((t, 'vibraphone', p, BEAT * 4 - .05, .32, 0))
    for b in range(4):
        tb = t + b * BEAT
        if tb >= DUR - .6: break
        quiet = any(s - .4 < tb < s + 1.2 for s in spot)                      # 聚光冻结时抽掉节奏，只留和弦（STYLE §7：关键承诺前的静）
        if not quiet:
            ev.append((tb, 'electric_bass', ROOT[ch], BEAT * .9, .55, 0))
            ev.append((tb, 'drum_kit', 'kick_drum_left' if b % 2 == 0 else 'snare_1', None, .45 if b % 2 == 0 else .3, 0))
            ev.append((tb + BEAT / 2, 'drum_kit', 'hi_hat_closed', None, .22, .3))
            ev.append((tb, 'marimba', RIFF[(bar * 4 + b) % 8], .2, .32, .2))
    bar += 1; t += BEAT * 4
for w in wipes: ev.append((w, 'drum_kit', 'crash_left', None, .22, -.3))   # 镲片高频瞬态是 AAC 真峰值过冲的主因，压轻
music = S.room(S.render(ev, dur=DUR), size=.28, mix=.12)
fade = int(.7 * SR); music[-fade:] *= np.linspace(1, 0, fade)[:, None]
write('assets/audio/music.wav', music)

# ───────── 吉祥物芯片音：方波 + 滑音（跳：上滑；落：下滑短促；脚步：极短）
def chip(f0, f1, d, v=.35, duty=.5):
    n = int(d * SR); f = np.linspace(f0, f1, n); ph = np.cumsum(f) / SR
    x = np.where((ph % 1) < duty, 1.0, -1.0) * np.exp(-np.arange(n) / SR / (d * .6))
    return (F.lp(x, 6000, 4) * v).astype(np.float32)        # 方波高频泛音多，AAC 后会冲出采样间峰值：先低通到 6 kHz

buf = foley([], DUR)
MAP = {  # 用户动作 → 拟音（lemo sfx 程序化合成，无授权要求）
    'key': ('click', .22, {'pitch': 1.1}), 'click': ('click', .35, {}), 'send': ('whoosh', .35, {'d': .25}),
    'whoosh': ('whoosh', .35, {'d': .35}), 'pane': ('pop', .3, {}), 'pop': ('pop', .28, {}), 'spot': ('ding', .3, {}),
    'darkon': ('thump', .45, {'f': 60}), 'wipe': ('whoosh', .3, {'d': .5}), 'hit': ('thump', .4, {}),
}
for e in EV:
    k, t = e['type'], e['t']
    if k in MAP:
        fn, g, kw = MAP[k]; F.add(buf, getattr(F, fn)(**kw), t, g * float(e.get('v', 1)), 0)
    elif k == 'jump': F.add(buf, chip(330, 880, .14), t, .5, 0)
    elif k == 'land': F.add(buf, chip(440, 160, .09), t, .5 * float(e.get('v', .6)) + .2, 0)
    elif k == 'step': F.add(buf, chip(700, 650, .03, duty=.25), t, .15, 0)
    elif k == 'morph':                                                           # 像素从 logo 的芽里飞出：芯片上行琶音
        for i, f in enumerate([523, 659, 784, 1047, 1319]): F.add(buf, chip(f, f, .07, .3), t + i * .13, .35, (i - 2) * .15)
    elif k == 'paste': F.add(buf, F.whoosh(d=.18), t, .3, 0)
if np.abs(buf).max() > .95:
    buf = np.stack([F.limit(buf[:, 0], .95), F.limit(buf[:, 1], .95)], 1).astype(np.float32)
write('assets/audio/foley.wav', buf)

credits(['vibraphone', 'marimba', 'electric_bass', 'drum_kit'])
