# pk06b — aim window

## Before / after / planted back out

Realistic pty sequence  raw Hold at Space  pk06  window 15  window 0 plant
Up -> Right -> Space   Right              0/6   6/6        0/6
Right -> Up -> Space   Up                 0/6   6/6        0/6
Up -> Left -> Space    Left               0/6   6/6        0/6
Left -> Up -> Space    Up                 0/6   6/6        0/6
Down -> Right -> Space Right              0/6   6/6        0/6
Right -> Down -> Space Down               0/6   6/6        0/6
Down -> Left -> Space  Left               0/6   6/6        0/6
Left -> Down -> Space  Down               0/6   6/6        0/6
Four single arrows                       8/8   8/8        8/8
No arrow                                 2/2   2/2        2/2

Six per order means Space 200/300/400 ms after the second arrow starts,
on both glyph tiers. The first arrow gets an initial delay and autorepeat,
then receives no more bytes; only the second repeats. Every session starts
fresh, records the accepted Space tick, the actual elapsed time, the raw
Hold mask and arrow timestamps, then checks terminal restoration.

The hypothesis reproduces: e.g. before Up->Right, Space tick 33 has Up's
last press at 24 and Right's at 31, raw Hold=8, aim=(1,0) instead of NE.
Reversed, raw Hold=1 and aim=(0,1). All 48 diagonal sessions fail before;
all 48 pass after while the raw Hold still contains only the last arrow.
This is a real pty fed a realistic last-key-only stream, not a claim that
every physical keyboard/terminal was measured. The old simultaneous-byte
row tested decoding, not this keyboard behavior, and missed the bug.

An initial timing harness accumulated select rounding in each relative
repeat wait: a requested 400 ms stretched beyond the proposed window.
The final row uses absolute deadlines and logs actual delay, so it does
not silently test a 600 ms chord as if it were 400 ms.

## Prediction (committed before reproduction or implementation)
The proposed last-key-only autorepeat stream should reproduce the failure:
Up repeats every two ticks, then Right alone repeats for 200–400 ms before
Space. Up should no longer be held at Space, so the current build aims E
instead of NE; reversed order should aim N instead of NE. Other diagonals
should likewise collapse to the last arrow. This is a hypothesis, not yet
a measured keyboard or terminal property. A real pty will drive those byte
streams, with the accepted Space tick's raw Hold set logged explicitly.

A 15-tick (500 ms) aim window should retain both recently pressed arrows
and restore every diagonal in both orders while single-arrow aims and the
no-arrow default stay unchanged. Contradictory arrows should choose the
later press, including event order inside one tick. Steering retains its
existing short Hold release; only leap aim gets the longer window.
Existing goldens may change when an earlier arrow now survives to a later
Space; new realistic timing goldens will be needed. Verified scores should
stay 51/51. Planting AIM_WINDOW_TICKS=0 should fail the realistic rows.

## Implementation and recommendation (not a ruling)
AIM_WINDOW_TICKS=15, inclusive of a press exactly 15 ticks before Space;
at 16 it expires unless still held. aim_arrows resolves opposing arrows
independently to the latest press/repeat. A monotonic byte-order stamp
breaks same-tick ties; arrows after Space cannot re-aim an accepted leap.
The engine's input.Hold is unchanged: its four existing last-press ticks
suffice for the window, and steering keeps its original release. No lair
change, dependency, pin bump or CI edit. The 15 ticks are proposed, not a
new ruling. The sector, arc, groups, backward trail cost, stamina and
cooldown are unchanged.

## Inputs verified
Base 9db10ce (pk06 head 49f3fe2 plus its materialized note).
Engine aa6c4dc0bc5071d3c07121451d913a8837cd2a6a, unchanged.
Wolf 0.2.35 cf0c13d, lupin 0.1.56, bundled std
2386522eb059cca5a84108562c2c0a0e72345d34. Both hosts stage the complete
release archive pair by the engine's fetcher and verify identity/digest.
notes/pk06b-evidence/digests-twice.txt records two matching API reads of
the Mac/Linux archive digests. The design, keys, sim, real pty hook and
pk06 evidence were read; no other game's code or material was consulted.

## Tests, goldens and score checks
160 checked tests with no SKIPs in the development suite. The sixteen-
subset aim table is replaced by real timing sequences: all eight diagonal
orders at 200/300/400 ms, cardinals and default; it asserts the first Hold
has lapsed. Two extra rows cover latest opposite per axis, same-tick byte
order, exact 15/16-tick boundary and unchanged steering release. Existing
sector/contact, backward, separation, camera, alternating group and replay
regressions remain. The new pty row checks the exact raw Hold snapshot as
well as the chosen aim in 58 sessions. The older 18 simultaneous-byte
sessions remain a decoder regression, explicitly not the diagonal proof.

Eight new golden cases cover both orders of every diagonal with only the
second key repeating for 400 ms. Tell and every arc tick are captured on
both glyph tiers: 38 cases x two tiers plus art = 77 directories. Every
pre-existing golden byte holds; no old golden is regenerated to excuse a
regression. New goldens land with the dated window behavior commit.

The final-head gate inventory is .lair/tools/check on nomad behind the
8 GB gate, and .lair/tools/in-container .lair/tools/check-linux on kasumi
under the shared cores-4-7 flock with LAIR_CPUS=4-7. It includes ten pty
rows, quit/typed-0x03/trap restoration, native/LLVM builds, selftest and
both glyph tiers. Native-backend goldens are checked separately as well.
Final-head results and log locations are recorded in PR Evidence.

Verified pk04-card/title scores remain 51/51 and were not re-recorded.
Fresh probes of both pk06 base and the window fix give leap-lands 856,
alternating-leap 4, unchanged. Correction to pk06's earlier note: its 958
claim for leap-lands is not reproduced by these fresh baseline/current
probes, nor by rerunning its preserved binary; the current measured value
is 856. This is an unverified golden scenario, not a moved verified score.
Raw fresh outputs are under notes/pk06b-evidence. No historical verified
record is rewritten. The earlier score discrepancy is reported rather
than guessed away or silently carried forward.

## Plant
PR 32, pk06b-plant-window, a921dc0, run 40213937781: setting the window
to zero fails test_pk06b_timing_table_diagonals_in_both_orders_cardinals_and_default
by name in its own CI Linux test step; the exact-boundary row fails too.
The mutant release binary also fails all 48 live diagonal sessions while
all ten cardinal/default controls pass. The draft remains open for the
coordinator, never to merge. Named CI lines and every local Hold/aim row
are preserved under notes/pk06b-evidence.

## Forbidden / follow-ons
No engine/pin/CI changes, other game material, model-server operations,
manual signal scripts, planning/memory/settings edits, attribution
trailers, merge, label, tag, release or issue action. The interrupt is the
engine pty runner's typed 0x03. README refreshed separately for controls,
counts and realistic timing coverage. Human play still judges the 500 ms
window; it intentionally accepts a recently released arrow and does not
claim true key-up. No new compiler/engine issue is established. This note
is committed as .txt and copied in full under the PR's Note.
