"""Pinned 'what you get' clip: luxury B&W shots + colour product shots, words exactly on the voice."""
import sys, os, subprocess
sys.path.insert(0, "/home/claude/tiktok")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import lux
from lux import W, H, FPS, LEAD
from words_day01 import W as WORDS

lux.KEYWORDS |= {"B2C", "B2B", "PRODUCTS", "SERVICES", "COURSES", "SEVENTEEN", "MILLION", "DOLLARS",
                 "TWENTY-NINE", "FOREVER", "SIXTEEN", "HUNDRED", "FORTY", "CLOSING", "APP", "WORKBOOK", "SYSTEM"}
T = 1.25
B = "/home/claude/tiktok/bg_lux/"; P = "/home/claude/tiktok/prod/"
# (start in original-speed seconds, image, mode)
SHOTS = [(0.0, B + "lux_02.jpg", "lux"), (3.76, P + "book.png", "prod"), (8.32, P + "situations.png", "prod"),
         (13.28, P + "lesson.png", "prod"), (17.76, P + "worksheets.png", "prod"), (21.28, P + "app.png", "prod"),
         (24.72, B + "lux_18.jpg", "lux"), (28.32, B + "lux_07.jpg", "lux"), (31.2, B + "lux_05.jpg", "lux"),
         (33.44, B + "lux_03.jpg", "lux"), (37.2, B + "lux_22.jpg", "lux"), (42.32, P + "book.png", "prod"),
         (45.92, B + "lux_09.jpg", "lux")]

def layout_limited(maxsize):
    orig = lux.layout
    def f(ch):
        words = [d["w"] for d in ch]
        for size in [s for s in (250, 220, 195, 170, 150, 130, 115, 100) if s <= maxsize]:
            fn = lux.fnt(size); widths = [fn.getlength(w) * lux.SQUEEZE for w in words]
            sp = fn.getlength(" ") * lux.SQUEEZE; lines, cur, cw = [], [], 0
            for i, w in enumerate(widths):
                if cur and cw + sp + w > lux.MAXW: lines.append(cur); cur, cw = [], 0
                cur.append(i); cw += (sp if len(cur) > 1 else 0) + w
            lines.append(cur)
            if max(widths) <= lux.MAXW and len(lines) <= 3: return size, lines
        return 100, [[i] for i in range(len(words))]
    return f

def prod_panel(path):
    im = Image.open(path).convert("RGB")
    maxw, maxh = 960, 700
    r = min(maxw / im.width, maxh / im.height); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    return im

def main(mp3, out):
    words = WORDS["pinned"]; chunks = lux.chunk(words, T)
    total = words[-1][2] / T + 0.8
    shots = [(s / T - (LEAD if i else 0), p, m) for i, (s, p, m) in enumerate(SHOTS)]
    vig = lux.vignette(); scl = lux.scanlines()
    rng = np.random.default_rng(7)
    grains = [np.asarray(Image.fromarray(rng.normal(0, 14, (H // 2, W // 2)).astype(np.float32)).resize((W, H), Image.NEAREST)) for _ in range(6)]
    cache = {}
    lux_layout = lux.layout; prod_layout = layout_limited(150)
    work = "/home/claude/tiktok/work/pinned"; os.makedirs(work, exist_ok=True)
    vid = f"{work}/video.mp4"; tmp = vid[:-4] + ".part.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
                           "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fi in range(int(round(total * FPS))):
        t = fi / FPS
        si = max(i for i in range(len(shots)) if shots[i][0] <= t)
        s0 = shots[si][0]; s1 = shots[si + 1][0] if si + 1 < len(shots) else total
        p = (t - s0) / max(0.1, s1 - s0); path, mode = shots[si][1], shots[si][2]
        dip = 1.0 if (t - s0 >= 0.12 or si == 0) else 0.4 + 5 * (t - s0)
        if mode == "lux":
            if path not in cache: cache[path] = lux.prep_bg(path)
            g = lux.bg_frame(cache[path], p, si) * 0.78 * vig * scl + grains[fi % 6]
            g = np.clip(g * dip, 0, 255).astype(np.uint8)
            frame = Image.fromarray(np.stack([g, g, g], -1)).convert("RGBA")
            lux.layout = lux_layout; lux.CY = 960
        else:
            if path not in cache: cache[path] = prod_panel(path)
            pan = cache[path]; z = 1.0 + 0.04 * p
            pz = pan.resize((int(pan.width * z), int(pan.height * z)), Image.BILINEAR)
            base = np.full((H, W), 14, np.float32) + grains[fi % 6] * 0.6
            base = np.clip(base * vig, 0, 255).astype(np.uint8)
            frame = Image.fromarray(np.stack([base] * 3, -1)).convert("RGBA")
            x = (W - pz.width) // 2; y = 600 - pz.height // 2
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([x + 10, y + 24, x + pz.width + 10, y + pz.height + 24], fill=(0, 0, 0, 200))
            frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(24)))
            frame.paste(pz, (x, y))
            if dip < 1:
                frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, dip)
            lux.layout = prod_layout; lux.CY = 1170
        cur = None
        for c in chunks:
            if c[0]["a"] - LEAD <= t < c[0]["z"]: cur = c
        if cur: lux.draw_chunk(frame, cur, t)
        pr.stdin.write(frame.convert("RGB").tobytes())
    pr.stdin.close(); assert pr.wait() == 0
    os.replace(tmp, vid)
    # gold call-to-action on top, then voice
    withcta = f"{work}/cta.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", "/home/claude/tiktok/cta_gold.png",
                    "-filter_complex", "[0:v][1:v]overlay=0:0", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", withcta], check=True)
    if not mp3: os.replace(withcta, out); return out
    wav = f"{work}/voice.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", f"atempo={T},loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", wav], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", withcta, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", "-movflags", "+faststart", out], check=True)
    return out

if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else None,
               sys.argv[2] if len(sys.argv) > 2 else "/home/claude/tiktok/out/pinned_silent.mp4"))
