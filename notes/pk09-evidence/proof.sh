#!/bin/bash
# notes/pk09-evidence/proof.sh — pk09's proof under the forced stall.
#
#   proof.sh RUNS LOAD OUT TRUNK_TREE TRUNK_BIN HEAD_TREE HEAD_BIN
#
# Run k (1..RUNS) is trunk's aim-window row, then the head's, each its own
# locked run (the lane's Mac wrapper: the mkdir build lock and the 8 GiB
# gate, mac-lock-run.sh here) of the engine's pty runner, `--rows
# aim-window`, inside stall.py's background clamp and LOAD busy processes.
# Each tree is a worktree pinned to its commit with `.lair/` staged at the
# pin; each binary was built from its commit. Interleaving the two rows
# gives them the same machine, hour and load. Every run prints `PROOF
# <label> run=<k> exit=<rc>`; 0 is green, 1 is red, anything else (3: the
# memory gate refused) stops the proof, since it is no verdict.
set -u
RUNS=$1 LOAD=$2 OUT=$3 TRUNK_TREE=$4 TRUNK_BIN=$5 HEAD_TREE=$6 HEAD_BIN=$7
WRAP=${PK09_WRAP:-/Users/mfwolffe/lanes/pk09/run}
STALL=$HEAD_TREE/notes/pk09-evidence/stall.py
mkdir -p "$OUT"
for k in $(seq -w 1 "$RUNS"); do
    for label in trunk head; do
        if [ "$label" = trunk ]; then tree=$TRUNK_TREE bin=$TRUNK_BIN; else tree=$HEAD_TREE bin=$HEAD_BIN; fi
        log=$OUT/$label-$k.log
        PK09_TREE=$tree "$WRAP" taskpolicy -c background python3 -I "$STALL" --load "$LOAD" -- \
            python3 -I .lair/tools/pty --bin "$bin" --rows aim-window >"$log" 2>&1
        rc=$?
        cp "$tree/target/pty/aim-window.txt" "$OUT/$label-$k-sessions.txt" 2>/dev/null || true
        echo "PROOF $label run=$k exit=$rc $(date +%H:%M:%S)"
        if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
            echo "PROOF STOPPED: $label run $k exited $rc (no verdict); see $log"
            exit 2
        fi
    done
done
for label in trunk head; do
    green=$(grep -l '^pty: aim-window ok' "$OUT"/$label-*.log 2>/dev/null | wc -l | tr -d ' ')
    red=$(grep -l '^pty: aim-window FAILED' "$OUT"/$label-*.log 2>/dev/null | wc -l | tr -d ' ')
    echo "PROOF SUMMARY $label: $green green, $red red of $RUNS"
done
echo "PROOF DONE"
