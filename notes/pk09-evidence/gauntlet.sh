#!/bin/bash
# notes/pk09-evidence/gauntlet.sh TREE — the final-head gauntlet on the Mac:
# the engine's `tools/check` list, one step at a time, each exit read
# directly, stopping on the first nonzero, every step printing
# `END <step> exit=N`; plus the aim-window oracle's controls on their own.
# TREE is a worktree pinned to the head commit with `.lair/` and
# `.wolf-bin/` staged (the lane rules: build from a commit, never the live
# tree). Run inside the Mac build lock and its memory gate.
set -u
cd "$1" || exit 2
LAIR_ROOT=$PWD/.lair
export LAIR_ROOT
step() {
    name=$1
    shift
    "$@"
    rc=$?
    echo "END $name exit=$rc"
    [ "$rc" -eq 0 ] || exit "$rc"
}
echo "gauntlet: $(git rev-parse HEAD) at $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname -s)"
step lair-pin test "$(cat .lair/LAIR-REV)" = "$(sed -n 's/^\([0-9a-f]\{40\}\).*/\1/p' lair.pin | head -1)"
step clean-tree test -z "$(git status --porcelain --untracked-files=no)"
step check-fmt .lair/tools/check-fmt
step test .lair/tools/test
step build .lair/tools/build --all
step selftest target/release/pack --selftest
step goldens .lair/tools/goldens
step aim-controls python3 -I tests/pty_rows.py
step pty python3 -I .lair/tools/pty --bin target/release/pack
echo "gauntlet: green at $(git rev-parse HEAD)"
