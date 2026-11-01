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

## Forbidden

No merge, label, tag, release, issue filed or closed; no attribution trailer. No build on the Mac; local
runs on hasu block B alone, both lock names held per run; kasumi not touched. No other implementation's
source read. No source, test, golden, tool or workflow of pack changed: `lair.pin`, its own `wolf-toolchain.toml` and the README's toolchain sentence and test count, this note and nothing else.

## Inputs verified

- Base: pack trunk `27848095`, as the contract read it on 2026-10-31. pk09 is live on pack with no branch
  yet; this PR touches only the pins (and the README lines they move), and whichever merges second rebases.
- The engine between `aa6c4dc0` and `df11d213`: 44 commits, lr01's mixer, lr03's held keys and lr04's
  control grammar in `src/` (17 files), plus r41q's toolchain pin. pack links no `sound` module and opts
  into neither input mode. lair#26's own gauntlet already ran pack's trunk on `df11d213`: 190 tests
  (128 pack's, 62 the engine's), 77 goldens ok, 0 DIFFERS, ten pty rows ok.
- pack's own `wolf-toolchain.toml`: no workflow step, tool or README line here reads it (the cache keys
  and the README name `.lair/wolf-toolchain.toml`; every tool runs from `.lair/`). Moved to the engine's
  values exactly (a `diff` of the two files' non-comment lines is empty) and proved against both API
  passes by script.
- **A finding, not this PR's:** pack's trunk nightly is red every night since 2026-10-26 on one macOS pty
  row, `aim-window` (pack#44; runs 40313128861, 40490102077, 40679567517, 40866380912, 41048076666,
  41194811528, all at `27848095` with the old pins), on timing: `rich up>right delay=400ms actual=433ms …
  aim=1,0 … expected=1,1`. The labelled `tier full` will likely show the same row red. pack#44 stays open;
  it is pack's own lane's (pk09 or after).
- README read: the toolchain sentence moves to `wolf 0.2.36, lupin 0.1.58`, and the unit-test count to
  "190 of them (pack 128, pinned engine 62)", a README-only commit. The old split "175 (pack 114, pinned
  engine 61)" did not match trunk either: trunk's nightly ran 175 as 128 pack's and 47 the engine's (by
  path, the symlinked engine modules).
- lair trunk read twice before the pin was written (`git ls-remote` at 00:55:19Z and 00:55:21Z, and the
  commits API): `df11d213785f7694bdf3f3572299abc550d8b903`, lair#26's merge (r41q's engine half). The
  digests behind it are lair#26's: the release API read twice, every pinned archive hashed twice, the
  identities read from the archives; this repo's gauntlet holds the staged `.lair/wolf-toolchain.toml` to
  the same two API passes by script (`engine-pin`).
- 0.2.36's prelude names (`VaList`, the four `va_*`, `env_arg0`, `env_args_bytes`): declared in no `.lu`
  file here, so no W0304 under `--deny-warnings`.
- **R-r41q-4, pack's own `wolf-toolchain.toml`:** (A) move it with the engine's values and say it is
  unread; (B) delete it. Recommend and implemented (A): the contract keeps this PR to the pins, and the
  file's removal (or a check that holds it equal to `.lair/`'s) is pack's own lane's, listed.
- **R-r41q-5, the README's test split:** (A) the measured path split, 128 + 62; (B) the total alone.
  Recommend and implemented (A), with the measurement named here.

## Evidence index

- `da7c53b` Predict lair.pin at df11d213 moves no frame
- `66f5570` lair.pin: the engine at df11d213 (wolf 0.2.36 / lupin 0.1.58)
- `2d25ad0` wolf-toolchain.toml: the engine's pair, 0.2.36 / 0.1.58 (CI reads .lair's)
- `085ba97` README: the pair 0.2.36 / 0.1.58 and 190 tests, pack 128 + engine 62 (README only)
- The gauntlet at the final head, on hasu block B (`/home/mfwolffe/lanes/r41q/bin/gauntlet-game.sh pack
  <sha>`, its log under `/home/mfwolffe/lanes/r41q/logs/`): the head asserted, `lair.pin` against lair's
  trunk read live, this repo's own toolchain file proved against the API passes, `tools/fetch-lair` (the
  staged `LAIR-REV` asserted), the staged engine's toolchain file proved against the API passes, the
  planner's tests, the image `localhost/r41q-pack-ci:fbee7e864f7dbee6`, `.lair/tools/fetch-toolchain`, then
  `.lair/tools/check-linux` in the container on CPUs 6-11, and the count (every test ok, zero FAILED, zero SKIP,
  the game's and the engine's split by path). Every step prints `END <step> exit=N`; the wrapper stops at
  the first nonzero one. The END lines and the counts are in the PR body.

## Done-when

The PR is open at its final head with `tier pr` green there, `Footprint: cross-cutting` (a pin), the audit
run once and passing but for the labelled `tier full`, which the orchestrator labels and watches (the
second host's goldens). Nothing to close or file here. pack#44 stays open (above).
