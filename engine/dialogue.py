"""Two-voice dialogue clip (customer vs closer) in the lux style.
Customer lines: white text + "CUSTOMER" tag.  Closer lines: gold text + "CLOSER" tag.
Final to-camera part: normal style (white + gold keywords), no tag.
usage: python3 dialogue.py SCRIPT video            -> out/<name>_silent.mp4 (with CTA)
       python3 dialogue.py SCRIPT voice c.mp3 a.mp3 -> out/<name>.mp4
SCRIPT is a module dlg_<name>.py with NAME, BG (list of jpgs), SEG [(speaker, src, [(w,s,e),...])], src in {"c","a"}."""
import sys, os, subprocess, importlib, random
sys.path.insert(0, "/home/claude/tiktok")
import numpy as np
from PIL import Image, ImageDraw
import lux
from lux import W, H, FPS, LEAD
T = 1.25; GAP = 0.28; PRE = 0.04; POST = 0.14
CTA = "/home/claude/tiktok/cta_gold.png"

def timeline(seg):
    """Place segments back to back (original-speed seconds). Returns [(speaker, src, cut_s, cut_e, offset, words)]."""
    out, cur = [], 0.0
    for spk, src, words in seg:
        s = words[0][1] - PRE; e = words[-1][2] + POST
        off = cur - s
        out.append((spk, src, s, e, off, [(w, a + off, b + off) for w, a, b in words]))
        cur += (e - s) + GAP
    return out

TAGS = {}
def tag_img(text, color):
    if text not in TAGS:
        f = lux.fnt(54); tw = f.getlength(text)
        w, h = int(tw + 64), 84
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([2, 2, w - 3, h - 3], radius=40, fill=(0, 0, 0, 170), outline=color + (255,), width=4)
        bb = f.getbbox(text); d.text(((w - tw) / 2, (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=color + (255,))
        TAGS[text] = im
    return TAGS[text]

def video(mod):
    tl = timeline(mod.SEG)
    chunks = []
    for spk, src, s, e, off, words in tl:
        for c in lux.chunk(words, T):
            for d in c:
                if spk == "CLOSER": d["hi"] = True
                elif spk == "CUSTOMER": d["hi"] = False
            chunks.append((spk, c))
    # chunk end: never run into the next chunk
    for i, (spk, c) in enumerate(chunks):
        nxt = chunks[i + 1][1][0]["a"] if i + 1 < len(chunks) else c[-1]["b"] + 0.9
        for d in c: d["z"] = min(d["z"], nxt)
    total = tl[-1][5][-1][2] / T + 0.8
    cuts = [0.0]; last_spk = None
    for spk, c in chunks:   # new background on every speaker change, or every ~3.4 s
        a = c[0]["a"] - LEAD
        if a > 0.5 and (spk != last_spk or a - cuts[-1] >= 3.4) and a - cuts[-1] > 1.0: cuts.append(a)
        last_spk = spk
    cuts.append(total)
    random.seed(mod.NAME); order = mod.BG[:]; random.shuffle(order)
    bgs = {}; vig = lux.vignette(); scl = lux.scanlines()
    rng = np.random.default_rng(7)
    grains = [np.asarray(Image.fromarray(rng.normal(0, 14, (H // 2, W // 2)).astype(np.float32)).resize((W, H), Image.NEAREST)) for _ in range(6)]
    work = f"/home/claude/tiktok/work/dlg_{mod.NAME}"; os.makedirs(work, exist_ok=True)
    vid = f"{work}/video.mp4"; tmp = vid[:-4] + ".part.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                           "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(int(round(total * FPS))):
        t = fi / FPS
        si = max(i for i in range(len(cuts) - 1) if cuts[i] <= t)
        path = order[si % len(order)]
        if path not in bgs: bgs[path] = lux.prep_bg(path)
        p = (t - cuts[si]) / max(0.1, cuts[si + 1] - cuts[si])
        g = lux.bg_frame(bgs[path], p, si) * 0.78 * vig * scl + grains[fi % 6]
        if t - cuts[si] < 0.12 and si > 0: g = g * (0.4 + 5 * (t - cuts[si]))
        frame = Image.fromarray(np.stack([np.clip(g, 0, 255).astype(np.uint8)] * 3, -1)).convert("RGBA")
        cur = None
        for spk, c in chunks:
            if c[0]["a"] - LEAD <= t < c[0]["z"]: cur = (spk, c)
        if cur:
            spk, c = cur
            lux.draw_chunk(frame, c, t)
            if spk in ("CUSTOMER", "CLOSER"):
                size, lines = lux.layout(c); lh = int(size * 0.92)
                top = lux.CY - lh * len(lines) // 2
                im = tag_img(spk, lux.WHITE if spk == "CUSTOMER" else lux.GOLD)
                frame.alpha_composite(im, ((W - im.size[0]) // 2, max(40, top - im.size[1] - 30)))
        pr.stdin.write(frame.convert("RGB").tobytes())
    pr.stdin.close(); assert pr.wait() == 0
    os.replace(tmp, vid)
    out = f"/home/claude/tiktok/out/{mod.NAME}_silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", CTA, "-filter_complex", "[0:v][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "8M", "-bufsize", "16M",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    return out

def voice(mod, cmp3, amp3):
    tl = timeline(mod.SEG); work = f"/home/claude/tiktok/work/dlg_{mod.NAME}"; os.makedirs(work, exist_ok=True)
    src = {"c": cmp3, "a": amp3}; inputs, parts = [], []
    for i, (spk, s_, s, e, off, words) in enumerate(tl):
        # each piece: loudness-matched cut, then silence gap
        inputs += ["-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", src[s_]]
        parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-15:TP=-1.5:LRA=11,"
                     f"afade=t=in:d=0.02,afade=t=out:st={max(0, e - s - 0.06):.3f}:d=0.06,apad=pad_dur={GAP:.3f}[p{i}]")
    fc = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(len(tl))) + f"concat=n={len(tl)}:v=0:a=1,atempo={T},loudnorm=I=-14:TP=-1.5:LRA=11[out]"
    wav = f"{work}/voice.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", wav], check=True)
    sil = f"/home/claude/tiktok/out/{mod.NAME}_silent.mp4"; out = f"/home/claude/tiktok/out/{mod.NAME}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sil, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", "-movflags", "+faststart", out], check=True)
    return out

if __name__ == "__main__":
    mod = importlib.import_module(f"dlg_{sys.argv[1]}")
    print(video(mod) if sys.argv[2] == "video" else voice(mod, sys.argv[3], sys.argv[4]))
