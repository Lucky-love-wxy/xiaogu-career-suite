#!/usr/bin/env python3
# 小谷 30s 配乐：numpy 合成，120 BPM（一拍 0.5s），段落与分镜对齐。
# 意图：OpenMontage 的免 key 配乐源（Pixabay）实测 403，其余要 key；先用合成垫底，平台发布时可换热门 BGM。
# 段落（100 BPM，一拍 0.6s，一小节 2.4s）：0–3 地址栏（木琴琶音，第 0 秒就有声）/ 3–10.8 主页与贴 JD（加底鼓）
#       10.85–13 等待生成（踩镲加密 + 噪声渐强，铺垫加速段）/ 13 回答出现（和弦重拍）/ 13–21.5 律动 / 21.5–24 收薄
#       24 收尾大和弦 + 25.2 芽长出时高音铃 / 之后余音到 30
# 输出 assets/audio/bed.wav（48k 立体声），响度由 render.mjs 统一收敛到 -14 LUFS。
import numpy as np
import wave
import os

SR = 48000
DUR = 30.0
BEAT = 0.6
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * gain * (1 + min(0, pan))

def mallet(m, dur=0.9):
    # 木琴感：基频 + 3.9 倍泛音（快衰减），短起音
    t = np.arange(int(SR * dur)) / SR
    f = midi(m)
    env = np.exp(-t * 5.5) * np.minimum(1, t / 0.003)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t * 18)) * env

def pad(ms, dur, attack=0.4):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / 0.4)
    s = sum(np.sin(2 * np.pi * midi(m) * t) + 0.3 * np.sin(2 * np.pi * midi(m) * 2.0 * t) for m in ms)
    return s / len(ms) * env

def kick():
    t = np.arange(int(SR * 0.3)) / SR
    f = 45 + 75 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 14)

rng = np.random.default_rng(7)  # 固定种子：每次渲染完全一致
def hat():
    t = np.arange(int(SR * 0.06)) / SR
    n = rng.standard_normal(len(t))
    n = np.diff(n, prepend=0)  # 粗糙高通
    return n * np.exp(-t * 70)

def bell(m, dur=2.2):
    t = np.arange(int(SR * dur)) / SR
    f = midi(m)
    env = np.exp(-t * 2.2)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 4)) * env


AM, F, C, G = [57, 60, 64], [53, 57, 60], [48, 55, 60, 64], [55, 59, 62]
ARP = {"Am": [69, 72, 76, 72], "F": [65, 69, 72, 69], "C": [67, 72, 76, 72], "G": [67, 71, 74, 71]}
PROG = [(AM, "Am"), (F, "F"), (C, "C"), (G, "G")]
BAR = BEAT * 4

def bar(t0, i, arp_gain=0.2, kick_on=True, hats=False, dur=BAR):
    ch, arp = PROG[i % 4]
    add(pad(ch, dur), t0, 0.11)
    n = int(round(dur / (BEAT / 2)))
    for k in range(n):
        add(mallet(ARP[arp][k % 4]), t0 + k * BEAT / 2, arp_gain, pan=(-0.3 if k % 2 else 0.3))
    if kick_on:
        for b in range(int(round(dur / BEAT))):
            add(kick(), t0 + b * BEAT, 0.5)
    if hats:
        for b in range(int(round(dur / BEAT))):
            add(hat(), t0 + b * BEAT + BEAT / 2, 0.07, pan=0.4)

# 0–3：只有琶音（不打鼓）
bar(0.0, 0, kick_on=False, dur=3.0)
# 3–10.8：主页、贴 JD
t, i = 3.0, 1
while t < 10.8 - 0.01:
    d = min(BAR, 10.85 - t); bar(t, i, dur=d); t += d; i += 1
# 10.85–13：等待生成，踩镲十六分音符加密 + 噪声渐强
n = int(2.15 / (BEAT / 4))
for k in range(n):
    add(hat(), 10.85 + k * BEAT / 4, 0.05 + 0.08 * k / n, pan=(0.3 if k % 2 else -0.3))
tt = np.arange(int(SR * 2.15)) / SR
riser = rng.standard_normal(len(tt)) * (tt / 2.15) ** 2
add(np.diff(riser, prepend=0) * 0.6, 10.85, 0.25)
add(pad(F, 2.15, 0.6), 10.85, 0.1)
# 13：回答出现，和弦重拍
add(kick(), 13.0, 0.7); add(bell(84, 1.6), 13.0, 0.15)
t, i = 13.0, 2
while t < 21.5 - 0.01:
    d = min(BAR, 21.5 - t); bar(t, i, hats=True, dur=d); t += d; i += 1
# 21.5–24：收薄，只留垫和少量木琴（聚焦「仍需确认」）
add(pad(AM, 2.5, 0.2), 21.5, 0.1)
for k, m in enumerate([76, 72, 69, 72]):
    add(mallet(m, 1.0), 21.5 + k * BEAT, 0.16)
# 24：收尾
add(pad(C + [72], 6.0, 0.02), 24.0, 0.15)
add(kick(), 24.0, 0.7)
add(mallet(60, 2.0), 24.0, 0.3); add(mallet(64, 2.0), 24.0, 0.25)
add(bell(84), 25.2, 0.22); add(bell(88), 25.45, 0.12)
for k, m in enumerate([72, 76, 79, 84]):
    add(mallet(m, 1.2), 26.4 + k * BEAT, 0.12)
# 结尾 1.5s 渐弱，避免截断爆音
fade = np.ones(N)
fade[-int(SR * 1.5):] = np.linspace(1, 0, int(SR * 1.5))
st = np.stack([L * fade, R * fade], axis=1)
st /= np.max(np.abs(st)) * 1.12
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/bed.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("assets/audio/bed.wav", DUR, "s")
