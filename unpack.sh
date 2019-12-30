#!/bin/bash
set -e

[ $# -lt 1 ] && echo "$0 FILE" && exit 1

file="$(realpath "$1")"
cd "$(dirname "$0")"

if [ ! -d squashfs-tools ]; then
  echo "==> Building patched unsquashfs"
  ./prepare-unsquashfs.sh
fi

unsquashfs="$(realpath squashfs-tools/squashfs-tools/unsquashfs)"

echo "==> Decrypting the file"
python3 decryptor.py "$file"

echo "==> Unpacking using binwalk"

# binwalk can't unpack that squashfs file
set +e

cd "$(dirname "$file")"
file="$(basename "$file")"

binwalk -e "$file.raw"

set -e

cd "_$file.raw.extracted"

rm -rf squashfs-root

echo "==> Unpacking the squashfs file"
"$unsquashfs" *.squashfs

echo
echo "=== Voila! ==="
echo "See the $(realpath squashfs-root) directory"
