import tkinter as tk
import math
import threading
import time
from typing import Optional, Tuple


LAND_POINTS = [
    # North America
    (70,-140),(72,-130),(71,-120),(70,-110),(68,-90),(65,-85),(62,-75),(60,-65),
    (58,-68),(55,-60),(50,-55),(48,-53),(47,-54),(50,-56),(52,-58),(55,-62),
    (57,-60),(60,-64),(63,-68),(65,-72),(68,-78),(70,-80),(72,-85),(72,-95),
    (70,-100),(68,-108),(65,-118),(62,-128),(59,-135),(56,-130),(52,-128),
    (49,-124),(47,-122),(45,-124),(42,-124),(38,-122),(35,-120),(32,-117),
    (30,-110),(28,-105),(25,-100),(22,-98),(20,-87),(16,-87),(15,-85),
    (10,-83),(8,-77),(8,-80),(10,-85),(12,-87),(15,-90),(18,-92),
    (20,-90),(22,-88),(25,-90),(28,-95),(30,-97),(32,-100),(35,-102),
    (38,-105),(40,-108),(42,-110),(44,-112),(46,-112),(48,-110),(50,-108),
    (52,-110),(55,-115),(57,-120),(58,-125),(55,-130),(50,-125),(48,-122),
    (45,-120),(42,-118),(40,-120),(38,-122),(37,-120),(35,-118),(33,-115),
    (32,-115),(30,-110),(28,-108),(26,-103),(24,-99),(22,-98),(20,-95),
    (49,-95),(50,-92),(52,-88),(54,-84),(56,-78),(58,-72),(60,-68),
    (62,-72),(64,-78),(65,-82),(67,-86),(68,-90),(70,-95),(72,-100),
    (74,-105),(76,-110),(78,-114),(80,-115),(82,-80),(80,-70),(78,-68),
    (76,-72),(74,-78),(72,-82),(70,-82),(68,-82),(66,-78),(64,-72),
    (62,-68),(60,-64),(58,-60),(56,-58),(54,-58),(52,-56),(50,-56),
    # South America
    (12,-72),(10,-62),(8,-60),(5,-52),(2,-52),(0,-50),(-3,-42),
    (-5,-35),(-8,-35),(-10,-37),(-12,-40),(-15,-42),(-18,-40),
    (-20,-40),(-23,-43),(-25,-48),(-28,-50),(-30,-52),(-32,-52),
    (-34,-54),(-38,-58),(-40,-62),(-42,-65),(-45,-67),(-48,-68),
    (-50,-68),(-52,-68),(-54,-68),(-55,-67),(-53,-63),(-50,-60),
    (-48,-58),(-45,-55),(-42,-52),(-40,-50),(-38,-48),(-35,-45),
    (-32,-42),(-28,-38),(-25,-35),(-22,-42),(-20,-45),(-18,-48),
    (-15,-50),(-12,-52),(-10,-50),(-8,-48),(-5,-45),(-2,-45),
    (0,-48),(2,-50),(5,-53),(8,-58),(10,-62),
    (-20,-60),(-22,-62),(-25,-58),(-28,-55),(-30,-56),(-32,-58),
    (-35,-60),(-38,-62),(-40,-64),(-42,-66),(-45,-68),(-48,-70),
    # Europe
    (71,28),(70,25),(68,20),(65,14),(62,5),(59,5),(56,8),(54,10),
    (52,5),(50,2),(48,-2),(46,-2),(43,-2),(41,-8),(38,-8),(36,-5),
    (36,2),(38,8),(40,5),(42,2),(44,8),(46,12),(48,15),(50,18),
    (52,20),(54,18),(56,22),(58,25),(60,28),(62,30),(64,26),(66,22),
    (68,18),(70,20),(72,24),(73,22),(72,18),(70,14),(68,10),(65,8),
    (62,8),(60,5),(58,5),(56,10),(54,12),(52,12),(50,8),(48,8),
    (46,6),(44,8),(42,12),(40,15),(38,15),(36,12),(38,8),(40,5),
    (42,3),(44,0),(46,-2),(48,0),(50,3),(52,5),(54,8),(56,12),
    (58,15),(60,18),(62,22),(64,26),(66,28),(68,30),(70,28),
    (48,20),(50,22),(52,24),(54,20),(56,22),(58,24),(60,28),
    (62,25),(60,24),(58,22),(56,18),(54,15),(52,15),(50,15),
    (48,15),(46,15),(44,12),(42,15),(40,18),(38,20),(36,22),
    # Africa
    (36,10),(34,10),(30,32),(28,30),(25,25),(22,20),(18,15),
    (15,12),(12,15),(10,12),(8,5),(5,2),(2,10),(0,10),
    (-2,12),(-5,12),(-8,15),(-10,18),(-12,15),(-15,12),
    (-18,12),(-20,15),(-22,18),(-25,20),(-28,18),(-30,18),
    (-32,20),(-34,22),(-35,25),(-34,28),(-32,30),(-30,32),
    (-28,33),(-25,35),(-22,35),(-20,35),(-18,38),(-15,40),
    (-12,42),(-10,42),(-8,40),(-5,38),(-2,35),(0,35),
    (2,40),(5,42),(8,45),(10,42),(12,42),(15,40),(18,38),
    (20,38),(22,38),(25,35),(28,32),(30,30),(32,28),(34,25),
    (36,22),(38,18),(40,15),(38,12),(36,10),
    (15,35),(18,38),(20,35),(22,32),(25,30),(28,28),(30,32),
    # Asia
    (70,140),(68,135),(65,130),(62,140),(60,143),(58,140),
    (55,135),(52,140),(50,142),(48,140),(45,135),(42,130),
    (40,128),(38,125),(35,120),(32,120),(30,122),(28,120),
    (25,118),(22,114),(20,110),(18,108),(15,108),(12,109),
    (10,104),(8,98),(5,100),(2,103),(0,104),(-2,108),
    (-5,110),(-8,115),(-10,120),(-8,125),(-5,120),(-2,115),
    (0,110),(2,108),(5,103),(8,98),(10,92),(12,80),
    (10,78),(8,77),(10,74),(12,70),(15,72),(18,72),
    (20,70),(22,68),(25,65),(28,60),(30,55),(32,50),
    (35,50),(38,48),(40,50),(42,52),(44,50),(46,48),
    (48,46),(50,48),(52,50),(54,52),(56,55),(58,60),
    (60,65),(62,68),(64,72),(66,70),(68,68),(70,68),
    (72,68),(73,68),(72,72),(70,75),(68,80),(66,82),
    (64,80),(62,75),(60,70),(58,65),(55,60),(52,58),
    (50,55),(48,52),(45,50),(42,50),(40,52),(38,55),
    (35,60),(32,62),(30,65),(28,68),(25,70),(22,70),
    (20,72),(18,72),(15,78),(12,80),(10,80),(8,77),
    (55,80),(58,82),(60,85),(62,88),(64,90),(66,88),
    (68,86),(70,82),(72,82),(73,80),(72,78),(70,78),
    (68,80),(66,82),(64,85),(62,88),(60,90),(58,88),
    (56,85),(55,82),(57,80),(60,78),(62,80),(64,82),
    (35,35),(38,38),(40,40),(42,42),(44,40),(46,38),
    (48,38),(50,40),(52,42),(50,45),(48,48),(46,50),
    (44,52),(42,55),(40,55),(38,52),(36,50),(35,48),
    # Australia
    (-15,130),(-12,135),(-15,140),(-18,145),(-22,150),
    (-25,153),(-28,153),(-30,153),(-32,152),(-34,150),
    (-36,148),(-38,145),(-38,140),(-36,136),(-35,135),
    (-32,132),(-30,128),(-27,125),(-25,120),(-22,115),
    (-20,118),(-18,122),(-15,125),(-13,130),(-15,130),
    (-22,128),(-25,132),(-28,135),(-30,138),(-28,140),
    (-25,138),(-22,132),
    # Japan
    (43,141),(41,140),(38,140),(36,138),(34,135),(34,132),
    (33,131),(34,130),(36,130),(38,131),(40,132),(42,140),
    (33,130),(31,130),(30,131),(31,132),(32,131),
    # UK
    (58,-3),(56,-4),(54,-3),(52,-2),(51,0),(52,2),(54,0),
    (56,-2),(58,0),(60,-2),(58,-4),
    # Indonesia
    (5,96),(3,98),(1,100),(-1,104),(-3,106),(-5,108),
    (-7,110),(-8,115),(-8,120),(-8,125),(-7,130),(-5,132),
    (-3,130),(-1,128),(1,125),(3,120),(5,118),(3,115),(1,110),
    # Greenland
    (83,-30),(82,-20),(80,-18),(78,-20),(76,-22),(74,-25),
    (72,-25),(70,-23),(68,-24),(70,-30),(72,-38),(74,-42),
    (76,-45),(78,-50),(80,-52),(82,-48),(83,-40),
]


