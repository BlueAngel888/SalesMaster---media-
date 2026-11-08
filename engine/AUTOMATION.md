# Daily automated run – Sales Master clips

Goal of each run: make **4 clips** (2 dialogue + 2 solo), publish them through Buffer at the day's best
times (America/New_York), and report to the owner in Romanian. Read `STYLE_RULES.md` first; it wins over
anything here. Never promise income. Never use the names eduKiwi, Doru, Pera, Hobby 2 Profit, H2P.

## 0. Setup (fresh container)
```bash
R=/home/claude/salesmaster---media-        # clone it if missing: git clone https://github.com/BlueAngel888/SalesMaster---media- $R
mkdir -p /home/claude/tiktok/{out,work,voices}
cp -r $R/engine/* /home/claude/tiktok/
ls /usr/share/fonts/opentype/inter/InterDisplay-Black.otf   # font must exist (apt-get install fonts-inter if not)
```
Read `engine/progress.json` (day number, next clip number, used topics).

## 1. Pick topics
If `engine/scripts/day{NN}_pending.json` exists for the current day (left by a blocked run), reuse those scripts
instead of writing new ones, then delete the file in the same commit as the finished clips.
From `engine/topics.json` take the first 2 unused `dialog` and first 2 unused `solo` topics. If fewer remain,
write new ones in the same style from the 24 lesson titles (lessons 1–24, see topics) and append them.

## 2. Write scripts (English)
- Spoken length 30–38 s before the 1.25x speed-up (≈ 80–95 words). First line = hook.
- Use ElevenLabs v4 tags sparingly: [confident] [calm] [serious] [whispers] [laughs] [hesitant] [unsure] [excited].
- **Solo** (voice Adam): hook → 3–4 short beats → end with "Follow. One sales skill every day." (or, every
  other clip, "The full system is inside Sales Master. Link in bio.").
- **Dialogue**: 4–6 short lines alternating CUSTOMER / CLOSER, then one LESSON paragraph spoken by Adam to the
  camera ending "It's inside Sales Master. Link in bio." Customer = Jessica.
  Generate ONE take per speaker: all CUSTOMER lines in script order separated by blank lines (one call), and
  all CLOSER + LESSON lines in order separated by blank lines (one call).

## 3. Voices (ElevenLabs connector)
- `creative_generate_speech`, model `eleven_v4`, `generations_count: 1`, flow `24TmATOBWucdT7nbRKD0`.
  Adam `eGSd0uV8dNQnZuEEX9lu`, Jessica `cgSgspJ2msm6clMCkdW9`.
- `creative_transcribe_audio` (model eleven_scribe_v1, connect_from = the TTS node id) → word timings.
- Poll `creative_get_flow_run_status` until done. Take each audio `content_url` and the transcript `words`.
- Download with curl to `/home/claude/tiktok/voices/Day{N}_clip{NN}_{ADAM|JESSICA}.mp3`.
  **If the download is refused (403 / connect_rejected): do not try other routes.** Send the owner the links with
  these exact file names (SendUserMessage), ask him to save them in "Claude Folder", and stop after step 4 with
  silent renders.

## 4. Render
Save transcript words as JSON, then:
```bash
cd /home/claude/tiktok
python3 autobuild.py solo   N clipNN words.json voice.mp3 DayN_clipNN_<topic>
python3 autobuild.py dialog N clipNN spec.json customer.mp3 closer.mp3 DayN_clipNN_<topic>
# spec.json = {"lines": [["CUSTOMER","..."],["CLOSER","..."],...,["LESSON","..."]],
#              "customer_words": [...], "closer_words": [...], "keywords": ["OFFER", ...]}
```
Backgrounds rotate automatically (new set every 3 clips). If `bg_day04_generated` is false, first generate 8
black-and-white luxury images (Rolls-Royce, Lamborghini, Rolex, Richard Mille, villa with pool, private jet,
yacht, Patek Philippe) with `creative_generate_image`, model seedream-5-lite, 1 variation each, 9:16, download
them to `/home/claude/tiktok/bg_day04/d4_01.jpg…d4_08.jpg`, commit them to `engine/bg_day04/`, set the flag.
This is the LAST image generation ever.
Check one frame per clip (ffmpeg -ss 5 … -frames:v 1, then Read the jpg): text readable, not under the CTA.

