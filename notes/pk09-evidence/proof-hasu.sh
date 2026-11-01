#!/bin/bash
# notes/pk09-evidence/proof-hasu.sh — the literal one-CPU witness on hasu,
# block B: run k (1..RUNS) is trunk's aim-window row, then the head's, each
# its own container run (crun.sh: both block-B locks for that run only)
# pinned by `taskset -c 6` INSIDE the container, so the pty runner, the
# game and stall.py's one busy process share one CPU. Trees are
# /home/mfwolffe/lanes/pk09/lane/{trunk,head}, each `git archive` of its
# commit with the engine and the x86-64 toolchain staged and the release
# binary built in the same image. Started with `setsid -f`; writes a pid
# file, a log and an exit marker.
#   proof-hasu.sh RUNS LOAD
set -u
L=/home/mfwolffe/lanes/pk09/lane
RUNS=$1 LOAD=$2
OUT=$L/proof
mkdir -p "$OUT"
echo $$ >"$OUT/pid"
rm -f "$OUT/exit"
for k in $(seq -w 1 "$RUNS"); do
    for label in trunk head; do
        bash "$L/crun.sh" 6 "$label" python3 -I /lane/stall.py --load "$LOAD" -- \
            python3 -I .lair/tools/pty --bin target/release/pack --rows aim-window >"$OUT/$label-$k.log" 2>&1
        rc=$?
        cp "$L/$label/target/pty/aim-window.txt" "$OUT/$label-$k-sessions.txt" 2>/dev/null || true
        echo "PROOF $label run=$k exit=$rc $(date +%T)"
        if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
            echo "PROOF STOPPED: $label run $k exited $rc"
            echo 2 >"$OUT/exit"
            exit 2
        fi
    done
done
for label in trunk head; do
    green=$(grep -l '^pty: aim-window ok' "$OUT"/$label-*.log | wc -l)
    red=$(grep -l '^pty: aim-window FAILED' "$OUT"/$label-*.log | wc -l)
    echo "PROOF SUMMARY $label: $green green, $red red of $RUNS"
done
echo "PROOF DONE"
echo 0 >"$OUT/exit"
