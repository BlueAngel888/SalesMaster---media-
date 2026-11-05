"""Render a day's clips silently (lux style + gold CTA). Voice gets added later with addvoice().
usage: python3 daily.py render dayNN clipA clipB ...   |   python3 daily.py voice dayNN clipX voice.mp3"""
import sys, os, glob, subprocess, importlib
sys.path.insert(0, "/home/claude/tiktok")
import lux
lux.KEYWORDS |= {"PRICE", "EXPENSIVE", "THEMSELVES", "RESULT", "PRODUCTS", "WHICH", "IF", "YES", "CLOSE", "ALTERNATIVE", "CANDLE", "FIFTY"}
BG = sorted(glob.glob("/home/claude/tiktok/bg_lux/*.jpg"))
CTA = "/home/claude/tiktok/cta_gold.png"

def render(day, clip):
    d = f"/home/claude/tiktok/bg_{day}"
    bgs = sorted(glob.glob(d + "/*.jpg")) if os.path.isdir(d) else BG
    W = importlib.import_module(f"words_{day}").W[clip]
    out = f"/home/claude/tiktok/out/{day}"; os.makedirs(out, exist_ok=True)
    raw = lux.render(f"{day}_{clip}", None, W, bgs, 1.25)
    final = f"{out}/{clip}_silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-i", CTA, "-filter_complex", "[0:v][1:v]overlay=0:0",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "8M", "-bufsize", "16M",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", final], check=True)
    return final

def addvoice(day, clip, mp3, name):
    out = f"/home/claude/tiktok/out/{day}"; sil = f"{out}/{clip}_silent.mp4"; wav = f"{out}/{clip}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "atempo=1.25,loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", wav], check=True)
    final = f"{out}/{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sil, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", "-movflags", "+faststart", final], check=True)
    return final

if __name__ == "__main__":
    if sys.argv[1] == "render":
        for c in sys.argv[3:]: print(render(sys.argv[2], c))
    else:
        print(addvoice(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
