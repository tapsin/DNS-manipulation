#!/bin/sh
# AppDir'den AppImage üretir. Çıktı masaüstündeki dns klasörüne kopyalanır.
set -e
cd "$(dirname "$0")"

# nfqws yoksa zapret'ten derle; arayüz kodunu AppDir içine kopyala
if [ ! -x AppDir/usr/bin/nfqws ]; then
    sh scripts/fetch-nfqws.sh
fi
cp discord_unblock.py AppDir/usr/bin/discord_unblock.py
chmod +x AppDir/AppRun AppDir/usr/bin/discord-unblock-run AppDir/usr/bin/nfqws

if [ ! -x appimagetool ]; then
    curl -fsSL -o appimagetool "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool
fi

ARCH=x86_64 ./appimagetool --appimage-extract-and-run AppDir discord-unblock-x86_64.AppImage

mkdir -p "$HOME/Desktop/dns"
cp discord-unblock-x86_64.AppImage "$HOME/Desktop/dns/"
echo "Hazır: $HOME/Desktop/dns/discord-unblock-x86_64.AppImage"
