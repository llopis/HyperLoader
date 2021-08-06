#!/bin/sh
set -e			# Stop on any failure
rm -rf build
mkdir -p build

sjasmplus --nologo --msg=war --raw=build/hyperld.bin --lst=build/HyperLd_list.txt src/Main.asm
iDSK -n build/HyperLoader.dsk > /dev/null 2>&1
iDSK build/HyperLoader.dsk -e 4000 -c 4000 -t 1 -i build/hyperld.bin > /dev/null 2>&1
