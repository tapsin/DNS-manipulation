#!/usr/bin/env python3
"""Discord bypass: Başlat / Durdur arayüzü.

Linux: nfqws + iptables (discord-unblock-run betiği, pkexec ile root).
Windows: winws.exe (zapret), yönetici olarak çalıştırılmalı.
Açılışta eksik bağımlılıklar kontrol edilir ve mümkünse kurulur.
"""
import ctypes
import os
import shutil
import subprocess
import sys
import webbrowser

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    tk = None

IS_WINDOWS = sys.platform == "win32"
BASE = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)
LOG_PATH = os.path.join(os.path.expanduser("~"), "discord-unblock.log")

# Linux
NFQWS = os.path.join(BASE, "nfqws")
RUN_SCRIPT = os.path.join(BASE, "discord-unblock-run")
# komut -> apt paketi
LINUX_COMMANDS = {"iptables": "iptables", "pkexec": "policykit-1", "pkill": "procps"}
# nfqws'in ihtiyaç duyduğu paylaşımlı kütüphane -> apt paketi
LINUX_LIBS = {
    "libnetfilter_queue.so.1": "libnetfilter-queue1",
    "libnfnetlink.so.0": "libnfnetlink0",
    "libmnl.so.0": "libmnl0",
}

# Windows
WINWS = os.path.join(BASE, "winws.exe")
WINWS_ARGS = ["--wf-tcp=443", "--dpi-desync=fake", "--dpi-desync-ttl=6"]
WINWS_FILES = ["winws.exe", "WinDivert.dll", "WinDivert64.sys"]
ZAPRET_RELEASES_URL = "https://github.com/bol-van/zapret/releases"
CREATE_NO_WINDOW = 0x08000000


def linux_missing_packages():
    packages = set()
    for cmd, pkg in LINUX_COMMANDS.items():
        if shutil.which(cmd) is None:
            packages.add(pkg)
    if os.path.exists(NFQWS):
        out = subprocess.run(["ldd", NFQWS], capture_output=True, text=True).stdout
        for lib, pkg in LINUX_LIBS.items():
            if f"{lib} => not found" in out:
                packages.add(pkg)
    return sorted(packages)


def windows_missing_files():
    return [f for f in WINWS_FILES if not os.path.exists(os.path.join(BASE, f))]


def ensure_dependencies():
    """Açılışta çağrılır. Her şey hazırsa True döner."""
    if IS_WINDOWS:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showerror("Yönetici gerekli",
                                 "Programı yönetici olarak çalıştırmalısın.")
            return False
        missing = windows_missing_files()
        if not missing:
            return True
        if messagebox.askyesno(
            "Eksik dosyalar",
            "Şu dosyalar eksik:\n" + "\n".join(missing) +
            "\n\nzapret Windows sürümünü indirme sayfasını açayım mı?\n"
            "Arşivden winws.exe, WinDivert.dll ve WinDivert64.sys dosyalarını bu klasöre koy.",
        ):
            webbrowser.open(ZAPRET_RELEASES_URL)
        return False

    if not os.path.exists(NFQWS) or not os.path.exists(RUN_SCRIPT):
        messagebox.showerror("Eksik dosyalar",
                             "nfqws veya discord-unblock-run bulunamadı. Program dosyaları eksik.")
        return False

    packages = linux_missing_packages()
    if not packages:
        return True
    if not messagebox.askyesno(
        "Eksik paketler",
        "Şu sistem paketleri eksik:\n" + "\n".join(packages) +
        "\n\nYönetici şifresiyle kurulsun mu?",
    ):
        return False
    result = subprocess.run(["pkexec", "apt-get", "install", "-y", *packages])
    if result.returncode != 0:
        messagebox.showerror(
            "Kurulamadı",
            "Paketler kurulamadı. Terminalden deneyebilirsin:\nsudo apt install " + " ".join(packages),
        )
        return False
    if linux_missing_packages():
        messagebox.showerror("Kurulamadı", "Bazı paketler hâlâ eksik. Programı yeniden başlat.")
        return False
    return True


class DiscordUnblockApp:
    def __init__(self, root):
        self.root = root
        self.proc = None
        self.log = None

        root.title("Discord Unblock")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.status = tk.Label(root, text="Durduruldu", font=("Sans", 14, "bold"), fg="gray")
        self.status.pack(padx=20, pady=(20, 10))

        buttons = tk.Frame(root)
        buttons.pack(padx=20, pady=(0, 20))
        self.start_btn = tk.Button(buttons, text="Start", width=10, bg="#2e7d32", fg="white",
                                   command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(buttons, text="Stop", width=10, bg="#c62828", fg="white",
                                  command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.poll()

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def start(self):
        if self.is_running():
            return
        try:
            self.log = open(LOG_PATH, "a")
            if IS_WINDOWS:
                self.proc = subprocess.Popen(
                    [WINWS] + WINWS_ARGS, cwd=BASE, stdout=self.log, stderr=self.log,
                    creationflags=CREATE_NO_WINDOW,
                )
            else:
                # Root için pkexec; çıkışta iptables kuralını run betiği temizler
                self.proc = subprocess.Popen(
                    ["pkexec", RUN_SCRIPT, NFQWS], stdout=self.log, stderr=self.log,
                )
        except OSError as e:
            messagebox.showerror("Hata", f"Başlatılamadı:\n{e}")
            self.proc = None
        self.refresh()

    def stop(self):
        try:
            if IS_WINDOWS:
                subprocess.run(["taskkill", "/F", "/IM", "winws.exe"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=CREATE_NO_WINDOW)
            else:
                # nfqws'e SIGINT gönder; run betiği çıkışta iptables kuralını siler
                subprocess.run(["pkexec", "pkill", "-INT", "-x", "nfqws"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if self.proc is not None:
                try:
                    self.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        except OSError as e:
            messagebox.showerror("Hata", f"Durdurulamadı:\n{e}")
        self.proc = None
        self.close_log()
        self.refresh()

    def close_log(self):
        if self.log is not None:
            self.log.close()
            self.log = None

    def refresh(self):
        if self.is_running():
            self.status.config(text="Çalışıyor", fg="#2e7d32")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status.config(text="Durduruldu", fg="gray")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def poll(self):
        # Süreç kendiliğinden kapanmışsa (hata, Ctrl+C vb.) arayüzü güncelle
        if self.proc is not None and self.proc.poll() is not None:
            self.proc = None
            self.close_log()
            self.refresh()
        self.root.after(1000, self.poll)

    def on_close(self):
        if self.is_running():
            self.stop()
        self.root.destroy()


def main():
    if tk is None:
        # Linux'ta python3-tk eksik: kur ve kendini yeniden başlat
        if not IS_WINDOWS and subprocess.run(
            ["pkexec", "apt-get", "install", "-y", "python3-tk"]
        ).returncode == 0:
            os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)])
        print("tkinter yok. Terminalden kur: sudo apt install python3-tk", file=sys.stderr)
        sys.exit(1)

    root = tk.Tk()
    root.withdraw()
    if not ensure_dependencies():
        root.destroy()
        return
    root.deiconify()
    DiscordUnblockApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
