# pk07 — the sight

The maintainer's word (2026-10-25): "The shadows' line of sight could use increasing in pack. Maybe just do it
yourself. Also why not let shadows spawn in the middle/offset on the path instead of always on forest edge. Maybe mix it
up a bit, some scroll into view on the path, others wait at forest edge, with line of sight at a proper angle to spot the
pack (audit the direction algorithm)." Done by the orchestrator by hand; contract `sprints/lair/07-the-sight/`.

## Before / after (pk04's census fixture, 20 seeds to row 1800, sensor-only)

Detections / births. "Centre" trots the path's centre, "far shoulder" the right shoulder two cells in from the edge.
The 80x24 before column reproduces pk04's after numbers exactly (4488/4522, 3502/4580), so the fixture is the same one.

| field   | centre before     | centre after       | far shoulder before | far shoulder after |
|---------|-------------------|--------------------|---------------------|--------------------|
| 80x24   | 4488/4522 99.25%  | 4539/4539 100.00%  | 3502/4580 76.46%    | 4560/4635 98.38%   |
| 200x60  | 679/3647 18.62%   | 4436/4513 98.29%   | 1992/3931 50.67%    | 3291/4503 73.08%   |

By band at 200x60, centre: forest edge 10.76% → 96.49%, inner verge 12.72% → 98.03%, shoulder 25.38% → 98.16%, the new
middle band 99.56%. By facing at 200x60, centre: down path 17.41% → 99.00%, diagonal down 18.53% → 99.60%, across
28.17% → 100.00%, diagonal up 17.10% → 98.78%, up path 12.15% → 86.45%. The whole table is
`notes/pk07-evidence/detection-summary.txt`; the raw runs are the four `census-*.txt.gz` beside it.

## Audit of the direction algorithm (pk04's)

1. **The range did not grow with the field.** `PERCEIVE` was 8 cells (Chebyshev) while the path's half width is a
   sixteenth to an eighth of the columns plus a thirty-second where the forest is thin: 5–12.5 cells at 80 columns,
   12.5–31 at 200. The field grows to fill the terminal, so on a wide terminal a forest-edge lurker could not see the
   centre of the path at all. pk04's census only ran at 80x24, where 99% looked fine; the 200x60 before column above
   (18.62%) is what the maintainer was playing.
2. **Two of five facings looked away from the oncoming pack**, evenly weighted: "diagonally up" and "up the path" see
   the pack only once it has passed and can only chase from behind.
3. **No spawn band reached the middle.** Edge (half + 0.5 cells), verge (half − 0.5), shoulder (half − 3); on a wide
   path the shoulder still reads as the edge, and nothing ever stood in the pack's way.
4. Sound and unchanged: the 60° half-cone with integer dot products, the 3-cell all-round contact radius, `spawn_side`
   (the outside of the bend), the lurk → stalk → chase step, the hit envelope.

## The change

- `perceive_range(s, sh)` = max(`PERCEIVE` = 12 cells, the lurker's row's half width + `PERCEIVE_ACROSS` = 4 cells).
  `shadow_perceives` takes the range as a parameter; `perceived_wolf` reads it once per shadow.
- A fourth spawn band, `SPAWN_BAND_MID`: the lurker waits on the path from the centre to half way out (seeded) and
  scrolls into view ahead of the pack. Shares edge 15 / verge 20 / shoulder 35 / middle 30 (`SPAWN_SHOULDER_PERCENT`
  is new; the middle is the remainder).
- Facings weighted toward the oncoming pack: down, diagonally down and across twice in eight each; diagonally up and up
  the path once each. A middle-band lurker always faces down the path (straight twice in three, diagonally toward the
  far verge once). The pk04 invariant holds: never a component into the woods.
