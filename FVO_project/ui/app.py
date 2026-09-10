import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import time
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner.port_scanner import PortScanner, COMMON_PORTS
from scanner.host_discovery import HostDiscovery
from scanner.vuln_scanner import VulnScanner
from scanner.geo_lookup import GeoLookup
from ai.ollama_client import GroqClient
from ai.exploit_engine import ExploitEngine
from ui.styles import *
from ui.matrix_canvas import MatrixRain, ScanProgressBar
from ui.globe_widget import Globe3D


class FVOApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FVO  EAGLE VULNERABILITY ORACLE")
        self.geometry("1500x940")
        self.minsize(1200, 760)
        self.configure(bg=BG_DEEP)
        self.resizable(True, True)

        self.port_scanner  = PortScanner(timeout=0.8, threads=300)
        self.host_discovery = HostDiscovery(timeout=1.5, threads=120)
        self.vuln_scanner  = VulnScanner()
        self.geo_lookup    = GeoLookup()
        self.groq          = GroqClient()
        self.exploit_engine = ExploitEngine(self.groq)

        self._scan_results   = {}
        self._vuln_findings  = []
        self._host_results   = []
        self._current_geo    = None
        self._scan_thread    = None
        self._ai_thread      = None

        self._setup_style()
        self._build_ui()
        self._check_groq_status()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ──────────────────────────────────────────────────────────────
    # Style
    # ──────────────────────────────────────────────────────────────
    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG_DEEP, borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=BG_PANEL, foreground=GREEN_DIM,
                    padding=[18, 7], font=FONT_MAIN, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", BG_CARD), ("active", BG_HOVER)],
              foreground=[("selected", GREEN_BRIGHT), ("active", GREEN_MID)])
        s.configure("Vertical.TScrollbar",
                    background=BG_PANEL, troughcolor=BG_DARK,
                    bordercolor=GREEN_DARK, arrowcolor=GREEN_MID)
        s.configure("TCombobox",
                    fieldbackground=BG_CARD, background=BG_PANEL,
                    foreground=GREEN_BRIGHT, selectbackground=BG_HOVER)
        s.map("TCombobox",
              fieldbackground=[("readonly", BG_CARD)],
              foreground=[("readonly", GREEN_BRIGHT)])

    # ──────────────────────────────────────────────────────────────
    # Root layout
    # ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_status_bar()

        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                              bg=BG_DEEP, sashwidth=4, relief="flat")
        pane.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        left = tk.Frame(pane, bg=BG_DEEP, width=290)
        pane.add(left, minsize=250)
        self._build_left_panel(left)

        right = tk.Frame(pane, bg=BG_DEEP)
        pane.add(right, minsize=800)
        self._build_tabs(right)

    # ──────────────────────────────────────────────────────────────
    # Header
    # ──────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_DARK, height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Matrix rain strip
        self.matrix_canvas = MatrixRain(hdr, width=220, height=72, speed=50)
        self.matrix_canvas.pack(side=tk.LEFT)

        # Divider
        tk.Frame(hdr, bg=GREEN_DIM, width=2).pack(side=tk.LEFT, fill=tk.Y, padx=0)

        # Titles
        title_f = tk.Frame(hdr, bg=BG_DARK)
        title_f.pack(side=tk.LEFT, padx=14, fill=tk.Y)
        tk.Label(title_f, text="▲ FVO  EAGLE  VULNERABILITY  ORACLE",
                 bg=BG_DARK, fg=GREEN_GLOW,
                 font=("Consolas", 16, "bold")).pack(anchor="w", pady=(10, 0))
        tk.Label(title_f,
                 text="  Custom Scanner  ·  CVE Engine  ·  Groq GPT-OSS 120B  ·  3D Globe",
                 bg=BG_DARK, fg=GREEN_DIM, font=FONT_SMALL).pack(anchor="w")

        # Right side indicators
        right_f = tk.Frame(hdr, bg=BG_DARK)
        right_f.pack(side=tk.RIGHT, padx=14, fill=tk.Y)
        self.groq_indicator = tk.Label(
            right_f, text="◉ GROQ: CHECKING",
            bg=BG_DARK, fg=AMBER, font=FONT_SMALL)
        self.groq_indicator.pack(anchor="e", pady=(10, 2))
        self.model_label = tk.Label(
            right_f, text=f"Model: {self.groq.model}",
            bg=BG_DARK, fg=GRAY_MID, font=FONT_SMALL)
        self.model_label.pack(anchor="e")

        tk.Frame(self, bg=GREEN_DIM, height=2).pack(fill=tk.X)
        self.matrix_canvas.start()

    # ──────────────────────────────────────────────────────────────
    # Status bar
    # ──────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = tk.Frame(self, bg="#020a04", height=24)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        tk.Frame(bar, bg=GREEN_DIM, width=2).pack(side=tk.LEFT, fill=tk.Y)
        self.status_label = tk.Label(bar, text="▸ READY — AWAITING TARGET",
                                     bg="#020a04", fg=GREEN_MID,
                                     font=FONT_SMALL, anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        self.time_label = tk.Label(bar, text="", bg="#020a04",
                                   fg=GRAY_MID, font=FONT_SMALL)
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self._tick()

    def _tick(self):
        self.time_label.config(text=time.strftime(" %H:%M:%S  %Y-%m-%d "))
        self.after(1000, self._tick)

    def _set_status(self, msg, color=GREEN_MID):
        self.status_label.config(text=f"▸ {msg}", fg=color)

    # ──────────────────────────────────────────────────────────────
    # Left panel (controls + 3D globe)
    # ──────────────────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        canvas = tk.Canvas(parent, bg=BG_DEEP, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=BG_DEEP)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas(e):
            canvas.itemconfig(win_id, width=e.width)

        inner.bind("<Configure>", _on_frame)
        canvas.bind("<Configure>", _on_canvas)

        # ── Globe card ──────────────────────────────────────────
        globe_card = tk.Frame(inner, bg=BG_CARD, padx=6, pady=6)
        globe_card.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(globe_card, text="◈ LIVE TARGET GLOBE",
                 bg=BG_CARD, fg=GREEN_MID, font=FONT_MAIN).pack(anchor="w")
        tk.Frame(globe_card, bg=GREEN_DARK, height=1).pack(fill=tk.X, pady=4)

        self.globe = Globe3D(globe_card, size=240)
        self.globe.pack(pady=4)
        self.globe.start()

        # Country info strip
        geo_strip = tk.Frame(globe_card, bg="#000d06", padx=6, pady=6)
        geo_strip.pack(fill=tk.X, pady=(2, 0))

        self.flag_label = tk.Label(geo_strip, text="🌐", bg="#000d06",
                                   font=("Segoe UI Emoji", 20))
        self.flag_label.pack(side=tk.LEFT, padx=(0, 8))

        geo_text_f = tk.Frame(geo_strip, bg="#000d06")
        geo_text_f.pack(side=tk.LEFT, fill=tk.X)

        self.country_label = tk.Label(
            geo_text_f, text="NO TARGET",
            bg="#000d06", fg=GREEN_BRIGHT,
            font=("Consolas", 11, "bold"), anchor="w")
        self.country_label.pack(anchor="w")

        self.city_label = tk.Label(
            geo_text_f, text="Set a target and scan",
            bg="#000d06", fg=GRAY_MID,
            font=FONT_SMALL, anchor="w")
        self.city_label.pack(anchor="w")

        self.isp_label = tk.Label(
            geo_text_f, text="",
            bg="#000d06", fg=CYAN_DIM,
            font=FONT_SMALL, anchor="w", wraplength=160)
        self.isp_label.pack(anchor="w")

        # Lat/Lon readout
        self.coords_label = tk.Label(
            globe_card, text="LAT — / LON —",
            bg=BG_CARD, fg=GREEN_DIM, font=FONT_SMALL)
        self.coords_label.pack(anchor="w")

        # ── Target config ───────────────────────────────────────
        self._section(inner, "▼ TARGET CONFIG")
        cfg = self._card(inner)

        self._lbl(cfg, "TARGET IP / HOSTNAME")
        self.target_var = tk.StringVar(value="192.168.1.1")
        self._entry(cfg, self.target_var)

        tk.Frame(cfg, bg=GREEN_DARK, height=1).pack(fill=tk.X, pady=6)
        self._lbl(cfg, "SCAN MODE")
        self.scan_mode = tk.StringVar(value="Common Ports")
        ttk.Combobox(cfg, textvariable=self.scan_mode,
                     values=["Common Ports", "Top 1024",
                              "Full Range (1-65535)", "Custom Range", "Stealth"],
                     state="readonly", font=FONT_SMALL).pack(fill=tk.X, pady=(2, 6))

        self._lbl(cfg, "CUSTOM PORT RANGE")
        self.port_range_var = tk.StringVar(value="1-1024")
        self._entry(cfg, self.port_range_var)

        self._lbl(cfg, "THREADS")
        self.threads_var = tk.IntVar(value=200)
        tk.Scale(cfg, from_=10, to=500, orient=tk.HORIZONTAL,
                 variable=self.threads_var, bg=BG_CARD, fg=GREEN_BRIGHT,
                 troughcolor=BG_PANEL, highlightthickness=0,
                 activebackground=GREEN_MID,
                 font=FONT_SMALL).pack(fill=tk.X, pady=(2, 6))

        self.scan_btn  = self._btn(cfg, "◉ START PORT SCAN",  self._start_port_scan, GREEN_BRIGHT)
        self.scan_btn.pack(fill=tk.X, pady=3)
        self.stop_btn  = self._btn(cfg, "■ STOP SCAN", self._stop_scan, RED_ALERT)
        self.stop_btn.pack(fill=tk.X, pady=2)
        self.stop_btn.config(state="disabled")

        # ── Host discovery ───────────────────────────────────────
        self._section(inner, "▼ NETWORK DISCOVERY")
        disc = self._card(inner)

        self._lbl(disc, "CIDR / RANGE (e.g. 192.168.1.0/24)")
        self.cidr_var = tk.StringVar(value=HostDiscovery().get_local_network())
        self._entry(disc, self.cidr_var)
        self.discover_btn = self._btn(disc, "◎ DISCOVER HOSTS", self._start_discovery, CYAN_BRIGHT)
        self.discover_btn.pack(fill=tk.X, pady=3)

        # ── AI shortcuts ─────────────────────────────────────────
        self._section(inner, "▼ AI ENGINE")
        ai_c = self._card(inner)
        self._btn(ai_c, "⚡ FULL AI SCAN ANALYSIS", self._ai_analyze_all, AMBER).pack(fill=tk.X, pady=2)
        self._btn(ai_c, "⚠ EXPLAIN TOP VULN",      self._ai_explain_top, RED_ALERT).pack(fill=tk.X, pady=2)

        # ── Local info ──────────────────────────────────────────
        self._section(inner, "▼ LOCAL INFO")
        info_c = self._card(inner)
        self.local_ip_lbl = tk.Label(info_c, text="LOCAL IP: detecting…",
                                     bg=BG_CARD, fg=CYAN_MID, font=FONT_SMALL)
        self.local_ip_lbl.pack(anchor="w")
        threading.Thread(target=self._detect_local_ip, daemon=True).start()

    # ──────────────────────────────────────────────────────────────
    # Widget helpers
    # ──────────────────────────────────────────────────────────────
    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=BG_DEEP, fg=GREEN_MID,
                 font=FONT_MAIN).pack(anchor="w", padx=8, pady=(10, 3))
        tk.Frame(parent, bg=GREEN_DARK, height=1).pack(fill=tk.X, padx=8)

    def _card(self, parent):
        f = tk.Frame(parent, bg=BG_CARD, padx=10, pady=8)
        f.pack(fill=tk.X, padx=8, pady=4)
        return f

    def _lbl(self, parent, text):
        tk.Label(parent, text=text, bg=BG_CARD, fg=GRAY_MID,
                 font=FONT_SMALL).pack(anchor="w")

    def _entry(self, parent, var):
        e = tk.Entry(parent, textvariable=var,
                     bg=BG_PANEL, fg=GREEN_BRIGHT,
                     insertbackground=GREEN_BRIGHT,
                     font=FONT_MAIN, relief="flat")
        e.pack(fill=tk.X, pady=(2, 6))
        return e

    def _btn(self, parent, text, cmd, color=GREEN_BRIGHT):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=BG_PANEL, fg=color, activebackground=BG_HOVER,
                      activeforeground=WHITE, font=FONT_SMALL,
                      relief="flat", bd=0, pady=6, cursor="hand2",
                      highlightthickness=1, highlightbackground=color)
        b.bind("<Enter>", lambda e, w=b: w.config(bg=BG_HOVER))
        b.bind("<Leave>", lambda e, w=b: w.config(bg=BG_PANEL))
        return b

    # ──────────────────────────────────────────────────────────────
    # Tabs
    # ──────────────────────────────────────────────────────────────
    def _build_tabs(self, parent):
        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill=tk.BOTH, expand=True)
        self._build_scan_tab()
        self._build_hosts_tab()
        self._build_vulns_tab()
        self._build_ai_tab()
        self._build_cve_tab()
        self._build_console_tab()

    def _text_widget(self, parent, height=20):
        frame = tk.Frame(parent, bg=BG_PANEL)
        txt = tk.Text(frame, bg=BG_DEEP, fg=GREEN_BRIGHT,
                      font=FONT_MONO, insertbackground=GREEN_BRIGHT,
                      relief="flat", bd=0, wrap=tk.WORD, height=height,
                      selectbackground=BG_HOVER, selectforeground=WHITE)
        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt.tag_configure("header",   foreground=GREEN_GLOW,    font=("Consolas", 11, "bold"))
        txt.tag_configure("open",     foreground=GREEN_BRIGHT)
        txt.tag_configure("critical", foreground=CRITICAL_COLOR)
        txt.tag_configure("high",     foreground=HIGH_COLOR)
        txt.tag_configure("medium",   foreground=MEDIUM_COLOR)
        txt.tag_configure("low",      foreground=LOW_COLOR)
        txt.tag_configure("info",     foreground=CYAN_BRIGHT)
        txt.tag_configure("dim",      foreground=GRAY_MID)
        txt.tag_configure("ai",       foreground=AMBER)
        txt.tag_configure("cyan",     foreground=CYAN_BRIGHT)
        txt.tag_configure("white",    foreground=WHITE)
        txt.tag_configure("geo",      foreground="#00e5ff",
                          font=("Consolas", 10, "bold"))
        return frame, txt

    def _append(self, w, text, tag=""):
        w.config(state=tk.NORMAL)
        w.insert(tk.END, text, tag)
        w.see(tk.END)

    def _clear(self, w):
        w.config(state=tk.NORMAL)
        w.delete("1.0", tk.END)

    def _topbar(self, tab, text, color=GREEN_MID):
        bar = tk.Frame(tab, bg=BG_DARK, height=34)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text=text, bg=BG_DARK, fg=color,
                 font=FONT_MAIN).pack(side=tk.LEFT, padx=12, pady=8)
        return bar

    # ── Scan tab ────────────────────────────────────────────────
    def _build_scan_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ◉ PORT SCAN  ")

        bar = self._topbar(tab, "PORT SCANNER — CUSTOM SOCKET ENGINE  (NO NMAP)")
        self.scan_progress = ScanProgressBar(bar, width=320, height=20)
        self.scan_progress.pack(side=tk.RIGHT, padx=12, pady=7)

        # Geo banner strip
        self.geo_banner = tk.Frame(tab, bg="#000d10", height=44)
        self.geo_banner.pack(fill=tk.X)
        self.geo_banner.pack_propagate(False)

        self.geo_flag_big = tk.Label(self.geo_banner, text="🌐",
                                     bg="#000d10",
                                     font=("Segoe UI Emoji", 24))
        self.geo_flag_big.pack(side=tk.LEFT, padx=10)

        geo_info_f = tk.Frame(self.geo_banner, bg="#000d10")
        geo_info_f.pack(side=tk.LEFT, fill=tk.Y, pady=4)

        self.geo_country_big = tk.Label(
            geo_info_f, text="TARGET COUNTRY  —  WAITING FOR SCAN",
            bg="#000d10", fg=CYAN_BRIGHT,
            font=("Consolas", 12, "bold"))
        self.geo_country_big.pack(anchor="w")

        self.geo_detail_big = tk.Label(
            geo_info_f, text="Scan a target to see geolocation data",
            bg="#000d10", fg=GRAY_MID, font=FONT_SMALL)
        self.geo_detail_big.pack(anchor="w")

        tk.Frame(tab, bg="#001a2e", height=1).pack(fill=tk.X)

        frm, self.scan_text = self._text_widget(tab)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        self._append(self.scan_text,
            "  ██████╗  ██████╗ ██████╗ ████████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗\n"
            "  ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║\n"
            "  ██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║     ███████║██╔██╗ ██║\n"
            "  ██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║     ██╔══██║██║╚██╗██║\n"
            "  ██║     ╚██████╔╝██║  ██║   ██║       ███████║╚██████╗██║  ██║██║ ╚████║\n"
            "  ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝\n\n",
            "header")
        self._append(self.scan_text,
            "  FVO Eagle Port Scanner — Custom socket engine, banner grabber, service detector\n"
            "  Enter a target in the left panel and click  [ ◉ START PORT SCAN ]\n\n",
            "dim")

    # ── Hosts tab ───────────────────────────────────────────────
    def _build_hosts_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ◎ HOST DISCOVERY  ")
        bar = self._topbar(tab, "NETWORK HOST DISCOVERY — PING SWEEP + TCP PROBE", CYAN_BRIGHT)
        self.disc_progress = ScanProgressBar(bar, width=320, height=20)
        self.disc_progress.pack(side=tk.RIGHT, padx=12, pady=7)
        frm, self.hosts_text = self._text_widget(tab)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._append(self.hosts_text, "  HOST DISCOVERY\n\n", "header")
        self._append(self.hosts_text,
            "  Probes every host via ICMP ping + TCP fallback (ports 80/443/22)\n"
            "  Enter a CIDR and click [ ◎ DISCOVER HOSTS ] in the left panel\n\n", "dim")

    # ── Vulns tab ───────────────────────────────────────────────
    def _build_vulns_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ⚠ VULNERABILITIES  ")
        bar = self._topbar(tab, "VULNERABILITY ANALYSIS — CVE SIGNATURES + BANNER MATCHING", CRITICAL_COLOR)
        self.vuln_count_lbl = tk.Label(bar, text="No scan data",
                                       bg=BG_DARK, fg=GRAY_MID, font=FONT_SMALL)
        self.vuln_count_lbl.pack(side=tk.RIGHT, padx=12)
        frm, self.vuln_text = self._text_widget(tab)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._append(self.vuln_text, "  VULNERABILITY SCANNER\n\n", "header")
        self._append(self.vuln_text,
            "  Run a Port Scan first — findings appear here automatically.\n"
            "  Detects: dangerous ports · outdated versions · weak TLS · info disclosure · known CVEs\n\n",
            "dim")

    # ── AI tab ─────────────────────────────────────────────────
    def _build_ai_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ⚡ AI EXPLOIT ENGINE  ")
        bar = self._topbar(tab, "GROQ GPT-OSS 120B — EXPLOIT ANALYSIS · OFFENSIVE / DEFENSIVE INTEL", AMBER)
        self._btn(bar, "⚙ GROQ API KEY", self._open_groq_settings, CYAN_BRIGHT).pack(
            side=tk.RIGHT, padx=8, pady=5)
        self._btn(bar, "■ STOP AI", self._stop_ai, RED_ALERT).pack(side=tk.RIGHT, padx=8, pady=5)
        frm, self.ai_text = self._text_widget(tab, height=18)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=(3, 0))

        inp = tk.Frame(tab, bg=BG_DARK, pady=5)
        inp.pack(fill=tk.X, side=tk.BOTTOM, padx=3, pady=3)
        tk.Label(inp, text="ASK AI ▸", bg=BG_DARK, fg=AMBER, font=FONT_MAIN).pack(side=tk.LEFT, padx=8)
        self.ai_q_var = tk.StringVar()
        e = tk.Entry(inp, textvariable=self.ai_q_var,
                     bg=BG_PANEL, fg=AMBER, insertbackground=AMBER,
                     font=FONT_MAIN, relief="flat")
        e.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        e.bind("<Return>", lambda _: self._ai_custom_query())
        self._btn(inp, "SEND ▸", self._ai_custom_query, AMBER).pack(side=tk.RIGHT, padx=4)
        self._btn(inp, "CLEAR", lambda: self._clear(self.ai_text), GRAY_MID).pack(side=tk.RIGHT, padx=4)

        self._append(self.ai_text, "  FVO AI EXPLOIT ENGINE — Powered by Groq GPT-OSS 120B\n\n", "header")
        self._append(self.ai_text,
            "  1. Run a port scan on a target first\n"
            "  2. Click [ ⚡ FULL AI SCAN ANALYSIS ] for the complete report\n"
            "  3. Click [ ⚠ EXPLAIN TOP VULN ] for the most critical vulnerability\n"
            "  4. Type any security question in the chat box below\n\n"
            "  Example queries:\n"
            "  • 'Explain CVE-2017-0144 EternalBlue offensive and defensive'\n"
            "  • 'How to exploit an open Redis port 6379 without auth'\n"
            "  • 'How does BlueKeep work and how to patch it'\n\n", "dim")

    # ── CVE tab ─────────────────────────────────────────────────
    def _build_cve_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ◈ CVE LOOKUP  ")
        self._topbar(tab, "CVE LOOKUP — AI-POWERED VULNERABILITY INTELLIGENCE", CYAN_BRIGHT)

        srch = tk.Frame(tab, bg=BG_DARK, pady=8)
        srch.pack(fill=tk.X, padx=3)
        tk.Label(srch, text="CVE ID ▸", bg=BG_DARK, fg=CYAN_BRIGHT, font=FONT_MAIN).pack(side=tk.LEFT, padx=8)
        self.cve_var = tk.StringVar(value="CVE-2017-0144")
        e = tk.Entry(srch, textvariable=self.cve_var,
                     bg=BG_PANEL, fg=CYAN_BRIGHT, insertbackground=CYAN_BRIGHT,
                     font=FONT_MAIN, relief="flat", width=22)
        e.pack(side=tk.LEFT, padx=4)
        e.bind("<Return>", lambda _: self._lookup_cve())
        self._btn(srch, "◈ LOOKUP", self._lookup_cve, CYAN_BRIGHT).pack(side=tk.LEFT, padx=4)
        for cve in ["CVE-2017-0144", "CVE-2019-0708", "CVE-2021-41773", "CVE-2014-3566"]:
            self._btn(srch, cve, lambda c=cve: (self.cve_var.set(c), self._lookup_cve()), CYAN_DIM).pack(side=tk.LEFT, padx=2)

        frm, self.cve_text = self._text_widget(tab)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._append(self.cve_text, "  CVE LOOKUP — AI-POWERED\n\n", "header")
        self._append(self.cve_text,
            "  Enter a CVE ID above to get:\n"
            "  • Technical mechanics of the vulnerability\n"
            "  • Offensive exploitation methodology\n"
            "  • Defensive countermeasures and detection rules\n\n", "dim")

    # ── Console tab ─────────────────────────────────────────────
    def _build_console_tab(self):
        tab = tk.Frame(self.nb, bg=BG_DEEP)
        self.nb.add(tab, text="  ◌ CONSOLE  ")
        bar = self._topbar(tab, "SYSTEM CONSOLE & EVENT LOG")
        self._btn(bar, "CLEAR", lambda: self._clear(self.console_text), GRAY_MID).pack(side=tk.RIGHT, padx=8, pady=5)
        frm, self.console_text = self._text_widget(tab)
        frm.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._log("FVO Eagle Vulnerability Oracle started")
        self._log(f"Python {sys.version.split()[0]} | Platform: {sys.platform}")
        self._log("Scanner: custom socket engine (no nmap)")
        self._log("Checking Groq AI…")

    # ──────────────────────────────────────────────────────────────
    # Geolocation helpers
    # ──────────────────────────────────────────────────────────────
    def _resolve_and_geolocate(self, target: str):
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            return None, None
        geo = self.geo_lookup.lookup(ip)
        return ip, geo

    def _update_geo_ui(self, geo: dict):
        if not geo:
            return
        self._current_geo = geo
        country   = geo.get("country", "Unknown")
        code      = geo.get("countryCode", "??")
        city      = geo.get("city", "")
        region    = geo.get("region", "")
        isp       = geo.get("isp", "")
        flag      = geo.get("flag", "🌐")
        lat       = geo.get("lat", 0.0)
        lon       = geo.get("lon", 0.0)
        tz        = geo.get("timezone", "")

        city_str  = f"{city}, {region}" if city and region else city or region
        detail    = f"{city_str} · {tz}" if city_str and tz else city_str or tz

        # Globe
        self.globe.set_target(lat, lon, country)
        # Left panel labels
        self.flag_label.config(text=flag)
        self.country_label.config(text=f"[{code}] {country}", fg=CYAN_BRIGHT)
        self.city_label.config(text=detail or "—")
        self.isp_label.config(text=isp[:50] if isp else "")
        self.coords_label.config(text=f"LAT {lat:.2f}°  /  LON {lon:.2f}°")
        # Top geo banner on scan tab
        self.geo_flag_big.config(text=flag)
        self.geo_country_big.config(
            text=f"  {flag}  [{code}] {country}  —  TARGET ORIGIN",
            fg=CYAN_BRIGHT)
        self.geo_detail_big.config(
            text=f"  {city_str}  |  ISP: {isp}  |  TZ: {tz}  |  {lat:.3f}°, {lon:.3f}°",
            fg=GRAY_MID)

    # ──────────────────────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────────────────────
    def _detect_local_ip(self):
        ip = HostDiscovery().get_local_ip()
        self.local_ip_lbl.config(text=f"LOCAL IP: {ip}")

    def _start_port_scan(self):
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("FVO", "Enter a target.")
            return

        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            messagebox.showerror("FVO", f"Cannot resolve: {target}")
            return

        mode = self.scan_mode.get()
        self.port_scanner.threads = self.threads_var.get()

        if mode == "Common Ports":
            port_list, port_range = list(COMMON_PORTS.keys()), None
        elif mode == "Top 1024":
            port_list, port_range = None, (1, 1024)
        elif mode == "Full Range (1-65535)":
            port_list, port_range = None, (1, 65535)
        elif mode == "Stealth":
            self.port_scanner.timeout = 2.5
            self.port_scanner.threads = 25
            port_list, port_range = list(COMMON_PORTS.keys()), None
        else:
            try:
                p = self.port_range_var.get().split("-")
                port_list, port_range = None, (int(p[0]), int(p[1]))
            except Exception:
                messagebox.showerror("FVO", "Invalid range. Use: 1-1024")
                return

        self._clear(self.scan_text); self._clear(self.vuln_text)
        self._scan_results = {}; self._vuln_findings = []
        self.nb.select(0)

        self._append(self.scan_text,
            f"  ╔══════════════════════════════════════════════════════╗\n"
            f"  ║  TARGET  : {ip:<42}║\n"
            f"  ║  MODE    : {mode:<42}║\n"
            f"  ║  THREADS : {self.threads_var.get():<42}║\n"
            f"  ╚══════════════════════════════════════════════════════╝\n\n",
            "header")
        self._append(self.scan_text,
            f"  {'PORT':<9} {'SERVICE':<16} {'STATE':<8} {'LATENCY':<10} BANNER\n"
            f"  {'─'*75}\n", "info")

        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.scan_progress.set_progress(0)
        self.scan_progress.start_animation()
        self._set_status(f"SCANNING {ip}  |  {mode}", CYAN_BRIGHT)
        self._log(f"Scan started: {ip}  mode={mode}", "cyan")

        def run():
            # Geolocation first
            geo = self.geo_lookup.lookup(ip)
            if geo:
                self.after(0, lambda: self._update_geo_ui(geo))
                country = geo.get("country", "")
                city    = geo.get("city", "")
                flag    = geo.get("flag", "🌐")
                geo_line = (
                    f"  GEO: {flag} {country}"
                    + (f", {city}" if city else "")
                    + f"  |  ISP: {geo.get('isp','')}  "
                    + f"  |  {geo.get('lat',0):.3f}°, {geo.get('lon',0):.3f}°\n\n"
                )
                self.after(0, lambda: self._append(self.scan_text, geo_line, "geo"))
                self.after(0, lambda: self._log(f"GEO: {flag} {country}", "cyan"))

            start = time.time()

            def on_port(r):
                port    = r["port"]
                service = r["service"]
                banner  = r.get("banner", "")
                latency = r["latency_ms"]
                bshort  = banner[:38].replace("\n", " ") if banner else ""
                line = f"  {port:<9} {service:<16} OPEN    {latency:>7}ms   {bshort}\n"
                self.after(0, lambda: self._append(self.scan_text, line, "open"))
                self._scan_results[port] = r
                for f in self.vuln_scanner.analyze_port(port, service, banner):
                    self._vuln_findings.append(f)

            def on_prog(done, total):
                pct = done / total
                self.after(0, lambda: self.scan_progress.set_progress(
                    pct, f"{done}/{total}"))

            if port_list:
                self.port_scanner.scan(ip, port_list=port_list,
                                       callback=on_port, progress_callback=on_prog)
            else:
                self.port_scanner.scan(ip, port_range=port_range,
                                       callback=on_port, progress_callback=on_prog)

            for port in self._scan_results:
                if port in (443, 8443, 465, 993, 995):
                    self._vuln_findings.extend(self.vuln_scanner.check_ssl(ip, port))

            elapsed = time.time() - start
            found   = len(self._scan_results)
            summary = (
                f"\n  {'═'*75}\n"
                f"  SCAN COMPLETE  |  Target: {ip}  |  Open: {found}  |  "
                f"Vulns: {len(self._vuln_findings)}  |  Time: {elapsed:.1f}s\n"
                f"  {'═'*75}\n"
            )
            self.after(0, lambda: self._append(self.scan_text, summary, "header"))
            self.after(0, self._update_vuln_tab)
            self.after(0, lambda: self.scan_progress.set_progress(1.0, "COMPLETE"))
            self.after(0, self.scan_progress.stop_animation)
            self.after(0, lambda: self._set_status(
                f"SCAN DONE — {found} ports  {len(self._vuln_findings)} vulns  {elapsed:.1f}s",
                GREEN_BRIGHT))
            self.after(0, lambda: self.scan_btn.config(state="normal"))
            self.after(0, lambda: self.stop_btn.config(state="disabled"))
            self.after(0, lambda: self._log(
                f"Scan done: {ip}  {found} open  {len(self._vuln_findings)} vulns  {elapsed:.1f}s", "open"))

        self._scan_thread = threading.Thread(target=run, daemon=True)
        self._scan_thread.start()

    def _stop_scan(self):
        self.port_scanner.stop()
        self.host_discovery.stop()
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.scan_progress.stop_animation()
        self._set_status("SCAN STOPPED", AMBER)
        self._log("Scan stopped by user", "medium")

    def _update_vuln_tab(self):
        self._clear(self.vuln_text)
        findings = self._vuln_findings
        if not findings:
            self._append(self.vuln_text, "\n  NO VULNERABILITIES DETECTED\n", "low")
            self._append(self.vuln_text,
                "  This does not guarantee security — run AI analysis for deeper insights.\n", "dim")
            self.vuln_count_lbl.config(text="0 vulnerabilities", fg=LOW_COLOR)
            return

        by_sev = {s: [] for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
        for f in findings:
            by_sev.setdefault(f.get("severity", "INFO"), []).append(f)

        counts = "  ".join(f"{s}:{len(by_sev[s])}" for s in by_sev if by_sev[s])
        self.vuln_count_lbl.config(text=counts,
                                    fg=CRITICAL_COLOR if by_sev["CRITICAL"] else HIGH_COLOR)

        self._append(self.vuln_text,
            f"  ╔══════════════════════════════════════════════════════╗\n"
            f"  ║  VULNERABILITY REPORT — {len(findings)} finding(s) detected{' '*(26-len(str(len(findings))))}║\n"
            f"  ║  {counts:<54}║\n"
            f"  ╚══════════════════════════════════════════════════════╝\n\n",
            "header")

        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
            grp = by_sev.get(sev, [])
            if not grp:
                continue
            tag = sev.lower()
            self._append(self.vuln_text,
                f"\n  ◈ [{sev}] — {len(grp)} finding(s)\n"
                f"  {'─'*65}\n", tag)
            for f in grp:
                self._append(self.vuln_text,
                    f"  Port  : {f.get('port','?')}/{f.get('service','?')}\n", tag)
                self._append(self.vuln_text,
                    f"  CVE   : {f.get('cve','N/A')}\n", "white")
                self._append(self.vuln_text,
                    f"  Desc  : {f.get('description','')}\n", "white")
                if f.get("banner"):
                    self._append(self.vuln_text,
                        f"  Banner: {f['banner'][:80]}\n", "dim")
                self._append(self.vuln_text, "\n", "")

        self.nb.select(2)

    def _start_discovery(self):
        cidr = self.cidr_var.get().strip()
        if not cidr:
            messagebox.showwarning("FVO", "Enter a CIDR range.")
            return
        self._clear(self.hosts_text)
        self._host_results = []
        self.nb.select(1)
        self._append(self.hosts_text,
            f"  HOST DISCOVERY — {cidr}\n"
            f"  Method: ICMP + TCP fallback\n  {'─'*60}\n\n", "header")
        self.disc_progress.set_progress(0)
        self.disc_progress.start_animation()
        self._set_status(f"DISCOVERING {cidr}", CYAN_BRIGHT)
        self.discover_btn.config(state="disabled")

        def run():
            start = time.time()

            def on_host(h):
                geo = self.geo_lookup.lookup(h["ip"])
                country_str = f"[{geo.get('countryCode','?')}]" if geo else ""
                line = (
                    f"  ◉ {h['ip']:<18} {(h.get('hostname','') or '—'):<32} "
                    f"{h.get('mac',''):<18} {country_str}\n"
                )
                self.after(0, lambda: self._append(self.hosts_text, line, "open"))
                self._host_results.append(h)

            def on_prog(done, total):
                self.after(0, lambda: self.disc_progress.set_progress(done / total, f"{done}/{total}"))

            results = self.host_discovery.scan_range(cidr, callback=on_host, progress_callback=on_prog)
            elapsed = time.time() - start
            self.after(0, lambda: self._append(self.hosts_text,
                f"\n  {'═'*60}\n  DONE — {len(results)} hosts alive  |  {elapsed:.1f}s\n  {'═'*60}\n",
                "header"))
            self.after(0, self.disc_progress.stop_animation)
            self.after(0, lambda: self.disc_progress.set_progress(1.0, "DONE"))
            self.after(0, lambda: self._set_status(f"DISCOVERY DONE — {len(results)} hosts", GREEN_BRIGHT))
            self.after(0, lambda: self.discover_btn.config(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def _ai_analyze_all(self):
        if not self._scan_results:
            messagebox.showinfo("FVO AI", "Run a port scan first.")
            return
        self.nb.select(3)
        target = self.target_var.get().strip()
        self._clear(self.ai_text)
        self._append(self.ai_text, f"  ⚡ FULL AI ANALYSIS FOR: {target}\n\n", "header")
        self._set_status("AI ANALYZING…", AMBER)

        def run():
            self.exploit_engine.generate_exploit_suggestions(
                target, self._scan_results, self._vuln_findings,
                on_token=lambda t: self.after(0, lambda: self._append(self.ai_text, t, "ai")),
                on_done=lambda _: (
                    self.after(0, lambda: self._append(self.ai_text, "\n\n  ✓ Analysis complete\n", "header")),
                    self.after(0, lambda: self._set_status("AI ANALYSIS COMPLETE", GREEN_BRIGHT))))
        self._ai_thread = threading.Thread(target=run, daemon=True)
        self._ai_thread.start()

    def _ai_explain_top(self):
        if not self._vuln_findings:
            messagebox.showinfo("FVO AI", "No vulnerabilities yet — run a scan first.")
            return
        self.nb.select(3)
        pri = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        top = min(self._vuln_findings, key=lambda f: pri.get(f.get("severity", "INFO"), 5))
        self._clear(self.ai_text)
        self._append(self.ai_text,
            f"  ⚡ AI DEEP ANALYSIS — {top.get('cve','?')} | {top.get('severity','?')}\n\n",
            "critical")
        def run():
            self.exploit_engine.analyze_vulnerability(
                top,
                on_token=lambda t: self.after(0, lambda: self._append(self.ai_text, t, "ai")),
                on_done=lambda _: (
                    self.after(0, lambda: self._append(self.ai_text, "\n\n  ✓ Done\n", "header")),
                    self.after(0, lambda: self._set_status("VULN ANALYSIS COMPLETE", GREEN_BRIGHT))))
        self._ai_thread = threading.Thread(target=run, daemon=True)
        self._ai_thread.start()

    def _ai_custom_query(self):
        query = self.ai_q_var.get().strip()
        if not query:
            return
        self.nb.select(3)
        self.ai_q_var.set("")
        self._append(self.ai_text, f"\n  ▸ YOU: {query}\n\n  ▸ FVO AI:\n", "cyan")

        ctx = ""
        if self._scan_results:
            ports_str = ", ".join(
                f"{p}({v.get('service','?')})" for p, v in list(self._scan_results.items())[:10])
            ctx = f"[Scan context — target: {self.target_var.get()}, open ports: {ports_str}]"
        if self._current_geo:
            ctx += f"\n[Geo context — {self._current_geo.get('country','')}]"

        def run():
            self.exploit_engine.custom_query(
                query, context=ctx,
                on_token=lambda t: self.after(0, lambda: self._append(self.ai_text, t, "ai")),
                on_done=lambda _: self.after(0, lambda: self._append(self.ai_text, "\n\n", "")))
        self._ai_thread = threading.Thread(target=run, daemon=True)
        self._ai_thread.start()

    def _open_groq_settings(self):
        dialog = tk.Toplevel(self)
        dialog.title("Groq API Key")
        dialog.geometry("560x220")
        dialog.resizable(False, False)
        dialog.configure(bg=BG_DARK)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="GROQ API KEY",
            bg=BG_DARK,
            fg=CYAN_BRIGHT,
            font=("Consolas", 13, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(
            dialog,
            text="Paste your key below. It is kept only in memory until the app closes.",
            bg=BG_DARK,
            fg=GRAY_MID,
            font=FONT_SMALL,
        ).pack(anchor="w", padx=18, pady=(0, 12))

        key_var = tk.StringVar()
        key_entry = tk.Entry(
            dialog,
            textvariable=key_var,
            show="*",
            bg=BG_PANEL,
            fg=CYAN_BRIGHT,
            insertbackground=CYAN_BRIGHT,
            font=FONT_MAIN,
            relief="flat",
        )
        key_entry.pack(fill=tk.X, padx=18, ipady=6)
        key_entry.focus_set()

        buttons = tk.Frame(dialog, bg=BG_DARK)
        buttons.pack(fill=tk.X, padx=18, pady=16)

        def save_key():
            key = key_var.get().strip()
            if not key:
                messagebox.showwarning("Groq API Key", "Paste a Groq API key first.", parent=dialog)
                return
            self.groq.set_api_key(key)
            dialog.destroy()
            self._check_groq_status()
            self._append(self.ai_text, "\n  [GROQ API KEY SET FOR THIS SESSION]\n\n", "info")

        def clear_key():
            self.groq.clear_api_key()
            dialog.destroy()
            self._check_groq_status()
            self._append(self.ai_text, "\n  [GROQ API KEY CLEARED]\n\n", "medium")

        self._btn(buttons, "USE KEY FOR THIS SESSION", save_key, CYAN_BRIGHT).pack(
            side=tk.RIGHT, padx=(6, 0))
        self._btn(buttons, "CLEAR KEY", clear_key, RED_ALERT).pack(side=tk.RIGHT, padx=6)
        self._btn(buttons, "CANCEL", dialog.destroy, GRAY_MID).pack(side=tk.RIGHT)

    def _stop_ai(self):
        self.groq.stop()
        self._append(self.ai_text, "\n\n  [AI STOPPED]\n\n", "medium")

    def _lookup_cve(self):
        cve_id = self.cve_var.get().strip()
        if not cve_id:
            return
        self.nb.select(4)
        self._clear(self.cve_text)
        self._append(self.cve_text, f"  ◈ ANALYZING: {cve_id}\n\n", "header")
        self._set_status(f"AI ANALYZING {cve_id}…", CYAN_BRIGHT)

        def run():
            self.exploit_engine.explain_cve(
                cve_id,
                on_token=lambda t: self.after(0, lambda: self._append(self.cve_text, t, "info")),
                on_done=lambda _: (
                    self.after(0, lambda: self._append(self.cve_text, "\n\n  ✓ Done\n", "header")),
                    self.after(0, lambda: self._set_status(f"{cve_id} DONE", GREEN_BRIGHT))))
        threading.Thread(target=run, daemon=True).start()

    def _log(self, msg: str, tag: str = "dim"):
        ts = time.strftime("%H:%M:%S")
        try:
            self._append(self.console_text, f"[{ts}] {msg}\n", tag)
        except Exception:
            pass

    def _check_groq_status(self):
        def check():
            ok, has_model, models = self.groq.is_available()
            if ok and has_model:
                self.after(0, lambda: self.groq_indicator.config(
                    text="◉ GROQ: READY", fg=GREEN_BRIGHT))
                self.after(0, lambda: self._log("Groq + GPT-OSS 120B ready", "open"))
            elif ok:
                self.after(0, lambda: self.groq_indicator.config(
                    text="◉ GROQ: MODEL UNAVAILABLE", fg=AMBER))
                self.after(0, lambda: self._log(
                    f"Groq key works, but {self.groq.model} is not available for this key.", "medium"))
            elif self.groq.has_api_key():
                self.after(0, lambda: self.groq_indicator.config(
                    text="◉ GROQ: KEY ERROR", fg=RED_ALERT))
                self.after(0, lambda: self._log(
                    "Groq key could not be verified. Open GROQ API KEY to replace it.", "critical"))
            else:
                self.after(0, lambda: self.groq_indicator.config(
                    text="◉ GROQ: API KEY NEEDED", fg=AMBER))
                self.after(0, lambda: self._log(
                    "Add GROQ_API_KEY or click GROQ API KEY in the AI tab.", "medium"))
        threading.Thread(target=check, daemon=True).start()

    def _on_close(self):
        self.matrix_canvas.stop()
        self.globe.stop()
        self.port_scanner.stop()
        self.host_discovery.stop()
        self.groq.stop()
        self.destroy()
