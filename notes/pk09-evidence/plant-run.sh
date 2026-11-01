#!/bin/bash
# notes/pk09-evidence/plant-run.sh — the plant's local run, inside the Mac
# lock (run from its worktree, pinned to the plant commit): the release
# build, then the unit tests, the aim-window row, and the row again under
# the forced stall (the background clamp and one busy process). Every step
# prints `END <step> exit=N` and every step runs: a plant is expected red.
set -u
step() {
    name=$1
    shift
    "$@"
    echo "END $name exit=$?"
}
echo "plant-run: $(git rev-parse HEAD) at $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname -s)"
step build .lair/tools/build --release
step test .lair/tools/test
step aim-window python3 -I .lair/tools/pty --bin target/release/pack --rows aim-window
cp target/pty/aim-window.txt target/pty/aim-window-unstalled.txt 2>/dev/null
step aim-window-stalled taskpolicy -c background python3 -I notes/pk09-evidence/stall.py --load 1 -- \
    python3 -I .lair/tools/pty --bin target/release/pack --rows aim-window
