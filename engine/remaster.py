"""Re-make already-posted clips with the FREE SALES TEST call to action (no price)."""
import subprocess, os, sys
sys.path.insert(0, "/home/claude/tiktok")
O = "/home/claude/tiktok/out"; R = "/home/claude/salesmaster---media-/clips"; M = f"{O}/remaster"
CTA = "/home/claude/tiktok/cta_gold.png"; COVER = "/home/claude/tiktok/cta_cover_free.png"
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p"]
def run(a): subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)

def mux(video, audio_src, out):
    run(["-i", video, "-i", audio_src, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out])

def rerender(day, clip, posted, name):          # old layout: render again with the new layout + new CTA
    import daily
    sil = daily.render(day, clip); mux(sil, posted, f"{M}/{name}.mp4")

def overlay(raw, posted, name):                 # raw = render without CTA (new layout)
    tmp = f"{M}/{name}_v.mp4"
    run(["-i", raw, "-i", CTA, "-filter_complex", "[0:v][1:v]overlay=0:0"] + ENC + [tmp])
    mux(tmp, posted, f"{M}/{name}.mp4"); os.remove(tmp)

def cover(posted, name):                        # new layout, CTA burned in: paint over it
    run(["-i", posted, "-i", COVER, "-filter_complex", "[0:v][1:v]overlay=0:0"] + ENC + ["-c:a", "copy", "-movflags", "+faststart", f"{M}/{name}.mp4"])

jobs = sys.argv[1:] or ["all"]
if "all" in jobs or "old" in jobs:
    for c, p, n in [("clip1", f"{O}/day01/Day1_clip1_gold.mp4", "Day1_clip1_FREE"), ("clip2", f"{O}/day01/Day1_clip2_gold.mp4", "Day1_clip2_FREE"),
                    ("clip3", f"{O}/day01/Day1_clip3_gold.mp4", "Day1_clip3_FREE")]:
        rerender("day01", c, p, n); print(n, flush=True)
    for c, p, n in [("clip4", f"{O}/day02/Day2_clip4_price.mp4", "Day2_clip4_price_FREE"), ("clip5", f"{O}/day02/Day2_clip5_result.mp4", "Day2_clip5_result_FREE"),
                    ("clip6", f"{O}/day02/Day2_clip6_close.mp4", "Day2_clip6_close_FREE")]:
        rerender("day02", c, p, n); print(n, flush=True)
    rerender("day03", "clip7", f"{O}/day03/Day3_clip7_expensive.mp4", "Day3_clip7_expensive_FREE"); print("clip7", flush=True)
if "all" in jobs or "new" in jobs:
    overlay("/home/claude/tiktok/work/lux_day03_clip8/video.mp4", f"{O}/day03/Day3_clip8_firstsale_v2.mp4", "Day3_clip8_firstsale_FREE")
    overlay("/home/claude/tiktok/work/lux_day03_clip9/video.mp4", f"{O}/day03/Day3_clip9_risk_v2.mp4", "Day3_clip9_risk_FREE")
    overlay("/home/claude/tiktok/work/dlg_Dialog_test_offerloop/video.mp4", f"{O}/Dialog_test_offerloop_v3.mp4", "Dialog_offerloop_FREE")
    for f in ["Day4_clip10_silence", "Day4_clip11_sellingishelping", "Day4_clip12_thinkaboutit", "Day4_clip13_status",
              "Day5_clip14_partner", "Day5_clip15_tonality", "Day5_clip16_justtheprice", "Day5_clip17_reps"]:
        cover(f"{R}/{f}.mp4", f + "_FREE"); print(f, flush=True)
print("DONE")
