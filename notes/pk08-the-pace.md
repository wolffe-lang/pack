# Note

pk08 — the pace. This complete note is in the PR body because the harness prohibits writing report `.md` files. Materialise it as `notes/pk08-the-pace.md` at merge.

## Before / after

20 seeds (1–20), centre trot, both sizes, full 180 seconds = 5,400 ticks at 30 Hz; retain the contract's original 4,320-tick checkpoint as 144 seconds (R-pk08-4). Here full health is restored before each step, so death does not censor the later counts; AI, motion, bodies and spawning still run. The largest clump is a visible connected component of same-bank lurkers linked within six cells and four rows, a conservative interpretation of “within one another”. Natural-health runs are preserved as MODE 0; they die and freeze before many late checkpoints. MODE 1/2/3 restore health to 100/50/25 before each step; the S rows record post-step health.

| field | first spawn median ticks before → after | range before → after | largest visible clump before → after | shadows alive 60 s before → after | 120 s | 144 s | 180 s |
|---|---|---|---|---|---|---|---|
| 80x24 | 453.5 → 759.5 | 73–1366 → 627–883 | 3 → 2 | 7.70 → 5.90 | 9.90 → 11.30 | 10.15 → 11.35 | 10.05 → 11.60 |
| 200x60 | 548.5 → 759.5 | 73–1366 → 627–883 | 7 → 5 | 7.45 → 5.40 | 11.10 → 11.20 | 10.65 → 11.10 | 11.95 → 11.50 |

Every first birth is lone and scheduled in 600–900 ticks (20–30 seconds); every subsequent successful event is at least 60 ticks later; no groups before tick 1800. The independent 100-seed full-health censuses reach maximum visible clumps **3 at 80x24 / 5 at 200x60**, first-birth range 605–898, median 754.5 ticks. Group admission considers offscreen lurkers as well. The 80-column second minute is more crowded (9.90 → 11.30 of the twelve-shadow cap); the opening is calmer, but this is not evidence that difficulty stayed unchanged.

Mean deer on screen across all seconds/seeds (health restored before each step; existing deer need not disappear on recovery):

| field | input health | before mean / max | after mean / max |
|---|---|---|---|
| 80x24 | 100 | 1.624 / 3 | 1.569 / 3 |
| 80x24 | 50 | 1.932 / 3 | 2.049 / 3 |
| 80x24 | 25 | 2.405 / 3 | 3.415 / 4 |
| 200x60 | 100 | 2.004 / 3 | 2.038 / 3 |
| 200x60 | 50 | 2.113 / 3 | 2.319 / 3 |
| 200x60 | 25 | 1.842 / 3 | 2.952 / 4 |

The full-health **controlled deer-only timelines at identical inputs** are byte-identical before/after at both sizes (`deer-full-{before,after}[-200].txt.gz`); the full-health unit test also compares exact birth ticks with the legacy roll/cap. The integrated centre-trot timeline above is not byte-identical: changing shadows changes collisions, movement and catches. No healthy deer rate or salt changed. The health term is zero at full, +50% at half, +100% at quarter or below, rounding fractional thousandths down. Only health strictly below half allows a fourth deer. Catch and feed mechanics are unchanged; there is no automatic healing.

### Survival control and ablations

The untouched pk03 probe now makes **zero leaps** on all five original seeds and dies by tick 2128; `survival-before.txt.gz` preserves that stale result. With the orchestrator's direction, the staged player changes only the attack condition to the crouch/windup, current directional reach, membership of the next alternating group, and aim arrows. Aim arrows also steer/sprint/stop as real keys do. The first five-seed runs remain beside the corrected controls.

R-pk08-5 corrects another fixture fault: “without deer” used to remove them only *after* step, letting a newborn affect separation for one tick. The staged simulation now disables spawning before separation in that control. The original ghost-deer outputs are retained, not presented as a true no-deer control. No gameplay flag or measurement instrumentation was added.

All following rows use the same adapted controller, seeds 1–20, and corrected no-deer control; death ticks, not an absolute 120-second survival promise, are the comparison.

