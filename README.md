# FVO-ORACLE

**Custom Python vulnerability scanner with AI-powered exploit and defense analysis.**
No nmap dependency — 100% original socket-based scanning engine, wrapped in a hacker-styled Tkinter GUI with a live matrix rain effect and animated globe.

![Platform](https://img.shields.io/badge/platform-Windows%2010-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/use-authorized%20testing%20only-red)

---

## Overview

FVO combines a custom-built network reconnaissance engine with an AI analysis layer (Groq API, GPT-OSS 120B) to take you from **raw port scan → vulnerability signatures → exploit chain and hardening guidance**, all inside one desktop tool.

## Features

### 🔌 Port Scanner
- Custom multi-threaded TCP scanner — no nmap
- Banner grabbing and service detection
- Scan modes: Common Ports, Top 1024, Full 65535, Custom Range, Stealth
- Adjustable thread count (10–500)

### 🌐 Host Discovery
- ICMP ping sweep with TCP fallback
- Auto-detects local network range
- Hostname reverse lookup
- MAC address retrieval (Windows ARP)

### 🛡️ Vulnerability Analysis
- Signature-based CVE matching on service banners
- Dangerous port detection
- SSL/TLS weakness detection
- Severity ranking: CRITICAL / HIGH / MEDIUM / LOW

### 🤖 AI Exploit Engine (Groq + GPT-OSS 120B)
- Full scan analysis: attack surface, exploit chains, hardening guide
- Offensive breakdown — how an attacker would exploit each finding
- Defensive breakdown — detection, patching, monitoring guidance
- Free-chat mode for ad-hoc security questions

### 🔍 CVE Lookup
- AI-powered deep dive on any CVE ID
- Mechanics, affected versions, PoC methodology
- Real-world exploitation history
- Defensive countermeasures

## Requirements

- Windows 10
- Python 3.10+ (3.14.2 recommended) — [python.org](https://python.org)
  - Ensure **"Add Python to PATH"** is checked during install
- Groq API key for AI features — [console.groq.com/keys](https://console.groq.com/keys)

## Installation

```bash
git clone https://github.com/taqi2508f-ui/FVO-ORACLE.git
cd FVO_project
requirements.bat
```

## Usage

```bash
launch.bat
```
or
```bash
python main.py
```

Set your Groq API key via the **GROQ API KEY** button in the AI tab, or export it before launch:
```bash
set GROQ_API_KEY=your_key_here
```

## Project Structure

```
FVO_project/
├── main.py                 # Entry point
├── launch.bat               # Windows launcher
├── requirements.bat          # Dependency installer
├── requirements.txt          # Python packages
├── scanner/
│   ├── port_scanner.py       # Custom TCP port scanner
│   ├── host_discovery.py     # Network host discovery
│   ├── geo_lookup.py         # Geolocation lookup
│   └── vuln_scanner.py       # Vulnerability signature engine
├── ai/
│   ├── ollama_client.py      # Groq API client (GPT-OSS 120B)
│   └── exploit_engine.py     # AI exploit & defense prompts
└── ui/
    ├── app.py                # Main application window
    ├── styles.py              # Hacker color theme
    ├── matrix_canvas.py        # Matrix rain + UI components
    └── globe_widget.py         # Animated globe widget
```

## Tech Stack

Python · Tkinter · Groq API (GPT-OSS 120B) · Custom socket-based scanning (no nmap)

## Disclaimer

This tool is for **authorized penetration testing and educational use only**. Only scan systems you own or have explicit written permission to test. The author accepts no responsibility for misuse.

---

Built by **CYBER-TAQI**
