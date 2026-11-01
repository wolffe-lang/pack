# pk09 — the prediction, before the first measurement and the first change

Written 2026-10-31 from the macOS job of nightly run 41194811528 (trunk 27848095), read once, before
any local run. Six problem lines in that job (the contract quotes five; the sixth is
`plain left>up delay=400ms actual=405ms Space=41 held=1 aim=0,1 left_at=25 up_at=41 expected=-1,1`).

## What the game's rule is (read from the source, not measured yet)

- Aim: an arrow counts for the leap when it is held (the engine's `Hold`) or its last press is at most
  `AIM_WINDOW_TICKS` = 15 ticks (500 ms) before the Space tick (`src/sim/sim.lu`, `aim_recent`). The
  Hold of any key ends at most 12 ticks after its last press, so the window decides alone.
- Hold: a press `gap` <= 5 ticks after the previous holds `rate + 1` ticks, `rate` the larger of the
  last two gaps; so a key repeating at 1-tick gaps is released 2 ticks after its last byte.
- Ticks: a byte is applied on the first tick the loop steps after reading it; a late wake steps every
  due tick at once with the keys on the first. A game-side stall therefore stamps a byte EARLIER than
  its wall arrival (the earliest missed tick), never later; only the writer's lateness, or tick
  quantisation (at most one tick), lengthens a gap in ticks.

## The cases, predicted

1. The four `expected=` lines (`up>right`, `down>left`, `left>down` rich and `left>up` plain, all at
   delay 400 ms): the first arrow's last byte was applied 16 ticks before Space (24 -> 40 three times,
   25 -> 41 once), one tick outside the window. The game applied its rule; **the row is wrong**. Its
   nominal gap from the first arrow's last byte to Space is the unmeasured 50 ms settle after that
   byte plus the 400 ms delay: 450 ms = 13.5 ticks against a 15-tick window, 1.5 ticks (50 ms) of
   margin. Its `actual=` figure omits the settle, so a session can show `actual=405ms` and still put
   more than 500 ms between the two bytes. I expect every such red, measured, to have a written gap
   (first arrow's last write to Space's write) above 500 ms.
2. The two `fixture Hold set is not the last key alone` lines (`rich up>right` and `plain right>up`,
   delay 200 ms): the row writes the second arrow's last repeat at `delay - 50 ms` and Space at
   `delay + lateness`, so Space trails the last repeat by a whole repeat interval plus the writer's
   lateness (64 and 82 ms here, 2 and 3 ticks), while a real keyboard would have sent one more repeat
   in that time. The Hold measured a 1-tick rate (two repeats applied on consecutive ticks) and released
   2 ticks after the last byte, so the raw Hold at Space is empty. The fixture refuses its own setup;
   the aim is right (1,1) in both. **The row is wrong.**
3. No case where the aim differs from what the rule gives on the ticks the game applied. The game's
   aim model is right by its own specification in all six. I predict the measurement finds no aim
   fault.

## The design question I expect to raise, not to fix

A last-key-only keyboard stops repeating the first arrow when the second is pressed, so the window
runs from the second arrow's press, not from the first arrow's release: a diagonal held longer than
about 450 ms before Space comes out as the second arrow's cardinal, by design (pk06b's 500 ms, which
"human play still judges"). That is the maintainer's feel, not a fault this lane may move. I will
recommend keeping it (R-pk09-1) and change no game code.

## The forced stall and the proof

- The Mac has no CPU affinity. The stall will be a competing CPU load with the game and the row run
  at a lowered priority, so both wake late as on a shared runner; measured, not assumed.
- Trunk's row under that stall: red in at least 1 of 20 runs, every red line one of the two classes
  above, never an aim that contradicts the applied ticks.
- The fixed row (injections paced by the game's own trace ticks, as cub's cb11/cb11b rows, the
  expected Hold and aim computed from the ticks the game applied by an oracle written from the rule):
  20 of 20 green under the same stall, with the applied gaps printed for every session.
- The plant `pk09-plant-aim` (the fixed head plus an input model that drops the second key of a
  diagonal): the new row red by name on every diagonal case, under the stall and without it; the
  unit test `test_pk06b_timing_table_diagonals_in_both_orders_cardinals_and_default` red too.
- No golden, no case, no replay, no engine or pin byte moves; the unit-test count is unchanged.