| variant | mean death tick with deer | without deer | median with / without | alive at 120 s with / without |
|---|---:|---:|---|---|
| Before | 3293.70 | 3151.50 | 2979.5 / 2662.5 | 8 / 5 |
| Original interpolation: pacing only | 2886.60 | 2804.20 | 2756 / 2788 | 1 / 1 |
| Original interpolation: pacing + clump cap | 2878.85 | 2798.05 | 2756 / 2788 | 1 / 1 |
| Original interpolation: all changes | 2880.60 | 2798.05 | 2774 / 2788 | 2 / 1 |
| Centred interpolation + cap, bonus disabled | 3215.60 | 3008.55 | 2871 / 2965 | 5 / 2 |
| Final: centred interpolation + cap + bonus | 3188.20 | 3008.55 | 2899 / 2965 | 4 / 2 |

**Pacing carried the regression.** The first interpolation systematically filled above the old quantised bands. R-pk08-6 centres it by subtracting half a thousandth for each formerly floored body term (1000 millionths total) and 500 millionths from the ramp, retaining the 1000-millionth floor and the gap compensation. One correction was measured; no third seed-driven iteration was made.

**Unmet numbers:** final mean lifespan is still 3.2% shorter with deer and 4.5% shorter without than before. The deer bonus does not demonstrate the requested survival benefit: mean 3188.20 versus 3215.60 without bonus (−0.85%), and 4 rather than 5 of twenty alive at 120 seconds. The final no-deer rows are byte-identical with/without bonus. More prey is observable, but catching it and its body interactions do not guarantee a net survival gain for this player. The historic 2–3 minute curve is not claimed, and a green software gate does not turn these misses into acceptance. Candidate follow-up knobs, **not changed here**, are a slower `SPAWN_RAMP_ROWS` slope and a reduced gap-compensation strength; either needs a fresh prediction and the same controls, not controller retuning.

Per-seed death ticks, each cell with deer / without (all intermediate ablations retained):

| seed | before | pace only | pace + cap | original all | centred no bonus | final |
|---|---|---|---|---|---|---|
| 1 | 2414/2414 | 2685/2656 | 2685/2656 | 2799/2656 | 2685/2656 | 2799/2656 |
| 2 | 2323/2139 | 2269/2256 | 2269/2256 | 2269/2256 | 2300/2523 | 2300/2523 |
| 3 | 3650/4315 | 2820/2886 | 2820/2886 | 2820/2886 | 3622/3543 | 3622/3543 |
| 4 | 1919/1662 | 2545/2259 | 2545/2259 | 2545/2259 | 2708/3485 | 2708/3485 |
| 5 | 3616/3264 | 2932/2886 | 2932/2886 | 2932/2886 | 3579/2971 | 3579/2971 |
| 6 | 2828/2723 | 2446/2905 | 2446/2905 | 2446/2905 | 2994/3070 | 2994/3070 |
| 7 | 2345/2361 | 2736/2690 | 2736/2690 | 2736/2690 | 2736/2690 | 2736/2690 |
| 8 | 3926/2992 | 2384/2322 | 2384/2322 | 2384/2322 | 2384/2322 | 2384/2322 |
| 9 | 6585/6506 | 5076/5034 | 4931/4935 | 4779/4935 | 5160/5118 | 5482/5118 |
| 10 | 2346/2346 | 2295/2274 | 2295/2274 | 2295/2274 | 2322/2351 | 2322/2351 |
| 11 | 3318/4722 | 3131/3120 | 3131/3120 | 3131/3120 | 4306/4306 | 4306/4306 |
| 12 | 2560/2602 | 2749/1873 | 2749/1873 | 2749/1873 | 2861/1873 | 2861/1873 |
| 13 | 2502/1973 | 2576/2269 | 2576/2269 | 2576/2269 | 2620/2645 | 2592/2645 |
| 14 | 3842/3693 | 2295/2229 | 2295/2229 | 2295/2229 | 4742/2434 | 4038/2434 |
| 15 | 3131/2543 | 3319/3440 | 3319/3440 | 3319/3440 | 3736/3506 | 3466/3506 |
| 16 | 4907/3555 | 3401/3250 | 3401/3250 | 3401/3250 | 3422/3126 | 3422/3126 |
| 17 | 4532/4697 | 2920/3126 | 2920/3126 | 2869/3126 | 2834/2962 | 2917/2962 |
| 18 | 1680/3516 | 2763/2963 | 2763/2963 | 2709/2963 | 2881/2968 | 2881/2968 |
| 19 | 2654/2504 | 3552/3278 | 3542/3254 | 3721/3254 | 3582/3254 | 3518/3254 |
| 20 | 4796/2503 | 2838/2368 | 2838/2368 | 2837/2368 | 2838/2368 | 2837/2368 |

