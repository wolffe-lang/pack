# pk06 — the directional leap

## Before and after

Scripted approach sector    old forward     new forward     new matching aim
N                          20/20           20/20           20/20
NE                         20/20           20/20           20/20
E                          20/20            0/20           20/20
SE                         20/20            0/20           20/20
S (alpha's six)            20/20            0/20           20/20
SW                         20/20            0/20           20/20
W                          20/20            0/20           20/20
NW                         20/20           20/20           20/20

Measurement                         before       after
Backward vs forward trail rows lost 0            0 (20 leaps, exact FP equality)
Burst leap cadence                  30/14=2.14/s 30/14=2.14/s
pk04-card.pk verified score         51           51
pk04-title.pk verified score        51           51
leap-lands.pk, 240 ticks            856 (2 hits) 958 (3 hits)
alternating-leap.pk, 24 ticks        4            4

The two verified replays hold and are not re-recorded. They contain no
leap events. The default leap in leap-lands gains one hit because its
forward sector now reaches six cells rather than four; score gains 100
for the kill and two from distance after that shadow is removed. This
unverified golden scenario's score difference is named, not silently
accepted as an old verified score.

Recipe: seeds 1–20, 80x24, the alpha alone active, selected as the second
leap group; every other wolf fixture-fainted. One target approaches along
each compass ray, scripted from eight to four grid cells at half a cell
a tick. Space at four cells; one leap, one target. The staged copy alone
disables ambient births and health recovery. This measures hit selection,
not survival or human aim. The initial stationary-target probe gave the
same counts; the final recipe explicitly scripts an approach. Trail cost
uses equal forward/backward leaps without a surviving enemy affecting
health: zero added cost, including the tell and arc. Up still sprints;
Space alone is the forward cost control. The sideways/backward unit rows
also put a second target outside the sector and prove it survives.

## Prediction (2026-10-25, committed before behavior changes)
The engine's input.Hold already answers held(h, tick) independently for
any key. Pack currently owns only left/right Holds and presses them after
processing Space; adding up/down Holds and sampling in event order in pack
should suffice without an engine change. Duplicate presses in one tick
must still count only once for each Hold.

An isolated active leaper, with one stationary target at four cells in each
of eight compass sectors, should hit 20/20 before in every sector. After,
a forward leap should hit N/NE/NW 20/20 and the other sectors 0/20;
matching the aim should hit 20/20 in each sector. At the alpha's six with
the alpha in the active second group, backward should hit 20/20 both
before and after; forward should miss after beyond the contact radius.
A backward arc should lose zero trail rows relative to an otherwise equal
forward leap: presentation offsets must not change physics or camera.
Cadence stays 30/14 = 2.14 accepted leaps/s while stamina lasts.
The verified pk04-card/title scores (51 each) should hold (no leap events).
Goldens with leaps should move: leap-lands, alternating-leap, and combat
cases whose hit selection changes; new eight-aim cases show tell and arc
on both tiers. Unrelated terrain, title, and art study sheets should hold.

## Recommendations (not rulings)
R-pk06-1 A: ±45 degrees, six-cell aimed reach, two-cell contact.
R-pk06-2 A: ordinary stamina/cooldown. These recommendations are implemented,
not decided. The arc remains a collision-clipped presentation offset, now
six grid cells out and back over eight ticks with one preceding tell tick;
no change to trail physics, camera, separation or alternating groups.
Diagonal distance is Chebyshev, as the game's reach has always been:
each coordinate advances six cells at the apex before body clipping.

## Forbidden
No other game's sources, assets or text, no extra dependency, engine edit,
pin change, CI edit, manual signal script, model-server operation, memory
or planning edit, merge, label, tag, release or issue action. The interrupt
witness is the engine pty runner's typed 0x03 byte through its own terminal.
Three draft plant PRs are deliberately left open for the coordinator.

## Inputs verified
Base f66f571; engine aa6c4dc0bc5071d3c07121451d913a8837cd2a6a, unchanged.
Pinned wolf 0.2.35 (cf0c13d), lupin 0.1.56, bundled std
2386522eb059cca5a84108562c2c0a0e72345d34. The whole release archive pair
is staged on each host by the engine's fetcher, never PATH wolf.
notes/pk06-evidence/digests-twice.txt records two identical release-API
reads of all four Mac/Linux compiler/interpreter archive digests; the
fetcher verifies them on download. The engine's version and std identity
gates pass. Read DESIGN and KEYS whole, pk04's note and census/parry
recipes, pk02 section 3, sim/art and the pinned engine input documentation.
The independent Hold instances suffice; no engine PR or pin bump is needed.

## Evidence
158 checked tests, zero SKIPs, on both hosts. Ten new rows cover all 16
held subsets, same-tick event order, duplicate bytes, autorepeat expiration,
refused presses, exact inclusive sector/range/contact boundaries for every
aim, the backward chaser and outside-sector survivor, active group only,
tell before arc on both tiers, no body overlap, return to formation, six
cell apex, resize preserving a compass vector, and both alternating groups.
Space alone and Up+Space have the identical forward aim; Up retains its
normal sprint action, which does not silently become part of Space alone.

macOS .lair/tools/check and Linux .lair/tools/in-container
.lair/tools/check-linux pass (kasumi, LAIR_CPUS=4-7, shared flock per run).
Both compile native and LLVM release, run selftest and all goldens, then
nine pty rows including restoration on quit, typed interrupt and planted
trap, held release, replay/card equality and title/save verification. The
new directional-chords row opens 18 fresh terminal sessions, default plus
eight arrow aims on both glyph tiers; each emits its expected live tell
and restores. Native-backend goldens are also checked separately on both
hosts, matching release. All 61 golden directories are byte-identical
across hosts/backends for their respective glyph tier. Glyph tiers are
different presentations of one sim, not claimed byte-equal to each other.

Golden provenance: the dated aim commit moves only leap-lands and
alternating-leap among the original cases: new hit envelope, committed aim,
one tell tick and six-cell arc. Nine new cases (N/default, Up, NE, E, SE,
S, SW, W, NW) capture both groups at every tick on both tiers. Art and
title sheets, and every unrelated existing case, hold. There are now 30
cases x two glyph tiers plus art, 61 directories. No fixture was updated
without a behavior reason.

Reproduce the census:
  python3 -I notes/pk06-evidence/stage.py --out target/pk06-census
Use --revision f66f571 for before, --kind scores for unmodified-simulation
replay scores. Build the staged main.lu with the pinned compiler and
WOLF_STD behind the host memory gate, then run it from the repo root.
Raw before/after census and score outputs are tracked beside the recipe.
All four Linux probe outputs compare byte-for-byte to the Mac outputs.

## Plants (named reds, left open)
aim      PR 28 run 40211361154 test_pk06_aim_table_all_sixteen_subsets
backward PR 29 run 40211366968 test_pk06_backward_resumes_forward_and_hits_only_its_sector
sector   PR 30 run 40211372109 test_pk06_sideways_hit_outside_sector_is_not_vanquished
Each own CI Linux unit-test step failed by name (trap(assert)); the
format gate passed. notes/pk06-evidence/plants-red.txt preserves the named
lines. Each plant is a pk06-plant-* draft and must never be merged.

## Follow-ons
R-pk06-1 A and R-pk06-2 A remain recommendations for play. The maintainer
should judge the six-cell arc and one-tick tell in a real terminal; inferred
holds can retain a recent tap for 400 ms and do not acquire real key-up.
No new compiler/engine issue found. Existing GUI terminal key/font-width
measurements and the PAX work remain outside this pass. README read and
refreshed in its own commit: controls, current build and test/case counts;
engine/build paragraphs remain current. No issue action requested here.

This lane's committed note is .txt because its tooling does not author
Markdown report files. The full text also appears under Note in the PR.
