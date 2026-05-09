# Git Gud Counter

import sys
import copy
import html as _html
import re as _re
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import json
import os
import threading
import time
import base64
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

APP_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)
DATA_DIR      = os.path.join(APP_DIR, "data")
LOGOS_DIR     = os.path.join(DATA_DIR, "logos")
TEMPLATES_DIR = os.path.join(DATA_DIR, "templates")
ASSETS_DIR    = os.path.join(APP_DIR,  "assets")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
STATE_FILE    = os.path.join(DATA_DIR, "state.json")
OVERLAY_PORT  = 7373

for d in [DATA_DIR, LOGOS_DIR, TEMPLATES_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

DEFAULT_SETTINGS = {
    "overlay": {
        "header_color":      "#cc0000",
        "header_alpha":      1.0,
        "header_text_color": "#ffffff",
        "body_bg":           "#1a1a1a",
        "body_alpha":        1.0,
        "body_text_color":   "#ffffff",
        "pb_color":          "#ffd700",
        "row_alt_color":     "#222222",
        "accent_color":      "#00ff88",
        "title":             "Sekiro - No Hit Run",
        "logo_path":         "",
        "font_header":       "Segoe UI",
        "font_table":        "Segoe UI",
        "size_title":        18,
        "size_subtitle":     12,
        "size_timer":        22,
        "size_table":        14,
        "size_total":        13,
        "show_timer":        True,
        "show_pb":           True,
        "show_blocks":       True,
        "show_path_hits":    True,
        "bg_image_path":     "",
        "bg_image_alpha":    0.4,
        "frame_image_path":  "",
        "width":             600,
    },
    "hotkeys": {
        "boss_hit":    "F1",
        "block":       "F2",
        "path_hit":    "F3",
        "start_timer": "F4",
        "stop_timer":  "F5",
        "reset_current":"F6",
        "save_pb":     "F7",
        "next_boss":   "F8",
        "prev_boss":   "F9",
        "reset_run":   "F10",
    }
}

DEFAULT_STATE = {
    "active_template": None,
    "current_boss_index": 0,
    "timer_running": False,
    "timer_elapsed": 0.0,
    "pb_time": None,
}

DEFAULT_TEMPLATE = {
    "name": "Mi Template",
    "game": "Mi Juego",
    "bosses": [
        {"name": "Boss 1", "hits": 0, "blocks": 0, "path_hits": 0, "pb_hits": 0},
        {"name": "Boss 2", "hits": 0, "blocks": 0, "path_hits": 0, "pb_hits": 0},
    ]
}

GAME_ASSETS = {
    "sekiro":      "sekiro_logo.png",
    "ds1":         "ds1_logo.png",
    "ds2":         "ds2_logo.png",
    "ds3":         "ds3_logo.png",
    "elden_ring":  "elden_ring_logo.png",
    "bloodborne":  "bloodborne_logo.png",
    "demon_souls": "demon_souls_logo.png",
}

def _boss(name):
    return {"name": name, "hits": 0, "blocks": 0, "path_hits": 0, "pb_hits": 0}

PRESET_TEMPLATES = {
    "sekiro_shura": {
        "name":       "Sekiro – Shura",
        "game":       "Sekiro: Shadows Die Twice",
        "game_key":   "sekiro",
        "run_title":  "Sekiro – Shura No Hit",
        "bosses": [_boss(n) for n in [
            "Genichiro",
            "Ogre",
            "Gyobu Masataka Oniwa",
            "Blazing Bull",
            "Genichiro, Way of Tomoe",
            "Gunfort",
            "Armored Warrior",
            "Folding Screen Monkeys",
            "Long-arm Centipede Giraffe",
            "Snake Eyes Shirafuji",
            "Corrupted Monk",
            "Guardian Ape",
            "Emma, the Gentle Blade",
            "Isshin Ashina",
        ]],
    },
    "sekiro_immortal_severance": {
        "name":       "Sekiro – Immortal Severance",
        "game":       "Sekiro: Shadows Die Twice",
        "game_key":   "sekiro",
        "run_title":  "Sekiro – Immortal Severance No Hit",
        "bosses": [_boss(n) for n in [
            "Genichiro",
            "Ogre",
            "Gyobu Masataka Oniwa",
            "Blazing Bull",
            "Genichiro, Way of Tomoe",
            "Gunfort",
            "Armored Warrior",
            "Folding Screen Monkeys",
            "Long-arm Centipede Giraffe",
            "Snake Eyes Shirafuji",
            "Corrupted Monk",
            "Guardian Ape",
            "Great Shinobi Owl",
            "True Corrupted Monk",
            "Divine Dragon",
            "Isshin, the Sword Saint",
        ]],
    },
    "sekiro_purification": {
        "name":       "Sekiro – Purification",
        "game":       "Sekiro: Shadows Die Twice",
        "game_key":   "sekiro",
        "run_title":  "Sekiro – Purification No Hit",
        "bosses": [_boss(n) for n in [
            "Genichiro",
            "Ogre",
            "Gyobu Masataka Oniwa",
            "Blazing Bull",
            "Genichiro, Way of Tomoe",
            "Gunfort",
            "Armored Warrior",
            "Folding Screen Monkeys",
            "Long-arm Centipede Giraffe",
            "Snake Eyes Shirafuji",
            "Corrupted Monk",
            "Guardian Ape",
            "Great Shinobi Owl",
            "True Corrupted Monk",
            "Divine Dragon",
            "Isshin, the Sword Saint",
            "Guardian Apes",
            "Juzou the Drunkard",
            "Lady Butterfly",
            "Juzou the Drunkard (2nd)",
            "Owl (Father)",
        ]],
    },
    "ds1": {
        "name":       "Dark Souls",
        "game":       "Dark Souls: Remastered",
        "game_key":   "ds1",
        "run_title":  "Dark Souls No Hit",
        "bosses": [_boss(n) for n in [
            "Asylum Demon",
            "Bell Gargoyles",
            "Quelaag",
            "Ceaseless Discharge",
            "Stray Demon",
            "Iron Golem",
            "Ornstein & Smough",
            "Pinwheel",
            "Nito",
            "Seath the Scaleless",
            "Sif, the Great Grey Wolf",
            "Bed of Chaos",
            "Four Kings",
            "Gwyn, Lord of Cinder",
        ]],
    },
}


def _safe_filename(name: str) -> str:
    sanitized = _re.sub(r'[^\w\-]', '_', name)
    return sanitized[:64] or "template"


def _safe_image_path(path: str) -> str:
    if not path:
        return ""
    try:
        resolved = os.path.realpath(os.path.abspath(path))
    except:
        return ""
    allowed_dirs = [
        os.path.realpath(LOGOS_DIR),
        os.path.realpath(ASSETS_DIR),
    ]
    for allowed in allowed_dirs:
        if resolved.startswith(allowed + os.sep) or resolved == allowed:
            ext = os.path.splitext(resolved)[1].lower()
            if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
                return resolved
    return ""


def _safe_color(value: str, default: str) -> str:
    if isinstance(value, str) and _re.match(r'^#[0-9a-fA-F]{3,6}$', value.strip()):
        return value.strip()
    return default


def _safe_alpha(value, default: float) -> float:
    try:
        v = float(value)
        return max(0.0, min(1.0, v))
    except:
        return default


def _safe_int(value, default: int, lo: int, hi: int) -> int:
    try:
        v = int(value)
        return max(lo, min(hi, v))
    except:
        return default


def _safe_font(value: str, default: str) -> str:
    if not isinstance(value, str):
        return default
    cleaned = _re.sub(r'[^\w\s\-]', '', value).strip()
    return cleaned[:64] or default


def _esc(value) -> str:
    return _html.escape(str(value), quote=True)


def seed_preset_templates(dm):
    for tid, tmpl in PRESET_TEMPLATES.items():
        if tid not in dm.templates:
            to_save = {k: v for k, v in tmpl.items() if k != "run_title"}
            dm.save_template(tid, to_save)

class DataManager:
    def __init__(self):
        self._lock     = threading.Lock()
        self.settings  = self._load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.state     = self._load_json(STATE_FILE,    DEFAULT_STATE)
        self.templates = self._load_templates()
        self.active_template = None
        seed_preset_templates(self)
        self.templates = self._load_templates()
        self._load_active_template()
        self._img_cache: dict = {}

    def _load_json(self, path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return copy.deepcopy(default)
            merged = {**default, **data}
            for k in default:
                if isinstance(default[k], dict) and k in merged:
                    if not isinstance(merged[k], dict):
                        merged[k] = copy.deepcopy(default[k])
                    else:
                        merged[k] = {**default[k], **merged[k]}
            return merged
        except:
            return copy.deepcopy(default)

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def save_state(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _load_templates(self):
        templates = {}
        for fname in os.listdir(TEMPLATES_DIR):
            if fname.endswith(".json"):
                path = os.path.join(TEMPLATES_DIR, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        tmpl = json.load(f)
                    for boss in tmpl.get("bosses", []):
                        boss.setdefault("hits",      0)
                        boss.setdefault("blocks",    0)
                        boss.setdefault("path_hits", 0)
                        boss.setdefault("pb_hits",   0)
                    templates[fname[:-5]] = tmpl
                except:
                    pass
        return templates

    def save_template(self, tid, template):
        safe_tid = _safe_filename(tid)
        self.templates[safe_tid] = template
        path = os.path.join(TEMPLATES_DIR, f"{safe_tid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

    def delete_template(self, tid):
        safe_tid = _safe_filename(tid)
        self.templates.pop(safe_tid, None)
        p = os.path.join(TEMPLATES_DIR, f"{safe_tid}.json")
        if os.path.exists(p):
            os.remove(p)

    def _load_active_template(self):
        aid = self.state.get("active_template")
        if aid and aid in self.templates:
            self.active_template = self._fix_template(copy.deepcopy(self.templates[aid]))
        elif self.templates:
            first = next(iter(self.templates))
            self.active_template = self._fix_template(copy.deepcopy(self.templates[first]))
            self.state["active_template"] = first
        else:
            self.save_template("default", copy.deepcopy(DEFAULT_TEMPLATE))
            self.active_template = self._fix_template(copy.deepcopy(DEFAULT_TEMPLATE))
            self.state["active_template"] = "default"

    def set_active_template(self, tid):
        if tid in self.templates:
            self.active_template = self._fix_template(copy.deepcopy(self.templates[tid]))
            self.state["active_template"] = tid
            self.state["current_boss_index"] = 0
            for boss in self.active_template["bosses"]:
                boss["hits"] = 0
                boss["blocks"] = 0
                boss["path_hits"] = 0
            self.save_state()

    def reset_run(self):
        self.state["current_boss_index"] = 0
        if self.active_template:
            for boss in self.active_template["bosses"]:
                boss["hits"] = 0
                boss["blocks"] = 0
                boss["path_hits"] = 0

    @staticmethod
    def _fix_boss(boss: dict) -> dict:
        boss.setdefault("hits",      0)
        boss.setdefault("blocks",    0)
        boss.setdefault("path_hits", 0)
        boss.setdefault("pb_hits",   0)
        return boss

    def _fix_template(self, tmpl: dict) -> dict:
        for boss in tmpl.get("bosses", []):
            self._fix_boss(boss)
        return tmpl

    def get_logo_b64(self):
        return self._img_b64(self.settings["overlay"].get("logo_path", ""))

    def get_bg_b64(self):
        return self._img_b64(self.settings["overlay"].get("bg_image_path", ""))

    def get_frame_b64(self):
        return self._img_b64(self.settings["overlay"].get("frame_image_path", ""))

    def _img_b64(self, path: str) -> str:
        safe = _safe_image_path(path)
        if not safe or not os.path.exists(safe):
            return ""
        try:
            mtime = os.path.getmtime(safe)
            cached = self._img_cache.get(safe)
            if cached and cached[0] == mtime:
                return cached[1]
            with open(safe, "rb") as f:
                data = f.read()
            if len(data) > 5 * 1024 * 1024:
                return ""
            ext = os.path.splitext(safe)[1].lower().replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            result = f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
            self._img_cache[safe] = (mtime, result)
            return result
        except:
            return ""


class RunTimer:
    def __init__(self):
        self._running = False
        self._start   = 0.0
        self._elapsed = 0.0

    def start(self):
        if not self._running:
            self._start   = time.time() - self._elapsed
            self._running = True

    def stop(self):
        if self._running:
            self._elapsed = time.time() - self._start
            self._running = False

    def reset(self):
        self._running = False
        self._elapsed = 0.0

    def toggle(self):
        self.stop() if self._running else self.start()

    @property
    def running(self): return self._running

    @property
    def elapsed(self):
        return time.time() - self._start if self._running else self._elapsed

    def format(self, secs=None):
        e = secs if secs is not None else self.elapsed
        h  = int(e // 3600)
        m  = int((e % 3600) // 60)
        s  = int(e % 60)
        cs = int((e % 1) * 100)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
        return f"{m:02d}:{s:02d}.{cs:02d}"


def build_overlay_data(dm: DataManager, timer: RunTimer) -> dict:
    s       = dm.settings["overlay"]
    tmpl    = dm.active_template or {"name": "—", "game": "—", "bosses": []}
    bosses  = tmpl.get("bosses", [])
    cur_idx = dm.state.get("current_boss_index", 0)
    pb_time = dm.state.get("pb_time")

    boss_list = []
    total_hits = total_blocks = total_path = total_pb = 0
    for i, boss in enumerate(bosses):
        hits   = boss.get("hits",      0)
        blocks = boss.get("blocks",    0)
        path   = boss.get("path_hits", 0)
        pb_h   = boss.get("pb_hits",   0)
        total_hits   += hits
        total_blocks += blocks
        total_path   += path
        total_pb     += pb_h
        if i == cur_idx:
            state = "current"
        elif i < cur_idx:
            state = "done_clean" if (hits + blocks + path) == 0 else "done_hit"
        else:
            state = "future"
        boss_list.append({
            "name": boss.get("name", "?"),
            "hits": hits, "blocks": blocks, "path": path, "pb": pb_h,
            "state": state, "alt": i % 2 == 1,
        })

    total_current = total_hits + total_blocks + total_path

    return {
        "timer":        timer.format(),
        "timer_running": timer.running,
        "pb_time":      timer.format(pb_time) if pb_time else None,
        "bosses":       boss_list,
        "totals":       {
            "hits":    total_hits,
            "blocks":  total_blocks,
            "path":    total_path,
            "pb":      total_pb,
            "current": total_current,
        },
        "settings": {
            "show_timer":     s.get("show_timer",     True),
            "show_pb":        s.get("show_pb",        True),
            "show_blocks":    s.get("show_blocks",    True),
            "show_path_hits": s.get("show_path_hits", True),
        }
    }


def build_overlay_html(dm: DataManager, timer: RunTimer) -> str:
    s    = dm.settings["overlay"]
    tmpl = dm.active_template or {"name": "—", "game": "—", "bosses": []}

    def hex_rgb(hex_color):
        h = hex_color.lstrip("#")
        if len(h) == 3: h = "".join(c*2 for c in h)
        return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

    header_color = _safe_color(s.get("header_color"),  "#cc0000")
    body_color   = _safe_color(s.get("body_bg"),        "#1a1a1a")
    alt_color    = _safe_color(s.get("row_alt_color"),  "#222222")
    hr,  hg,  hb  = hex_rgb(header_color)
    br2, bg2, bb2 = hex_rgb(body_color)
    ra_r,ra_g,ra_b= hex_rgb(alt_color)
    header_alpha  = _safe_alpha(s.get("header_alpha"), 1.0)
    body_alpha    = _safe_alpha(s.get("body_alpha"),   1.0)
    bg_alpha      = _safe_alpha(s.get("bg_image_alpha"), 0.4)

    font_h = _safe_font(s.get("font_header", "Segoe UI"), "Segoe UI")
    font_t = _safe_font(s.get("font_table",  "Segoe UI"), "Segoe UI")
    sz_title    = _safe_int(s.get("size_title",    18), 18, 8, 72)
    sz_subtitle = _safe_int(s.get("size_subtitle", 12), 12, 6, 48)
    sz_timer    = _safe_int(s.get("size_timer",    22), 22, 10, 72)
    sz_table    = _safe_int(s.get("size_table",    14), 14, 6, 48)
    sz_total    = _safe_int(s.get("size_total",    13), 13, 6, 36)
    width       = _safe_int(s.get("width",        600), 600, 200, 1920)

    header_text_color = _safe_color(s.get("header_text_color"), "#ffffff")
    body_text_color   = _safe_color(s.get("body_text_color"),   "#ffffff")
    accent_color      = _safe_color(s.get("accent_color"),      "#00ff88")
    pb_color          = _safe_color(s.get("pb_color"),          "#ffd700")

    logo_b64  = dm.get_logo_b64()
    bg_b64    = dm.get_bg_b64()
    frame_b64 = dm.get_frame_b64()

    logo_html  = f'<img src="{logo_b64}" class="logo" alt="logo">' if logo_b64 else ""

    bg_style = ""
    if bg_b64:
        bg_style = f"""
  body::before {{
    content: '';
    position: fixed; inset: 0;
    background: url('{bg_b64}') center/cover no-repeat;
    opacity: {bg_alpha:.2f};
    z-index: 0;
    pointer-events: none;
  }}
  .header, .timer-row-wrap, table, #tfoot {{ position: relative; z-index: 1; }}"""

    frame_html = ""
    if frame_b64:
        frame_html = f'<img src="{frame_b64}" class="frame-overlay" alt="">'

    show_blocks    = bool(s.get("show_blocks",    True))
    show_path_hits = bool(s.get("show_path_hits", True))
    block_th = "<th>Block</th>" if show_blocks    else ""
    path_th  = "<th>Path</th>"  if show_path_hits else ""

    gf_families = set()
    for f in [font_h, font_t]:
        name = f.replace(" ", "+")
        gf_families.add(f"family={name}:wght@400;500;700")
    gf_import = f"@import url('https://fonts.googleapis.com/css2?{'&'.join(gf_families)}&display=swap');"

    title_escaped = _esc(s.get("title", "No Hit Run"))
    game_escaped  = _esc(tmpl.get("game", ""))

    css_vars = f"""
    --header-bg:    rgba({hr},{hg},{hb},{header_alpha:.2f});
    --body-bg:      rgba({br2},{bg2},{bb2},{body_alpha:.2f});
    --header-text:  {header_text_color};
    --body-text:    {body_text_color};
    --accent:       {accent_color};
    --pb-color:     {pb_color};
    --hit-color:    #ff4444;
    --border:       rgba(255,255,255,0.12);
    --row-alt-bg:   rgba({ra_r},{ra_g},{ra_b},{body_alpha:.2f});
    --row-cur-bg:   rgba(255,255,255,0.09);
    --font-header:  '{font_h}', 'Rajdhani', sans-serif;
    --font-table:   '{font_t}', 'Rajdhani', sans-serif;
    --sz-title:     {sz_title}px;
    --sz-subtitle:  {sz_subtitle}px;
    --sz-timer:     {sz_timer}px;
    --sz-table:     {sz_table}px;
    --sz-total:     {sz_total}px;
    """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  {gf_import}
  :root {{ {css_vars} }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: transparent;
    font-family: var(--font-table);
    width: {width}px;
    overflow: visible;
    position: relative;
    display: inline-block;
  }}
  {bg_style}

  .frame-overlay {{
    position: fixed; inset: 0;
    width: 100%; height: 100%;
    object-fit: fill;
    pointer-events: none;
    z-index: 100;
  }}

  .header {{
    background: var(--header-bg);
    font-family: var(--font-header);
    display: flex; align-items: center;
    padding: 6px 10px; gap: 10px; min-height: 54px;
    border-bottom: 2px solid var(--accent);
    position: relative; z-index: 1;
  }}
  .logo {{ height: 42px; width: auto; object-fit: contain; border-radius: 3px; }}
  .header-texts {{ display: flex; flex-direction: column; }}
  .header-title {{
    color: var(--header-text);
    font-size: var(--sz-title); font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  }}
  .header-game {{
    color: var(--header-text); opacity: 0.75;
    font-size: var(--sz-subtitle); letter-spacing: 2px; text-transform: uppercase;
  }}

  .timer-row {{
    background: var(--body-bg);
    border-bottom: 1px solid var(--border);
    padding: 4px 10px; display: flex; align-items: center; gap: 12px;
    position: relative; z-index: 1;
    font-family: var(--font-header);
  }}
  .timer {{
    color: var(--accent);
    font-size: var(--sz-timer); font-weight: 700;
    font-variant-numeric: tabular-nums; letter-spacing: 2px;
  }}
  .pb-tag {{
    color: var(--pb-color);
    font-size: calc(var(--sz-timer) * 0.6); font-weight: 600; letter-spacing: 1px;
    background: rgba(255,215,0,0.12);
    padding: 2px 8px; border-radius: 3px;
    border: 1px solid rgba(255,215,0,0.4);
  }}

  table {{
    width: 100%; border-collapse: collapse;
    background: var(--body-bg);
    font-family: var(--font-table);
    position: relative; z-index: 1;
  }}
  thead tr {{ background: rgba(0,0,0,0.3); border-bottom: 2px solid var(--accent); }}
  th {{
    color: var(--accent);
    font-size: calc(var(--sz-table) * 0.8); text-transform: uppercase;
    letter-spacing: 1.5px; padding: 5px 8px; text-align: center; font-weight: 600;
  }}
  th:first-child {{ text-align: left; }}
  td {{
    color: var(--body-text);
    font-size: var(--sz-table); padding: 5px 8px;
    border-bottom: 1px solid var(--border);
  }}
  .num {{ text-align: center; font-variant-numeric: tabular-nums; }}
  .hit-num {{ color: var(--hit-color); font-weight: 700; }}
  .pb-num  {{ color: var(--pb-color); }}

  .row-current {{ background: var(--row-cur-bg) !important; }}
  .row-current td {{ color: #ffffff; font-weight: 600; }}
  .row-current .hit-num {{ color: #ff2222; font-size: calc(var(--sz-table) * 1.15); }}
  .row-done-clean td {{ color: #44cc66; }}
  .row-done-clean .boss-name::before {{ content: "✓ "; }}
  .row-done-hit td {{ color: #ff7777; }}
  .row-done-hit .boss-name::before {{ content: "✗ "; }}
  .row-future td {{ color: var(--body-text); opacity: 0.35; }}
  .row-alt {{ background: var(--row-alt-bg); }}
  .boss-name {{ font-weight: 500; max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}

  .total-row td {{
    border-top: 2px solid var(--accent);
    font-weight: 700; font-size: var(--sz-total);
    color: var(--accent);
    background: rgba(0,0,0,0.35); padding: 6px 8px;
  }}
  .total-row .hit-num {{ color: var(--hit-color); }}
  .diff-row td {{
    background: rgba(0,0,0,0.25); padding: 4px 8px;
    font-size: var(--sz-total); font-weight: 700;
    border-top: 1px solid rgba(255,255,255,0.06);
  }}
  .diff-worse   {{ color: #ff4444; }}
  .diff-better  {{ color: #44cc66; }}
  .diff-equal   {{ color: #aaaaaa; }}
  .diff-neutral {{ color: #666666; }}
</style>
</head>
<body>
{frame_html}
<div class="header">
  {logo_html}
  <div class="header-texts">
    <span class="header-title">{title_escaped}</span>
    <span class="header-game">{game_escaped}</span>
  </div>
</div>
<div id="timer-row"></div>
<table>
  <thead><tr><th>Boss</th><th>Hits</th>{block_th}{path_th}<th>PB(Now)</th></tr></thead>
  <tbody id="tbody"></tbody>
  <tfoot id="tfoot"></tfoot>
</table>

<script>
const SHOW_BLOCKS    = {'true' if show_blocks    else 'false'};
const SHOW_PATH_HITS = {'true' if show_path_hits else 'false'};

function esc(s) {{
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function formatRow(b) {{
  const blockTd = SHOW_BLOCKS    ? `<td class="num">${{b.blocks}}</td>` : '';
  const pathTd  = SHOW_PATH_HITS ? `<td class="num">${{b.path}}</td>`   : '';
  const marker  = b.state === 'current' ? '▶ ' : '';
  const alt     = b.alt ? ' row-alt' : '';
  const rowClass = 'row-' + b.state.replace(/_/g, '-');
  return `<tr class="${{rowClass}}${{alt}}">
    <td class="boss-name">${{marker}}${{esc(b.name)}}</td>
    <td class="num hit-num">${{b.hits}}</td>
    ${{blockTd}}${{pathTd}}
    <td class="num pb-num">${{b.pb}}(${{b.hits}})</td>
  </tr>`;
}}

async function poll() {{
  try {{
    const r = await fetch('/data');
    const d = await r.json();

    const timerDiv = document.getElementById('timer-row');
    if (d.settings.show_timer) {{
      const pbStr = (d.pb_time && d.settings.show_pb)
        ? `<span class="pb-tag">PB ${{d.pb_time}}</span>` : '';
      timerDiv.className = 'timer-row';
      timerDiv.innerHTML = `<span class="timer">${{d.timer}}</span>${{pbStr}}`;
    }} else {{
      timerDiv.innerHTML = '';
    }}

    document.getElementById('tbody').innerHTML = d.bosses.map(formatRow).join('');

    const blockTotal = SHOW_BLOCKS    ? `<td class="num">${{d.totals.blocks}}</td>` : '';
    const pathTotal  = SHOW_PATH_HITS ? `<td class="num">${{d.totals.path}}</td>`   : '';
    const diff = d.totals.current - d.totals.pb;
    let diffStr = '—';
    let diffClass = 'diff-neutral';
    if (d.totals.pb > 0) {{
      if (diff > 0)      {{ diffStr = `+${{diff}}`; diffClass = 'diff-worse'; }}
      else if (diff < 0) {{ diffStr = `${{diff}}`;  diffClass = 'diff-better'; }}
      else               {{ diffStr = '=';           diffClass = 'diff-equal'; }}
    }}
    document.getElementById('tfoot').innerHTML = `
      <tr class="total-row">
        <td>Total</td>
        <td class="num hit-num">${{d.totals.hits}}</td>
        ${{blockTotal}}${{pathTotal}}
        <td class="num pb-num">${{d.totals.pb}}</td>
      </tr>
      <tr class="diff-row">
        <td>vs PB</td>
        <td colspan="${{2 + (SHOW_BLOCKS?1:0) + (SHOW_PATH_HITS?1:0)}}" class="num ${{diffClass}}">${{diffStr}}</td>
        <td></td>
      </tr>`;
  }} catch(e) {{}}
  setTimeout(poll, 200);
}}

poll();
</script>
</body>
</html>"""


_dm_ref    = None
_timer_ref = None

class OverlayHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        req_path = urlparse(self.path).path
        if req_path == "/overlay":
            body = build_overlay_html(_dm_ref, _timer_ref).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        elif req_path == "/data":
            body = json.dumps(build_overlay_data(_dm_ref, _timer_ref), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "http://localhost")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

def start_server(dm, timer):
    global _dm_ref, _timer_ref
    _dm_ref = dm; _timer_ref = timer
    srv = HTTPServer(("127.0.0.1", OVERLAY_PORT), OverlayHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class HotkeyManager:
    def __init__(self, dm: DataManager, timer: RunTimer, refresh_cb, root=None):
        self.dm             = dm
        self.timer          = timer
        self._raw_cb        = refresh_cb
        self._root          = root
        self._lock          = threading.Lock()
        self._hooks         = []
        self._scan_map      = {}
        self._stop_watchdog = threading.Event()

    def refresh_cb(self):
        if self._root:
            self._root.after_idle(self._raw_cb)
        else:
            self._raw_cb()

    def _build_key_map(self):
        hk = self.dm.settings["hotkeys"]
        mapping = {}
        binds = [
            ("boss_hit",      hk.get("boss_hit",      ""), self._boss_hit),
            ("block",         hk.get("block",         ""), self._block),
            ("path_hit",      hk.get("path_hit",      ""), self._path_hit),
            ("start_timer",   hk.get("start_timer",   ""), self._start_timer),
            ("stop_timer",    hk.get("stop_timer",    ""), self._stop_timer),
            ("reset_current", hk.get("reset_current", ""), self._reset_current),
            ("save_pb",       hk.get("save_pb",       ""), self._save_pb),
            ("next_boss",     hk.get("next_boss",     ""), self._next_boss),
            ("prev_boss",     hk.get("prev_boss",     ""), self._prev_boss),
            ("reset_run",     hk.get("reset_run",     ""), self._reset_run),
        ]
        for action, key, fn in binds:
            if not key:
                continue
            k = key.strip().lower()
            if k in mapping:
                continue
            mapping[k] = fn
        return mapping

    def register_all(self):
        self.unregister_all()
        self._do_register()
        self._stop_watchdog.clear()
        t = threading.Thread(target=self._watchdog_loop, daemon=True)
        t.start()

    def _do_register(self):
        try:
            import keyboard
            key_map = self._build_key_map()
            new_scan_map = {}
            for key_str, fn in key_map.items():
                try:
                    sc = keyboard.key_to_scan_codes(key_str)
                    if sc:
                        new_scan_map[sc[0]] = (key_str, fn)
                except:
                    pass

            def _dispatch(event):
                with self._lock:
                    entry = self._scan_map.get(event.scan_code)
                if entry:
                    key_str, fn = entry
                    try:
                        expected = keyboard.key_to_scan_codes(key_str)
                        if event.scan_code in expected:
                            fn()
                    except:
                        fn()

            h = keyboard.on_press(_dispatch, suppress=False)
            with self._lock:
                self._scan_map = new_scan_map
                self._hooks.append(h)
        except:
            pass

    def _watchdog_loop(self):
        import keyboard
        while not self._stop_watchdog.wait(60):
            try:
                with self._lock:
                    hooks_copy = list(self._hooks)
                    self._hooks.clear()
                    self._scan_map = {}
                for h in hooks_copy:
                    try:
                        keyboard.unhook(h)
                    except:
                        pass
                self._do_register()
            except:
                pass

    def unregister_all(self):
        self._stop_watchdog.set()
        try:
            import keyboard
            with self._lock:
                hooks_copy = list(self._hooks)
                self._hooks.clear()
                self._scan_map = {}
            for h in hooks_copy:
                try:
                    keyboard.unhook(h)
                except:
                    pass
        except:
            pass

    def _get_boss(self):
        tmpl = self.dm.active_template
        if not tmpl: return None, -1
        idx = self.dm.state.get("current_boss_index", 0)
        bosses = tmpl.get("bosses", [])
        if 0 <= idx < len(bosses):
            boss = bosses[idx]
            boss.setdefault("hits", 0)
            boss.setdefault("blocks", 0)
            boss.setdefault("path_hits", 0)
            boss.setdefault("pb_hits", 0)
            return bosses, idx
        return None, -1

    def _boss_hit(self):
        bosses, idx = self._get_boss()
        if bosses:
            bosses[idx]["hits"] = bosses[idx].get("hits", 0) + 1
            self.refresh_cb()

    def _block(self):
        bosses, idx = self._get_boss()
        if bosses:
            bosses[idx]["blocks"] = bosses[idx].get("blocks", 0) + 1
            self.refresh_cb()

    def _path_hit(self):
        bosses, idx = self._get_boss()
        if bosses:
            bosses[idx]["path_hits"] = bosses[idx].get("path_hits", 0) + 1
            self.refresh_cb()

    def _start_timer(self):
        self.timer.start()
        self.refresh_cb()

    def _stop_timer(self):
        self.timer.stop()
        self.refresh_cb()

    def _reset_current(self):
        bosses, idx = self._get_boss()
        if bosses:
            bosses[idx].update({"hits": 0, "blocks": 0, "path_hits": 0})
            self.refresh_cb()

    def _reset_run(self):
        self.dm.reset_run()
        self.timer.reset()
        self.refresh_cb()

    def _save_pb(self):
        self.timer.stop()
        self.dm.state["pb_time"] = self.timer.elapsed
        tmpl = self.dm.active_template
        tid  = self.dm.state.get("active_template")
        if tmpl and tid:
            for boss in tmpl["bosses"]:
                boss["pb_hits"] = (boss.get("hits", 0) +
                                   boss.get("blocks", 0) +
                                   boss.get("path_hits", 0))
            saved = self.dm.templates.get(tid, {})
            for i, boss in enumerate(saved.get("bosses", [])):
                if i < len(tmpl["bosses"]):
                    boss["pb_hits"] = tmpl["bosses"][i].get("pb_hits", 0)
            self.dm.save_template(tid, saved)
        self.dm.save_state()
        self.refresh_cb()

    def _next_boss(self):
        tmpl = self.dm.active_template
        if not tmpl: return
        idx   = self.dm.state.get("current_boss_index", 0)
        count = len(tmpl.get("bosses", []))
        if idx < count - 1:
            self.dm.state["current_boss_index"] = idx + 1
            self.refresh_cb()

    def _prev_boss(self):
        idx = self.dm.state.get("current_boss_index", 0)
        if idx > 0:
            self.dm.state["current_boss_index"] = idx - 1
            self.refresh_cb()


class NoHitApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Git Gud Counter")
        self.root.geometry("920x660")
        self.root.configure(bg="#12121f")
        self.root.resizable(True, True)

        self.dm    = DataManager()
        self.timer = RunTimer()
        saved_elapsed = self.dm.state.get("timer_elapsed", 0.0)
        if saved_elapsed and saved_elapsed > 0:
            self.timer._elapsed = float(saved_elapsed)
        self.server = start_server(self.dm, self.timer)
        self.hkm   = HotkeyManager(self.dm, self.timer, self._refresh_live, self.root)
        self.hkm.register_all()

        self._style()
        self._build_ui()
        self._refresh_live()
        self._tick()

    def _style(self):
        s = ttk.Style()
        s.theme_use("clam")
        # Base
        s.configure(".", background="#12121f", foreground="#c4b5fd",
                    fieldbackground="#1a1a2e", bordercolor="#2a2a45",
                    lightcolor="#2a2a45", darkcolor="#0d0d18",
                    troughcolor="#1a1a2e", selectbackground="#4c3d8a",
                    selectforeground="#e0e0ff")
        # Notebook
        s.configure("TNotebook", background="#0d0d18", tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab", background="#0d0d18", foreground="#3a3a6a",
                    padding=[14,6], font=("Segoe UI",9))
        s.map("TNotebook.Tab",
              background=[("selected","#12121f")],
              foreground=[("selected","#a78bfa")])
        # Buttons
        s.configure("TButton", background="#1e1535", foreground="#a78bfa",
                    relief="flat", padding=[10,5], font=("Segoe UI",9,"bold"),
                    bordercolor="#4c3d8a")
        s.map("TButton", background=[("active","#2a1f50")])
        s.configure("Green.TButton", background="#1e1535", foreground="#a78bfa",
                    bordercolor="#4c3d8a")
        s.map("Green.TButton", background=[("active","#2a1f50")])
        s.configure("Gray.TButton", background="#1a1a2e", foreground="#6060a0",
                    bordercolor="#2a2a45")
        s.map("Gray.TButton", background=[("active","#22223a")])
        s.configure("Accent.TButton", background="#4c3d8a", foreground="#e0e0ff",
                    bordercolor="#6d5fc7")
        s.map("Accent.TButton", background=[("active","#5a4a9a")])
        # Entry
        s.configure("TEntry", fieldbackground="#1a1a2e", foreground="#e0e0ff",
                    insertcolor="#a78bfa", bordercolor="#2a2a45", relief="flat", padding=4)
        # Labels
        s.configure("TLabel", background="#12121f", foreground="#6060a0",
                    font=("Segoe UI",9))
        # Combobox
        s.configure("TCombobox", fieldbackground="#1a1a2e", foreground="#e0e0ff",
                    selectbackground="#4c3d8a", background="#1a1a2e",
                    arrowcolor="#6060a0")
        # Scrollbar
        s.configure("TScrollbar", background="#1a1a2e", troughcolor="#0d0d18",
                    arrowcolor="#3a3a6a", bordercolor="#0d0d18")
        s.configure("Treeview", background="#0d0d18", foreground="#8080c0",
                    fieldbackground="#0d0d18", rowheight=28, font=("Segoe UI",9))
        s.configure("Treeview.Heading", background="#12121f", foreground="#4c3d8a",
                    font=("Segoe UI",8,"bold"), relief="flat")
        s.map("Treeview", background=[("selected","#1e1535")],
              foreground=[("selected","#c4b5fd")])
        # LabelFrame
        s.configure("TLabelframe", background="#12121f", foreground="#3a3a6a",
                    bordercolor="#2a2a45", relief="solid")
        s.configure("TLabelframe.Label", background="#12121f", foreground="#4c3d8a",
                    font=("Segoe UI",9))
        # Checkbutton
        s.configure("TCheckbutton", background="#12121f", foreground="#8080c0")
        # Scale
        s.configure("TScale", background="#12121f", troughcolor="#1a1a2e")

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#0d0d18", height=50)
        top.pack(fill="x"); top.pack_propagate(False)

        tk.Label(top, text="⚔ GIT GUD COUNTER", bg="#0d0d18", fg="#a78bfa",
                 font=("Segoe UI",14,"bold")).pack(side="left", padx=16, pady=8)

        url_f = tk.Frame(top, bg="#0d0d18"); url_f.pack(side="left", padx=20, pady=8)
        tk.Label(url_f, text="OBS URL:", bg="#0d0d18", fg="#3a3a6a",
                 font=("Segoe UI",9)).pack(side="left")
        url_var = tk.StringVar(value=f"http://localhost:{OVERLAY_PORT}/overlay")
        tk.Entry(url_f, textvariable=url_var, bg="#1a1a2e", fg="#a78bfa",
                 font=("Courier",9), relief="flat", width=34,
                 state="readonly", readonlybackground="#1a1a2e").pack(side="left", padx=4)
        ttk.Button(url_f, text="Copiar", style="Gray.TButton",
                   command=lambda: self._copy_url(url_var.get())).pack(side="left")

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=6, pady=4)

        self.tab_run       = tk.Frame(self.nb, bg="#12121f")
        self.tab_templates = tk.Frame(self.nb, bg="#12121f")
        self.tab_hotkeys   = tk.Frame(self.nb, bg="#12121f")
        self.tab_overlay   = tk.Frame(self.nb, bg="#12121f")

        self.nb.add(self.tab_run,       text="  Run Activo  ")
        self.nb.add(self.tab_templates, text="  Templates  ")
        self.nb.add(self.tab_hotkeys,   text="  Hotkeys  ")
        self.nb.add(self.tab_overlay,   text="  Overlay  ")

        self._build_run_tab()
        self._build_templates_tab()
        self._build_hotkeys_tab()
        self._build_overlay_tab()

    def _build_run_tab(self):
        tab = self.tab_run

        top = tk.Frame(tab, bg="#12121f"); top.pack(fill="x", padx=10, pady=8)

        left = tk.Frame(top, bg="#12121f"); left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Template activo:", bg="#12121f", fg="#8080c0",
                 font=("Segoe UI",9)).pack(side="left")
        self.tmpl_var   = tk.StringVar()
        self.tmpl_combo = ttk.Combobox(left, textvariable=self.tmpl_var, width=22, state="readonly")
        self.tmpl_combo.pack(side="left", padx=6)
        ttk.Button(left, text="▶ Iniciar Run", style="Green.TButton",
                   command=self._start_run).pack(side="left", padx=6)
        ttk.Button(left, text="⏹ Reset Run", style="Gray.TButton",
                   command=self._reset_run_btn).pack(side="left", padx=2)

        right = tk.Frame(top, bg="#0d0d18"); right.pack(side="right", padx=4)
        self.timer_lbl = tk.Label(right, text="00:00.00", bg="#0d0d18", fg="#a78bfa",
                                   font=("Courier",22,"bold"))
        self.timer_lbl.pack(padx=16, pady=4)
        tbf = tk.Frame(right, bg="#0d0d18"); tbf.pack(pady=(0,4))
        ttk.Button(tbf, text="▶ Iniciar", style="Green.TButton",
                   command=self.hkm._start_timer).pack(side="left", padx=2)
        ttk.Button(tbf, text="⏸ Detener", style="Gray.TButton",
                   command=self.hkm._stop_timer).pack(side="left", padx=2)
        ttk.Button(tbf, text="↺ Reset",  style="Gray.TButton",
                   command=self._reset_timer).pack(side="left", padx=2)
        ttk.Button(tbf, text="★ PB",  style="Green.TButton",
                   command=self._save_pb).pack(side="left", padx=2)
        self.pb_lbl = tk.Label(right, text="", bg="#0d0d18", fg="#f59e0b", font=("Segoe UI",9))
        self.pb_lbl.pack(pady=(0,4))

        tf = tk.Frame(tab, bg="#12121f"); tf.pack(fill="both", expand=True, padx=10, pady=4)
        cols = ("boss","hits","blocks","path","pb")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for col, label, w in [("boss","Boss",200),("hits","Hits",70),
                               ("blocks","Blocks",70),("path","Path Hits",80),("pb","PB (Actual)",100)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=w, anchor="center" if col != "boss" else "w")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("current",    background="#1e1535", foreground="#c4b5fd")
        self.tree.tag_configure("done_clean", background="#0d1a18", foreground="#34d399")
        self.tree.tag_configure("done_hit",   background="#1a0d1a", foreground="#f87171")
        self.tree.tag_configure("future",     foreground="#2a2a4a")

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)

        bot = tk.Frame(tab, bg="#12121f"); bot.pack(fill="x", padx=10, pady=6)
        self.cur_boss_lbl = tk.Label(bot, text="Boss actual: —", bg="#12121f",
                                      fg="#a78bfa", font=("Segoe UI",10,"bold"))
        self.cur_boss_lbl.pack(side="left")
        bf = tk.Frame(bot, bg="#12121f"); bf.pack(side="right")
        ttk.Button(bf, text="◀ Anterior", style="Gray.TButton",
                   command=self.hkm._prev_boss).pack(side="left", padx=2)
        ttk.Button(bf, text="Siguiente ▶", style="Green.TButton",
                   command=self.hkm._next_boss).pack(side="left", padx=2)

        hf = tk.Frame(tab, bg="#0d0d18"); hf.pack(fill="x", padx=10, pady=(0,8))
        tk.Label(hf, text="Manual:", bg="#0d0d18", fg="#3a3a6a", font=("Segoe UI",9)).pack(side="left", padx=8)
        for label, cmd, style in [
            ("+ Hit Boss",    self.hkm._boss_hit,      "TButton"),
            ("+ Block",       self.hkm._block,         "Gray.TButton"),
            ("+ Path Hit",    self.hkm._path_hit,      "Gray.TButton"),
            ("- Undo Hit",    self._undo_hit,           "Gray.TButton"),
            ("- Undo Block",  self._undo_block,         "Gray.TButton"),
            ("- Undo Path",   self._undo_path,          "Gray.TButton"),
            ("Reset Boss",    self.hkm._reset_current, "Gray.TButton"),
        ]:
            ttk.Button(hf, text=label, style=style, command=cmd).pack(side="left", padx=3, pady=4)

        self._refresh_template_combo()

    def _on_tree_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        all_items = self.tree.get_children()
        try:
            idx = all_items.index(sel[0])
        except ValueError:
            return
        tmpl = self.dm.active_template
        if tmpl and 0 <= idx < len(tmpl.get("bosses", [])):
            self.dm.state["current_boss_index"] = idx
            self._refresh_live()

    def _build_templates_tab(self):
        tab = self.tab_templates
        paned = tk.PanedWindow(tab, orient="horizontal", bg="#12121f",
                               sashrelief="flat", sashwidth=4)
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(paned, bg="#12121f", width=180); paned.add(left, minsize=160)
        tk.Label(left, text="TEMPLATES", bg="#12121f", fg="#a78bfa",
                 font=("Segoe UI",10,"bold")).pack(pady=6)
        self.tmpl_listbox = tk.Listbox(left, bg="#1a1a2e", fg="#c4b5fd", selectbackground="#4c3d8a",
                                        selectforeground="#fff", relief="flat",
                                        font=("Segoe UI",10), activestyle="none",
                                        highlightthickness=0)
        self.tmpl_listbox.pack(fill="both", expand=True, padx=4)
        self.tmpl_listbox.bind("<<ListboxSelect>>", self._on_tmpl_list_select)
        br = tk.Frame(left, bg="#12121f"); br.pack(fill="x", padx=4, pady=4)
        ttk.Button(br, text="+ Nuevo",  style="Green.TButton",
                   command=self._new_template).pack(side="left", padx=2)
        ttk.Button(br, text="✕ Borrar", style="Gray.TButton",
                   command=self._delete_template).pack(side="left", padx=2)

        right = tk.Frame(paned, bg="#12121f"); paned.add(right, minsize=300)
        self.tmpl_editor_frame = right
        self._build_template_editor(right)
        self._refresh_tmpl_list()

    def _build_template_editor(self, parent):
        for w in parent.winfo_children(): w.destroy()
        meta = ttk.LabelFrame(parent, text="Información del Template", padding=8)
        meta.pack(fill="x", padx=8, pady=6)
        tk.Label(meta, text="Nombre:", bg="#12121f", fg="#8080c0").grid(row=0, column=0, sticky="w", pady=2)
        self.te_name = ttk.Entry(meta, width=28); self.te_name.grid(row=0, column=1, columnspan=2, sticky="ew", padx=4)
        tk.Label(meta, text="Juego:",  bg="#12121f", fg="#8080c0").grid(row=1, column=0, sticky="w", pady=2)
        self.te_game = ttk.Entry(meta, width=28); self.te_game.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4)
        tk.Label(meta, text="Logo (game_key):", bg="#12121f", fg="#8080c0").grid(row=2, column=0, sticky="w", pady=2)
        self.te_game_key = ttk.Combobox(meta, width=16, state="readonly",
                                         values=[""] + list(GAME_ASSETS.keys()))
        self.te_game_key.grid(row=2, column=1, sticky="w", padx=4)
        tk.Label(meta, text="(enlaza el logo automático)", bg="#12121f", fg="#3a3a6a",
                 font=("Segoe UI",8,"italic")).grid(row=2, column=2, sticky="w")
        meta.columnconfigure(1, weight=1)

        bf = ttk.LabelFrame(parent, text="Bosses (orden del run)", padding=8)
        bf.pack(fill="both", expand=True, padx=8, pady=4)
        bft = tk.Frame(bf, bg="#12121f"); bft.pack(fill="x", pady=(0,4))
        self.boss_entry = ttk.Entry(bft, width=22); self.boss_entry.pack(side="left")
        self.boss_entry.bind("<Return>", lambda e: self._add_boss_to_template())
        for label, cmd, style in [
            ("+ Agregar",  self._add_boss_to_template, "Green.TButton"),
            ("↑ Subir",    lambda: self._move_boss(-1), "Gray.TButton"),
            ("↓ Bajar",    lambda: self._move_boss(1),  "Gray.TButton"),
            ("✕ Quitar",   self._remove_boss,           "Gray.TButton"),
        ]:
            ttk.Button(bft, text=label, style=style, command=cmd).pack(side="left", padx=2)
        self.boss_listbox = tk.Listbox(bf, bg="#1a1a2e", fg="#c4b5fd", selectbackground="#4c3d8a",
                                        selectforeground="#fff", relief="flat",
                                        font=("Segoe UI",10), activestyle="none",
                                        highlightthickness=0)
        self.boss_listbox.pack(fill="both", expand=True)
        self.boss_listbox.bind("<Double-Button-1>", self._rename_boss)
        ttk.Button(parent, text="💾 Guardar Template", style="Green.TButton",
                   command=self._save_current_template).pack(pady=8)
        self._current_edit_template = None


    # Tabla de traducción keysym de Tk → nombre para la lib keyboard
    TK_TO_KB = {
        "slash": "/", "backslash": "\\", "minus": "-", "equal": "=",
        "bracketleft": "[", "bracketright": "]", "semicolon": ";",
        "apostrophe": "'", "grave": "`", "comma": ",", "period": ".",
        "space": "space", "Return": "enter", "BackSpace": "backspace",
        "Delete": "delete", "Escape": "escape", "Tab": "tab",
        "Up": "up", "Down": "down", "Left": "left", "Right": "right",
        "Prior": "page up", "Next": "page down",
        "Home": "home", "End": "end", "Insert": "insert",
        "KP_0":"num 0","KP_1":"num 1","KP_2":"num 2","KP_3":"num 3",
        "KP_4":"num 4","KP_5":"num 5","KP_6":"num 6","KP_7":"num 7",
        "KP_8":"num 8","KP_9":"num 9","KP_Add":"num +","KP_Subtract":"num -",
        "KP_Multiply":"num *","KP_Divide":"num /","KP_Decimal":"num .",
        "KP_Enter":"num enter","KP_Home":"num 7","KP_Up":"num 8",
        "KP_Prior":"num 9","KP_Left":"num 4","KP_Begin":"num 5",
        "KP_Right":"num 6","KP_End":"num 1","KP_Down":"num 2",
        "KP_Next":"num 3","KP_Insert":"num 0","KP_Delete":"num .",
        "F1":"f1","F2":"f2","F3":"f3","F4":"f4","F5":"f5",
        "F6":"f6","F7":"f7","F8":"f8","F9":"f9","F10":"f10",
        "F11":"f11","F12":"f12",
        "Control_L":"ctrl","Control_R":"ctrl",
        "Alt_L":"alt","Alt_R":"alt",
        "Shift_L":"shift","Shift_R":"shift",
    }

    def _build_hotkeys_tab(self):
        tab = self.tab_hotkeys
        frame = ttk.LabelFrame(tab, text="Hotkeys Globales", padding=16)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(frame, text="Hacé click en un campo y presioná la tecla deseada.",
                 bg="#12121f", fg="#3a3a6a", font=("Segoe UI",9,"italic")).pack(pady=(0,12))

        self.hk_vars    = {}
        self._hk_active = None
        self._hk_active_data = (None, None, None)

        actions = [
            ("boss_hit",      "Hit en Boss"),
            ("block",         "Block"),
            ("path_hit",      "Hit en el camino"),
            ("start_timer",   "Iniciar Timer"),
            ("stop_timer",    "Detener Timer"),
            ("reset_current", "Reset Boss Actual"),
            ("reset_run",     "Reset Run Completo"),
            ("save_pb",       "Guardar PB"),
            ("next_boss",     "Siguiente Boss"),
            ("prev_boss",     "Boss Anterior"),
        ]
        grid = tk.Frame(frame, bg="#12121f"); grid.pack(fill="both")

        COLOR_IDLE    = "#1a1a2e"
        COLOR_ACTIVE  = "#2a1f50"
        FG_IDLE       = "#a78bfa"
        FG_ACTIVE     = "#e0e0ff"

        def deactivate(entry, var, key):
            """Salir del modo captura sin cambiar el valor."""
            entry.configure(bg=COLOR_IDLE, fg=FG_IDLE)
            # Restaurar valor guardado (por si se puso "..." )
            var.set(self.dm.settings["hotkeys"].get(key, ""))
            self._hk_active = None

        def make_field(parent, row, action_key):
            saved = self.dm.settings["hotkeys"].get(action_key, "")
            var = tk.StringVar(value=saved)
            self.hk_vars[action_key] = var

            entry = tk.Entry(
                parent, textvariable=var, width=16,
                justify="center", state="readonly",
                readonlybackground=COLOR_IDLE, fg=FG_IDLE,
                font=("Courier", 10, "bold"),
                relief="flat", cursor="hand2",
                disabledbackground=COLOR_IDLE,
            )
            entry.grid(row=row, column=1, padx=8, pady=3, ipady=4)

            def on_click(e):
                if self._hk_active and self._hk_active is not entry:
                    prev_entry, prev_var, prev_key = self._hk_active_data
                    deactivate(prev_entry, prev_var, prev_key)

                self._hk_active = entry
                self._hk_active_data = (entry, var, action_key)
                entry.configure(readonlybackground=COLOR_ACTIVE, fg=FG_ACTIVE)
                var.set("...")
                entry.focus_set()

            def on_keypress(e):
                if self._hk_active is not entry:
                    return "break"

                keysym = e.keysym
                if keysym in ("Control_L","Control_R","Alt_L","Alt_R",
                              "Shift_L","Shift_R","Super_L","Super_R",
                              "Caps_Lock","Num_Lock","Scroll_Lock"):
                    return "break"

                base = self.TK_TO_KB.get(keysym, keysym.lower())

                mods = []
                ctrl_held  = bool(e.state & 0x4)  and base != "ctrl"
                shift_held = bool(e.state & 0x1)  and base != "shift"
                alt_held   = bool((e.state & 0x8) or (e.state & 0x20000)) and base != "alt" and ctrl_held

                if ctrl_held:  mods.append("ctrl")
                if alt_held:   mods.append("alt")
                if shift_held: mods.append("shift")
                mods.append(base)
                result = "+".join(mods)

                var.set(result)
                entry.configure(readonlybackground=COLOR_IDLE, fg=FG_IDLE)
                self._hk_active = None
                return "break"

            def on_focus_out(e):
                if self._hk_active is entry:
                    deactivate(entry, var, action_key)

            entry.bind("<Button-1>",  on_click)
            entry.bind("<KeyPress>",  on_keypress)
            entry.bind("<FocusOut>",  on_focus_out)

        for i, (action_key, label) in enumerate(actions):
            tk.Label(grid, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",10), width=24, anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=3)
            make_field(grid, i, action_key)

        ttk.Button(frame, text="💾 Guardar Hotkeys", style="Green.TButton",
                   command=self._save_hotkeys).pack(pady=(16,0))

    def _build_overlay_tab(self):
        tab = self.tab_overlay
        canvas = tk.Canvas(tab, bg="#12121f", highlightthickness=0)
        sb = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg="#12121f")
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _on_wheel(e):
            if self.nb.index(self.nb.select()) == self.nb.index(self.tab_overlay):
                canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_wheel)
        sf.bind("<MouseWheel>", _on_wheel)

        color_btns   = {}
        color_labels = {}

        def add_color_row(parent, row, label, key):
            tk.Label(parent, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",9)).grid(row=row, column=0, sticky="w", pady=3, padx=4)
            val = self.dm.settings["overlay"].get(key, "#888888")
            btn = tk.Button(parent, bg=val, width=4, relief="flat",
                            command=lambda k=key: self._pick_color(k, color_btns[k], color_labels[k]))
            btn.grid(row=row, column=1, padx=8)
            color_btns[key]   = btn
            lbl = tk.Label(parent, text=val, bg="#12121f", fg="#3a3a6a", font=("Courier",9))
            lbl.grid(row=row, column=2, sticky="w")
            color_labels[key] = lbl

        def add_alpha_row(parent, row, label, key):
            tk.Label(parent, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",9)).grid(row=row, column=0, sticky="w", pady=3, padx=4)
            var = tk.DoubleVar(value=self.dm.settings["overlay"].get(key, 1.0))
            scale = ttk.Scale(parent, from_=0.0, to=1.0, orient="horizontal", variable=var, length=150)
            scale.grid(row=row, column=1, columnspan=2, padx=8, sticky="w")
            val_lbl = tk.Label(parent, text=f"{var.get():.2f}", bg="#12121f", fg="#3a3a6a", font=("Courier",9))
            val_lbl.grid(row=row, column=3, sticky="w")
            def on_change(*_):
                self.dm.settings["overlay"][key] = round(var.get(), 2)
                val_lbl.configure(text=f"{var.get():.2f}")
            var.trace_add("write", on_change)

        def add_size_row(parent, row, label, key, lo=8, hi=72):
            tk.Label(parent, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",9)).grid(row=row, column=0, sticky="w", pady=3, padx=4)
            var = tk.IntVar(value=self.dm.settings["overlay"].get(key, 14))
            val_lbl = tk.Label(parent, text=f"{var.get()}px", bg="#12121f", fg="#a78bfa",
                               font=("Courier",9), width=5)
            val_lbl.grid(row=row, column=3, sticky="w")
            scale = ttk.Scale(parent, from_=lo, to=hi, orient="horizontal", variable=var, length=150,
                              command=lambda v, vr=var, vl=val_lbl, k=key: (
                                  vr.set(int(float(v))),
                                  vl.configure(text=f"{int(float(v))}px"),
                                  self.dm.settings["overlay"].__setitem__(k, int(float(v)))
                              ))
            scale.grid(row=row, column=1, columnspan=2, padx=8, sticky="w")

        def get_system_fonts():
            fonts = set()
            try:
                import winreg
                for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                    try:
                        key = winreg.OpenKey(root, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
                        for i in range(winreg.QueryInfoKey(key)[1]):
                            name, _, _ = winreg.EnumValue(key, i)
                            name = name.split(" (")[0].strip()
                            if name.endswith(" Bold"): name = name[:-5].strip()
                            if name.endswith(" Italic"): name = name[:-7].strip()
                            if name.endswith(" Regular"): name = name[:-8].strip()
                            fonts.add(name)
                        winreg.CloseKey(key)
                    except:
                        pass
            except:
                pass
            return sorted(fonts) if fonts else []

        system_fonts = get_system_fonts()

        def add_font_row(parent, row, label, key):
            tk.Label(parent, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",9)).grid(row=row, column=0, sticky="w", pady=3, padx=4)
            var = tk.StringVar(value=self.dm.settings["overlay"].get(key, "Segoe UI"))

            if system_fonts:
                combo = ttk.Combobox(parent, textvariable=var, width=24,
                                     values=system_fonts)
                combo.grid(row=row, column=1, columnspan=2, padx=8, sticky="w")
                note = tk.Label(parent, text="o escribí el nombre de una Google Font",
                                bg="#12121f", fg="#3a3a6a", font=("Segoe UI",7))
                note.grid(row=row, column=3, sticky="w")
            else:
                entry = ttk.Entry(parent, textvariable=var, width=24)
                entry.grid(row=row, column=1, columnspan=2, padx=8, sticky="w")
                note = tk.Label(parent, text="nombre exacto de Google Fonts o sistema",
                                bg="#12121f", fg="#3a3a6a", font=("Segoe UI",7))
                note.grid(row=row, column=3, sticky="w")

            def on_change(*_):
                self.dm.settings["overlay"][key] = var.get().strip()
            var.trace_add("write", on_change)

        def add_image_row(parent, row, label, key, extra_controls=None):
            tk.Label(parent, text=label, bg="#12121f", fg="#8080c0",
                     font=("Segoe UI",9)).grid(row=row, column=0, sticky="w", pady=3, padx=4)
            cur = os.path.basename(self.dm.settings["overlay"].get(key,"")) or "Sin imagen"
            lbl = tk.Label(parent, text=cur, bg="#12121f", fg="#3a3a6a", font=("Segoe UI",8), width=18, anchor="w")
            lbl.grid(row=row, column=1, sticky="w", padx=4)
            def pick():
                path = filedialog.askopenfilename(
                    title=f"Seleccionar {label}",
                    filetypes=[("Imágenes","*.png *.jpg *.jpeg *.gif *.bmp *.webp"),("Todos","*.*")])
                if path:
                    dest = os.path.join(LOGOS_DIR, os.path.basename(path))
                    shutil.copy2(path, dest)
                    self.dm.settings["overlay"][key] = dest
                    lbl.configure(text=os.path.basename(dest))
            def clear():
                self.dm.settings["overlay"][key] = ""
                lbl.configure(text="Sin imagen")
            ttk.Button(parent, text="Explorar…", style="Gray.TButton", command=pick).grid(row=row, column=2, padx=4)
            ttk.Button(parent, text="Quitar",    style="Gray.TButton", command=clear).grid(row=row, column=3, padx=2)

        hf = ttk.LabelFrame(sf, text="Header (zona superior)", padding=10)
        hf.pack(fill="x", padx=10, pady=6)
        tk.Label(hf, text="Título:", bg="#12121f", fg="#8080c0").grid(row=0, column=0, sticky="w", pady=3)
        self.ov_title = ttk.Entry(hf, width=30)
        self.ov_title.insert(0, self.dm.settings["overlay"].get("title",""))
        self.ov_title.grid(row=0, column=1, columnspan=3, sticky="ew", padx=8)
        tk.Label(hf, text="Logo:", bg="#12121f", fg="#8080c0").grid(row=1, column=0, sticky="w", pady=3)
        self.ov_logo_lbl = tk.Label(hf,
            text=os.path.basename(self.dm.settings["overlay"].get("logo_path","")) or "Sin logo",
            bg="#12121f", fg="#3a3a6a", font=("Segoe UI",8))
        self.ov_logo_lbl.grid(row=1, column=1, sticky="w", padx=8)
        ttk.Button(hf, text="Explorar…", style="Gray.TButton", command=self._pick_logo).grid(row=1, column=2, padx=4)
        ttk.Button(hf, text="Quitar",    style="Gray.TButton", command=self._clear_logo).grid(row=1, column=3, padx=4)
        add_color_row(hf, 2, "Color fondo header:",   "header_color")
        add_alpha_row(hf, 3, "Transparencia header:", "header_alpha")
        add_color_row(hf, 4, "Color texto header:",   "header_text_color")

        ff = ttk.LabelFrame(sf, text="Fuentes", padding=10)
        ff.pack(fill="x", padx=10, pady=6)
        tk.Label(ff, text="Las fuentes de Google Fonts se cargan automáticamente en el overlay.",
                 bg="#12121f", fg="#3a3a6a", font=("Segoe UI",8,"italic")).grid(
                 row=0, column=0, columnspan=4, sticky="w", pady=(0,6))
        add_font_row(ff, 1, "Fuente Header/Timer:", "font_header")
        add_font_row(ff, 2, "Fuente Tabla/Bosses:", "font_table")

        szf = ttk.LabelFrame(sf, text="Tamaño de texto", padding=10)
        szf.pack(fill="x", padx=10, pady=6)
        add_size_row(szf, 0, "Título (header):",    "size_title",    10, 48)
        add_size_row(szf, 1, "Subtítulo (juego):",  "size_subtitle",  8, 32)
        add_size_row(szf, 2, "Timer:",              "size_timer",    14, 60)
        add_size_row(szf, 3, "Texto tabla:",        "size_table",     8, 32)
        add_size_row(szf, 4, "Total / Diff:",       "size_total",     8, 28)

        bf = ttk.LabelFrame(sf, text="Tabla / Cuerpo", padding=10)
        bf.pack(fill="x", padx=10, pady=6)
        add_color_row(bf, 0, "Fondo tabla:",         "body_bg")
        add_alpha_row(bf, 1, "Transparencia tabla:", "body_alpha")
        add_color_row(bf, 2, "Texto tabla:",          "body_text_color")
        add_color_row(bf, 3, "Color fila alt:",       "row_alt_color")
        add_color_row(bf, 4, "Color acento:",         "accent_color")
        add_color_row(bf, 5, "Color PB:",             "pb_color")

        af = ttk.LabelFrame(sf, text="Assets (Imágenes de diseño)", padding=10)
        af.pack(fill="x", padx=10, pady=6)
        tk.Label(af, text="Fondo (detrás de la tabla):", bg="#12121f", fg="#8080c0",
                 font=("Segoe UI",9,"bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,2))
        add_image_row(af, 1, "Imagen de fondo:", "bg_image_path")
        add_alpha_row(af, 2, "Opacidad del fondo:", "bg_image_alpha")
        tk.Label(af, text="Marco / Frame (encima de todo):", bg="#12121f", fg="#8080c0",
                 font=("Segoe UI",9,"bold")).grid(row=3, column=0, columnspan=4, sticky="w", pady=(8,2))
        tk.Label(af, text="Usá una imagen PNG con transparencia. Se estira para cubrir el overlay.",
                 bg="#12121f", fg="#3a3a6a", font=("Segoe UI",8,"italic")).grid(
                 row=4, column=0, columnspan=4, sticky="w", pady=(0,4))
        add_image_row(af, 5, "Imagen de marco:", "frame_image_path")

        vf = ttk.LabelFrame(sf, text="Columnas visibles", padding=10)
        vf.pack(fill="x", padx=10, pady=6)
        self.ov_show_timer  = tk.BooleanVar(value=self.dm.settings["overlay"].get("show_timer",  True))
        self.ov_show_pb     = tk.BooleanVar(value=self.dm.settings["overlay"].get("show_pb",     True))
        self.ov_show_blocks = tk.BooleanVar(value=self.dm.settings["overlay"].get("show_blocks", True))
        self.ov_show_path   = tk.BooleanVar(value=self.dm.settings["overlay"].get("show_path_hits", True))
        for var, label in [(self.ov_show_timer,  "Mostrar Timer"),
                            (self.ov_show_pb,    "Mostrar PB"),
                            (self.ov_show_blocks,"Mostrar columna Blocks"),
                            (self.ov_show_path,  "Mostrar columna Path Hits")]:
            ttk.Checkbutton(vf, text=label, variable=var).pack(anchor="w", pady=2)

        df = ttk.LabelFrame(sf, text="Dimensiones del Overlay", padding=10)
        df.pack(fill="x", padx=10, pady=6)
        tk.Label(df, text="Ancho (px):", bg="#12121f", fg="#8080c0").grid(row=0, column=0, sticky="w", pady=3)
        self.ov_width = ttk.Entry(df, width=8)
        self.ov_width.insert(0, str(self.dm.settings["overlay"].get("width", 600)))
        self.ov_width.grid(row=0, column=1, padx=8)

        ttk.Button(sf, text="💾 Guardar configuración del Overlay", style="Green.TButton",
                   command=lambda: self._save_overlay_settings(color_btns)).pack(pady=10)
        self._color_btns   = color_btns
        self._color_labels = color_labels

    def _copy_url(self, url):
        self.root.clipboard_clear(); self.root.clipboard_append(url)
        messagebox.showinfo("Copiado", f"URL copiada:\n{url}\n\nPegala en OBS → Browser Source → URL")

    def _start_run(self):
        tid = self.tmpl_var.get()
        if tid:
            self.dm.set_active_template(tid)
            tmpl = self.dm.templates.get(tid, {})

            preset = PRESET_TEMPLATES.get(tid)
            title  = preset.get("run_title", tmpl.get("name", "")) if preset else tmpl.get("name", "")
            self.dm.settings["overlay"]["title"] = title

            game_key  = tmpl.get("game_key", "")
            logo_file = GAME_ASSETS.get(game_key, "")
            logo_path = os.path.join(ASSETS_DIR, logo_file) if logo_file else ""
            if logo_path and os.path.exists(logo_path):
                self.dm.settings["overlay"]["logo_path"] = logo_path

            self.dm.save_settings()

            try:
                self.ov_title.delete(0, "end")
                self.ov_title.insert(0, self.dm.settings["overlay"]["title"])
                cur_logo = os.path.basename(self.dm.settings["overlay"].get("logo_path","")) or "Sin logo"
                self.ov_logo_lbl.configure(text=cur_logo)
            except:
                pass

        self.timer.reset()
        self.timer.start()
        self._refresh_live()

    def _reset_run_btn(self):
        self.dm.reset_run()
        self.timer.reset()
        self._refresh_live()

    def _reset_timer(self): self.timer.reset()

    def _save_pb(self):
        self.hkm._save_pb()   # para el timer y guarda pb_time
        pb_str = self.timer.format(self.dm.state.get("pb_time"))
        messagebox.showinfo("PB Guardado", f"PB guardado: {pb_str}")

    def _undo_hit(self):
        bosses, idx = self.hkm._get_boss()
        if bosses:
            bosses[idx]["hits"] = max(0, bosses[idx].get("hits", 0) - 1)
            self._refresh_live()

    def _undo_block(self):
        bosses, idx = self.hkm._get_boss()
        if bosses:
            bosses[idx]["blocks"] = max(0, bosses[idx].get("blocks", 0) - 1)
            self._refresh_live()

    def _undo_path(self):
        bosses, idx = self.hkm._get_boss()
        if bosses:
            bosses[idx]["path_hits"] = max(0, bosses[idx].get("path_hits", 0) - 1)
            self._refresh_live()

    def _refresh_template_combo(self):
        names = list(self.dm.templates.keys())
        self.tmpl_combo["values"] = names
        active = self.dm.state.get("active_template","")
        self.tmpl_combo.set(active if active in names else (names[0] if names else ""))

    def _refresh_tmpl_list(self):
        self.tmpl_listbox.delete(0,"end")
        for tid in self.dm.templates:
            t      = self.dm.templates[tid]
            name   = t.get("name", tid)
            prefix = "⭐ " if tid in PRESET_TEMPLATES else ""
            self.tmpl_listbox.insert("end", f"{prefix}{name}")
        self._tmpl_ids = list(self.dm.templates.keys())

    def _on_tmpl_list_select(self, event=None):
        sel = self.tmpl_listbox.curselection()
        if not sel: return
        tid  = self._tmpl_ids[sel[0]]
        tmpl = self.dm.templates[tid]
        self._current_edit_template = tid
        self.te_name.delete(0,"end"); self.te_name.insert(0, tmpl.get("name",""))
        self.te_game.delete(0,"end"); self.te_game.insert(0, tmpl.get("game",""))
        self.te_game_key.set(tmpl.get("game_key", ""))
        self.boss_listbox.delete(0,"end")
        for boss in tmpl.get("bosses",[]): self.boss_listbox.insert("end", boss.get("name","?"))

    def _new_template(self):
        tid = f"template_{int(time.time())}"
        self.dm.save_template(tid, {"name":"Nuevo Template","game":"Juego","bosses":[]})
        self._refresh_tmpl_list(); self._refresh_template_combo()
        self._tmpl_ids = list(self.dm.templates.keys())
        if tid in self._tmpl_ids:
            i = self._tmpl_ids.index(tid)
            self.tmpl_listbox.selection_clear(0,"end"); self.tmpl_listbox.selection_set(i)
            self.tmpl_listbox.see(i); self._on_tmpl_list_select()

    def _delete_template(self):
        sel = self.tmpl_listbox.curselection()
        if not sel: return
        tid  = self._tmpl_ids[sel[0]]
        name = self.dm.templates.get(tid, {}).get("name", tid)
        if messagebox.askyesno("Confirmar", f"¿Borrar template '{name}'?"):
            self.dm.delete_template(tid)
            self._refresh_tmpl_list(); self._refresh_template_combo()
            self._build_template_editor(self.tmpl_editor_frame)

    def _add_boss_to_template(self):
        name = self.boss_entry.get().strip()
        if name: self.boss_listbox.insert("end", name); self.boss_entry.delete(0,"end")

    def _remove_boss(self):
        sel = self.boss_listbox.curselection()
        if sel: self.boss_listbox.delete(sel[0])

    def _move_boss(self, direction):
        sel = self.boss_listbox.curselection()
        if not sel: return
        idx = sel[0]; new = idx + direction
        if 0 <= new < self.boss_listbox.size():
            val = self.boss_listbox.get(idx)
            self.boss_listbox.delete(idx); self.boss_listbox.insert(new, val)
            self.boss_listbox.selection_set(new)

    def _rename_boss(self, event=None):
        sel = self.boss_listbox.curselection()
        if not sel: return
        idx = sel[0]; old = self.boss_listbox.get(idx)
        win = tk.Toplevel(self.root); win.title("Renombrar Boss")
        win.geometry("300x100"); win.configure(bg="#12121f"); win.grab_set()
        tk.Label(win, text="Nuevo nombre:", bg="#12121f", fg="#8080c0").pack(pady=8)
        var = tk.StringVar(value=old)
        entry = ttk.Entry(win, textvariable=var, width=24); entry.pack(); entry.focus()
        def confirm(e=None):
            new = var.get().strip()
            if new:
                self.boss_listbox.delete(idx); self.boss_listbox.insert(idx, new)
                self.boss_listbox.selection_set(idx)
            win.destroy()
        entry.bind("<Return>", confirm)
        ttk.Button(win, text="OK", command=confirm).pack(pady=6)

    def _save_current_template(self):
        tid  = self._current_edit_template or f"template_{int(time.time())}"
        name = self.te_name.get().strip() or "Sin nombre"
        game = self.te_game.get().strip() or ""
        bosses = []
        is_active = (tid == self.dm.state.get("active_template"))
        live_bosses = self.dm.active_template.get("bosses", []) if (is_active and self.dm.active_template) else []
        for i in range(self.boss_listbox.size()):
            bname = self.boss_listbox.get(i)
            existing = next((b for b in live_bosses if b.get("name") == bname), None)
            if existing is None:
                existing = next((b for b in self.dm.templates.get(tid,{}).get("bosses",[])
                                 if b.get("name") == bname), {})
            bosses.append({"name": bname, "hits": existing.get("hits",0),
                           "blocks": existing.get("blocks",0),
                           "path_hits": existing.get("path_hits",0),
                           "pb_hits": existing.get("pb_hits",0)})
        game_key = self.te_game_key.get().strip()
        self.dm.save_template(tid, {"name": name, "game": game,
                                    "game_key": game_key, "bosses": bosses})
        self._current_edit_template = tid
        self._refresh_tmpl_list(); self._refresh_template_combo()
        messagebox.showinfo("Guardado", f"Template '{name}' guardado.")

    def _save_hotkeys(self):
        for key, var in self.hk_vars.items():
            self.dm.settings["hotkeys"][key] = var.get().strip()
        self.dm.save_settings(); self.hkm.register_all()
        messagebox.showinfo("Hotkeys", "Hotkeys guardados y reregistrados.")

    def _pick_color(self, key, btn, lbl):
        color = colorchooser.askcolor(color=self.dm.settings["overlay"].get(key,"#ff0000"),
                                      title=f"Color: {key}")[1]
        if color:
            self.dm.settings["overlay"][key] = color
            btn.configure(bg=color); lbl.configure(text=color)

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar logo",
            filetypes=[("Imágenes","*.png *.jpg *.jpeg *.gif *.bmp *.webp"),("Todos","*.*")])
        if path:
            dest = os.path.join(LOGOS_DIR, os.path.basename(path))
            shutil.copy2(path, dest)
            self.dm.settings["overlay"]["logo_path"] = dest
            self.ov_logo_lbl.configure(text=os.path.basename(dest))

    def _clear_logo(self):
        self.dm.settings["overlay"]["logo_path"] = ""
        self.ov_logo_lbl.configure(text="Sin logo")

    def _save_overlay_settings(self, color_btns):
        s = self.dm.settings["overlay"]
        s["title"]          = self.ov_title.get()
        s["show_timer"]     = self.ov_show_timer.get()
        s["show_pb"]        = self.ov_show_pb.get()
        s["show_blocks"]    = self.ov_show_blocks.get()
        s["show_path_hits"] = self.ov_show_path.get()
        try:
            s["width"] = int(self.ov_width.get())
        except:
            pass
        self.dm.save_settings()
        messagebox.showinfo("Overlay", "Configuración guardada. El overlay se actualiza en 1 segundo.")

    def _refresh_live(self):
        tmpl = self.dm.active_template
        if not tmpl: return
        for row in self.tree.get_children(): self.tree.delete(row)

        cur_idx  = self.dm.state.get("current_boss_index", 0)
        bosses   = tmpl.get("bosses", [])
        cur_name = "—"

        for i, boss in enumerate(bosses):
            hits   = boss.get("hits",      0)
            blocks = boss.get("blocks",    0)
            path   = boss.get("path_hits", 0)
            if i == cur_idx:
                tag = "current"; cur_name = boss.get("name","?")
            elif i < cur_idx:
                tag = "done_clean" if (hits + blocks + path) == 0 else "done_hit"
            else:
                tag = "future"

            pb = boss.get("pb_hits", 0)
            self.tree.insert("", "end", values=(
                ("▶ " if i == cur_idx else "") + boss.get("name","?"),
                hits, boss.get("blocks",0), boss.get("path_hits",0),
                f"{pb} ({hits})"
            ), tags=(tag,))

        self.cur_boss_lbl.configure(text=f"Boss actual: {cur_name}")
        pb_time = self.dm.state.get("pb_time")
        if pb_time:
            self.pb_lbl.configure(text=f"PB: {self.timer.format(pb_time)}")
        else:
            self.pb_lbl.configure(text="")

    def _tick(self):
        self.timer_lbl.configure(text=self.timer.format())
        self.root.after(50, self._tick)

    def on_close(self):
        self.hkm.unregister_all()
        self.timer.stop()
        self.dm.state["timer_elapsed"] = self.timer.elapsed
        self.dm.save_state()
        self.dm.save_settings()
        self.root.destroy()


def main():
    root = tk.Tk()
    app  = NoHitApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()