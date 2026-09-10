BG_DEEP = "#020a04"
BG_DARK = "#050f07"
BG_PANEL = "#07140a"
BG_CARD = "#0a1e0e"
BG_HOVER = "#0d2612"

GREEN_BRIGHT = "#00ff41"
GREEN_MID = "#00cc33"
GREEN_DIM = "#007a1f"
GREEN_DARK = "#003d0f"
GREEN_GLOW = "#39ff14"

CYAN_BRIGHT = "#00e5ff"
CYAN_MID = "#00b8d4"
CYAN_DIM = "#006064"

AMBER = "#ffab00"
RED_ALERT = "#ff1744"
RED_MID = "#d50000"

WHITE = "#e0ffe8"
GRAY_MID = "#4a7a55"
GRAY_DIM = "#2a4a33"

CRITICAL_COLOR = "#ff1744"
HIGH_COLOR = "#ff6d00"
MEDIUM_COLOR = "#ffab00"
LOW_COLOR = "#76ff03"
INFO_COLOR = "#00e5ff"

FONT_MAIN = ("Consolas", 11)
FONT_LARGE = ("Consolas", 13, "bold")
FONT_TITLE = ("Consolas", 15, "bold")
FONT_BIG = ("Consolas", 20, "bold")
FONT_SMALL = ("Consolas", 9)
FONT_MONO = ("Courier New", 10)

SEVERITY_COLORS = {
    "CRITICAL": CRITICAL_COLOR,
    "HIGH": HIGH_COLOR,
    "MEDIUM": MEDIUM_COLOR,
    "LOW": LOW_COLOR,
    "INFO": INFO_COLOR,
}

TAG_COLORS = {
    "critical": {"bg": "#1a0000", "fg": CRITICAL_COLOR},
    "high": {"bg": "#1a0800", "fg": HIGH_COLOR},
    "medium": {"bg": "#1a1000", "fg": MEDIUM_COLOR},
    "low": {"bg": "#0a1500", "fg": LOW_COLOR},
    "open": {"bg": "#001a08", "fg": GREEN_BRIGHT},
    "info": {"bg": "#001a1a", "fg": CYAN_BRIGHT},
    "header": {"bg": "#000000", "fg": GREEN_GLOW},
}
