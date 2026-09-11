"""
ExpedUP - Configuration & Constants
Universal Entity, Brand & Name Expedition Engine
"""

VERSION = "1.0.0"
APP_NAME = "ExpedUP"
APP_SUBTITLE = "Universal Word, Brand & Name Online Expedition Engine"

# Default User-Agent list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.2478.80"
]

# Social Media & Platform Profiles to Probe
SOCIAL_PLATFORMS = [
    {"name": "Instagram", "url_template": "https://www.instagram.com/{target}/", "category": "Social / Visual"},
    {"name": "Threads", "url_template": "https://www.threads.net/@{target}", "category": "Social / Microblog"},
    {"name": "TikTok", "url_template": "https://www.tiktok.com/@{target}", "category": "Social / Video"},
    {"name": "Twitter / X", "url_template": "https://twitter.com/{target}", "category": "Social / News"},
    {"name": "Facebook", "url_template": "https://www.facebook.com/{target}/", "category": "Social / Community"},
    {"name": "LinkedIn Company", "url_template": "https://www.linkedin.com/company/{target}/", "category": "Professional"},
    {"name": "GitHub", "url_template": "https://github.com/{target}", "category": "Developer"},
    {"name": "YouTube", "url_template": "https://www.youtube.com/@{target}", "category": "Video"},
    {"name": "Pinterest", "url_template": "https://www.pinterest.com/{target}/", "category": "Lifestyle / E-Commerce"},
    {"name": "Snapchat", "url_template": "https://www.snapchat.com/add/{target}", "category": "Social / Instant"},
    {"name": "Reddit User", "url_template": "https://www.reddit.com/user/{target}/", "category": "Community"},
    {"name": "Medium", "url_template": "https://medium.com/@{target}", "category": "Publications"},
    {"name": "Telegram", "url_template": "https://t.me/{target}", "category": "Messaging"},
    {"name": "Behance", "url_template": "https://www.behance.net/{target}", "category": "Design Portfolio"},
    {"name": "SoundCloud", "url_template": "https://soundcloud.com/{target}", "category": "Audio / Music"}
]

# Top Domain Extensions for Brand/Name Probe
DOMAIN_TLDS = [
    ".com", ".com.gh", ".org", ".net", ".store", ".online", ".co", ".io", 
    ".shop", ".africa", ".ng", ".ke", ".co.uk", ".app", ".tech"
]

# Theme Tokens (Light Mode Default with full Dark Mode support, inspired by Vectihost & Selligine design systems)
# Uses (light_mode_color, dark_mode_color) tuples so CustomTkinter natively switches every element on appearance change.
THEME_COLORS = {
    # Surfaces & Backgrounds
    "bg": ("#f1f5f9", "#0b0f19"),              # Page canvas (slate-100 in light / deep obsidian in dark)
    "card": ("#ffffff", "#111827"),            # Card surface (pure white in light / slate-900 in dark)
    "card_subtle": ("#f8fafc", "#1e293b"),     # Muted item box (slate-50 in light / slate-800 in dark)
    "card_alt": ("#e2e8f0", "#182234"),       # Active item box
    "input_bg": ("#ffffff", "#0f172a"),        # Text entry background
    "border": ("#e2e8f0", "#1f2937"),          # Card border (slate-200 in light / slate-800 in dark)
    "border_strong": ("#cbd5e1", "#374151"),   # Stronger divider
    
    # Typography
    "text_primary": ("#0f172a", "#f8fafc"),    # Headings & primary labels (slate-900 / slate-50)
    "text_secondary": ("#475569", "#94a3b8"),  # Subtitles & secondary notes (slate-600 / slate-400)
    "text_muted": ("#94a3b8", "#64748b"),      # Placeholders & timestamps

    # Primary Action (Royal Blue)
    "primary": ("#2563eb", "#3b82f6"),
    "primary_hover": ("#1d4ed8", "#2563eb"),
    
    # Secondary Action (Slate Neutral)
    "secondary": ("#f1f5f9", "#1e293b"),
    "secondary_hover": ("#e2e8f0", "#334155"),
    "secondary_text": ("#334155", "#e2e8f0"),

    # Status & Accents
    "accent": ("#0284c7", "#38bdf8"),          # Sky Blue
    "accent_purple": ("#7c3aed", "#a855f7"),  # Purple
    "success": ("#16a34a", "#10b981"),         # Emerald Green
    "warning": ("#d97706", "#f59e0b"),         # Amber
    "danger": ("#dc2626", "#ef4444"),          # Rose Red

    # Terminal Console (Always Dark for contrast)
    "console_bg": ("#0f172a", "#050811"),
    "console_text": ("#38bdf8", "#38bdf8"),
}

# Window Geometry
DEFAULT_WINDOW_WIDTH = 1260
DEFAULT_WINDOW_HEIGHT = 840
MIN_WINDOW_WIDTH = 1050
MIN_WINDOW_HEIGHT = 680

# Default Artifacts & Export Path
DEFAULT_EXPORT_DIR = "artifacts/expeditions"