The host reboot at 16:21 EDT on 2026-10-25 cut the first `survival20-clump` execution before it wrote any row. Completed `survival20-before` and `survival20-pace` outputs survived in the worktree and were not rerun; only the empty clump run and subsequent final run resumed. The reported host panic was IOGPUFamily; this note makes no causal claim about the game or probe. All work and scratch stayed under `~/lanes/pk08/`; memory gates waited three minutes and retried below 8 GB free+inactive+speculative. No packages, pool hosts or servers were touched.

## Prediction

Committed before the first simulation edit: `fb16b780712770f3c464c68015af515e90c16585`, `notes/pk08-evidence/prediction.txt`, including the before table. Expected median first birth 750±100 ticks, all first births 600–900 and lone, gap≥60, no groups before1800, clumps≤5 over100seeds, alive60 in5–9 and alive120 in9–12 at both sizes. All these numerical pace predictions hit. Healthy isolated deer equality hit; bonus survival benefit missed as above.

Recommendations implemented, never decided by the lane: R-pk08-1 A (continuous roll plus deadline/gap), R-pk08-2 A then B (other bank, otherwise defer), R-pk08-3 A (bounded health bonus/fourth deer). The orchestrator accepted R-pk08-4 (30 Hz correction), R-pk08-5 (true no-deer control and twenty seeds), R-pk08-6 (centred interpolation). `docs/DESIGN.md` marks proposed constants; no further tuning iteration is hidden.

## Forbidden

Original work only; no other game's code, assets, text or music. No engine, pin, CI, toolchain, host configuration or planning-repository change. No package installation, pool/server access, labels, merge, tag, release or issues filed/closed. No attribution/co-author trailers. No CI polling or waiting; each immediate single listing after a plant PR opened returned `[]`, a registration race, and was not retried. Orchestrator recovers the ids and verifies Linux named reds.

## Inputs verified

- Base `8d02cfda`, fetched from pack trunk; worktree `/Users/mfwolffe/lanes/pk08/pack`, branch `pk08`.
- Engine `aa6c4dc0bc5071d3c07121451d913a8837cd2a6a`, unchanged `lair.pin`, staged with `tools/fetch-lair`.
- wolf0.2.35 `cf0c13d38479f444b69bb8356ad5709d07eff323`, archive SHA256 `240b84d079b1b9a0d88681ac08fca4816f84778e2d6c94c435ceb2dd6a5f042a`.
- lupin0.1.56 `28547b4324524d5477a6e54e4f6888462461a21f`, archive SHA256 `9133bfdbb95f6a18745439bf0b2b5280860a5bfeaf9ae038ea120a72d58f7687`.
- std `2386522eb059cca5a84108562c2c0a0e72345d34`. The pinned fetcher verified archive digests; release API digests, staged stamp, engine identity and std revision read twice again and identical.
- README, DESIGN, sim module/spawn/lurker/deer code, trail curve, pk03/pk07 notes and fixtures, lair engine design, campaign, RULES§1–10 and wolf guide read. README refreshed for the opening, groups, deer, `--start` and175 tests.

## Evidence index

