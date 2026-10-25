# pk00 — the prediction, written before the first change (2026-10-25T04:33:39Z)

The contract asks five things be predicted before a line of the engine exists. Each is answered here and
scored in the note's measurements section (hit, miss, or partly).

1. **Render cost.** A scrolling frame changes nearly every cell (the path moves one row a tick), so the diff
   is close to a full repaint: ~1,900 cells at 80x24, ~12,000 at 200x60. With SGR runs coalesced I expect
   ~10 bytes a cell and the diff built in 0.3 to 0.6 ms at 80x24 on release (the 1 ms bar met) and 2.5 to
   4.5 ms at 200x60 (the 4 ms bar at risk; if missed, by the per-cell UTF-8 encoding, not the compare).
   The write itself (one fs.write_chunk of ~20 KB) is outside the render number.
2. **os_signal_wait_fds on stdin, macOS against Linux.** The call behaves identically for a wait that ends by
   a byte, by the deadline and by a meaning; the spec names the select(2) fallback for a descriptor poll
   refuses, which macOS's tty is the classic case of, so I predict no divergence there. The likelier first
   finding is a wolf-std surface gap, not the wait: fs.read_into's List.reset refused on the checked
   machine (lupin and the checked tier lag it, wolf-interp#289), or term.size answering 0x0 in the pty
   runner before the runner has set the window size.
3. **The first rich glyph at the wrong width on Terminal.app.** A braille cell (U+2800 block, used for
   foliage): Terminal.app draws braille from a fallback font whose advance is not the cell's. Half-blocks
   (U+2580 block) and heavy box drawing (U+2500 block) render at one cell. The lane cannot run Terminal.app
   or iTunes2 unattended under RULES section 4, so this prediction is scored by the maintainer's run of the
   probe (pack --probe-glyphs), recorded in docs/GLYPHS.md with the date.
4. **The decoder's table.** About 24 rows: 4 CSI arrows, 4 SS3 arrows, 4 Shift+arrow (ESC [ 1 ; 2 X), the
   other modifier values recognised and mapped to the bare arrow (Alt, Ctrl, Shift+Ctrl: 4 rows as one
   rule), Space, z, q, Esc, Ctrl-C, Enter, a CSI-u form recognised and ignored, an unknown CSI consumed.
5. **The two paths at the first try.** They will NOT agree at the first try: the pty capture carries the
   alternate-screen entry, the cursor hide and the final restore blob, and the terminal model's handling of
   one of them (my guess: the leave sequence clearing the model's screen, or SGR 0 between runs) will
   differ from the headless frame by a style field, not a glyph. One iteration fixes it.

Also predicted, outside the five: the 30 Hz tick holds with zero wake-ups between ticks at idle (one poll a
tick, 300 context switches over 10 s plus the runtime's own); the headless goldens are byte-identical on
macOS and Linux at the first try (the simulation is integer-only); the plain tier never needs a glyph above
127, so PAX's font row is the rich tier's list alone.
