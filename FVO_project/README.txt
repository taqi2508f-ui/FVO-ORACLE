
 ███████╗██╗   ██╗ ██████╗     ████████╗ ██████╗  ██████╗ ██╗
 ██╔════╝██║   ██║██╔═══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
 █████╗  ██║   ██║██║   ██║       ██║   ██║   ██║██║   ██║██║
 ██╔══╝  ╚██╗ ██╔╝██║   ██║       ██║   ██║   ██║██║   ██║██║
 ██║      ╚████╔╝ ╚██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗
 ╚═╝       ╚═══╝   ╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝

 FVO — Eagle Vulnerability Oracle v1.0
 ========================================
 Custom Python vulnerability scanning tool with AI analysis.
 NO NMAP — 100% custom socket-based engine.

 REQUIREMENTS
 ============
 - Windows 10
 - Python 3.10+ (recommended: 3.14.2) — https://python.org
   > Make sure "Add Python to PATH" is checked during install
 - Groq API key (for AI features) — https://console.groq.com/keys
   > Use the GROQ API KEY button in the AI tab, or set GROQ_API_KEY before launch.

 QUICK START
 ===========
 1. Double-click requirements.bat  (installs all dependencies)
 2. Double-click launch.bat        (starts the tool)
      OR
    python main.py

 FEATURES
 ========
 PORT SCANNER (Tab 1)
   - Custom multi-threaded TCP scanner (no nmap)
   - Banner grabbing / service detection
   - Modes: Common Ports, Top 1024, Full 65535, Custom Range, Stealth
   - Adjustable thread count (10–500)

 HOST DISCOVERY (Tab 2)
   - ICMP ping sweep + TCP fallback
   - Auto-detects your local network range
   - Hostname reverse lookup
   - MAC address retrieval (Windows ARP)

 VULNERABILITIES (Tab 3)
   - Signature-based CVE matching on banners
   - Dangerous port detection
   - SSL/TLS weakness detection
   - Severity ranking: CRITICAL / HIGH / MEDIUM / LOW

 AI EXPLOIT ENGINE (Tab 4) — Requires Groq + GPT-OSS 120B
   - Full scan analysis: attack surface, exploit chains, hardening guide
   - Offensive: how an attacker would exploit each vulnerability
   - Defensive: detection, patching, monitoring guidance
   - Free-chat AI for any security question

 CVE LOOKUP (Tab 5)
   - AI-powered deep analysis of any CVE
   - Mechanics, affected versions, PoC methodology
   - Real-world exploitation history
   - Defensive countermeasures

 FOLDER STRUCTURE
 ================
 main.py             — Entry point
 launch.bat          — Windows launcher
 requirements.bat    — Dependency installer
 requirements.txt    — Python packages
 scanner/
   port_scanner.py   — Custom TCP port scanner
   host_discovery.py — Network host discovery
   vuln_scanner.py   — Vulnerability signature engine
 ai/
   ollama_client.py  — Groq API client (GPT-OSS 120B)
   exploit_engine.py — AI exploit & defense prompts
 ui/
   app.py            — Main application window
   styles.py         — Hacker color theme
   matrix_canvas.py  — Matrix rain + UI components

 DISCLAIMER
 ==========
 This tool is for authorized penetration testing and educational use only.
 Only scan systems you own or have explicit written permission to test.
 The author accepts no responsibility for misuse.

