# pk02 — the prediction, written before the first change (2026-10-25T07:30Z)

The contract names five things to predict. Each is scored in the note's measurements section.

1. **Whether a chase at 1.3 v reads as a threat at 30 Hz, or needs the eyes to pulse.** The chase speed
   alone will not read as a threat: 1.3 v is 52 against the trot's 40, a closing speed of 12 FP units a
   tick (0.047 cells a tick), so a shadow five cells behind the alpha takes about 100 ticks (3.5 s) to
   close, and at the alpha's eye that is a sprite creeping up the bottom of the screen one cell every
   twenty ticks. What reads is the turn: a shadow ahead slides down the screen at the trot plus its own
   approach, slows, stops, and climbs back — the direction change is what the eye catches, as the bump was
   in pk01. I predict the chase needs two more cues to read as menace: the red eyes pulsing while the shadow
   chases (steady while it lurks: a change in the one colour both tiers share), and the shadow drawn on the
   path's background (it leaves the forest floor's dark for the earth) so its black body is a silhouette.
   I will build the pulse and predict the maintainer keeps it.
2. **How many shadows at once the pack can survive without a parry.** With `DAMAGE` 10 a landed group
   attack and 5 alone, `ATTACK_COOLDOWN` 30 ticks (one landing a second per shadow in reach), and a leap
   that vanquishes everything within `LEAP_REACH` 3 cells at `LEAP_STAMINA` 60 of 300 (a cooldown of 20
   ticks, so about five leaps before the pant): two shadows at once are survivable on leaps alone (one leap
   takes both if they arrive together; a 3.5 s chase gap between them is a leap each); three are a fight
   (the third lands once or twice: 10 to 20 health, one wolf down); four at once without a parry cost the
   pack two wolves and the run if a second group arrives before health recovers — and nothing recovers
   health in this build (deer are pk03's), so every landed attack is permanent. I predict the maintainer's
   first tuning message is about recovery or the damage, not the speeds.
3. **The render cost with a dozen shadows at 200x60.** A dozen shadows are 72 cells of 12,000; the render
   is terrain-bound. I predict the average stays within 15 percent of pk01's 235 us rich on kasumi (the
   shadows move against the scroll, so more cells change a frame than the pack's) and far under the 4 ms
   bar; the simulation's cost — the separation rule over 17 bodies is 136 pairs a pass, up to five passes,
   and the flocking is another 144 pair reads — stays under the render's. The idle row stays at one wake a
   tick (nothing in the shadows reads the clock).
4. **How many new goldens.** Five cases the contract names (spawn and chase, a group attack, a leap that
   lands, a parry that turns an attack, a death and its card), each on two tiers: 10 directories, 31 in all.
   Every existing golden except `standstill` moves, because the spawn roll makes shadows appear in every
   trotting case's first lattice of rows (the rate is 2 to 8 thousandths a tick, so a 60-frame case has a
   one-in-three chance of a spawn; the 480-frame `faint-return` and the 240-frame `sprint-exhaust` are near
   certain to) — and even without a spawn, the separation rule's generalisation must not move a pack-only
   frame, which the unchanged `standstill` golden witnesses. I predict I will NOT be able to keep the
   pack-only goldens byte-stable and will regenerate them, saying which moved for a spawn and which did not.
5. **Whether the card's numbers are the first the player sees.** Yes, by construction: nothing in the field
   draws a digit (posture is the HUD, the trace goes to standard error), and the card is drawn from the
   same cell model on both tiers after the last landed attack. The one leak I predict I have to guard is
   the closing line on standard error, which already prints cells and health after the terminal is
   restored: it stays, because it is after the card, and the headless goldens pin that the field has no
   digit before the card frame (a test will scan every pre-card frame for `0`-`9`).

Also predicted: the goldens are byte-identical across the two hosts at the first try (integer arithmetic
throughout); the pty rows pass unchanged (Space and `z` are already typed by the `quit` row and now act);
the first wolf gap I meet is the checked machine's step budget again (a chase-to-death scenario needs more
than 600 ticks, so it is a golden, not a unit test), and the second is the mixed-payload interpolation ICE
(wolf-lang#950) if I interpolate a row carrying a payload in the card's save message — I will name #950
there and spell the message without the row.
