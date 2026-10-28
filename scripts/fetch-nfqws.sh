#!/bin/sh
# zapret kaynağını indirir, nfqws'i derler ve AppDir içine koyar.
# Kullanım (proje klasöründen): sh scripts/fetch-nfqws.sh
set -e
cd "$(dirname "$0")/.."

if [ ! -d build/zapret ]; then
    mkdir -p build
    git clone --depth 1 https://github.com/bol-van/zapret.git build/zapret
fi

make -C build/zapret/nfq
mkdir -p AppDir/usr/bin
cp build/zapret/nfq/nfqws AppDir/usr/bin/nfqws
echo "nfqws hazır: AppDir/usr/bin/nfqws"
