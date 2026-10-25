# pk01 — the prediction, written before the first change (2026-10-25T06:20Z)

The contract names five things to predict; the orchestrator's message of the same morning (the maintainer's
four rulings from play) adds a sixth. Each is scored in the note's measurements section.

1. **The four-tick latency outlier.** pk00's runner timed the first byte after a key, which counts a frame
   already in flight; the sound measurement is to the frame that carries the key. With a marker on that
   frame (`--trace` printing the key's tick of arrival and the tick its effect is drawn), I predict the
   median lands at one tick plus the render (25-40 ms on both hosts) and the p90 under two ticks: the
   outliers were the instrument's, not the loop's. The one real cost I expect to see in the trace is the
   pty master handing the game a key just after a tick deadline, which is one tick of wait by design.
2. **The input drift the maintainer felt** (the orchestrator's first item). Not the queue: every key that
   arrived is applied in the one tick that consumes the list. The cause is the steering model: a tap moves
   `heading_target` by 24 and autorepeat saturates it at 64 within a few taps, and the target relaxes
   toward straight at `RETURN_RATE` = 1 a tick, so after the last byte the heading stays off-axis for up
   to 64 ticks (two seconds) and the wolf keeps moving sideways. The trace will show the last byte's tick
   and the heading still non-zero 40-60 ticks later. The fix is a held-key model (a key is held while its
   repeats keep arriving, released when none arrives within the measured repeat interval plus a margin)
   with the heading returning at the turn rate, not at 1 a tick.
3. **The per-slot lag at 30 Hz.** A lag of 2 and 4 ticks between the leading, flanking and trailing slots
   reads as a ripple without interpolation: at 30 Hz a cell-sized step per tick is already smooth to the
   eye, and the wolves are three cells wide, so a two-tick offset in heading is a visible lean. I predict
   no interpolation is needed, and that the drift-and-bump rule (R-pk01-2 C) is what makes the formation
   look alive, not the lag alone.
4. **Render cost with five wolves at 200x60.** Negligible against the terrain: five sprites are 30 cells of
   12,000. I predict the average stays within 10 percent of pk00's 244 us on the Linux host and under the
   4 ms bar by more than a factor of ten; the forest's density channel (one more noise read per row, not
   per cell) adds under 5 percent.
5. **New goldens.** Seven cases (a formation turn with a bump, a sprint to exhaustion with five wolves, a
   faint and a return, a clearing, a dense stand, a resize mid-run with the pack, the wide field) on two
   tiers plus the art sheets: 15 golden directories, up from 13; every existing golden moves because the
   trot speed and the steering model change.
6. **The forest's density on the plain tier.** A clearing reads as a place at one glyph a cell: grass
   (`"` `'`) to the verge and the odd trunk against a dark floor is a visibly different texture from the
   canopy's `& % *`. A dense stand against thin woods is the harder read on the plain tier, since both are
   canopy glyphs; I predict it reads by the trunk count and the path narrowing, and that the rich tier's
   braille densities make it plain.

Also predicted: the goldens are byte-identical across the two hosts at the first try (integer arithmetic
throughout, as pk00's were); the pty rows pass unchanged once the new flags are debug-gated; the first
wolf/wolf-std gap I meet is in the checked machine's modelling of a larger struct graph (five wolves in a
list inside the Sim) rather than in any surface.
