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
| `t TICK KEY` | a key at a tick: `up`, `down`, `left`, `right`, `parry`, `leap`, `quit`, `interrupt` |
| `t TICK size WxH` | the terminal was resized at that tick |
| `t TICK health N` | the pack's health changed by N (negative or positive) at that tick: the goldens' channel for fainting and return until pk02's shadows deal damage, and what the debug keys `-` and `=` record under `--debug` |

Ticks count from 0 and never decrease; several events may share a tick and are applied in file order. The
four header lines must all be present; a missing one, an unknown word, a bad number or a tick that goes
backwards is a parse failure, and `pack` says so and exits 2.

## What the engine does with it

- `pack --replay FILE` plays the run live on your terminal, ignoring the keyboard except that the game ends
  after the last recorded tick (`--ticks N` runs exactly N ticks instead). The terminal must be at least the
  recorded size.
- `pack --headless --script FILE --frames N --every K --tier T --dump DIR` runs N ticks without a terminal and
  writes every Kth frame as `frame-NNNN.txt` (the glyphs, one line a row) and `frame-NNNN.sty` (the styles:
  runs of `fg,bg,attrs*count` a row), and the last frame as `final.txt` and `final.sty`. Flags given on the
  command line override the file's header; `--seed` given overrides the file's seed.
- `pack --record FILE` saves the run you just played, in this format, when the game ends.

A held key is in the file as what the terminal sent: its first press and every autorepeat, each at its tick.
The simulation reads the hold from those ticks alone, so a replay steers exactly as the hand did.

A high score, once pk02 brings the card, is a replay anyone can verify by re-running it.
