# DNS-manipulation: Discord bağlantı aracı

Bu araç, Discord'a giden HTTPS bağlantısını ağdaki DPI cihazının kesmesini engellemek için [zapret](https://github.com/bol-van/zapret) araçlarını (`nfqws` ve Windows'ta `winws`) başlatıp durdurur.

- DNS ayarlarını **değiştirmez**.
- Bir proxy veya VPN **kullanmaz**. Bağlantın doğrudan Discord'a gider.
- Başlat (**Start**) ve Durdur (**Stop**) butonu olan küçük bir pencere açar.
- Eksik olan parçaları açılışta kontrol eder ve mümkünse kurar.

> Bu araç yalnızca kendi bağlantın için tasarlandı. Kullanımının yerel mevzuata uygunluğundan sen sorumlusun.

---

## Windows (adım adım)

### 1. Python'u kur

1. Tarayıcıyla <https://www.python.org/downloads/> adresine git.
2. Sarı **Download Python** düğmesine bas.
3. İndirilen dosyayı aç.
4. Açılan pencerenin **en altında** olan **"Add python.exe to PATH"** kutucuğunu işaretle.
5. **Install Now** düğmesine bas ve bitmesini bekle.

### 2. Bu projeyi indir

1. Bu sayfanın üstündeki yeşil **Code** düğmesine bas.
2. **Download ZIP**'e tıkla.
3. İnen zip dosyasına sağ tıkla → **Tümünü ayıkla** → masaüstünü seç.
4. Oluşan klasörün adı `DNS-manipulation` olsun.

### 3. zapret'in Windows dosyalarını indir

1. Tarayıcıyla <https://github.com/bol-van/zapret/releases> adresine git.
2. En üstteki (en yeni) sürümü bul ve içindeki Windows zip dosyasını indir.
3. Zip'i aç. İçinde `winws` geçen bir klasör göreceksin, o klasörü aç.
4. Şu üç dosyayı kopyala:
   - `winws.exe`
   - `WinDivert.dll`
   - `WinDivert64.sys`
5. Bunları **`DNS-manipulation`** klasörünün içine yapıştır. `discord_unblock.py` dosyasının yanında olmalılar.

Klasörün son hali şöyle görünmeli:

```
DNS-manipulation\
  discord_unblock.py
  winws.exe
  WinDivert.dll
  WinDivert64.sys
  README.md
```

### 4. Programı yönetici olarak çalıştır

Program yönetici yetkisi ister. Bu yüzden şöyle açacaksın:

1. Başlat menüsüne `cmd` yaz.
2. **Komut İstemi**'ne sağ tıkla → **Yönetici olarak çalıştır** → **Evet**.
3. Klasöre gir. Masaüstünde kaydettiysen şunu yaz (kullanıcı adını kendine göre değiştir):

   ```
   cd C:\Users\KULLANICI_ADIN\Desktop\DNS-manipulation
   ```

4. Programı başlat:

   ```
   python discord_unblock.py
   ```

Pencere açılır. Eksik dosya varsa bir uyarı çıkar ve zapret sayfasını açmayı teklif eder.

### 5. Kullan

1. Pencerede **Start**'a bas. Durum yeşil **Çalışıyor** olur.
2. Discord'u aç.
3. İşin bitince **Stop**'a bas ve pencereyi kapat.

> İstersen `discord_unblock.py` dosyasını tek bir `.exe` dosyasına çevirebilirsin:
> `pip install pyinstaller` ardından `pyinstaller --onefile --windowed --uac-admin discord_unblock.py` komutu. Oluşan `dist\discord_unblock.exe` dosyasını `winws.exe` ve WinDivert dosyalarının yanına koy. Bu sürümde Python kurmana gerek kalmaz.

---

## Linux (Pop!_OS, Ubuntu, Debian)

### 1. Terminali aç

Klavyede `Ctrl + Alt + T` bas.

### 2. Gerekli paketleri kur

Şu komutu yapıştır, Enter'a bas ve yönetici şifreni gir:

```bash
sudo apt install -y git make gcc libnetfilter-queue-dev libnfnetlink-dev libmnl-dev libcap-dev zlib1g-dev python3-tk
```

Bu, nfqws'i derlemek ve arayüzü açmak için gereken paketleri kurar.

### 3. Projeyi indir

```bash
cd ~/Desktop
git clone https://github.com/KULLANICI_ADIN/DNS-manipulation.git
cd DNS-manipulation
```

`KULLANICI_ADIN` yerine GitHub kullanıcı adını yaz.

### 4. nfqws'i derle

```bash
sh scripts/fetch-nfqws.sh
```

zapret kaynağını indirir ve `nfqws` programını derler. Birkaç saniye sürer. Sonunda `nfqws hazır` yazısını görmelisin.

### 5. Programı oluştur

```bash
sh build-appimage.sh
```

Bu komut AppImage üretir ve `~/Desktop/dns/` klasörüne kopyalar. İnternet bağlantısı gerekir, çünkü `appimagetool` aracını indirir.

### 6. Programı çalıştır

Masaüstündeki `dns` klasörüne git. `discord-unblock-x86_64.AppImage` dosyasına çift tıkla.

Çalışmazsa terminalden dene:

```bash
chmod +x ~/Desktop/dns/discord-unblock-x86_64.AppImage
~/Desktop/dns/discord-unblock-x86_64.AppImage
```

Pencere açılınca **Start**'a bas. Yönetici şifresi sorulursa gir. Durum yeşil **Çalışıyor** olur.

### 7. Kullan

1. Discord'u aç.
2. İşin bitince **Stop**'a bas ve pencereyi kapat.

> **İpucu:** AppImage'ı kurmadan denemek istersen `python3 AppDir/usr/bin/discord_unblock.py` komutunu da kullanabilirsin.

---

## Sorun giderme

| Belirti | Ne yapmalı |
|---|---|
| Discord hâlâ açılmıyor | Logu aç: Linux'ta `cat ~/discord-unblock.log`, Windows'ta `%USERPROFILE%\discord-unblock.log` dosyası. Hata metnini bir issue'ya yapıştır. |
| Windows'ta "yönetici olarak çalıştırın" uyarısı | `cmd`'yi yönetici olarak açtığından emin ol (adım 4). |
| Linux'ta şifre penceresi çıkmıyor | `sudo apt install -y policykit-1` çalıştır ve programı yeniden aç. |
| Discord açılıyor ama ses/görüntülü arama çalışmıyor | Bu araç yalnızca TCP 443 trafiğini düzeltir. Ses trafiği UDP kullanır ve bu sürümde kapsanmıyor. |
| Eksik dosya uyarısı | Windows'ta 3. adımdaki üç dosyanın doğru klasörde olduğunu kontrol et. Linux'ta `sh scripts/fetch-nfqws.sh` komutunu tekrar çalıştır. |

---

## Proje dosyaları

| Dosya | Ne işe yarar |
|---|---|
| `discord_unblock.py` | Start/Stop arayüzü ve açılış kontrolleri (Linux ve Windows). |
| `AppDir/` | AppImage'ın içeriği: giriş noktası, masaüstü girdisi, ikon ve Linux çalıştırıcı betiği. |
| `scripts/fetch-nfqws.sh` | zapret'ten `nfqws`'i indirip derler. |
| `build-appimage.sh` | AppImage üretir. |
