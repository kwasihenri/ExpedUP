"""
ExpedUP Engine - Deep Search, Reconnaissance & Intelligence Probe
Modular, multi-source expedition engine.
"""

import urllib.request
import urllib.parse
import json
import ssl
import time
import re
import socket
import random
from typing import Dict, List, Callable, Optional
from config import USER_AGENTS, SOCIAL_PLATFORMS, DOMAIN_TLDS
from settings_manager import load_settings

# Configure permissive SSL context for reconnaissance
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def is_search_result_relevant(target: str, title: str, snippet: str, url: str, strict: bool = False) -> bool:
    """
    Verify that a search result is genuinely related to the target keyword,
    filtering out engine fallback/trending links and accidental substring collisions.
    """
    if not target:
        return True

    clean_target = re.sub(r'[^a-zA-Z0-9]', '', target.lower())
    if not clean_target:
        return True

    combined_text = f"{title} {snippet}".lower()
    url_lower = url.lower()

    # 1. Target appears as an explicit word boundary in title or snippet
    word_pat = rf'\b{re.escape(clean_target)}\b'
    if re.search(word_pat, combined_text) or target.lower() in combined_text:
        return True

    # 2. Target is the dedicated second-level domain (e.g. waitrive.com, luuksgh.org)
    domain_pat = rf'(?:^|https?://(?:[a-z0-9-]+\.)?){re.escape(clean_target)}\.[a-z]{{2,}}'
    if re.search(domain_pat, url_lower):
        return True

    # 3. Target is the primary user handle or route slug in the path
    # e.g. /luuksgh/ or /@luuksgh or /user/luuksgh or /company/luuksgh
    # Excludes random hyphenated blog slugs like '...cant-waitrive/123'
    slug_pat = rf'/(?:@|company/|in/|pages?/|user/)?{re.escape(clean_target)}(?:/|$|\.|\?)'
    if re.search(slug_pat, url_lower):
        return True

    return False


