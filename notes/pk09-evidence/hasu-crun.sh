#!/bin/bash
# pk09 on hasu: run CMD in the lane's container, pinned with taskset INSIDE
# it to CPUS (block B is 6-11), holding both block-B locks for this run only
# (the block name outside), waiting in a loop that prints every 4 minutes.
# Usage: crun.sh CPUS TREE CMD...   (TREE under /home/mfwolffe/lanes/pk09/lane,
# mounted at /lane; the command runs in /lane/TREE)
set -u
export PATH=$HOME/lanes/hasu-env/bin:$HOME/lanes/hasu-env/profile/bin:$PATH
L=/home/mfwolffe/lanes/pk09/lane
img=localhost/pk09-pack-ci:fbee7e864f7dbee6
cpus=$1
tree=$2
shift 2
while :; do
    flock -E 75 -w 240 /home/mfwolffe/lanes/hasu-block-B.lock \
        flock -E 75 -w 240 /home/mfwolffe/lanes/hasu-B.lock \
        podman run --rm --memory 12g -v "$L:/lane" -w "/lane/$tree" "$img" taskset -c "$cpus" "$@"
    rc=$?
    [ "$rc" -eq 75 ] || exit "$rc"
    echo "crun: $(date +%T) block B is held; waiting" >&2
done
