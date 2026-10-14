#!/usr/bin/env python3
# 小谷 15s 配乐：numpy 合成，120 BPM（一拍 0.5s），段落与分镜对齐。
# 意图：OpenMontage 的免 key 配乐源（Pixabay）实测 403，其余要 key；先用合成垫底，平台发布时可换热门 BGM。
# 段落：0–3 钩子（木琴琶音，第 0 秒就有声）/ 3–5 转折（加底鼓）/ 5–11 证明（和弦进行 + 底鼓 + 踩镲，
#       三行字落在 5.0 / 6.5 / 8.0 加高音强调）/ 11–12 屏息（只剩长音）/ 12–15 品牌（大和弦 + 12.5 芽长出时高音铃）
# 输出 assets/audio/bed.wav（48k 立体声），响度由 render.mjs 统一收敛到 -14 LUFS。
import numpy as np
import wave
import os

SR = 48000
DUR = 15.0
BEAT = 0.5
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

# 和弦（A 小调）：Am – F – C – G – Am，品牌落 C 大
AM, F, C, G = [57, 60, 64], [53, 57, 60], [48, 55, 60, 64], [55, 59, 62]
ARP = {"Am": [69, 72, 76, 72], "F": [65, 69, 72, 69], "C": [67, 72, 76, 72], "G": [67, 71, 74, 71]}

# 0–3 钩子：Am 琶音八分音符 + 垫
add(pad(AM, 3.0, 0.05), 0, 0.10)
for k in range(12):
    add(mallet(ARP["Am"][k % 4]), k * 0.25, 0.22, pan=(-0.3 if k % 2 else 0.3))
# 3–5 转折：F，加底鼓（每拍）
add(pad(F, 2.0), 3.0, 0.12)
for k in range(8):
    add(mallet(ARP["F"][k % 4]), 3.0 + k * 0.25, 0.22, pan=(-0.3 if k % 2 else 0.3))
for b in range(4):
    add(kick(), 3.0 + b * BEAT, 0.55)
# 5–11 证明：C – G – Am，每小节 2s；三行字落在 5.0 / 6.5 / 8.0，各加一个高八度强调音
for bar, (ch, arp) in enumerate([(C, "C"), (G, "G"), (AM, "Am")]):
    t0 = 5.0 + bar * 2.0
    add(pad(ch, 2.0), t0, 0.12)
    for k in range(8):
        add(mallet(ARP[arp][k % 4]), t0 + k * 0.25, 0.22, pan=(-0.3 if k % 2 else 0.3))
    for b in range(4):
        add(kick(), t0 + b * BEAT, 0.55)
        add(hat(), t0 + b * BEAT + 0.25, 0.08, pan=0.4)
for t_acc, m_acc in [(5.0, 84), (6.5, 86), (8.0, 88)]:
    add(mallet(m_acc, 1.2), t_acc, 0.3)
# 11–12 屏息：只留一个长音
add(pad([57, 64], 1.0, 0.1), 11.0, 0.08)
add(mallet(76, 1.0), 11.0, 0.18)
# 12–15 品牌：C 大和弦 + 底鼓重拍 + 12.5 高音铃（芽长出）
add(pad(C + [72], 3.0, 0.02), 12.0, 0.16)
add(kick(), 12.0, 0.7)
add(mallet(60, 2.0), 12.0, 0.3)
add(mallet(64, 2.0), 12.0, 0.25)
add(bell(84), 12.5, 0.22)
add(bell(88), 12.75, 0.12)

# 结尾 0.3s 渐弱，避免截断爆音
fade = np.ones(N)
fade[-int(SR * 0.3):] = np.linspace(1, 0, int(SR * 0.3))
st = np.stack([L * fade, R * fade], axis=1)
st /= np.max(np.abs(st)) * 1.12
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/bed.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("assets/audio/bed.wav", DUR, "s")
