#!/bin/bash
# pk09 on hasu: unpack a tree, stage the engine at its pin and the pinned
# toolchain, build the lane's image (once). Usage: stage.sh NAME (trunk|head)
set -eu
export PATH=$HOME/lanes/hasu-env/bin:$HOME/lanes/hasu-env/profile/bin:$PATH
L=/home/mfwolffe/lanes/pk09/lane
export TMPDIR=$L/tmp
mkdir -p "$TMPDIR"
cd "$L"
name=$1
rm -rf "$name"
tar -xf "$name.tar"
cd "$name"
tools/fetch-lair
.lair/tools/fetch-toolchain
tag=$(sha256sum .lair/ci/Containerfile | cut -c1-16)
img=localhost/pk09-pack-ci:$tag
if ! podman image inspect "$img" >/dev/null 2>&1; then
    podman build --memory 12g -t "$img" -f .lair/ci/Containerfile .lair/ci
fi
echo "stage: $name ready, image $img"
