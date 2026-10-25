# What the terminals send

The decoder (`src/input/input.lu`) reads bytes into keys from this table. A row says what a terminal was
measured to send for a control, how, and when; a row marked owed has not been measured yet and says how to
measure it. The decoder's unit tests feed every sequence here whole and split at every byte.

## The controls

| control | bytes | decoded as |
|---|---|---|
| Up | `ESC [ A` or `ESC O A` | sprint burst |
| Down | `ESC [ B` or `ESC O B` | stop |
| Left | `ESC [ D` or `ESC O D` | steer left |
| Right | `ESC [ C` or `ESC O C` | steer right |
| Shift+Down | `ESC [ 1 ; 2 B` | parry (campaign R-PK-3) |
| Shift+Up, Shift+Left, Shift+Right | `ESC [ 1 ; 2 A`, `D`, `C` | the bare arrow |
| Alt, Ctrl, Shift+Ctrl, Shift+Alt with an arrow | `ESC [ 1 ; m X`, m = 1 + Shift + 2 Alt + 4 Ctrl | the bare arrow |
| Space | `20` | leap |
| `z`, `Z` | `7A`, `5A` | parry (the alias) |
| `q`, `Q` | `71`, `51` | quit: a run or the death card returns to the title, the title leaves (pk03; under `--no-title` the program leaves as before) |
| `s`, `S` | `73`, `53` | save the replay, on the death card alone (pk02); dropped in play, never recorded |
| `r`, `R` | `72`, `52` | on the title card (pk03): run the same seed again; dropped in play, never recorded |
| `p`, `P` | `70`, `50` | on the title card: play the last saved replay |
| `/` | `2F` | on the title card: the prompt for a replay's name; the decoder then runs in text mode (printable bytes are characters, Enter `0D`/`0A` and Backspace `7F`/`08` keys of their own, Esc the cancel) until Enter or Esc |
| `-`, `_` and `=`, `+` | `2D`, `5F`, `3D`, `2B` | the debug keys: the pack's health down and up by ten, acted on only under `--debug` (otherwise dropped) |
| Esc | `1B` alone, nothing after it for 50 ms | quit: a run or a replay returns to the title, the title leaves (under `--no-title`, the program leaves) |
| Ctrl-C | the terminal's interrupt signal (raw mode keeps `signals` on); as the byte `03` where a terminal passes it | the program leaves from anywhere, the terminal restored |
| kitty keyboard protocol | `ESC [ code ; mods u` | recognised and ignored (pack never enables the protocol) |
| the editing block, function keys | `ESC [ n ~`, `ESC [ [ A`, `ESC O P` | recognised and ignored |

## A held key

A terminal has no key-up. A held arrow arrives as its sequence once, then again after the keyboard's initial
repeat delay (about 225 to 500 ms on macOS, 250 ms on the Linux VT), then at the repeat rate (about 33 to
120 ms). The game reads the hold from the ticks the bytes arrive on (`docs/DESIGN.md`, the steering
paragraph): a lone press steers for 400 ms, a run of repeats steers until one repeat interval plus a tick
passes with none, and the heading then returns at the turn rate. The pty row `held-run` types such a run and
measures the release.

## Measured

| terminal | arrows | Shift+arrow | measured |
|---|---|---|---|
| the Linux VT (kasumi's kernel 7.2) | `ESC [ A`-`D` | `ESC [ 1 ; 2 A`-`D`; with Ctrl `1 ; 5`, Alt `1 ; 3`, Shift+Ctrl `1 ; 6`, Shift+Alt `1 ; 4` | pax lane px59, black-box through a pty on the VT, `pax/notes/px59/vt2.rows` lines 72-89 (2026-10) |
| PAX's console | the VT's, by construction | the VT's: `ESC [ 1 ; m X`, m = 1 + Shift + 2 Alt + 4 Ctrl | pax `kernel/console/console.lu`'s header (px58, px59), which cites the same rows |
| the pseudo-terminal runner (`tools/pty`) | sends `ESC [ B` and `ESC [ 1 ; 2 B` itself | the game decoded both in every run of the `quit` and `sigint` rows on macOS and Linux (pk00) | pk00, 2026-10-25 |
| macOS Terminal.app | owed | owed | run `tools/keyprobe` in Terminal.app, press each control, paste the table here with the date |
| iTerm2 | owed | owed | the same |

The two macOS terminals are owed because a lane cannot drive a GUI terminal from a script under the rules
of the Mac it runs on (RULES section 4: builds and tests only). `tools/keyprobe` puts the terminal in raw
mode, prints the bytes of each key pressed in hex, and restores on `q`; two minutes in each terminal fill
the rows. The expectation from xterm's documented behaviour, which both follow, is the first table's: the
CSI arrows in normal cursor mode, `ESC O` forms in application cursor mode (pack never sets it), and
`1 ; 2` for Shift. iTerm2 with its "report modifiers like xterm" setting off sends the bare arrow for
Shift+Down, in which case the parry is `z`.
