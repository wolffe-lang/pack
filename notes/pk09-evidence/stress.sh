#!/bin/bash
# notes/pk09-evidence/stress.sh — two runs past the proof, each inside the Mac
# lock from the head's pinned tree: the aim-window row under the heavy stall
# (the background clamp and 12 busy processes, which starve the row itself),
# and every pty row under the proof's stall (one busy process). Every step
# runs and prints `END <step> exit=N`; these are measurements, not gates.
set -u
step() {
    name=$1
    shift
    "$@"
    echo "END $name exit=$?"
}
echo "stress: $(git rev-parse HEAD) at $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname -s)"
step aim-window-load12 taskpolicy -c background python3 -I notes/pk09-evidence/stall.py --load 12 -- \
    python3 -I .lair/tools/pty --bin target/release/pack --rows aim-window
cp target/pty/aim-window.txt target/pty/aim-window-load12.txt 2>/dev/null
step all-rows-load1 taskpolicy -c background python3 -I notes/pk09-evidence/stall.py --load 1 -- \
    python3 -I .lair/tools/pty --bin target/release/pack
