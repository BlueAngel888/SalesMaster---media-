"""Luxury-style TikTok clip: black & white luxury photo backgrounds (slow zoom, grain, scanlines)
and huge condensed captions that show exactly the spoken words, word by word, on the voice.
usage: python3 lux.py <clipname> <voice.mp3> <words_module:key> <bg_dir> [tempo]"""
import sys, os, re, random, subprocess, importlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
WHITE = (245, 245, 240); GOLD = (236, 196, 44)
SQUEEZE = 0.74          # horizontal squeeze -> condensed poster look
MAXW = 900              # text column width
CY = 960                # vertical centre of the caption block
LEAD = 0.06             # word appears a hair before it is heard

KEYWORDS = {"MONEY", "RICH", "SELLING", "SELL", "SELLS", "SOLD", "SALES", "SALE", "PRICE", "JOB", "JOBS",
            "CUSTOMER", "CUSTOMERS", "SILENCE", "THINK", "PAID", "HONEST", "QUESTION", "GOOD", "PAYS",
            "NEVER", "ONE", "SHUT", "UP", "WAIT", "THEM", "MINUTE", "YOURSELF", "OPPOSITE", "FIRST"}

_fc = {}
def fnt(size):
    if size not in _fc: _fc[size] = ImageFont.truetype(FONT, size)
    return _fc[size]

def clean(w):
    return re.sub(r"[^A-Za-z0-9'$%&\-]", "", w.replace("—", "")).upper()

def chunk(words, tempo):
    """words: [(text, start, end)] at 1.0x -> chunks of 1-3 words, split at punctuation."""
    out, cur = [], []
    for i, (w, a, b) in enumerate(words):
        cw = clean(w)
        if not cw: continue
        emph = (w.strip('"“”.,!?:;…—').isupper() and len(cw) > 1) or cw in KEYWORDS
        cur.append({"w": cw, "a": a / tempo, "b": b / tempo, "hi": emph})
        if re.search(r"[.?!,:…—]\"?$", w) or len(cur) == 3:
            out.append(cur); cur = []
    if cur: out.append(cur)
    for i, c in enumerate(out):
        nxt = out[i + 1][0]["a"] if i + 1 < len(out) else c[-1]["b"] + 0.9
        c_end = min(nxt, c[-1]["b"] + 0.7)          # leave a short gap in long pauses
        for d in c: d["z"] = c_end
    return out

def layout(ch):
    """Each word on its own line when big; pick the largest size that fits."""
    words = [d["w"] for d in ch]
    for size in (250, 220, 195, 170, 150, 130, 115):
        f = fnt(size)
        widths = [f.getlength(w) * SQUEEZE for w in words]
        # greedy lines
        lines, cur, cw = [], [], 0
        sp = f.getlength(" ") * SQUEEZE
        for i, w in enumerate(widths):
            if cur and cw + sp + w > MAXW: lines.append(cur); cur, cw = [], 0
            cur.append(i); cw += (sp if len(cur) > 1 else 0) + w
        lines.append(cur)
        if max(widths) <= MAXW and len(lines) <= 3: return size, lines
    return 115, [[i] for i in range(len(words))]

_wc = {}
def word_img(text, size, color):
    k = (text, size, color)
    if k not in _wc:
        f = fnt(size); bb = f.getbbox(text)
        w, h = bb[2] + 20, int(size * 1.05) + 20
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((10, 10 - bb[1] + int(size * 0.04)), text, font=f, fill=color + (255,))
        im = im.resize((max(1, int(w * SQUEEZE)), h), Image.LANCZOS)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].point(lambda v: int(v * 0.75)))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        _wc[k] = (im, sh)
    return _wc[k]

def draw_chunk(frame, ch, t):
    size, lines = layout(ch)
    lh = int(size * 0.92)
    y0 = CY - lh * len(lines) // 2
    sp = fnt(size).getlength(" ") * SQUEEZE
    for li, idxs in enumerate(lines):
        imgs = [word_img(ch[i]["w"], size, GOLD if ch[i]["hi"] else WHITE) for i in idxs]
        tot = sum(im.size[0] for im, _ in imgs) + sp * (len(idxs) - 1) - 20 * len(idxs) * SQUEEZE
        x = (W - tot) / 2 - 10
        for i, (im, sh) in zip(idxs, imgs):
            d = ch[i]; age = t - (d["a"] - LEAD)
            if age >= 0:
                p = min(1.0, age / 0.12)
                s = 1.18 - 0.18 * p
                im2, sh2 = im, sh
                if s != 1.0:
                    sz = (max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s)))
                    im2 = im.resize(sz, Image.BILINEAR); sh2 = sh.resize(sz, Image.BILINEAR)
                if p < 1: im2 = im2.copy(); im2.putalpha(im2.split()[3].point(lambda v, p=p: int(v * p)))
                ox = int(x - (im2.size[0] - im.size[0]) / 2); oy = int(y0 + li * lh - (im2.size[1] - im.size[1]) / 2)
                frame.alpha_composite(sh2, (ox + 4, oy + 8)); frame.alpha_composite(im2, (ox, oy))
            x += im.size[0] + sp - 20 * SQUEEZE

# ---------------- background ----------------
BAND_H = 700            # height of the cinematic picture band
BAND_Y = (H - BAND_H) // 2

