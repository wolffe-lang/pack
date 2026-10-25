# The replay file (`.pk`)

A run of pack is a pure function of four things: the seed, the tier, the size of the field and the inputs,
each stamped with the tick it arrived on. A `.pk` file holds exactly those, so anyone can re-run it and get
the same frames, byte for byte, on any machine. The same text is the headless script the goldens are made
from, and the file `--record` writes at the end of a game.

## The format

Plain text, one fact a line. A blank line or one starting with `#` is ignored.

```
pk 1
seed 42
tier rich
size 80x24
start 600
# score 1240
t 30 up
t 30 left
t 95 size 100x30
t 110 health -25
t 120 quit
```

| line | meaning |
|---|---|
| `pk 1` | the format's version; a reader refuses any other number |
| `seed N` | the world's seed, any integer (negative too) |
| `tier rich` or `tier plain` | the glyph tier the run was drawn with (the simulation does not depend on it; the frames do) |
| `size WxH` | the field's columns and rows at the start |
| `start N` | optional (pk03): the run begins N rows up the path, the same forest; the distance, the difficulty curve and the dusk read from there. Absent, 0. `--start N` on the command line overrides it |
| `# score N` | optional (pk03, R-pk03-2 A): the score the run reached, written by the death card's `s`. A comment to every reader; the title and `--replay` re-run the simulation headless and compare: a match is shown as `verified`, a mismatch as `UNVERIFIED` with both numbers, a file without the line as the re-run's score alone — never silently accepted |
| `t TICK KEY` | a key at a tick: `up`, `down`, `left`, `right`, `parry`, `leap`, `quit`, `interrupt`; the quit (or the interrupt) that ended the run is recorded too, so a replay ends where the run did and shows the death card for as long as it was up (pk02) |
| `t TICK size WxH` | the terminal was resized at that tick |
| `t TICK health N` | the pack's health changed by N (negative or positive) at that tick: the goldens' and debug's channel (what the debug keys `-` and `=` record under `--debug`). The shadows' damage is never an event: shadows are the seed's, so their bites follow from the seed and the keys |

Ticks count from 0 and never decrease; several events may share a tick and are applied in file order. The
four header lines must all be present (`start` may be absent); a missing one, an unknown word, a bad number
or a tick that goes backwards is a parse failure, and `pack` says so and exits 2.

## What the engine does with it

- `pack --replay FILE` plays the run live on your terminal, ignoring the keyboard (q, Esc and Ctrl-C leave
  it, pk03) until the last recorded tick (`--ticks N` runs exactly N ticks instead); the card's last line and
  the closing line carry the verdict on its `# score`. The terminal must be at least the recorded size. From
  the title card (pk03) `p` plays the last saved replay and `/` one by name typed at the prompt; the title
  then reports the verdict, and the run returns to the title.
- `pack --headless --script FILE --frames N --every K --tier T --dump DIR` runs N ticks without a terminal and
  writes every Kth frame as `frame-NNNN.txt` (the glyphs, one line a row) and `frame-NNNN.sty` (the styles:
  runs of `fg,bg,attrs*count` a row), and the last frame as `final.txt` and `final.sty`. Flags given on the
  command line override the file's header; `--seed` given overrides the file's seed.
- `pack --record FILE` saves the run you just played, in this format, when the game ends.
- On the death card (pk02) `s` saves the run as `pack-SEED-SCORE.pk` in the working directory, or at
  `--record`'s path when one was given, with a `quit` at the tick of the press appended, so the file ends
  there, and the `# score N` line (pk03); the card then names the file and the title's best file records
  the path. `q` leaves the card for the title (or quits under `--no-title`; `--record`, if given, writes the
  file again with the real quit unless the card saved it there). A high score is such a file: `pack --replay
  FILE` re-runs it to the same card and verifies the score, and `pack --headless --script FILE --frames N
  --dump DIR` writes the same frames on any machine. The verification re-runs the simulation alone, no
  render: a five-minute replay (9,000 ticks) takes about a quarter of a second on the maintainer's Mac.

A held key is in the file as what the terminal sent: its first press and every autorepeat, each at its tick.
The simulation reads the hold from those ticks alone, so a replay steers exactly as the hand did.

A shadow's spawn is never in the file, nor a deer's (pk03): both come from the world's hash of the tick, so
the same seed and keys meet the same shadows and the same deer. The pty runner's `card` row plays a run to its death, saves from the card, and
re-runs the file twice to byte-identical frames equal to the card the player saw.
