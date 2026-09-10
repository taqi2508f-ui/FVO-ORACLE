import tkinter as tk
import random
import math
from .styles import BG_DEEP, GREEN_BRIGHT, GREEN_MID, GREEN_DIM, GREEN_DARK


CHARS = (
    "01アイウエオカキクケコサシスセソタチツテトナニヌネノ"
    "ハヒフヘホマミムメモヤユヨラリルレロワヲン"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*<>/?|"
)


class MatrixRain(tk.Canvas):
    def __init__(self, parent, width=200, height=200, speed=60, **kwargs):
        super().__init__(
            parent, width=width, height=height,
            bg=BG_DEEP, highlightthickness=0, **kwargs
        )
        self.w = width
        self.h = height
        self.speed = speed
        self.cols = max(1, width // 14)
        self.drops = [random.randint(-50, 0) for _ in range(self.cols)]
        self.char_ids = {}
        self.running = False
        self._job = None
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.w = event.width
        self.h = event.height
        self.cols = max(1, self.w // 14)
        while len(self.drops) < self.cols:
            self.drops.append(random.randint(-50, 0))
        self.drops = self.drops[:self.cols]

    def start(self):
        self.running = True
        self._animate()

    def stop(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job)

    def _animate(self):
        if not self.running:
            return
        self.delete("all")

        col_w = max(1, self.w // self.cols)

        for i, y in enumerate(self.drops):
            char = random.choice(CHARS)
            x = i * col_w + col_w // 2

            if 0 <= y * 18 < self.h:
                self.create_text(
                    x, y * 18,
                    text=char, fill=GREEN_BRIGHT,
                    font=("Consolas", 11, "bold"),
                    anchor="center"
                )

            trail_len = random.randint(6, 18)
            for j in range(1, trail_len + 1):
                ty = y - j
                if 0 <= ty * 18 < self.h:
                    ratio = 1 - (j / trail_len)
                    intensity = int(ratio * 200)
                    green_val = max(20, intensity)
                    color = f"#00{green_val:02x}0{min(green_val // 4, 9):x}"
                    try:
                        trail_char = random.choice(CHARS)
                        self.create_text(
                            x, ty * 18,
                            text=trail_char,
                            fill=f"#{0:02x}{green_val:02x}{0:02x}",
                            font=("Consolas", 9),
                            anchor="center"
                        )
                    except Exception:
                        pass

            if self.drops[i] * 18 > self.h and random.random() > 0.95:
                self.drops[i] = random.randint(-30, -5)
            else:
                self.drops[i] += 1

        self._job = self.after(self.speed, self._animate)


class GlowLabel(tk.Label):
    def __init__(self, parent, text="", glow_color=GREEN_BRIGHT, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.glow_color = glow_color
        self._phase = 0
        self._pulsing = False
        self._job = None

    def start_pulse(self, speed=80):
        self._pulsing = True
        self._pulse(speed)

    def stop_pulse(self):
        self._pulsing = False
        if self._job:
            self.after_cancel(self._job)

    def _pulse(self, speed):
        if not self._pulsing:
            return
        self._phase += 0.15
        intensity = int((math.sin(self._phase) + 1) / 2 * 180 + 75)
        r = min(255, intensity // 4)
        g = min(255, intensity)
        b = min(255, intensity // 8)
        color = f"#{r:02x}{g:02x}{b:02x}"
        try:
            self.config(fg=color)
        except Exception:
            pass
        self._job = self.after(speed, lambda: self._pulse(speed))


class ThreeDFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        from .styles import BG_CARD, GREEN_DIM, BG_PANEL
        bg = kwargs.pop("bg", BG_CARD)
        super().__init__(parent, bg=bg, **kwargs)
        self._shadow = tk.Frame(parent, bg=GREEN_DIM, height=2)


class ScanProgressBar(tk.Canvas):
    def __init__(self, parent, width=400, height=22, **kwargs):
        from .styles import BG_PANEL, GREEN_BRIGHT, GREEN_DIM, BG_DARK
        super().__init__(
            parent, width=width, height=height,
            bg=BG_PANEL, highlightthickness=1,
            highlightbackground=GREEN_DIM, **kwargs
        )
        self.w = width
        self.h = height
        self._progress = 0
        self._label = ""
        self._scan_phase = 0
        self._job = None
        self._animating = False
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.w = event.width
        self.h = event.height
        self._draw()

    def set_progress(self, value: float, label: str = ""):
        self._progress = max(0.0, min(1.0, value))
        self._label = label
        self._draw()

    def _draw(self):
        from .styles import BG_PANEL, GREEN_BRIGHT, GREEN_MID, GREEN_DIM, CYAN_BRIGHT
        self.delete("all")
        self.create_rectangle(0, 0, self.w, self.h, fill="#020a04", outline="")

        if self._progress > 0:
            fill_w = int(self.w * self._progress)
            for x in range(0, fill_w, 2):
                ratio = x / max(1, fill_w)
                g = int(180 + ratio * 75)
                r = int(ratio * 30)
                color = f"#{r:02x}{min(255,g):02x}{int(ratio*20):02x}"
                self.create_line(x, 0, x, self.h, fill=color)

            self.create_line(fill_w, 0, fill_w, self.h, fill=GREEN_BRIGHT, width=2)

        if self._animating:
            self._scan_phase = (self._scan_phase + 3) % self.w
            for i in range(0, 6):
                sx = (self._scan_phase + i * 8) % self.w
                alpha = 1 - i / 6
                g = int(alpha * 200)
                self.create_line(sx, 0, sx, self.h, fill=f"#00{g:02x}00")

        pct = int(self._progress * 100)
        label_text = f"{self._label}  {pct}%" if self._label else f"{pct}%"
        self.create_text(
            self.w // 2, self.h // 2,
            text=label_text,
            fill=GREEN_BRIGHT if self._progress < 1 else "#39ff14",
            font=("Consolas", 9, "bold"),
            anchor="center"
        )

    def start_animation(self):
        self._animating = True
        self._animate()

    def stop_animation(self):
        self._animating = False
        if self._job:
            self.after_cancel(self._job)

    def _animate(self):
        if not self._animating:
            return
        self._draw()
        self._job = self.after(50, self._animate)
