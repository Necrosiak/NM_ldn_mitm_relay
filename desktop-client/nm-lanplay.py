#!/usr/bin/env python3
"""
NM-LanPlay — NetworkMemories LAN Play Client
GUI wrapper for switch-lan-play, pre-configured for the NetworkMemories relay server.

Compatible with:
  - Nintendo Switch (unmodded, LAN mode games)
  - Ryujinx / Yuzu / Sudachi / Citron (emulators)
  - Switch CFW without ldn_mitm (LAN mode games only)

For modded Switch with ldn_mitm: use the sysmodule instead (no PC needed).
"""

import sys, os, platform, subprocess, threading, socket, json, time
import tkinter as tk
from tkinter import scrolledtext, messagebox
import urllib.request

APP_NAME    = "NM-LanPlay"
APP_VERSION = "1.0.0"
RELAY_HOST  = "193.70.35.100"
RELAY_PORT  = 11451
RELAY_ADDR  = f"{RELAY_HOST}:{RELAY_PORT}"

BG_DARK  = "#0f0f1a"
BG_CARD  = "#1a1a2e"
BG_CARD2 = "#16213e"
ACCENT   = "#e94560"
TEXT     = "#eaeaea"
TEXT_DIM = "#8888aa"
GREEN    = "#00c896"
RED      = "#e94560"
YELLOW   = "#f5a623"

def get_bin_path():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    name = "lan-play.exe" if platform.system() == "Windows" else "lan-play"
    return os.path.join(base, "bin", name)

def check_relay():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.sendto(b"\x00\x00\x00\x00\x00", (RELAY_HOST, RELAY_PORT))
        s.close()
        return True
    except Exception:
        return False

