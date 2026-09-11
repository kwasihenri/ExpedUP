"""
ExpedUP Icon Manager
Provides crisp, dynamically-colored vector-rendered icons using CustomTkinter CTkImage and PIL.
Assets are sourced from Tabler Icons (MIT License) stored locally in assets/icons/.
"""

import os
from typing import Tuple, Optional
from PIL import Image
import customtkinter as ctk

# Base directory for icons
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ICONS_DIR = os.path.join(_BASE_DIR, "assets", "icons")

# Cache to avoid re-opening / re-tinting icons
_CACHE: dict = {}

# Friendly aliases mapping to filename in assets/icons/
_ALIASES = {
    "target": "target.png",
    "search": "search.png",
    "users": "users.png",
    "user": "users.png",
    "profile": "users.png",
    "world": "world.png",
    "globe": "world.png",
    "phone": "phone.png",
    "mail": "mail.png",
    "email": "mail.png",
    "at": "at.png",
    "mention": "at.png",
    "hash": "hash.png",
    "tag": "hash.png",
    "terminal": "terminal.png",
    "console": "terminal.png",
    "dashboard": "dashboard.png",
    "chart": "dashboard.png",
    "play": "play.png",
    "launch": "play.png",
    "loader": "loader.png",
    "spinner": "loader.png",
    "stop": "stop.png",
    "abort": "stop.png",
    "bolt": "bolt.png",
    "zap": "bolt.png",
    "trash": "trash.png",
    "clear": "trash.png",
    "download": "download.png",
    "export": "download.png",
    "file-text": "file-text.png",
    "markdown": "file-text.png",
    "table": "table.png",
    "csv": "table.png",
    "code": "code.png",
    "json": "code.png",
    "folder": "folder.png",
    "dir": "folder.png",
    "copy": "copy.png",
    "clipboard": "copy.png",
    "external-link": "external-link.png",
    "open": "external-link.png",
    "circle-check": "circle-check.png",
    "verified": "circle-check.png",
    "circle": "circle.png",
    "pending": "circle.png",
    "check": "check.png",
    "refresh": "refresh.png"
}

def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex string (e.g. #00FFCC or 00FFCC) to (R, G, B) tuple."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return (255, 255, 255)

def _tint_image(image: Image.Image, hex_color: str) -> Image.Image:
    """Tint transparent outline image with given hex color preserving alpha antialiasing."""
    rgba = image.convert("RGBA")
    alpha = rgba.split()[3]
    r, g, b = _hex_to_rgb(hex_color)
    solid = Image.new("RGBA", rgba.size, (r, g, b, 255))
    solid.putalpha(alpha)
    return solid

from typing import Tuple, Optional, Union

def get_icon(name: str, size: Tuple[int, int] = (16, 16), color: Union[str, Tuple[str, str], None] = None) -> ctk.CTkImage:
    """
    Get or load a CTkImage icon with dynamic size and light/dark color tinting.

    :param name: Icon name or alias (e.g. 'search', 'target', 'copy', 'world')
    :param size: Tuple of (width, height) in pixels
    :param color: Hex color string (e.g. '#2563eb') or (light_color, dark_color) tuple.
                  If None, automatically defaults to slate for light mode and white for dark mode.
    :return: ctk.CTkImage instance ready for buttons, labels, and frames
    """
    if isinstance(color, (tuple, list)) and len(color) >= 2:
        light_color = str(color[0]).upper()
        dark_color = str(color[1]).upper()
    elif color:
        light_color = str(color).upper()
        dark_color = str(color).upper()
    else:
        # Default contrast: slate-700 in light mode, clean white in dark mode
        light_color = "#334155"
        dark_color = "#F8FAFC"

    cache_key = (name.lower(), size, light_color, dark_color)

    if cache_key in _CACHE:
        return _CACHE[cache_key]

    filename = _ALIASES.get(name.lower(), f"{name}.png")
    icon_path = os.path.join(_ICONS_DIR, filename)

    if not os.path.exists(icon_path):
        # Graceful fallback: 1x1 transparent image
        fallback_img = Image.new("RGBA", size, (0, 0, 0, 0))
        ctk_img = ctk.CTkImage(light_image=fallback_img, dark_image=fallback_img, size=size)
        _CACHE[cache_key] = ctk_img
        return ctk_img

    try:
        raw_img = Image.open(icon_path)
        light_tinted = _tint_image(raw_img, light_color)
        dark_tinted = _tint_image(raw_img, dark_color) if dark_color != light_color else light_tinted
        ctk_img = ctk.CTkImage(light_image=light_tinted, dark_image=dark_tinted, size=size)
        _CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        fallback_img = Image.new("RGBA", size, (0, 0, 0, 0))
        return ctk.CTkImage(light_image=fallback_img, dark_image=fallback_img, size=size)

