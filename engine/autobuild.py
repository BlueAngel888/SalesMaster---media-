"""Helpers for the daily automated run (see AUTOMATION.md).

  python3 autobuild.py solo  DAY CLIP words.json voice.mp3 OUTNAME
      words.json = the `words` list from an ElevenLabs transcription (tags like [calm] are dropped)
  python3 autobuild.py dialog DAY CLIP spec.json customer.mp3 closer.mp3 OUTNAME
      spec.json = {"lines": [["CUSTOMER","text"],["CLOSER","text"],...,["LESSON","text"]],
                   "customer_words": [...], "closer_words": [...], "keywords": ["OFFER",...]}
      Each speaker's lines were generated in ONE take, in script order; words are assigned to lines by word count.
Outputs land in /home/claude/tiktok/out/dayNN/OUTNAME.mp4
"""
import sys, os, json, re, glob, types, importlib
sys.path.insert(0, "/home/claude/tiktok")

BG_SETS = ["bg_lux:0:12", "bg_lux:12:24", "bg_day03:0:8", "bg_day04:0:8"]

def clean(words):
    return [(w["text"], float(w["start"]), float(w["end"])) for w in words
            if w.get("type", "word") == "word" and not w["text"].startswith("[")]

def bg_for(clip_no):
    """New background set every 3 clips, rotating through the existing sets (no new images after clip 12)."""
    sets = [s for s in BG_SETS if glob.glob(f"/home/claude/tiktok/{s.split(':')[0]}/*.jpg")]
    name, a, b = sets[((clip_no - 1) // 3) % len(sets)].split(":")
    return sorted(glob.glob(f"/home/claude/tiktok/{name}/*.jpg"))[int(a):int(b)]

def solo(day, clip, words_json, mp3, outname):
    import lux, subprocess, daily
    words = clean(json.load(open(words_json)))
    n = int(re.sub(r"\D", "", clip))
    out_dir = f"/home/claude/tiktok/out/day{int(day):02d}"; os.makedirs(out_dir, exist_ok=True)
    silent = lux.render(clip, None, words, bg_for(n), tempo=1.25, out=f"{out_dir}/{clip}_silent_raw.mp4")
    cta = f"{out_dir}/{clip}_silent.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", "/home/claude/tiktok/cta_gold.png",
                    "-filter_complex", "[0:v][1:v]overlay=0:0", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", cta], check=True)
    wav = f"{out_dir}/{clip}_voice.wav"; out = f"{out_dir}/{outname}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "atempo=1.25,loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", wav], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cta, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-shortest", "-movflags", "+faststart", out], check=True)
    return out

def dialog(day, clip, spec_json, cmp3, amp3, outname):
    import lux, dialogue, daily
    spec = json.load(open(spec_json))
    lux.KEYWORDS |= set(k.upper() for k in spec.get("keywords", []))
    pools = {"c": clean(spec["customer_words"]), "a": clean(spec["closer_words"])}
    pos = {"c": 0, "a": 0}; seg = []
    for spk, text in spec["lines"]:
        src = "c" if spk == "CUSTOMER" else "a"
        n = len(re.sub(r"\[[^\]]*\]", "", text).split())
        ws = pools[src][pos[src]:pos[src] + n]; pos[src] += n
        if ws: seg.append((spk, src, ws))
    for k in pools:   # leftover words (transcription split differently) go to the speaker's last segment
        if pos[k] < len(pools[k]):
            last = max(i for i, s in enumerate(seg) if s[1] == k)
            seg[last] = (seg[last][0], k, seg[last][2] + pools[k][pos[k]:])
    n = int(re.sub(r"\D", "", clip))
    mod = types.SimpleNamespace(NAME=f"day{int(day):02d}_{outname}", BG=bg_for(n), SEG=seg)
    dialogue.video(mod); out = dialogue.voice(mod, cmp3, amp3)
    out_dir = f"/home/claude/tiktok/out/day{int(day):02d}"; os.makedirs(out_dir, exist_ok=True)
    final = f"{out_dir}/{outname}.mp4"; os.replace(out, final); return final

def add_cover(path, title, kicker):
    """Built-in cover on the first ~1.1 s (see cover.py). Every clip gets one."""
    import cover
    return cover.apply(path, path, title, kicker or "SALES MASTER")

if __name__ == "__main__":
    # optional last args on every command: --cover "HOOK TITLE" [--kicker "WHAT IF..."]
    a = sys.argv
    title = kicker = None
    if "--cover" in a:
        i = a.index("--cover"); title = a[i + 1]; del a[i:i + 2]
    if "--kicker" in a:
        i = a.index("--kicker"); kicker = a[i + 1]; del a[i:i + 2]
    if a[1] == "solo": out = solo(a[2], a[3], a[4], a[5], a[6])
    elif a[1] == "dialog": out = dialog(a[2], a[3], a[4], a[5], a[6], a[7])
    if title: add_cover(out, title, kicker)
    print(out)