class NMLanPlay(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("580x520")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)
        self.process = None
        self.running = False
        self._build_ui()
        self._check_binary()
        threading.Thread(target=self._ping_relay, daemon=True).start()

    def _build_ui(self):
        # Header
        h = tk.Frame(self, bg=BG_CARD, pady=12)
        h.pack(fill="x")
        tk.Label(h, text="NetworkMemories", font=("Segoe UI", 9), bg=BG_CARD, fg=ACCENT).pack()
        tk.Label(h, text="LAN Play Client", font=("Segoe UI", 18, "bold"), bg=BG_CARD, fg=TEXT).pack()
        tk.Label(h, text=f"v{APP_VERSION}  —  Emulateurs & Switch non moddees",
                 font=("Segoe UI", 8), bg=BG_CARD, fg=TEXT_DIM).pack()

        # Status bar
        sb = tk.Frame(self, bg=BG_CARD2, pady=8, padx=16)
        sb.pack(fill="x", pady=(2,0))
        tk.Label(sb, text="Relay NM :", font=("Segoe UI", 9), bg=BG_CARD2, fg=TEXT_DIM).pack(side="left")
        self.lbl_relay = tk.Label(sb, text="  Verification...", font=("Segoe UI", 9, "bold"), bg=BG_CARD2, fg=YELLOW)
        self.lbl_relay.pack(side="left", padx=4)

        # Config
        cf = tk.LabelFrame(self, text=" Configuration reseau ", bg=BG_DARK, fg=TEXT_DIM,
                           font=("Segoe UI", 8), padx=12, pady=8)
        cf.pack(fill="x", padx=16, pady=(12,4))

        r1 = tk.Frame(cf, bg=BG_DARK)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="IP LAN virtuelle :", width=18, anchor="w",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.entry_ip = tk.Entry(r1, font=("Segoe UI", 9), width=18,
                                  bg=BG_CARD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=4)
        self.entry_ip.insert(0, "10.13.1.2")
        self.entry_ip.pack(side="left", padx=4)
        tk.Label(r1, text="(unique par joueur, 10.13.x.x)",
                 font=("Segoe UI", 8), bg=BG_DARK, fg=TEXT_DIM).pack(side="left", padx=4)

        r2 = tk.Frame(cf, bg=BG_DARK)
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Serveur relay :", width=18, anchor="w",
                 font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_DIM).pack(side="left")
        self.entry_relay = tk.Entry(r2, font=("Segoe UI", 9), width=28,
                                     bg=BG_CARD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=4)
        self.entry_relay.insert(0, RELAY_ADDR)
        self.entry_relay.pack(side="left", padx=4)

        # Buttons
        bf = tk.Frame(self, bg=BG_DARK)
        bf.pack(fill="x", padx=16, pady=8)
        self.btn = tk.Button(bf, text="  SE CONNECTER",
                              font=("Segoe UI", 10, "bold"),
                              bg=ACCENT, fg="white", relief="flat",
                              activebackground="#c73550", activeforeground="white",
                              padx=20, pady=8, cursor="hand2",
                              command=self._toggle)
        self.btn.pack(side="left", padx=(0,8))
        self.lbl_status = tk.Label(bf, text="Deconnecte", font=("Segoe UI", 9), bg=BG_DARK, fg=TEXT_DIM)
        self.lbl_status.pack(side="left", padx=8)
        tk.Button(bf, text="Guide Switch", font=("Segoe UI", 8),
                  bg=BG_CARD2, fg=TEXT_DIM, relief="flat", padx=10, pady=8,
                  cursor="hand2", command=self._guide).pack(side="right")

        # Log
        lf = tk.LabelFrame(self, text=" Logs ", bg=BG_DARK, fg=TEXT_DIM,
                            font=("Segoe UI", 8), padx=4, pady=4)
        lf.pack(fill="both", expand=True, padx=16, pady=(0,8))
        self.log = scrolledtext.ScrolledText(lf, height=8, font=("Consolas", 8),
                                              bg="#0a0a14", fg="#88ff88",
                                              insertbackground="white", relief="flat", state="disabled")
        self.log.pack(fill="both", expand=True)

        tk.Label(self, text="Switch moddee ? Utilise le sysmodule ldn_mitm — pas besoin de ce client",
                 font=("Segoe UI", 7), bg=BG_DARK, fg=TEXT_DIM).pack(pady=(0,6))

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _check_binary(self):
        p = get_bin_path()
        if not os.path.exists(p):
            self._log(f"ATTENTION : Binaire lan-play introuvable : {p}")
            self._log("  Telecharge depuis : github.com/spacemeowx2/switch-lan-play/releases")
            self._log(f"  Place dans : {os.path.dirname(p)}")
            self.btn.configure(state="disabled", bg="#555")
        else:
            self._log(f"OK Binaire trouve : {p}")
            if platform.system() != "Windows":
                os.chmod(p, 0o755)

    def _ping_relay(self):
        ok = check_relay()
        if ok:
            self.lbl_relay.configure(text=f"OK {RELAY_ADDR}", fg=GREEN)
            self._log(f"OK Relay NM accessible : {RELAY_ADDR}")
        else:
            self.lbl_relay.configure(text="Inaccessible", fg=RED)
            self._log(f"ATTENTION Relay NM inaccessible : {RELAY_ADDR}")

    def _toggle(self):
        if self.running: self._disconnect()
        else: self._connect()

    def _connect(self):
        binary = get_bin_path()
        relay  = self.entry_relay.get().strip()
        ip     = self.entry_ip.get().strip()
        if not relay:
            messagebox.showwarning("Config", "Adresse du relay manquante.")
            return
        cmd = [binary, "--relay-server-addr", relay]
        if ip:
            cmd += ["--fake-internet", "--ip", f"{ip}/16"]
        self._log(f"\nLancement : {' '.join(cmd)}\n")
        try:
            kw = {"creationflags": subprocess.CREATE_NO_WINDOW} if platform.system() == "Windows" else {}
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT, text=True, **kw)
            self.running = True
            self.btn.configure(text="  DECONNECTER", bg="#555")
            self.lbl_status.configure(text="Connecte au relay", fg=GREEN)
            threading.Thread(target=self._read_output, daemon=True).start()
        except PermissionError:
            self._log("ERREUR : Lance en Administrateur (Windows requis pour Npcap).")
        except Exception as e:
            self._log(f"ERREUR : {e}")

    def _disconnect(self):
        if self.process:
            self.process.terminate()
            self.process = None
        self.running = False
        self.btn.configure(text="  SE CONNECTER", bg=ACCENT)
        self.lbl_status.configure(text="Deconnecte", fg=TEXT_DIM)
        self._log("\nDeconnecte du relay.\n")

    def _read_output(self):
        if not self.process: return
        for line in self.process.stdout:
            line = line.rstrip()
            if line: self._log(f"  {line}")
        self._disconnect()

    def _guide(self):
        import webbrowser
        webbrowser.open("https://github.com/Necrosiak/NM_ldn_mitm_relay")

    def on_close(self):
        if self.running: self._disconnect()
        self.destroy()

if __name__ == "__main__":
    app = NMLanPlay()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
