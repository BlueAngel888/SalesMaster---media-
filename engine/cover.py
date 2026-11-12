"""Built-in cover: the first ~1.1 s of every clip shows a cover card over the video, so every platform
(TikTok, Instagram, YouTube Shorts) uses it as the thumbnail without anyone picking a frame.

  python3 cover.py IN.mp4 OUT.mp4 "TITLE TEXT" [KICKER]
      TITLE  = the clip's hook, 2-7 words, UPPERCASE works best ("SAY THE PRICE... THEN STOP")
      KICKER = small gold line above the title. Default "SALES MASTER". Use "WHAT IF..." for What If clips.
Voice is untouched (audio is stream-copied); the card fades out over 0.25 s while the clip keeps playing.
"""
import sys, subprocess, textwrap, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "/usr/share/fonts/opentype/inter"
GOLD = (236, 196, 44)
W, H = 1080, 1920


def font(name, size):
    for n in (name, "Inter-Black.otf"):
        p = os.path.join(F, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(title, kicker, out_png, bg_frame=None):
    # opaque card: the clip's first frame, heavily blurred and darkened (hides the clip's own captions/CTA)
    if bg_frame and os.path.exists(bg_frame):
        base = Image.open(bg_frame).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(28))
        base = Image.blend(base, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)
        img = base.convert("RGBA")
    else:
        img = Image.new("RGBA", (W, H), (8, 8, 8, 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([(140, 560), (940, 1360)], fill=GOLD + (40,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    d = ImageDraw.Draw(img)
    title = title.upper()
    size = 150
    while size > 70:
        ft = font("InterDisplay-Black.otf", size)
        lines = wrap(d, title, ft, W - 140)
        if len(lines) <= 4:
            break
        size -= 8
    lh = int(size * 1.02)
    whatif = kicker.upper().startswith("WHAT IF")
    fk = font("InterDisplay-Black.otf", 96 if whatif else 54)
    block = 80 + len(lines) * lh
    y = (H - block) // 2 - 60
    # kicker in gold with letter spacing
    k = kicker.upper() if whatif else " ".join(kicker.upper())
    kw = d.textlength(k, font=fk)
    if whatif:
        y -= 60
    d.text(((W - kw) / 2, y), k, font=fk, fill=GOLD + (255,))
    y += 160 if whatif else 110
    # gold bar
    d.rectangle([(W / 2 - 70, y - 30), (W / 2 + 70, y - 22)], fill=GOLD + (255,))
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=ft)
        x = (W - tw) / 2
        # last line gold, others white
        col = GOLD + (255,) if (i == len(lines) - 1 and len(lines) > 1) else (255, 255, 255, 255)
        # shadow
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, y + 6), ln, font=ft, fill=(0, 0, 0, 200))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d = ImageDraw.Draw(img)
        d.text((x, y), ln, font=ft, fill=col)
        y += lh
    img.save(out_png)
    return out_png


def apply(inp, out, title, kicker="SALES MASTER", hold=0.85, fade=0.25):
    png = out + ".cover.png"
    frame = out + ".f0.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.6", "-i", inp, "-frames:v", "1", frame], check=True)
    card(title, kicker, png, frame)
    os.remove(frame)
    end = hold + fade
    flt = (f"[1:v]format=rgba,fade=t=out:st={hold}:d={fade}:alpha=1,setpts=PTS-STARTPTS[c];"
           f"[0:v][c]overlay=0:0:enable='lte(t,{end})'[v]")
    tmp = out + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", inp, "-loop", "1", "-t", str(end + 0.1), "-i", png,
                    "-filter_complex", flt, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out)
    os.remove(png)
    return out


if __name__ == "__main__":
    a = sys.argv
    print(apply(a[1], a[2], a[3], a[4] if len(a) > 4 else "SALES MASTER"))