def _project_3d(lat_deg, lon_deg, rot_x, rot_y, radius, cx, cy):
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg + rot_y)

    x = math.cos(lat) * math.cos(lon)
    y = math.sin(lat)
    z = math.cos(lat) * math.sin(lon)

    cos_rx = math.cos(math.radians(rot_x))
    sin_rx = math.sin(math.radians(rot_x))
    y2 = y * cos_rx - z * sin_rx
    z2 = y * sin_rx + z * cos_rx

    if z2 < 0:
        return None, None, False

    sx = cx + x * radius
    sy = cy - y2 * radius
    return sx, sy, True


class Globe3D(tk.Canvas):
    def __init__(self, parent, size=300, **kwargs):
        super().__init__(
            parent, width=size, height=size,
            bg="#000d02", highlightthickness=0, **kwargs
        )
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.radius = int(size * 0.42)
        self.rot_y = 0.0
        self.rot_x = -15.0
        self.spin_speed = 0.5
        self.running = False
        self._job = None

        self.target_lat = None
        self.target_lon = None
        self.target_country = ""
        self.target_pulse = 0.0
        self._highlight_frames = 0

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        s = min(event.width, event.height)
        self.size = s
        self.cx = s // 2
        self.cy = s // 2
        self.radius = int(s * 0.42)

    def set_target(self, lat: float, lon: float, country: str = ""):
        self.target_lat = lat
        self.target_lon = lon
        self.target_country = country
        self._highlight_frames = 120
        self.target_pulse = 0.0

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
        self.rot_y += self.spin_speed
        if self.rot_y >= 360:
            self.rot_y -= 360
        if self._highlight_frames > 0:
            self._highlight_frames -= 1
            self.target_pulse += 0.25
        self._draw()
        self._job = self.after(30, self._animate)

    def _draw(self):
        self.delete("all")
        cx, cy, r = self.cx, self.cy, self.radius

        # Deep space background
        self.create_oval(
            cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8,
            fill="#000a18", outline="#001a30", width=2
        )

        # Atmosphere glow rings
        for i in range(5):
            pad = 2 + i * 3
            alpha = 255 - i * 45
            g_val = max(0, 80 - i * 15)
            b_val = max(0, 180 - i * 35)
            color = f"#00{g_val:02x}{b_val:02x}"
            self.create_oval(
                cx - r - pad, cy - r - pad,
                cx + r + pad, cy + r + pad,
                outline=color, width=1
            )

        # Ocean base
        self.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="#001a2e", outline="#003366", width=1
        )

        # Ocean shading gradient (concentric bands)
        steps = 12
        for i in range(steps, 0, -1):
            ratio = i / steps
            fr = int(0 + ratio * 0)
            fg = int(20 + ratio * 40)
            fb = int(35 + ratio * 60)
            shade_r = int(r * ratio * 0.95)
            self.create_oval(
                cx - shade_r, cy - shade_r,
                cx + shade_r, cy + shade_r,
                fill=f"#{fr:02x}{fg:02x}{fb:02x}", outline=""
            )

        # Latitude grid lines
        for lat in range(-75, 90, 15):
            pts = []
            for lon_step in range(0, 361, 4):
                lon = lon_step - 180
                sx, sy, vis = _project_3d(lat, lon, self.rot_x, self.rot_y, r, cx, cy)
                if vis:
                    pts.append((sx, sy))
                else:
                    if len(pts) >= 4:
                        flat = [v for p in pts for v in p]
                        self.create_line(*flat, fill="#003a55", width=1, smooth=False)
                    pts = []
            if len(pts) >= 4:
                flat = [v for p in pts for v in p]
                self.create_line(*flat, fill="#003a55", width=1, smooth=False)

        # Longitude grid lines
        for lon_offset in range(0, 180, 20):
            for lon_base in [lon_offset, lon_offset + 180]:
                pts = []
                for lat_step in range(-90, 91, 3):
                    sx, sy, vis = _project_3d(lat_step, lon_base, self.rot_x, self.rot_y, r, cx, cy)
                    if vis:
                        pts.append((sx, sy))
                    else:
                        if len(pts) >= 4:
                            flat = [v for p in pts for v in p]
                            self.create_line(*flat, fill="#003a55", width=1)
                        pts = []
                if len(pts) >= 4:
                    flat = [v for p in pts for v in p]
                    self.create_line(*flat, fill="#003a55", width=1)

        # Land masses
        for lat_deg, lon_deg in LAND_POINTS:
            sx, sy, vis = _project_3d(lat_deg, lon_deg, self.rot_x, self.rot_y, r, cx, cy)
            if vis:
                pt_size = 2
                self.create_oval(
                    sx - pt_size, sy - pt_size,
                    sx + pt_size, sy + pt_size,
                    fill="#00b34a", outline=""
                )

        # Equator line highlight
        pts = []
        for lon_step in range(0, 361, 3):
            lon = lon_step - 180
            sx, sy, vis = _project_3d(0, lon, self.rot_x, self.rot_y, r, cx, cy)
            if vis:
                pts.append((sx, sy))
            else:
                if len(pts) >= 4:
                    flat = [v for p in pts for v in p]
                    self.create_line(*flat, fill="#004d2a", width=1)
                pts = []

        # Target IP location marker
        if self.target_lat is not None and self._highlight_frames > 0:
            tx, ty, t_vis = _project_3d(
                self.target_lat, self.target_lon,
                self.rot_x, self.rot_y, r, cx, cy
            )
            if t_vis:
                pulse = abs(math.sin(self.target_pulse))
                ring_r = int(6 + pulse * 14)

                for ring in range(3):
                    rr = ring_r + ring * 6
                    alpha = int((1 - ring / 3) * 255)
                    self.create_oval(
                        tx - rr, ty - rr, tx + rr, ty + rr,
                        outline=f"#ff{int(alpha*0.3):02x}00",
                        width=2 - ring
                    )

                self.create_oval(tx - 5, ty - 5, tx + 5, ty + 5, fill="#ff3300", outline="#ff6600", width=2)
                self.create_oval(tx - 2, ty - 2, tx + 2, ty + 2, fill="#ffffff", outline="")

                line_color = f"#ff{int(pulse * 150):02x}00"
                self.create_line(tx - 12, ty, tx + 12, ty, fill=line_color, width=1)
                self.create_line(tx, ty - 12, tx, ty + 12, fill=line_color, width=1)

        # Specular highlight (top-left sheen)
        self.create_oval(
            cx - r + 8, cy - r + 8,
            cx - r + r // 2, cy - r + r // 2,
            fill="#001a26", outline=""
        )

        # Globe border
        self.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline="#00ff88", width=1, fill=""
        )

        # Rotation indicator tick
        tick_lon = -self.rot_y % 360 - 180
        tick_x, tick_y, tick_vis = _project_3d(0, tick_lon, self.rot_x, self.rot_y, r, cx, cy)
        if tick_vis:
            self.create_line(cx, cy - r - 2, cx, cy - r - 8, fill="#00ff88", width=2)