- `notes/pk08-evidence/stage.py`, `census.lu.in`, `survival.lu.in`, `summarise.py`, `verify.py`: staged fixtures, never gameplay instrumentation. Release probes use the pinned compiler with `WOLF_MIDEND=0`, behind `/Users/mfwolffe/lanes/pk08/run` (8 GB memory check/retry and exec).
- `before-{80x24,200x60}.txt.gz`, `final-{80x24,200x60}.txt.gz`: per-second shadow/deer/health samples, each birth's seed/tick and id (group size is the number of births at that tick), every ten-second bin reproducible by `summarise.py`. `after-*.txt.gz` are the first, upward-biased interpolation, not the final curve.
- `final-clumps-{80,200}.txt.gz`: final100-seed clump censuses; `clumps-100-*.txt.gz` retain the intermediate curve. `verify.py` checks record counts, first bounds, actual event gaps, early groups, deer cap,100-seed cap and control equalities without rerunning simulations.
- `deer-full-{before,after}[-200].txt.gz`: byte-identical healthy isolated timelines. `survival-before`, `playing-{before,after}`, `no-bonus` preserve stale/initial controls; `survival20-{before,pace,clump,after,centred-no-bonus,centred}.txt.gz` hold every ablation above.
- Both terminal recordings redone using `notes/pk07-evidence/record.py`; `recorded-{card,title}.pk` copied to `tests/replays/pk04-{card,title}.pk`, score185 pinned. Fixed the recorder's double-wait bug (a reaped WNOHANG child was waited a second time). Real pty replay tests pass.
- Six shadow golden cases retimed to meaningful first births, windup884/landing896, leap884 and parry895; the zero-health death case dies933. Twelve directories moved: `death-card-{plain,rich}`, `group-attack-{plain,rich}`, `leap-lands-{plain,rich}`, `parry-turns-{plain,rich}`, `shadow-lunge-{plain,rich}`, `spawn-chase-{plain,rich}`. Other directories and art held. `golden-trace.txt.gz` records event timing.
- Final-head local `.lair/tools/check`: **green**,175 passed,0 failed/rejected/unsupported/SKIP; native and release builds, selftest,77 golden directories, all ten named pty rows including18 fresh directional sessions and58 aim-window sessions. Log `/Users/mfwolffe/lanes/pk08/check-at-final-head.log` (began2026-10-25 16:45 EDT, head `e10835f2818ada427bc2d74f1171653af3ffdce1`). Linux x86-64 evidence comes from this PR's CI, not the Mac.
- Draft plant #37 `pk08-plant-gap`, head `f3dc37a`: local `test_pk08_spawn_gap_and_no_groups_in_first_minute` FAILED;174pass/1fail.
- Draft plant #38 `pk08-plant-clump`, head `3adf298`: local `test_pk08_clump_cap_seeds_1_10` and nine other batches FAILED;165pass/10fail.
- Draft plant #39 `pk08-plant-deer`, head `2a2f725`: local `test_pk08_deer_bonus_zero_at_full_and_capped` and `test_pk08_full_health_deer_birth_timeline_matches_legacy` FAILED;173pass/2fail. Plant logs `/Users/mfwolffe/lanes/pk08/plant-{gap,clump,deer}.log`. Immediate CI listings returned[]; orchestrator verification remains.

Related commits:
- `131b45f` paced simulation, bank admission and health bonus.
- `aea28ba`, `66060a1` fine-rate interpolation and its measured centring correction.
- `f08787e` regression tests; `fe2a760` replays; `0e0a3cf` recorder reaping.
- `613021e`, `e8b868d` DESIGN/README; `0f6aa96`, `02032ab` meaningful capture windows and goldens.
- `6604763`, `e10835f` compressed final evidence and its verifier.

## Done-when

- [x] Prediction committed before simulation edits; before/after at both sizes,180 seconds and144-second checkpoint.
- [x] First birth, gap, group gate, clump cap100seeds, health zero/cap tests; healthy controlled deer equality.
- [x] Final-head complete local gate green,175 tests and0 SKIP; meaningful goldens; both recorded replays reverified.
- [x] Three draft fault plants locally red by name, open for the orchestrator.
- [x] Proposed constants and README current; no engine/pin/CI changes.
- [ ] Linux `tier pr` green at final head and the three plant runs red by their named rows (orchestrator; no lane wait).
- [ ] Survival parity and deer survival-benefit targets: **not demonstrated**, quantitative misses above; play/ruling remains, not an automatic green from tests.
- [ ] Materialise this Note as `notes/pk08-the-pace.md` at merge; read the actual audit result before merging.

Play `/Users/mfwolffe/lanes/pk08/pack/target/pack` (also `target/release/pack`), especially a wide terminal. Prune only this lane's `/Users/mfwolffe/lanes/pk08/pack/target/` staged probes/build outputs when no longer needed, then `.wolf-bin/`, `.lair/`, `/Users/mfwolffe/lanes/pk08/scratch/` and this one worktree at close; retain the play binary until play and logs until audit. No other worktree or host directory is in the prune list. No issue is filed or closed by this lane; report the stale historical control and unmet survival benefit if a follow-up is wanted.

