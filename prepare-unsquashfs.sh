#!/bin/sh
set -e

git clone https://github.com/plougher/squashfs-tools

patch -p0 <squashfs-tools.patch

cd squashfs-tools/squashfs-tools
make unsquashfs

echo unsquashfs prepared
echo squashfs-tools/squashfs-tools/unsquashfs