- The two recorded terminal fixtures (`tests/replays/pk04-card.pk`, `pk04-title.pk`) no longer verified: with seed 16's
  shadows spawning elsewhere no bite landed after the debug key took the health to zero, so the run never died (score 55,
  dead false). Both were re-recorded through an 80x24 pty with `notes/pk07-evidence/record.py` (the same procedure as a
  terminal: `--debug`, the health key ten times, the fatal bite, `s` then `q`); both record score 56 and the test pins 56.
- Goldens regenerated (`.lair/tools/goldens --update`): the six shadow cases moved on both tiers (death-card,
  group-attack, leap-lands, parry-turns, shadow-lunge, spawn-chase); the art sheets and the wolves-only cases held.

## Prediction

Written in the contract before the census ran: on a wide terminal a forest-edge lurker could not see the centre of the
path, and that, not pk04's cone, was the complaint. Numerically: 200x60 centre detection under 30% before and over 90%
after; 80x24 unchanged within a point. Scored: 18.62% → 98.29% at 200x60; 99.25% → 100.00% at 80x24. The far-shoulder
200x60 case was not predicted; it moved 50.67% → 73.08%, the forest-edge band least (51% → 64%): a shadow on the far
edge of a 60-cell-wide path still cannot see a pack hugging the other edge, by design.

## Forbidden

No other game's code, assets, text or music (the lair rule). No engine (`lair`) change; no pin change; no CI change.
No ruling decided: `PERCEIVE` 12, `PERCEIVE_ACROSS` 4 and the band shares are proposals, written into `docs/DESIGN.md`
as such, for the maintainer to tune by play.

## Inputs verified

- pack trunk `e6c778d` (pk06b's note), lair at `lair.pin`, toolchain `.lair/wolf-toolchain.toml` (wolf 0.2.35 pin
  cf0c13d, lupin 0.1.56), staged by `tools/fetch-lair` and `.lair/tools/fetch-toolchain` into a fresh worktree.
- pk04's census fixture `notes/pk04-evidence/census.lu.in` and `stage.py`, copied to `notes/pk07-evidence/` with a
  `--size` option and an engine-module fallback (`src/world`, `src/input` are symlinks into `.lair/` and not in this
  repo's history); the before fixtures staged with `--revision origin/trunk`.
- `world.FP` = 256 (lair `src/world/world.lu`).

## Evidence index

- `notes/pk07-evidence/detection-summary.txt` — the four censuses by band and facing (sha 73838635…).
- `notes/pk07-evidence/census-{before,after}-{80x24,200x60}.txt.gz` — the raw B/D/M/END lines.
- `notes/pk07-evidence/stage.py`, `census.lu.in`, `summarise.py`, `record.py` — the fixtures and the harness.
- `notes/pk07-evidence/recorded-{card,title}.pk` — the recordings as taken (copied into `tests/replays/`).
- Local gate: `.lair/tools/check` (fmt, test, build --all, selftest, goldens, pty) — see the PR body for the run.
- CI: the PR's `tier pr` run at the final head (ids in the PR body).
- Plants: `pk07-plant-range` (the range back to `PERCEIVE` alone) must turn `test_pk07_a_forest_edge_lurker_sees_across_a_wide_path`
  red; `pk07-plant-mid` (no middle band) must turn the band assertions in `test_pk04_detection_cone_contact_and_outward_spawn_bands`
  red. Ids in the PR body.

## Done-when

- `.lair/tools/check` green at the final head; CI `tier pr` green; both plants red by name.
- `docs/DESIGN.md` carries the new constants as proposals; this note and its evidence are in the tree.
- The maintainer plays it: `~/lanes/pk07/pack/target/pack` (seed of choice; a wide terminal is the case that changed).

## Follow-ons (not done here)

- A lurker's facing could turn toward a perceived wolf before the chase (today the chase's heading does it).
- The far-shoulder case on a very wide path: a forest-edge lurker on the opposite edge stays blind by design; if the
  maintainer wants every edge lurker to see the whole path, `PERCEIVE_ACROSS` becomes "the path's full width".
- pk05/cb05 (PAX) unchanged.