## 5. Publish files
Copy finals to `$R/clips/`, commit + push (commit trailers from the session's attribution reminder).
Public URL: `https://raw.githubusercontent.com/BlueAngel888/SalesMaster---media-/main/clips/<file>.mp4`
(verify with `gh api repos/BlueAngel888/SalesMaster---media-/contents/clips/<file>.mp4 --jq .size`).

## 6. Schedule in Buffer
Org `6aebe3cacd3a1b8f70a4d89b`. TikTok `6aebe4bee29c69a17167ef79`, YouTube `6aebe43fe29c69a17167e720`,
Instagram (business) `6aed79c1e29c69a1717da5ff`. `mode: customScheduled`, `schedulingType:
automatic`, `isAiGenerated: true`. YouTube: `categoryId "27"`, privacy public, madeForKids false, title ≤70
chars. Instagram: type reel, shouldShareToFeed true, isAiGenerated true. Skip any slot already in the past; use the
next free slot later that day.

Slots (ET), dialogue clips get the 1st and 3rd slot:

| Day | TikTok | YouTube Shorts |
|---|---|---|
| Mon | 08:07 · 11:13 · 13:07 · 21:47 | 11:23 · 12:37 · 18:23 · 20:37 |
| Tue | 06:07 · 07:13 · 20:47 · 22:07 | 11:07 · 11:52 · 19:13 · 20:37 |
| Wed | 06:07 · 20:13 · 21:07 · 22:07 | 12:07 · 13:37 · 19:13 · 20:37 |
| Thu | 06:07 · 13:07 · 19:47 · 22:07 | 12:13 · 14:07 · 18:23 · 19:37 |
| Fri | 18:07 · 19:13 · 20:07 · 22:07 | 11:07 · 11:47 · 12:23 · 12:52 |
| Sat | 15:07 · 16:07 · 17:07 · 20:47 | 14:07 · 15:13 · 16:07 · 16:52 |
| Sun | 09:07 · 12:07 · 13:07 · 19:47 | 17:07 · 18:13 · 19:07 · 19:52 |

Instagram Reels (Buffer 2026 data, ET):
Mon 18:07 · 19:07 · 20:07 · 21:13 — Tue 15:07 · 17:07 · 19:07 · 20:13 — Wed 08:07 · 12:07 · 18:07 · 20:07 —
Thu 07:07 · 08:07 · 09:07 · 19:13 — Fri 06:07 · 20:13 · 21:07 · 22:07 — Sat 20:07 · 21:07 · 22:07 · 22:43 —
Sun 20:07 · 21:07 · 22:07 · 22:43

**Buffer free plan = max 10 scheduled posts at once.** 4 clips x 3 platforms = 12. Schedule in this order until
Buffer refuses: all TikTok, then all Instagram, then YouTube. For anything that did not fit, put the file link +
captions in the final message so the owner can post it himself (or it gets picked up on the next run if there
is room). Never delete or change posts the owner created.

Captions per STYLE_RULES (TikTok max 5 hashtags; YouTube 3 hashtags in description + title; Instagram max 5).
Also write `clips/DayN_captions.txt` with the TikTok / YouTube (title, description, tags) / Instagram packs.

## 7. Wrap up
Update `progress.json` (next_day+1, next_clip+4, used ids), commit + push.
If the owner's computer is linked, send each clip with SendUserFile and copy clips + captions into
`/Users/Florin/Desktop/Claude Folder` with device_commit_files.
Final SendUserMessage (Romanian): which 4 clips, topics, posting times, anything that failed.