def prep_bg(path):
    """Wide image -> band (BAND_H tall, with room to zoom) plus a dim blurred fill for the rest of the frame."""
    im = Image.open(path).convert("L")
    tw, th = int(W * 1.12), int(BAND_H * 1.12)
    r = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    l = (im.width - tw) // 2; tp = (im.height - th) // 2
    band = im.crop((l, tp, l + tw, tp + th))
    band = band.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
    band = ImageOps.autocontrast(band, cutoff=1); band = ImageEnhance.Contrast(band).enhance(1.12)
    fill = im.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    return np.asarray(band, dtype=np.float32), np.asarray(fill, dtype=np.float32) * 0.18

def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1.05 - 0.55 * d ** 2, 0.25, 1).astype(np.float32)

def scanlines():
    s = np.ones((H, W), np.float32); s[::4, :] = 0.88; return s

def bg_frame(pair, p, kind):
    """p 0..1 through the shot; slow push-in, alternating pan direction."""
    arr, fill = pair
    z = 1.0 + 0.07 * p
    th, tw = arr.shape
    cw, chh = int(tw / 1.12 / z), int(th / 1.12 / z)
    cx = (tw - cw) / 2 + (1 if kind % 2 else -1) * 0.03 * tw * (p - 0.5)
    cy = (th - chh) / 2
    crop = arr[int(cy):int(cy) + chh, int(cx):int(cx) + cw]
    band = np.asarray(Image.fromarray(crop.astype(np.uint8)).resize((W, BAND_H), Image.BILINEAR), dtype=np.float32)
    out = fill.copy()
    # soft edges on the band
    ramp = np.ones(BAND_H, np.float32); e = 60
    ramp[:e] = np.linspace(0, 1, e); ramp[-e:] = np.linspace(1, 0, e)
    a = ramp[:, None]
    out[BAND_Y:BAND_Y + BAND_H] = band * a + out[BAND_Y:BAND_Y + BAND_H] * (1 - a)
    return out

def render(clip, mp3, words, bg_paths, tempo=1.25, out=None):
    work = f"/home/claude/tiktok/work/lux_{clip}"; os.makedirs(work, exist_ok=True)
    chunks = chunk(words, tempo)
    voice_end = words[-1][2] / tempo
    total = voice_end + 0.8
    # one background per ~3.5 s, cut on a chunk boundary
    cuts = [0.0]
    for c in chunks:
        if c[0]["a"] - cuts[-1] >= 3.4: cuts.append(c[0]["a"] - LEAD)
    cuts.append(total)
    random.seed(clip); order = bg_paths[:]; random.shuffle(order)
    bgs = {}
    vig = vignette(); scl = scanlines()
    rng = np.random.default_rng(7); grains = [rng.normal(0, 14, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
    grains = [np.asarray(Image.fromarray(g).resize((W, H), Image.NEAREST)) for g in grains]
    vid = f"{work}/video.mp4"; tmp = vid[:-4] + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(total * FPS)); ci = 0
    for fi in range(n):
        t = fi / FPS
        si = max(i for i in range(len(cuts) - 1) if cuts[i] <= t)
        path = order[si % len(order)]
        if path not in bgs: bgs[path] = prep_bg(path)
        p = (t - cuts[si]) / max(0.1, cuts[si + 1] - cuts[si])
        g = bg_frame(bgs[path], p, si)
        g = g * 0.78 * vig * scl + grains[fi % 6]
        if t - cuts[si] < 0.12 and si > 0: g = g * (0.4 + 5 * (t - cuts[si]))   # quick dip on cut
        g = np.clip(g, 0, 255).astype(np.uint8)
        frame = Image.fromarray(np.stack([g, g, g], -1)).convert("RGBA")
        cur = None
        for c in chunks:
            if c[0]["a"] - LEAD <= t < c[0]["z"]: cur = c
        if cur: draw_chunk(frame, cur, t)
        pr.stdin.write(frame.convert("RGB").tobytes())
    pr.stdin.close()
    if pr.wait() != 0: raise SystemExit("ffmpeg failed")
    os.replace(tmp, vid)
    if mp3 is None: return vid
    wav = f"{work}/voice.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", f"atempo={tempo},loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", wav], check=True)
    out = out or f"/home/claude/tiktok/out/{clip}_lux.mp4"; tmp = out[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", tmp], check=True)
    os.replace(tmp, out); return out

def preview(words, bg_paths, times, path, tempo=1.25):
    """Still frames at given times (for checking layout)."""
    chunks = chunk(words, tempo); vig = vignette(); scl = scanlines()
    ims = []
    for k, t in enumerate(times):
        arr = prep_bg(bg_paths[k % len(bg_paths)])
        g = np.clip(bg_frame(arr, 0.5, k) * 0.78 * vig * scl, 0, 255).astype(np.uint8)
        fr = Image.fromarray(np.stack([g, g, g], -1)).convert("RGBA")
        cur = None
        for c in chunks:
            if c[0]["a"] - LEAD <= t < c[0]["z"]: cur = c
        if cur: draw_chunk(fr, cur, t + 0.5)
        ims.append(fr.convert("RGB").resize((270, 480)))
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, im in enumerate(ims): sheet.paste(im, (i * 270, 0))
    sheet.save(path)

if __name__ == "__main__":
    clip, mp3, wk, bgdir = sys.argv[1:5]
    mod, key = wk.split(":"); words = importlib.import_module(mod).W[key]
    bgs = sorted(os.path.join(bgdir, f) for f in os.listdir(bgdir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    tempo = float(sys.argv[5]) if len(sys.argv) > 5 else 1.25
    print(render(clip, mp3, words, bgs, tempo))
