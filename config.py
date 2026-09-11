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

# Color Tokens for CustomTkinter UI
THEME_COLORS = {
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "secondary": "#475569",
    "secondary_hover": "#334155",
    "success": "#16a34a",
    "warning": "#ca8a04",
    "danger": "#dc2626",
    "card_dark": "#1e293b",
    "card_light": "#f8fafc",
    "bg_dark": "#0f172a",
    "bg_light": "#ffffff",
    "text_dark": "#f8fafc",
    "text_light": "#0f172a",
    "subtext_dark": "#94a3b8",
    "subtext_light": "#64748b",
    "border_dark": "#334155",
    "border_light": "#e2e8f0"
}
