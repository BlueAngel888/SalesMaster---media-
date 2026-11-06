"""Test dialogue: offer loops (course lesson 22)."""
import glob, lux
from words_day01 import _p
lux.KEYWORDS |= {"OFFER", "LOOP", "NO", "PROS", "BACK", "TESTIMONIAL", "PAYMENTS"}
NAME = "Dialog_test_offerloop"
BG = sorted(glob.glob("/home/claude/tiktok/bg_lux/*.jpg"))[12:]
SEG = [
 ("CUSTOMER", "c", _p("""I 0.24 0.48|love 0.56 0.8|it... 0.88 1.44|but 1.68 1.92|two 2 2.24|thousand 2.28 2.64|dollars? 2.72 3.68|I 3.92 3.96|can't 4 4.24|do 4.32 4.4|that 4.48 4.56|right 4.64 4.8|now. 4.88 5.52""")),
 ("CLOSER", "a", _p("""I 0.24 0.28|hear 0.32 0.48|you. 0.56 1.12|If 1.44 1.52|we 1.6 1.68|split 1.76 2|it 2.04 2.08|into 2.16 2.4|two 2.48 2.72|payments... 3.04 3.84|would 3.92 4|that 4.08 4.16|work? 4.28 4.64""")),
 ("CUSTOMER", "c", _p("""Hmm... 5.6 6.56|maybe. 7.04 7.56|That's 7.6 7.92|still 8.04 8.16|a 8.32 8.36|lot. 8.4 9.28""")),
 ("CLOSER", "a", _p("""Okay. 4.96 5.6|Three 5.68 5.76|payments. 5.92 6.72|And 6.76 6.8|in 6.88 6.96|return... 7.24 7.92|you 8 8.08|give 8.16 8.24|me 8.28 8.32|a 8.48 8.56|short 8.64 8.72|testimonial. 9.04 9.64""")),
 ("CUSTOMER", "c", _p("""Deal. 9.36 10|Where 10.08 10.16|do 10.2 10.24|I 10.4 10.44|sign? 10.48 11.04""")),
 ("LESSON", "a", _p("""Most 10 10.24|people 10.44 10.64|quit 10.8 10.96|after 11.12 11.28|the 11.32 11.36|first 11.44 11.68|no. 11.76 12.48|Pros 12.68 12.88|have 12.96 13.04|the 13.12 13.2|next 13.28 13.52|offer 13.68 13.84|ready. 14 14.56|And 14.64 14.72|every 14.8 15.04|time 15.16 15.28|you 15.36 15.44|give 15.52 15.68|something... 15.92 16.48|you 16.56 16.64|ask 16.8 16.96|for 17.04 17.12|something 17.28 17.44|back. 17.52 18.32|That's 18.44 18.64|an 18.72 18.8|offer 18.88 19.12|loop. 19.2 19.76|It's 19.8 19.92|inside 20.12 20.32|Sales 20.4 20.72|Master. 20.8 21.52|Link 21.64 21.76|in 21.8 21.84|bio. 21.92 22.56""")),
]
