#!/bin/bash
# pk09's Mac wrapper: the Mac build lock (mkdir directory protocol, pid and
# lane inside), the 8 GiB vm_stat gate inside the lock (a printing wait
# loop), then the command, waited on; the lock removed by its holder only.
set -u
LOCK=/Users/mfwolffe/lanes/mac-build.lock
export TMPDIR=/Users/mfwolffe/lanes/pk09/tmp
export LAIR_LANE_HOST=nomad
mkdir -p "$TMPDIR"
until mkdir "$LOCK" 2>/dev/null; do
    holder=$(cat "$LOCK/pid" 2>/dev/null || true)
    lane=$(cat "$LOCK/lane" 2>/dev/null || true)
    if [ -n "$holder" ] && ! kill -0 "$holder" 2>/dev/null; then
        echo "pk09: the lock's holder pid $holder ($lane) is dead; removing the lock" >&2
        rm -rf "$LOCK"
        continue
    fi
    echo "pk09: $(date +%H:%M:%S) the Mac build lock is held by pid ${holder:-?} (${lane:-?}); waiting" >&2
    sleep 30
done
echo $$ >"$LOCK/pid"
echo pk09 >"$LOCK/lane"
trap 'rm -rf "$LOCK"' EXIT
while :; do
    pages=$(vm_stat | awk '/Pages (free|inactive|speculative)/ {gsub("\\.","",$NF); s+=$NF} END {printf "%d", s}')
    bytes=$((pages * 16384))
    if [ "$bytes" -ge $((8 * 1024 * 1024 * 1024)) ]; then
        echo "pk09: $(date +%H:%M:%S) gate ok: $((bytes / 1048576)) MiB free+inactive+speculative" >&2
        break
    fi
    echo "pk09: $(date +%H:%M:%S) gate: $((bytes / 1048576)) MiB < 8 GiB; waiting" >&2
    sleep 60
done
cd "${PK09_TREE:-/Users/mfwolffe/lanes/pk09/pack}"
"$@" &
child=$!
wait "$child"
rc=$?
exit "$rc"
