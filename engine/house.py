"""Original royalty-free house loop (124 BPM, A minor): kick, clap, hats, offbeat bass, chord stabs.
usage: python3 house.py out.wav seconds [seed]"""
import sys, numpy as np, wave
SR = 48000; BPM = 124; BEAT = 60 / BPM
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 1)

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d); return e

def lp(x, cut):  # one-pole low-pass
    a = np.exp(-2 * np.pi * cut / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y

def hp(x, cut): return x - lp(x, cut)

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(1.6 * np.sin(ph) * env(n, 0.001, 0.16)) * 0.95

def clap():
    n = int(0.25 * SR); x = rng.normal(0, 1, n)
    x = hp(lp(x, 2600), 900) * env(n, 0.001, 0.07); return x * 0.9

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); x = hp(rng.normal(0, 1, n), 7000)
    return x * env(n, 0.0005, 0.06 if open_ else 0.015) * (0.35 if open_ else 0.25)

def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR; out = 0
    for d in (-detune, 0, detune):
        out = out + 2 * ((t * freq * (1 + d)) % 1) - 1
    return out / 3

def note(m): return 440 * 2 ** ((m - 69) / 12)

# A minor: Am - F - C - G, one chord per bar
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]

def render(seconds):
    n = int(seconds * SR); L = np.zeros(n); R = np.zeros(n)
    def add(sig, start, pan=0.0, g=1.0):
        s = int(start * SR); e = min(n, s + len(sig))
        if s >= n: return
        seg = sig[:e - s] * g; L[s:e] += seg * (1 - pan) ; R[s:e] += seg * (1 + pan)
    K, C = kick(), clap()
    bars = int(seconds / (4 * BEAT)) + 1
    for b in range(bars):
        root, chord = PROG[b % 4]; t0 = b * 4 * BEAT
        for q in range(4):
            add(K, t0 + q * BEAT)
            add(hat(open_=True), t0 + q * BEAT + BEAT / 2, pan=0.25)
            for s16 in (0.25, 0.75):
                add(hat(), t0 + q * BEAT + s16 * BEAT, pan=-0.25)
            if q in (1, 3): add(C, t0 + q * BEAT, g=0.8)
            # offbeat bass
            bn = int(BEAT * 0.45 * SR)
            bass = lp(saw(note(root - 12), bn, 0.004), 420) * env(bn, 0.003, 0.12)
            add(np.tanh(2.2 * bass) * 0.55, t0 + q * BEAT + BEAT / 2)
        # chord stabs on the "and" of 1 and 3, plus a pushed stab
        for pos in (0.5, 1.75, 2.5, 3.5):
            sn = int(0.22 * SR); st = sum(saw(note(m), sn, 0.006) for m in chord) / 3
            st = lp(st, 1800 + 900 * np.sin(b / 3)) * env(sn, 0.004, 0.09) * 0.38
            add(st, t0 + pos * BEAT, pan=-0.15)
            add(st * 0.35, t0 + pos * BEAT + 0.75 * BEAT, pan=0.35)   # dotted echo
    mix = np.stack([L, R], 1)
    mix = np.tanh(mix * 0.9)                                         # glue
    fade = int(1.0 * SR); mix[:fade] *= np.linspace(0, 1, fade)[:, None]; mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return (mix / np.max(np.abs(mix)) * 0.89)

if __name__ == "__main__":
    out, secs = sys.argv[1], float(sys.argv[2])
    y = (render(secs) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
    print(out)
