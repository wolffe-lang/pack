# pk03 — the prediction, written before the first change (2026-10-25T08:40Z)

The contract names five things to predict. Each is scored in the note's section 2.

1. **Whether the deer read as prey at one glyph a cell.** Standing, no: pk00's sprite (`▀` over `█` in
   173, a tan column two cells tall) is a trunk's shape in a trunk's colour family, and at rest on the
   verge it will read as a tree. What makes it prey is motion against the pack's: a deer that walks
   across the path while the world scrolls is the one thing in the field moving sideways on its own, and
   a deer that flees up the path at 1.5 v pulls away from the trot (the pack must sprint, 1.8 v, to close
   on it, and pays stamina for the meal: the design). I predict the flee reads and the stand does not, and
   that the maintainer's first word on the deer is about its shape (wider, a head cell beside the body)
   rather than its behaviour. I will give the deer a two-cell body on the rich tier (head and body side
   by side, the same two code points, so GLYPHS.md gains no row) and predict that is still too little at
   rest.
2. **The curve's shape that makes a two-minute run survivable with deer and not without.** Today the rate
   is `2 + rows/200 + density × 6/256` thousandths a tick, so seed 16's stand gives 7 from row 0 (a group
   of three within three seconds) and a clearing gives 2. A gentle first minute needs the start low and
   the density's say capped early: I predict the shape `min(base + rows/150 + density × 6/256, ceiling)`
   with the base 1, groups above 5 and a ceiling of 12, and a ramp that holds the total under 3 for the
   first 30 s (about 140 rows) however dense the stand. At the trot (4.7 rows a second) that gives rate 1
   to 3 in the first minute (singles, one every 11 to 33 s), 4 to 8 in the second (groups), the ceiling
   around the fourth minute. Damage when a group is not leapt is about 20 health a second (pk02's
   measurement), so a two-minute run leaks 30 to 60 health a minute under competent play (one group in
   three missed); a deer at `FEED` 25 every 20 s (`DEER_RATE` about 2 thousandths a tick, caught two in
   three) returns about 50 a minute. I predict the survivable-with and not-without pair on one scripted
   seed is reachable within an hour of probing, and that the probe's script needs a sprint timed at each
   deer, since the deer's flee speed (60) is above the trot (40).
3. **The render cost with deer, a dozen shadows and the dusk blend at 200x60.** The blend changes colours,
   not glyphs, and it will be computed once a frame (fourteen roles), not once a cell, so the per-cell
   cost is unchanged: within 10 percent of pk02's 247 us on kasumi and 166 on nomad. The cost that is new
   is the diff's, not the render's: on a frame where the palette steps, every cell's style changes and the
   diff writes the whole screen (about 18 KB at 200x60 rich, the first frame's cost); with the blend in
   256-colour indices a step happens every few seconds at most, so the average over 300 frames moves
   under 5 percent and the max on a stepping frame roughly doubles, still far under 4 ms. The idle row
   stays at one wake a tick (nothing in dusk reads the clock).
4. **How many new goldens.** Five cases (a deer fleeing and caught; dusk at three distances as one case
   written at three frames, or three cases; the title card; a restart from the title), each on two tiers:
   10 directories, 41 in all. Every existing shadow golden moves, because the curve moves the rate and the
   roll against it: seed 16's group at tick 87 is a roll under 7 that a lower first-minute rate misses, so
   the five pk02 cases are re-timed and their comments rewritten; the pack-only cases move where a deer
   now spawns in them (`faint-return` and `sprint-exhaust` are long enough to be near certain). I predict
   `standstill` holds again (a deer that spawns ahead of a standing pack is on the screen, so it may not:
   if it moves, the deer is why). The art sheet moves for the deer's new shape.
5. **Whether the title's headless re-run of a long replay is fast enough to feel instant.** The re-run
   needs the simulation alone, no render: a step is a few microseconds for the pack and some tens with a
   dozen shadows (136 pairs a separation pass, the cohesion's reads). A five-minute replay is 9,000 ticks:
   I predict 50 to 300 ms on nomad and under 500 ms on kasumi, which is a blink and not a wait; the card
   shows the verified score without a "verifying" frame. If it is over half a second I will measure which
   part and say so, not add a spinner.

Also predicted: the goldens byte-identical across the hosts at the first try (integer arithmetic
throughout, the dusk blend in integer steps); the seven pty rows pass unchanged and the eighth (the title's
restart) needs the title to be skippable for the existing rows — I predict `--seed` on the command line
still goes straight to the title, so every row gains one keypress, and I will add a `--no-title` flag for
the rows that measure the run alone rather than retype seven rows. The first wolf gap: none new — the best
file needs a date and `std.time.now_iso8601` exists; the risk is #950 if I interpolate a row with a
payload in the best file's refusal, which I will spell without the row.