class ExpedUPEngine:
    def __init__(self, log_cb: Optional[Callable[[str], None]] = None,
                 progress_cb: Optional[Callable[[int, int, str], None]] = None,
                 result_cb: Optional[Callable[[str, dict], None]] = None,
                 settings: Optional[dict] = None):
        self.log_cb = log_cb or (lambda msg: None)
        self.progress_cb = progress_cb or (lambda c, t, s: None)
        self.result_cb = result_cb or (lambda cat, item: None)
        self.stop_requested = False
        self.current_target = ""
        self.strict_keyword = False

        # Load engine configuration
        self.settings = dict(settings) if settings else load_settings()
        self.timeout = int(self.settings.get("request_timeout", 12))
        self.min_delay = float(self.settings.get("min_delay", 0.8))
        self.max_delay = float(self.settings.get("max_delay", 1.4))
        self.ua_rotation = bool(self.settings.get("user_agent_rotation", True))
        self.enabled_platforms = set(self.settings.get("enabled_platforms", [p["name"] for p in SOCIAL_PLATFORMS]))
        self.domain_tlds = list(self.settings.get("domain_tlds", DOMAIN_TLDS))

        # Results storage
        self.results = {
            "target": "",
            "location": "",
            "category": "",
            "phone": "",
            "timestamp": "",
            "queries_executed": [],
            "search_results": [],
            "social_profiles": [],
            "domains": [],
            "entities": {
                "phones": set(),
                "emails": set(),
                "mentions": set(),
                "hashtags": set()
            }
        }

    def stop(self):
        """Signal engine to stop running expedition."""
        self.stop_requested = True
        self.log("[!] Expedition stop requested by user.")

    def log(self, message: str):
        """Send message to logging callback."""
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.log_cb(formatted)

    def get_headers(self) -> dict:
        """Return headers with modern user agent and clean browser parity."""
        ua = random.choice(USER_AGENTS) if self.ua_rotation else USER_AGENTS[0]
        return {
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9"
        }

    # ---------------------------------------------------------
    # 1. Search Engine Probing (DuckDuckGo Lite, Bing, Yahoo)
    # ---------------------------------------------------------
    def search_duckduckgo_html(self, query: str) -> List[dict]:
        """Perform search query via DuckDuckGo HTML endpoint with resilient block parsing."""
        if self.stop_requested:
            return []

        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=self.get_headers())
        results = []

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=self.timeout) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                blocks = html.split('<div class="result results_links')
                for b in blocks[1:]:
                    # Extract title
                    m_t = re.search(r'<h2[^>]*class="[^"]*result__title[^"]*"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', b, re.DOTALL)
                    if not m_t:
                        m_t = re.search(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', b, re.DOTALL)

                    # Extract snippet
                    m_s = re.search(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', b, re.DOTALL)
                    if not m_s:
                        m_s = re.search(r'<div[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</div>', b, re.DOTALL)

                    href = ""
                    title = ""
                    snip = ""

                    if m_t:
                        href = m_t.group(1)
                        title = re.sub(r'<[^>]+>', '', m_t.group(2)).strip()
                    if m_s:
                        snip = re.sub(r'<[^>]+>', '', m_s.group(1)).strip()
                        if not href and 'href="' in m_s.group(0):
                            m_sh = re.search(r'href="([^"]+)"', m_s.group(0))
                            if m_sh:
                                href = m_sh.group(1)

                    if "uddg=" in href:
                        m_u = re.search(r"uddg=([^&]+)", href)
                        if m_u:
                            href = urllib.parse.unquote(m_u.group(1))

                    if href and not href.startswith("/") and (title or snip):
                        # Filter out irrelevant search engine filler results
                        if not is_search_result_relevant(self.current_target, title, snip, href, self.strict_keyword):
                            continue

                        item = {
                            "engine": "DuckDuckGo",
                            "query": query,
                            "title": title or "Web Finding",
                            "url": href,
                            "snippet": snip
                        }
                        results.append(item)
                        self.harvest_entities(f"{title} {snip}")
                        self.result_cb("search", item)

        except Exception as e:
            self.log(f"DDG search notice on '{query}': {e}")

        return results

    def search_bing(self, query: str) -> List[dict]:
        """Perform search query via Bing with robust block and lineclamp parsing."""
        if self.stop_requested:
            return []

        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&setlang=en-US"
        headers = self.get_headers()
        headers["Cookie"] = "SRCHHPGUSR=ADLT=OFF&NRSLT=20;"
        headers["Accept-Language"] = "en-US,en;q=0.9"
        req = urllib.request.Request(url, headers=headers)
        results = []

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=self.timeout) as resp:
                html_text = resp.read().decode("utf-8", errors="ignore")
                blocks = html_text.split('<li class="b_algo"')
                for b in blocks[1:]:
                    m_title = re.search(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', b, re.DOTALL)
                    href = m_title.group(1) if m_title else ""
                    title = re.sub(r"<[^>]+>", "", m_title.group(2)).strip() if m_title else ""

                    # Unwrap Bing tracking redirect URL to canonical destination
                    if "u=a1" in href:
                        import base64
                        m_u = re.search(r"[?&](?:amp;)?u=a1([^&]+)", href)
                        if m_u:
                            try:
                                b64 = m_u.group(1)
                                b64 += "=" * ((4 - len(b64) % 4) % 4)
                                decoded_url = base64.urlsafe_b64decode(b64).decode("utf-8", errors="ignore")
                                if decoded_url.startswith("http"):
                                    href = decoded_url
                            except Exception:
                                pass

                    m_snip = re.search(r'<div class="b_caption">.*?<p[^>]*>(.*?)</p>', b, re.DOTALL)
                    if not m_snip:
                        m_snip = re.search(r'<p class="b_lineclamp[^"]*">(.*?)</p>', b, re.DOTALL)
                    snip = re.sub(r"<[^>]+>", "", m_snip.group(1)).strip() if m_snip else ""

                    import html
                    title = html.unescape(title)
                    snip = html.unescape(snip)

                    if href and not href.startswith("/") and (title or snip):
                        # Filter out irrelevant search engine filler results
                        if not is_search_result_relevant(self.current_target, title, snip, href, self.strict_keyword):
                            continue

                        item = {
                            "engine": "Bing",
                            "query": query,
                            "title": title or "Web Finding",
                            "url": href,
                            "snippet": snip
                        }
                        results.append(item)
                        self.harvest_entities(f"{title} {snip}")
                        self.result_cb("search", item)
        except Exception as e:
            self.log(f"Bing search notice on '{query}': {e}")

        return results

    # ---------------------------------------------------------
    # 2. Social Media & Digital Identity Probing
    # ---------------------------------------------------------
    def probe_social_profile(self, platform: dict, target: str) -> dict:
        """Probe platform URL for target presence and metadata, enriching with cached search snippets."""
        if self.stop_requested:
            return {}

        clean_target = target.lower().replace(" ", "")
        url = platform["url_template"].format(target=clean_target)
        req = urllib.request.Request(url, headers=self.get_headers())

        status = 0
        title = ""
        og_title = ""
        og_desc = ""
        og_image = ""
        html = ""

        tiktok_user_found = False
        not_found_explicit = False

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=self.timeout) as resp:
                status = resp.getcode()
                html = resp.read().decode("utf-8", errors="ignore")

                # Extract title
                m_t = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                title = m_t.group(1).strip() if m_t else ""

                # Extract OpenGraph tags
                m_ot = re.search(r'''<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']*)["']''', html, re.IGNORECASE)
                og_title = m_ot.group(1).strip() if m_ot else ""

                m_od = re.search(r'''<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']*)["']''', html, re.IGNORECASE)
                og_desc = m_od.group(1).strip() if m_od else ""

                m_oi = re.search(r'''<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']*)["']''', html, re.IGNORECASE)
                og_image = m_oi.group(1).strip() if m_oi else ""

                if not og_desc:
                    m_d = re.search(r'''<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']''', html, re.IGNORECASE)
                    og_desc = m_d.group(1).strip() if m_d else ""

                # Dedicated TikTok profile rehydration data parsing
                if "tiktok" in platform["name"].lower() and html:
                    m_tt = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html, re.DOTALL)
                    if m_tt:
                        try:
                            tt_data = json.loads(m_tt.group(1))
                            user_detail = tt_data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {})
                            user_info = user_detail.get("userInfo", {})
                            user_obj = user_info.get("user", {})
                            stats_obj = user_info.get("stats", {})
                            status_code = user_detail.get("statusCode", -1)
                            if user_obj and user_obj.get("uniqueId") and status_code == 0:
                                tiktok_user_found = True
                                unique_id = user_obj.get("uniqueId")
                                nickname = user_obj.get("nickname") or unique_id
                                sig = user_obj.get("signature", "")
                                followers = stats_obj.get("followerCount", 0)
                                title = f"{nickname} (@{unique_id}) on TikTok"
                                og_title = title
                                if sig:
                                    og_desc = sig
                                    self.harvest_entities(sig)
                                elif followers:
                                    og_desc = f"{nickname} on TikTok with {followers:,} followers."
                            elif status_code in [10221, 10222] or (not user_obj and status_code != 0):
                                not_found_explicit = True
                        except Exception:
                            pass

                self.harvest_entities(f"{title} {og_title} {og_desc}")

        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            status = 0

        # Correlate with search engine results for richer metadata / cached bio
        # (Overcomes SPA login walls for Instagram, TikTok, Threads, Facebook)
        snippet_bio = ""
        matched_search_url = False
        plat_domain = urllib.parse.urlparse(url).netloc.replace("www.", "")

        # Target must be the actual account handle on this platform
        # e.g. facebook.com/luuksgh, instagram.com/luuksgh, tiktok.com/@luuksgh, youtube.com/@luuksgh
        profile_url_pat = rf'https?://(?:[a-z0-9-]+\.)?{re.escape(plat_domain)}/(?:@|company/|in/|pages?/|user/)?{re.escape(clean_target)}(?:/|$|\?)'

        for s_res in self.results.get("search_results", []):
            s_url = s_res.get("url", "")
            is_plat_profile = bool(re.search(profile_url_pat, s_url, re.IGNORECASE))
            has_mention_in_snip = (plat_domain in s_url and bool(re.search(rf'@{re.escape(clean_target)}\b', f"{s_res.get('title', '')} {s_res.get('snippet', '')}", re.IGNORECASE)))

            if is_plat_profile or has_mention_in_snip:
                matched_search_url = True
                snip = s_res.get("snippet", "")
                if snip and len(snip) > len(snippet_bio):
                    snippet_bio = snip
                self.harvest_entities(f"{s_res.get('title', '')} {snip}")

        # Determine existence confidence
        plat_key = platform["name"].lower()
        title_lower = title.strip().lower()
        og_title_lower = og_title.strip().lower()
        og_desc_lower = og_desc.strip().lower()

        # Specific platform generic landing page / login-wall detection
        is_generic_title = False
        if "instagram" in plat_key:
            if title_lower in ["instagram", "log in • instagram", "login • instagram", "create an account or log in to instagram", "login on instagram", "instagram post"] or "log in" in title_lower:
                is_generic_title = True
        elif "threads" in plat_key:
            if title_lower in ["threads", "log in • threads", "login • threads", "threads • log in"] or "log in" in title_lower or title_lower == "threads":
                is_generic_title = True
        elif "tiktok" in plat_key:
            if tiktok_user_found:
                is_generic_title = False
            elif "make your day" in title_lower or title_lower in ["tiktok", "tiktok - make your day"]:
                is_generic_title = True
        elif "reddit" in plat_key:
            if title_lower in ["reddit", "reddit - dive into anything", "reddit - explore anything"]:
                is_generic_title = True
        elif "telegram" in plat_key:
            # Telegram displays a placeholder page for unclaimed handles with title 'Telegram: Contact @...' and no tgme_page_extra
            if ("tgme_page_extra" not in html) and (title_lower.startswith("telegram: contact @") or "if you have telegram, you can contact @" in html.lower()):
                is_generic_title = True
        elif "linkedin" in plat_key:
            if title_lower in ["linkedin", "sign in", "log in", "authwall"] or "sign in" in title_lower:
                is_generic_title = True
        elif "facebook" in plat_key:
            if title_lower in ["facebook", "log in to facebook", "log into facebook"] or "log in" in title_lower:
                is_generic_title = True
        elif "pinterest" in plat_key:
            if title_lower in ["pinterest", "explore", ""]:
                is_generic_title = True

        has_login_wall = any(w in title_lower for w in ["log in", "login", "create an account", "redirecting"])
        not_found = not_found_explicit or any(w in title_lower or w in og_title_lower or w in og_desc_lower for w in [
            "not found", "404", "page isn't available", "doesn't exist",
            "user not found", "nobody on reddit goes by that name",
            "this account doesn't exist", "sorry, this page isn't available"
        ])

        has_target_mention = (
            clean_target in title_lower or
            clean_target in og_title_lower or
            clean_target in og_desc_lower
        )

        exists = False
        if matched_search_url:
            exists = True
        elif tiktok_user_found:
            exists = True
        elif status in [200, 301, 302, 307, 999] and not not_found and not is_generic_title:
            if has_target_mention:
                exists = True
            elif plat_key in ["github", "linkedin company", "linkedin profile", "youtube", "twitter / x", "dev.to", "hashnode"]:
                exists = True

        final_desc = og_desc
        if snippet_bio:
            if not final_desc or (has_login_wall and not tiktok_user_found) or len(snippet_bio) > len(final_desc):
                final_desc = snippet_bio

        if exists and final_desc:
            self.harvest_entities(final_desc)

        profile = {
            "platform": platform["name"],
            "category": platform["category"],
            "url": url,
            "status": status if status else (200 if matched_search_url else 0),
            "exists": exists,
            "title": title or og_title or (f"{platform['name']} profile" if exists else ""),
            "description": final_desc if exists else "",
            "image": og_image if exists else ""
        }

        if exists:
            self.result_cb("social", profile)

        return profile

    # ---------------------------------------------------------
    # 3. Domain & DNS Probing
    # ---------------------------------------------------------
    def probe_domain(self, domain_name: str) -> dict:
        """Check DNS and HTTP availability of a domain."""
        if self.stop_requested:
            return {}

        ip = None
        http_code = 0
        title = ""

        try:
            ip = socket.gethostbyname(domain_name)
        except Exception:
            ip = None

        # Attempt direct HTTPS/HTTP connection to fetch site title & bio
        for scheme in ["https", "http"]:
            if title or http_code == 200:
                break
            url = f"{scheme}://{domain_name}"
            req = urllib.request.Request(url, headers=self.get_headers())
            try:
                with urllib.request.urlopen(req, context=SSL_CTX, timeout=self.timeout) as resp:
                    http_code = resp.getcode()
                    html_content = resp.read(20480).decode("utf-8", errors="ignore")
                    m_t = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
                    title = m_t.group(1).strip() if m_t else ""
                    import html
                    title = html.unescape(title)
                    self.harvest_entities(f"{title} {html_content}")
                    if not ip:
                        ip = "Resolved via HTTP"
            except Exception:
                pass

        is_registered = bool(ip or http_code in [200, 301, 302, 307, 308, 403])

        res = {
            "domain": domain_name,
            "resolved_ip": ip if is_registered else None,
            "is_registered": is_registered,
            "status_code": http_code,
            "title": title
        }

        if is_registered:
            self.result_cb("domain", res)

        return res

    # ---------------------------------------------------------
    # 4. Intelligence & Entity Harvesting (Regex)
    # ---------------------------------------------------------
    def harvest_entities(self, text: str):
        """Extract phone numbers, emails, mentions, and hashtags with live callback."""
        if not text:
            return

        # 1. WhatsApp and contact-labeled numbers (e.g., WhatsApp 0573061008, Tel: +233...)
        labeled_phones = re.findall(
            r'(?:whatsapp|wa\.me\/?|tel|phone|contact|call|mobile)[\s:📱📞]*(\+?[\d\s\-()]{9,18})',
            text,
            re.IGNORECASE
        )
        for lp in labeled_phones:
            cleaned = re.sub(r'[^\d+]', '', lp)
            if 9 <= len(cleaned) <= 15:
                val = lp.strip().rstrip('.,;:')
                if val not in self.results["entities"]["phones"] and cleaned not in self.results["entities"]["phones"]:
                    self.results["entities"]["phones"].add(val)
                    self.result_cb("entity", {"type": "phone", "value": val})

        # 2. Compact 10-digit local numbers (e.g. 0573061008 in Ghana, UK 07xxx, Nigeria 080xxx)
        compact_phones = re.findall(r'\b0[1-9]\d{8}\b', text)
        for cp in compact_phones:
            if cp not in self.results["entities"]["phones"]:
                self.results["entities"]["phones"].add(cp)
                self.result_cb("entity", {"type": "phone", "value": cp})

        # 3. Standard & international formatted phones
        phones = re.findall(r'(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b', text)
        for p in phones:
            cleaned = re.sub(r'[^\d+]', '', p)
            if 9 <= len(cleaned) <= 15:
                p_str = p.strip().rstrip('.,;:')
                # Avoid catching pure years or zip codes
                if len(cleaned) >= 9 and p_str not in self.results["entities"]["phones"]:
                    self.results["entities"]["phones"].add(p_str)
                    self.result_cb("entity", {"type": "phone", "value": p_str})

        # Emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        for e in emails:
            if not any(e.lower().endswith(x) for x in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]):
                e_str = e.lower().strip().rstrip('.,;:')
                if e_str not in self.results["entities"]["emails"]:
                    self.results["entities"]["emails"].add(e_str)
                    self.result_cb("entity", {"type": "email", "value": e_str})

        # Mentions (@handle)
        mentions = re.findall(r'@[a-zA-Z0-9_.-]{3,30}', text)
        for m in mentions:
            m_str = m.strip().rstrip('.,;:')
            if m_str not in self.results["entities"]["mentions"]:
                self.results["entities"]["mentions"].add(m_str)
                self.result_cb("entity", {"type": "mention", "value": m_str})

        # Hashtags (#hashtag)
        hashtags = re.findall(r'#[a-zA-Z0-9_]{3,35}', text)
        for h in hashtags:
            h_str = h.strip().rstrip('.,;:')
            if h_str not in self.results["entities"]["hashtags"]:
                self.results["entities"]["hashtags"].add(h_str)
                self.result_cb("entity", {"type": "hashtag", "value": h_str})

    # ---------------------------------------------------------
    # 5. Master Expedition Runner
    # ---------------------------------------------------------
    def run_expedition(self, target: str, location: str = "", category: str = "",
                       phone: str = "", deep_level: str = "Standard",
                       strict_keyword: bool = False) -> dict:
        """Run the complete multi-source intelligence expedition pipeline."""
        self.stop_requested = False
        self.current_target = target
        self.strict_keyword = strict_keyword
        start_time = time.time()
        self.results["target"] = target
        self.results["location"] = location
        self.results["category"] = category
        self.results["phone"] = phone
        self.results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        self.log(f"=== Starting ExpedUP Expedition for: '{target}' ===")
        if strict_keyword:
            self.log("[Mode] Strict Go By Keyword ENABLED (Exact matches only; loose pivots suppressed)")
        if location:
            self.log(f"Location anchor: {location}")
        if category:
            self.log(f"Category anchor: {category}")
        if phone:
            self.log(f"Contact anchor: {phone}")

        # Build query matrix
        if strict_keyword:
            # Strict mode: Only exact quoted queries to prevent search engine drift
            queries = [
                f'"{target}"',
                f'"{target}" instagram',
                f'"{target}" tiktok',
                f'"{target}" facebook',
                f'"{target}" contact'
            ]
            if location:
                queries.append(f'"{target}" "{location}"')
            if category:
                queries.append(f'"{target}" "{category}"')
            if phone:
                queries.append(f'"{target}" "{phone}"')
        else:
            # Standard comprehensive multi-axis query matrix
            queries = [
                target,
                f'"{target}"'
            ]
            if location:
                queries.extend([f"{target} {location}", f'"{target}" "{location}"'])
                for loc_part in location.split(","):
                    part = loc_part.strip()
                    if part and f'"{target}" {part}' not in queries:
                        queries.append(f'"{target}" {part}')

            if category:
                queries.extend([f"{target} {category}", f'"{target}" {category}'])
                for cat_word in category.replace("&", " ").split():
                    w = cat_word.strip()
                    if len(w) > 3 and f'"{target}" {w}' not in queries:
                        queries.append(f'"{target}" {w}')

            if phone:
                queries.extend([f'"{phone}"', f"{target} {phone}"])

            # Natural social & discovery probes
            queries.extend([
                f'"{target}" linkedin',
                f'"{target}" github',
                f'"{target}" dev',
                f'"{target}" portfolio',
                f'"{target}" instagram',
                f'"{target}" tiktok',
                f'"{target}" facebook',
                f'"{target}" whatsapp',
                f'"{target}" contact'
            ])

        platforms_to_probe = [p for p in SOCIAL_PLATFORMS if p["name"] in self.enabled_platforms]
        total_steps = len(queries) + len(platforms_to_probe) + len(self.domain_tlds)
        current_step = 0

        # Phase 1: Search Engine Crawling (Multi-Engine: Bing + DuckDuckGo)
        self.log(f"Phase 1/3: Launching search engine queries ({len(queries)} probes)...")
        for q in queries:
            if self.stop_requested:
                break
            current_step += 1
            self.progress_cb(current_step, total_steps, f"Searching: {q[:32]}...")
            self.log(f"Probing search index: {q}")

            # Primary: Bing
            bing_res = self.search_bing(q)
            self.results["search_results"].extend(bing_res)
            time.sleep(random.uniform(self.min_delay * 0.4, self.max_delay * 0.6))

            # Complementary: DuckDuckGo
            ddg_res = self.search_duckduckgo_html(q)
            self.results["search_results"].extend(ddg_res)
            time.sleep(random.uniform(self.min_delay * 0.4, self.max_delay * 0.6))

        # Adaptive Pivot: If location was not specified and not in strict mode, check if initial search discovered regional anchors
        if not location and not strict_keyword and not self.stop_requested:
            discovered_locs = set()
            known_loc_tags = ["takoradi", "sekondi", "accra", "kumasi", "axim", "lagos", "london", "toronto", "atlanta", "chicago"]
            for h in self.results["entities"]["hashtags"]:
                h_low = h.lower()
                for kloc in known_loc_tags:
                    if kloc in h_low:
                        discovered_locs.add(kloc.capitalize())
            for dloc in list(discovered_locs)[:2]:
                followup_q = f'"{target}" {dloc}'
                if followup_q not in queries and not self.stop_requested:
                    self.log(f"Adaptive Pivot: Discovered regional anchor '{dloc}', probing: {followup_q}")
                    bing_res = self.search_bing(followup_q)
                    self.results["search_results"].extend(bing_res)
                    time.sleep(random.uniform(self.min_delay * 0.4, self.max_delay * 0.6))

        # Deduplicate search results
        seen_urls = set()
        dedup_search = []
        for r in self.results["search_results"]:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                dedup_search.append(r)
        self.results["search_results"] = dedup_search

        # Phase 2: Social Media Platform Verification
        self.log(f"Phase 2/3: Probing {len(platforms_to_probe)} enabled social platforms...")
        for plat in platforms_to_probe:
            if self.stop_requested:
                break
            current_step += 1
            self.progress_cb(current_step, total_steps, f"Checking {plat['name']}...")
            self.log(f"Probing platform: {plat['name']}...")
            prof = self.probe_social_profile(plat, target)
            if prof:
                self.results["social_profiles"].append(prof)
            time.sleep(random.uniform(self.min_delay * 0.75, self.max_delay * 0.85))

        # Phase 3: Domain & DNS Reconnaissance
        self.log(f"Phase 3/3: Probing domain names and DNS records ({len(self.domain_tlds)} TLDs)...")
        clean_target = re.sub(r'[^a-zA-Z0-9-]', '', target.lower())
        for tld in self.domain_tlds:
            if self.stop_requested:
                break
            current_step += 1
            domain = f"{clean_target}{tld}"
            self.progress_cb(current_step, total_steps, f"Probing DNS: {domain}...")
            dom_res = self.probe_domain(domain)
            if dom_res:
                self.results["domains"].append(dom_res)
            time.sleep(max(0.1, self.min_delay * 0.4))

        # Phase 4: Intelligence & Blueprint Synthesis
        self.log("Phase 4/4: Synthesizing business profile, developer roadmap, and brand clearance...")
        self.progress_cb(total_steps, total_steps, "Synthesizing Intelligence...")
        try:
            from intelligence_synthesizer import synthesize_intelligence
            intelligence = synthesize_intelligence(target, self.results)
            self.results["intelligence"] = intelligence

            bp = intelligence.get("business_profile", {})
            bc = intelligence.get("brand_clearance", {})
            dr = intelligence.get("digital_roadmap", {})

            self.log(f"[Synthesis] Brand Clearance Score: {bc.get('uniqueness_score', 0)}/100 ({bc.get('clearance_rating', '')})")
            self.log(f"[Synthesis] Operating Base: {bp.get('operating_base', 'Undetected')}")
            self.log(f"[Synthesis] Primary Contact: {bp.get('primary_contact', 'N/A')}")
            self.log(f"[Synthesis] Digital Roadmap: {len(dr.get('recommended_platform_modules', []))} platform modules recommended.")
        except Exception as syn_err:
            self.log(f"[Synthesis] Notice: {syn_err}")

        elapsed = round(time.time() - start_time, 2)
        self.progress_cb(total_steps, total_steps, "Expedition Complete!")
        self.log(f"=== Expedition Complete in {elapsed}s ===")
        active_socials = len([p for p in self.results['social_profiles'] if p.get('exists')])
        reg_domains = len([d for d in self.results['domains'] if d.get('is_registered')])
        self.log(f"Discovered: {len(self.results['search_results'])} search links, "
                 f"{active_socials} active social profiles, "
                 f"{reg_domains} registered domains, "
                 f"{len(self.results['entities']['phones'])} phone numbers, "
                 f"{len(self.results['entities']['emails'])} emails.")

        # Auto-export if enabled in settings
        if self.settings.get("auto_export_all", False):
            try:
                from exporters import export_all_formats
                export_dir = self.settings.get("export_dir", "artifacts/expeditions")
                if export_dir:
                    exported = export_all_formats(self.results, export_dir)
                    self.log(f"[Auto-Export] Generated files in: {export_dir}")
            except Exception as exp_err:
                self.log(f"[Auto-Export] Warning: {exp_err}")

        return self.results
