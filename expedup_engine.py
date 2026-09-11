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

# Configure permissive SSL context for reconnaissance
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


class ExpedUPEngine:
    def __init__(self, log_cb: Optional[Callable[[str], None]] = None,
                 progress_cb: Optional[Callable[[int, int, str], None]] = None,
                 result_cb: Optional[Callable[[str, dict], None]] = None):
        self.log_cb = log_cb or (lambda msg: None)
        self.progress_cb = progress_cb or (lambda c, t, s: None)
        self.result_cb = result_cb or (lambda cat, item: None)
        self.stop_requested = False

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
        """Return headers with a randomized modern user agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

    # ---------------------------------------------------------
    # 1. Search Engine Probing (DuckDuckGo Lite, Bing, Yahoo)
    # ---------------------------------------------------------
    def search_duckduckgo_lite(self, query: str) -> List[dict]:
        """Perform search query via DuckDuckGo Lite."""
        if self.stop_requested:
            return []

        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": query}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self.get_headers())
        results = []

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                snippets = re.findall(r'<td class="result-snippet">(.*?)</td>', html, re.DOTALL)
                links = re.findall(r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)

                for i in range(min(len(links), len(snippets))):
                    href, title = links[i]
                    if "uddg=" in href:
                        m_u = re.search(r"uddg=([^&]+)", href)
                        if m_u:
                            href = urllib.parse.unquote(m_u.group(1))
                    
                    snip = re.sub(r"<[^>]+>", "", snippets[i]).strip()
                    title = re.sub(r"<[^>]+>", "", title).strip()

                    if href and not href.startswith("/"):
                        item = {
                            "engine": "DuckDuckGo",
                            "query": query,
                            "title": title,
                            "url": href,
                            "snippet": snip
                        }
                        results.append(item)
                        self.harvest_entities(f"{title} {snip}")
                        self.result_cb("search", item)

        except Exception as e:
            self.log(f"DDG Lite error on '{query}': {e}")

        return results

    def search_bing(self, query: str) -> List[dict]:
        """Perform search query via Bing."""
        if self.stop_requested:
            return []

        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=self.get_headers())
        results = []

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                blocks = html.split('<li class="b_algo"')
                for b in blocks[1:]:
                    m_title = re.search(r'<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', b, re.DOTALL)
                    href = m_title.group(1) if m_title else ""
                    title = re.sub(r"<[^>]+>", "", m_title.group(2)) if m_title else ""

                    m_snip = re.search(r'<div class="b_caption">.*?<p[^>]*>(.*?)</p>', b, re.DOTALL)
                    snip = re.sub(r"<[^>]+>", "", m_snip.group(1)) if m_snip else ""

                    if href and title:
                        item = {
                            "engine": "Bing",
                            "query": query,
                            "title": title.strip(),
                            "url": href.strip(),
                            "snippet": snip.strip()
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
        """Probe platform URL for target presence and metadata."""
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

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as resp:
                status = resp.getcode()
                html = resp.read().decode("utf-8", errors="ignore")

                # Extract title
                m_t = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                title = m_t.group(1).strip() if m_t else ""

                # Extract OpenGraph tags
                m_ot = re.search(r'<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']*)["']', html, re.IGNORECASE)
                og_title = m_ot.group(1).strip() if m_ot else ""

                m_od = re.search(r'<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']*)["']', html, re.IGNORECASE)
                og_desc = m_od.group(1).strip() if m_od else ""

                m_oi = re.search(r'<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']*)["']', html, re.IGNORECASE)
                og_image = m_oi.group(1).strip() if m_oi else ""

                if not og_desc:
                    m_d = re.search(r'<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']', html, re.IGNORECASE)
                    og_desc = m_d.group(1).strip() if m_d else ""

                self.harvest_entities(f"{title} {og_title} {og_desc}")

        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            status = 0

        # Determine existence confidence
        exists = status in [200, 301, 302, 307] and "not found" not in title.lower() and "404" not in title.lower()

        profile = {
            "platform": platform["name"],
            "category": platform["category"],
            "url": url,
            "status": status,
            "exists": exists,
            "title": title or og_title,
            "description": og_desc,
            "image": og_image
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

        if ip:
            url = f"https://{domain_name}"
            req = urllib.request.Request(url, headers=self.get_headers())
            try:
                with urllib.request.urlopen(req, context=SSL_CTX, timeout=8) as resp:
                    http_code = resp.getcode()
                    html = resp.read(20480).decode("utf-8", errors="ignore")
                    m_t = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
                    title = m_t.group(1).strip() if m_t else ""
                    self.harvest_entities(f"{title} {html}")
            except Exception:
                http_code = 0

        res = {
            "domain": domain_name,
            "resolved_ip": ip,
            "is_registered": ip is not None,
            "status_code": http_code,
            "title": title
        }

        if ip is not None:
            self.result_cb("domain", res)

        return res

    # ---------------------------------------------------------
    # 4. Intelligence & Entity Harvesting (Regex)
    # ---------------------------------------------------------
    def harvest_entities(self, text: str):
        """Extract phone numbers, emails, mentions, and hashtags."""
        if not text:
            return

        # Phone numbers (international and regional formats)
        phones = re.findall(r'(?:\+?\d{1,3}[-\s.]?)?\(?\d{2,4}\)?[-\s.]?\d{3}[-\s.]?\d{3,4}', text)
        for p in phones:
            cleaned = re.sub(r'[^\d+]', '', p)
            if 8 <= len(cleaned) <= 15:
                self.results["entities"]["phones"].add(p.strip())

        # Emails
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        for e in emails:
            if not any(e.lower().endswith(x) for x in [".png", ".jpg", ".jpeg", ".webp"]):
                self.results["entities"]["emails"].add(e.lower().strip())

        # Mentions (@handle)
        mentions = re.findall(r'@[a-zA-Z0-9_.-]{3,30}', text)
        for m in mentions:
            self.results["entities"]["mentions"].add(m.strip())

        # Hashtags (#hashtag)
        hashtags = re.findall(r'#[a-zA-Z0-9_]{3,35}', text)
        for h in hashtags:
            self.results["entities"]["hashtags"].add(h.strip())

    # ---------------------------------------------------------
    # 5. Master Expedition Runner
    # ---------------------------------------------------------
    def run_expedition(self, target: str, location: str = "", category: str = "",
                       phone: str = "", deep_level: str = "Standard") -> dict:
        """Run the complete multi-source expedition pipeline."""
        self.stop_requested = False
        start_time = time.time()
        self.results["target"] = target
        self.results["location"] = location
        self.results["category"] = category
        self.results["phone"] = phone
        self.results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        self.log(f"=== Starting ExpedUP Expedition for: '{target}' ===")
        if location:
            self.log(f"Location anchor: {location}")
        if category:
            self.log(f"Category anchor: {category}")
        if phone:
            self.log(f"Contact anchor: {phone}")

        # Build query matrix
        queries = [
            target,
            f'"{target}"'
        ]
        if location:
            queries.extend([f"{target} {location}", f'"{target}" "{location}"'])
        if category:
            queries.extend([f"{target} {category}", f'"{target}" {category}'])
        if phone:
            queries.extend([f'"{phone}"', f"{target} {phone}"])

        # Social dorks
        queries.extend([
            f'site:instagram.com "{target}"',
            f'site:tiktok.com "{target}"',
            f'site:facebook.com "{target}"',
            f'site:linkedin.com "{target}"'
        ])

        total_steps = len(queries) + len(SOCIAL_PLATFORMS) + len(DOMAIN_TLDS)
        current_step = 0

        # Phase 1: Search Engine Crawling
        self.log(f"Phase 1/3: Launching search engine queries ({len(queries)} probes)...")
        for q in queries:
            if self.stop_requested:
                break
            current_step += 1
            self.progress_cb(current_step, total_steps, f"Searching: {q[:30]}...")
            self.log(f"Probing search index: {q}")

            ddg_res = self.search_duckduckgo_lite(q)
            self.results["search_results"].extend(ddg_res)
            time.sleep(random.uniform(1.0, 1.8))

            if deep_level == "Deep":
                bing_res = self.search_bing(q)
                self.results["search_results"].extend(bing_res)
                time.sleep(random.uniform(1.0, 1.5))

        # Deduplicate search results
        seen_urls = set()
        dedup_search = []
        for r in self.results["search_results"]:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                dedup_search.append(r)
        self.results["search_results"] = dedup_search

        # Phase 2: Social Media Platform Verification
        self.log(f"Phase 2/3: Probing {len(SOCIAL_PLATFORMS)} social media platforms...")
        for plat in SOCIAL_PLATFORMS:
            if self.stop_requested:
                break
            current_step += 1
            self.progress_cb(current_step, total_steps, f"Checking {plat['name']}...")
            self.log(f"Probing platform: {plat['name']}...")
            prof = self.probe_social_profile(plat, target)
            if prof:
                self.results["social_profiles"].append(prof)
            time.sleep(random.uniform(0.6, 1.2))

        # Phase 3: Domain & DNS Reconnaissance
        self.log(f"Phase 3/3: Probing domain names and DNS records...")
        clean_target = re.sub(r'[^a-zA-Z0-9-]', '', target.lower())
        for tld in DOMAIN_TLDS:
            if self.stop_requested:
                break
            current_step += 1
            domain = f"{clean_target}{tld}"
            self.progress_cb(current_step, total_steps, f"Probing DNS: {domain}...")
            dom_res = self.probe_domain(domain)
            if dom_res:
                self.results["domains"].append(dom_res)
            time.sleep(0.3)

        elapsed = round(time.time() - start_time, 2)
        self.progress_cb(total_steps, total_steps, "Expedition Complete!")
        self.log(f"=== Expedition Complete in {elapsed}s ===")
        self.log(f"Discovered: {len(self.results['search_results'])} search links, "
                 f"{len([p for p in self.results['social_profiles'] if p.get('exists')])} active social profiles, "
                 f"{len([d for d in self.results['domains'] if d.get('is_registered')])} registered domains, "
                 f"{len(self.results['entities']['phones'])} phone numbers, "
                 f"{len(self.results['entities']['emails'])} emails.")

        return self.results
