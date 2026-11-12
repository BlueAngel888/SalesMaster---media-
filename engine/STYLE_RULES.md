# Sales Master clip rules (agreed with the owner, keep for every future day)

- 3 clips per day, English, voice "Adam - Dominant, Firm" (eGSd0uV8dNQnZuEEX9lu), eleven_v4, 1 take, sped up 1.25x.
- On-screen text = exactly the spoken words, word by word, from ElevenLabs word timings. No extra captions.
- Gold 3D CTA overlay at the bottom of every clip: engine/cta_gold.png = "FREE SALES TEST · LINK IN BIO!" (owner, 9 Nov 2026).
  NEVER show or say a price in clips, captions or titles any more. The clip sends people to the free test (funnel), not to the checkout.
- NO music in the delivered clips (owner adds trending sounds inside TikTok).
- NO automatic posting via Buffer. Deliver clips in chat; owner posts to TikTok, then Instagram and YouTube.
- Under every delivered clip, a full pack for all 3 platforms (also saved as DayN_captions.txt in the owner's Mac "Claude Folder"):
  - TikTok: keyword-first caption (searchable phrase in the first line) + MAX 5 hashtags (TikTok cap since Aug 2025).
  - YouTube Shorts: viral title <=70 chars, keyword in the first 40, no hashtags in the title; description with
    keyword hook line + link line + 3 hashtags (the first 3 show above the title); tags field <=500 chars.
  - Instagram Reels: keyword-first caption (first 125 chars visible) + MAX 5 hashtags (more = reach penalty).
  - Hashtag mix: 1 broad (#sales/#business), 2 niche (#salestips #closing...), 1 audience (#entrepreneur/#sidehustle),
    1 discovery (#learnontiktok on TT, #shorts on YT). Keep #salesmaster as the branded one where room allows.
  - Viral hooks: curiosity / "stop doing X" / mistake framing / numbers. Never promise income.
  - Re-check platform hashtag rules with a web search before changing this format.
- Backgrounds: a NEW set every 3 clips (every day), black & white, famous luxury brands:
  Rolls-Royce, Lamborghini, Ferrari, Bentley, Rolex, Richard Mille, Patek Philippe, villas with pools,
  private jets, yachts. Model: bytedance-seedream-5-lite (~$0.04/image), ~8 images per day, 16:9.
- Background budget: new sets only until clip 12 (sets: bg_lux for clips 1-6, bg_day03 for clips 7-9,
  bg_day04 for clips 10-12). From clip 13 on, generate NOTHING new: rotate the existing sets in order,
  one set per day (bg_lux first half, bg_lux second half, bg_day03, bg_day04, then repeat).
- Never promise income. Never use the names eduKiwi, Doru, Pera, Hobby 2 Profit, H2P.
- Beacons store: https://beacons.ai/sales_master (course price: $199 since 9 Nov 2026). Instagram: salesmaster898. TikTok: salsemaster.
- File names must be specific and easy to recognise (owner request):
  - delivered clips: DayN_clipNN_<topic>.mp4, captions: DayN_captions.txt
  - voice downloads: in the message, give each link with the name to save it as, e.g. Day4_clip10_ADAM.mp3 /
    Day4_clip10_JESSICA.mp3 (ElevenLabs always names downloads content.mp3).
- Dialogue format (two voices) available: engine/dialogue.py + dlg_<name>.py. Customer = Jessica
  (cgSgspJ2msm6clMCkdW9, white text, CUSTOMER tag), closer = Adam (gold text, CLOSER tag), lesson to camera at the end.
- Layout: text centre CY=720 (owner: "a bit higher") and gold CTA at y 1167-1379 (moved up 250 px) so nothing sits under TikTok's bottom caption/username UI.
- Posting (owner, 6 Nov 2026): post via Buffer (TikTok + YouTube; Instagram when connected), 3 clips/day, at the
  most-viewed times, audience US -> America/New_York. Use a few minutes off the hour.
  TikTok (Buffer 2026, 7M posts): Mon 1pm/11am/8am · Tue 6am/10pm/7am · Wed 10pm/6am/9pm · Thu 1pm/10pm/6am ·
  Fri 6pm/10pm/8pm · Sat 5pm/4pm/3pm · Sun 9am/1pm/12pm.
  YouTube Shorts (Hopper 2026): Mon 11am-1pm & 6-9pm · Tue 11am-12pm · Wed 12-2pm & 7-9pm · Thu 12-3pm & 6-8pm ·
  Fri 11am-1pm · Sat 2-5pm · Sun 5-8pm.
  Clips are published from public raw URLs in clips/ of this repo. Buffer free plan: max 10 scheduled posts at once.
- Owner (10 Nov 2026): do platform/repo/store settings yourself whenever a tool allows it (e.g. the built-in browser when he is
  signed in there); only ask him for steps nothing available can do (passwords, admin-only GitHub settings).
- Free test page (live since 10 Nov 2026): https://blueangel888.github.io/SalesMaster---media-/ (docs/ on main).


## Owner rules from 12 Nov
- Max 4 clips per day in total, per platform: 2 dialogue + 1 solo + 1 WHAT IF. No reposts of old clips.
- Every clip has a built-in cover on its first ~1.1 s (engine/cover.py): blurred clip frame, gold kicker,
  big white hook with the last line in gold. Kicker "SALES MASTER", or "WHAT IF..." on WHAT IF clips.
- WHAT IF clips: open with "What if...", cover kicker WHAT IF. Topics: course lessons + money themes (making money,
  side income, selling houses / real estate / cars, raises). Core message: everything is a sale.
  Never promise income, never say easy/fast money; results depend on the work.

## Persuasion playbook (owner, 12 Nov): every script and cover follows this
Structure of every clip (30-38 s spoken, before 1.25x):
1. **HOOK, 0-2 s, money pain.** Name a money frustration the viewer already feels, in "you" language, concrete and
   relatable, never shaming: "Paycheck gone by the 20th?", "Working 50 hours and still broke?", "Someone with less
   talent than you just closed a deal you didn't." The cover text = the hook (works muted).
2. **AGITATE, 2-8 s.** Make the cost of doing nothing felt (loss aversion): "Every month you don't learn this, someone
   else takes the deal." One sentence, then a short pause.
3. **REFRAME, 8-15 s.** The real problem isn't the job or the economy, it's the missing skill: "The money goes to
   whoever can sell." Everything is a sale: houses, cars, insurance, services, your raise, your rent.
4. **SOLUTION, 15-28 s.** One concrete technique from the course (the lesson of the topic): the exact words to say.
   Give real value; the viewer must learn something usable today.
5. **BRIDGE + CTA, last 4-6 s.** Future pacing + low-friction step: "Picture your next client saying yes... Take the
   free sales test. Link in bio." (Never the price.)

Persuasion tools to use (honest, no tricks):
- Open loop in the first 3 s, closed near the end ("...and the third one is the one that closes.").
- Pattern interrupt: an unexpected line or contrast ("Real estate agents don't sell houses.").
- Specific details beat vague claims (numbers of steps, calls, seconds of silence; never income numbers).
- Loss aversion > gain: "what you're leaving on the table", "the deal someone else takes".
- Identity: "Closers don't...", "Amateurs ask if, pros ask which."
- Mild presupposition / embedded direction: "When you take the test, watch question 5."
- Social proof only if real. Never invent testimonials, results or numbers of students.
- Commission angle, worded as opportunity: "Get paid per deal", "the conversation every commission depends on",
  "one closed deal can cover the course" (rarely, always "can").
Forbidden: income promises or amounts, "easy/fast/guaranteed money", fake urgency/scarcity, shaming poverty,
fake testimonials, medical/legal/financial advice. Footer line in captions is enough as disclaimer.

Cover titles (3-7 words, uppercase, hook = cover): money pain or curiosity. Examples:
"PAYCHECK GONE BY THE 20TH?", "THEY SOLD IT. YOU DIDN'T.", "GET PAID PER DEAL?", "THE CONVERSATION BEHIND EVERY
COMMISSION", "WHY BROKE PEOPLE HATE SELLING", "SAY THIS AND STOP TALKING". WHAT IF clips: kicker "WHAT IF..." +
question ("YOU GOT PAID EVERY TIME YOU CLOSED?").

Voice / intonation (ElevenLabs v4, natural, not announcer):
- Write how people talk: short sentences, contractions, one idea per sentence, a few fragments ("Not the price. Doubt.").
- Pauses with "..." before the key line and after the hook question. Max one [pause]-style beat per 2 sentences.
- Tags sparingly, matched to the beat: hook [serious] or [curious]; agitate [calm]; reframe [confident];
  technique [confident]; CTA [warm] or [calm]. Never [excited] on money lines (sounds like a scam).
- Emphasis by word choice and position (end of sentence), not ALL CAPS in the script.
- Dialogues: the customer sounds real (hesitant, skeptical), the closer calm and slow; nobody "pitches".
