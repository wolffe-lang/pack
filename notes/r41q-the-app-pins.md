# r41q — pack to lair `df11d213` (wolf 0.2.36 / lupin 0.1.58)

_pack's part of r41q (the apps, the games and the docs to the published pair), after the engine's (lair#26)._

## Prediction

Written before the first change (2026-11-01, base trunk at `lair.pin` `aa6c4dc0`).

- `lair.pin` moves `aa6c4dc0` to **`df11d213`** (lair trunk, read twice): 44 engine commits, lr01's mixer,
  lr03's held keys, lr04's strict keyboard-control grammar and r41q's toolchain pin. pack opts into neither
  input mode and links no `sound` module, so no frame moves. pack's own `wolf-toolchain.toml` moves to the
  same pair, though nothing in pack's CI reads it (its cache keys and README name `.lair/wolf-toolchain.toml`).
  Only the pins move (pk09 is live on pack).
- The engine's own toolchain file at `df11d213` names wolf 0.2.36 / lupin 0.1.58 / std `78b9d3cb` (lair#26,
  r41q's engine half): `.lair/tools/fetch-toolchain` accepts the linux x86-64 archives by digest and
  `.lair/tools/lib-toolchain.sh` accepts `wolf 0.2.36 (wolfgang, pin 5adf3d9)`, `lupin 0.1.58 (wolf-interp,
  reference interpreter at pin a5378e3)` and `STD-REV` `78b9d3cb`. No source here declares the names 0.2.36
  adds to the prelude (`VaList`, the four `va_*`, `env_arg0`, `env_args_bytes`), so `--deny-warnings` sees
  no W0304.
- `tier pr` stays green with the counts lair's gauntlet already measured for pack's trunk on this engine
  (`df11d213`, 2026-11-01): **190 tests** (trunk's 175 plus 15 engine tests), zero SKIPs, both builds, the
  selftest, **77 goldens byte for byte**, **ten pty rows ok**.
- `tier full` will probably be **red on the macOS `aim-window` pty row**, and not because of this change:
  that row has failed every nightly at trunk `27848095` with the old pins since 2026-10-26 (pack#44; runs
  40313128861 to 41194811528), on timing (`actual=433ms … expected=1,1`). A finding, listed.
- The README's toolchain sentence (0.2.35 / 0.1.56) and its unit-test count (175: pack 114, the pinned
  engine 61) move with the pin, in a README-only commit, from this head's measured split.
