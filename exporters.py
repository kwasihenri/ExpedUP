"""
ExpedUP Exporters - Intelligence Dossier & Data Exporters
Outputs findings into Publication-Grade Markdown Dossiers, JSON, and CSV formats.
Fulfills the 2 core ExpedUP capabilities:
1. For Developers Building Systems for People (business profile, operational bottlenecks, and digital roadmap blueprint).
2. For Brand Creators Seeking Unique Names (brand collision matrix, domain clearance, uniqueness score, and alternative name mixes).
"""

import os
import json
import csv
import re
import time
from typing import Dict, Any


def generate_markdown_dossier(data: Dict[str, Any]) -> str:
    """Generate a clean, publication-ready 9-section Markdown dossier from expedition data."""
    target = data.get("target", "Target")
    timestamp = data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
    location = data.get("location", "Not specified")
    category = data.get("category", "Not specified")
    phone = data.get("phone", "Not specified")

    search_res = data.get("search_results", [])
    social_res = [s for s in data.get("social_profiles", []) if s.get("exists")]
    domains = [d for d in data.get("domains", []) if d.get("is_registered")]
    available_domains = [d for d in data.get("domains", []) if not d.get("is_registered")]
    entities = data.get("entities", {})

    phones = list(entities.get("phones", []))
    emails = list(entities.get("emails", []))
    mentions = list(entities.get("mentions", []))
    hashtags = list(entities.get("hashtags", []))

    intelligence = data.get("intelligence")
    if not intelligence:
        from intelligence_synthesizer import synthesize_intelligence
        intelligence = synthesize_intelligence(target, data)

    bp = intelligence.get("business_profile", {})
    bc = intelligence.get("brand_clearance", {})
    dr = intelligence.get("digital_roadmap", {})

    md = []
    md.append(f"# ExpedUP Intelligence Dossier — {target}")
    md.append(f"**Generated:** {timestamp} | **Engine:** ExpedUP v1.0.0 (Open Source Reconnaissance Engine)\n")
    md.append("---")

    # Section 1: Executive Overview & Brand Clearance
    score = bc.get("uniqueness_score", 0)
    score_bar = "█" * (score // 10) + "░" * (10 - (score // 10))
    md.append("## 1. Executive Reconnaissance & Brand Clearance Snapshot")
    md.append(f"**Brand Clearance & Uniqueness Score:** `{score}/100` `[{score_bar}]` — **{bc.get('clearance_rating', 'EVALUATED')}**\n")
    md.append(f"> **Verdict:** {bc.get('verdict', '')}\n")
    md.append("| Core Metric | Assessment |")
    md.append("|---|---|")
    md.append(f"| **Target Entity / Brand** | `{target}` |")
    md.append(f"| **Handle Collision Rate** | {bc.get('handle_collision_rate', 'N/A')} |")
    md.append(f"| **Domain Collision Rate** | {bc.get('domain_collision_rate', 'N/A')} |")
    md.append(f"| **Active Social Channels** | {len(social_res)} verified profiles |")
    md.append(f"| **Registered Web Domains** | {len(domains)} active TLDs |")
    md.append(f"| **Web Search Discoveries** | {len(search_res)} indexed entries |")
    md.append(f"| **Identified Contacts** | {len(phones)} phone(s), {len(emails)} email(s) |")
    if bc.get("search_collision_impact"):
        md.append(f"| **Web Footprint Collision** | `{bc.get('search_collision_impact')}` |")
        md.append(f"| **Social Collision Impact** | `{bc.get('social_collision_impact')}` |")
        md.append(f"| **Commercial Identity Collision** | `{bc.get('commercial_collision_impact')}` |")
        md.append(f"| **Domain Namespace Collision** | `{bc.get('domain_collision_impact')}` |")
    md.append("\n")

    # Section 2: Business Profile & Operational Model (Use Case 1)
    md.append("---")
    md.append("## 2. Business Profile & Operational Model")
    md.append(f"- **Brand Name:** `{bp.get('brand_name', target)}`")
    md.append(f"- **Operating Base:** `{bp.get('operating_base', 'Global / Digital Operations')}`")
    md.append(f"- **Mobility Model:** `{bp.get('mobility_model', 'On-site / In-studio')}`")
    md.append(f"- **Detected Industries:** {', '.join([f'`{ind}`' for ind in bp.get('industries', [])]) or 'General Commercial'}")
    md.append(f"- **Primary Direct Contact:** `{bp.get('primary_contact', 'Not publicly disclosed')}`")
    if phones:
        md.append(f"- **Verified Phone Numbers:** {', '.join([f'`{p}`' for p in phones])}")
    if emails:
        md.append(f"- **Discovered Emails:** {', '.join([f'`{e}`' for e in emails])}")
    md.append("\n")

    # Section 3: Core Service & Product Offerings (Use Case 1)
    md.append("---")
    md.append("## 3. Core Service & Product Lines Identified")
    services = bp.get("services", [])
    if services:
        for idx, s in enumerate(services, 1):
            md.append(f"### 3.{idx}. {s.get('service', 'Service Offering')}")
            md.append(f"{s.get('description', '')}\n")
    else:
        md.append("_No specialized service offerings detected from public profiles._\n")

    # Section 4: Developer Digital Roadmap & System Architecture (Use Case 1)
    md.append("---")
    md.append("## 4. Developer Digital Roadmap & System Architecture Blueprint")
    md.append(f"> **Current Operational State:**\n> {dr.get('current_state', 'Manual commerce workflow.')}\n")

    md.append("### 4.1. Operational Bottlenecks Identified")
    for b in dr.get("primary_bottlenecks", []):
        md.append(f"- ⚠️ **{b}**")
    md.append("\n")

    md.append("### 4.2. Recommended Platform Modules")
    md.append("| Module Name | Functional Purpose |")
    md.append("|---|---|")
    for mod in dr.get("recommended_platform_modules", []):
        md.append(f"| **{mod.get('module')}** | {mod.get('purpose')} |")
    md.append("\n")

    md.append("### 4.3. Recommended Technical Stack & Architecture")
    arch = dr.get("recommended_architecture", {})
    md.append(f"- **Backend Architecture:** `{arch.get('backend', 'RESTful API Service')}`")
    md.append(f"- **Frontend Experience:** `{arch.get('frontend', 'Modern Responsive Mobile-First App')}`")
    md.append("- **Database Entities (Schema Blueprint):**")
    for entity in arch.get("database_entities", []):
        md.append(f"  - `{entity}`")
    md.append("- **Third-Party Integrations:**")
    for integ in arch.get("integrations", []):
        md.append(f"  - 🔌 **{integ}**")
    md.append("\n")

    # Section 5: Brand Clearance & Alternative Name Mixes (Use Case 2)
    md.append("---")
    md.append("## 5. Brand Clearance & Name Collision Matrix")
    md.append("### 5.1. Handle Availability Breakdown")
    occupied = bc.get("occupied_platforms", [])
    free = bc.get("free_platforms", [])
    md.append(f"- **Occupied Platforms ({len(occupied)}):** {', '.join([f'🔴 **{p}**' for p in occupied]) if occupied else 'None (All available)'}")
    md.append(f"- **Available Platforms ({len(free)}):** {', '.join([f'🟢 **{p}**' for p in free]) if free else 'None'}\n")

    md.append("### 5.2. Domain Registration Status")
    reg_d = bc.get("registered_domains", [])
    avail_d = bc.get("available_domains", [])
    md.append(f"- **Registered Domains ({len(reg_d)}):** {', '.join([f'`{d}`' for d in reg_d]) if reg_d else 'None detected'}")
    md.append(f"- **Available Domains ({len(avail_d)}):** {', '.join([f'`{d}`' for d in avail_d]) if avail_d else 'None'}\n")

    md.append("### 5.3. Recommended Alternative Brand Mixes & Handles")
    md.append("If this brand name is contested, the following clean, collision-free variations are recommended for brand creators:\n")
    alternatives = bc.get("recommended_alternatives", [])
    if alternatives:
        md.append("| Alternative Handle / Brand Mix | Recommended Use |")
        md.append("|---|---|")
        for alt in alternatives:
            md.append(f"| `@{alt}` | Brand handle, social username, or web domain |")
    md.append("\n")

    # Section 6: Verified Social Media & Digital Footprints
    md.append("---")
    md.append("## 6. Verified Social Media & Digital Footprints")
    if social_res:
        md.append("| Platform | Category | URL | Status / Bio Snippet |")
        md.append("|---|---|---|---|")
        for s in social_res:
            p_name = s.get("platform", "")
            p_cat = s.get("category", "")
            p_url = s.get("url", "")
            desc = s.get("description", "") or s.get("title", "")
            clean_desc = desc.strip().replace("\n", " ")[:140]
            md.append(f"| **{p_name}** | {p_cat} | [{p_url}]({p_url}) | {clean_desc} |")
    else:
        md.append("_No verified active social profiles detected for this handle._")
    md.append("\n")

    # Section 7: Discovered Web Index & Search Results
    md.append("---")
    md.append("## 7. Discovered Web Index & Search Evidence")
    if search_res:
        for idx, item in enumerate(search_res[:25], 1):
            s_title = item.get("title", "No Title")
            s_url = item.get("url", "#")
            s_snip = item.get("snippet", "No snippet available.")
            s_engine = item.get("engine", "Search Engine")
            md.append(f"### 7.{idx}. {s_title}")
            md.append(f"- **URL:** [{s_url}]({s_url})")
            md.append(f"- **Source:** {s_engine}")
            md.append(f"- **Snippet:** > {s_snip}\n")
    else:
        md.append("_No direct web search snippets indexed._\n")

    # Section 8: Discovered Contact Entities
    md.append("---")
    md.append("## 8. Discovered Contact Entities & Social Graph")
    md.append("### Phone & Messaging Contacts")
    if phones:
        for p in phones:
            md.append(f"- 📱 Phone / WhatsApp: `{p}`")
    else:
        md.append("_No phone numbers discovered._")

    md.append("\n### Email Addresses")
    if emails:
        for e in emails:
            md.append(f"- ✉️ Email: `{e}`")
    else:
        md.append("_No email addresses discovered._")

    md.append("\n### Key Social Mentions")
    if mentions:
        md.append(", ".join([f"`{m}`" for m in mentions[:25]]))
    else:
        md.append("_No social mentions detected._")

    md.append("\n### Recurring Hashtags")
    if hashtags:
        md.append(", ".join([f"`{h}`" for h in hashtags[:25]]))
    else:
        md.append("_No hashtags detected._")

    # Section 9: Domain & DNS Availability Status
    md.append("\n\n---")
    md.append("## 9. Domain & DNS Availability Status")
    all_doms = data.get("domains", [])
    if all_doms:
        md.append("| Domain | Status | Resolved IP | HTTP Code | Web Page Title |")
        md.append("|---|---|---|---|---|")
        for d in all_doms:
            d_name = d.get("domain", "")
            d_is_reg = d.get("is_registered", False)
            d_status = "🔴 Registered" if d_is_reg else "🟢 Available"
            d_ip = d.get("resolved_ip") or "N/A"
            d_code = d.get("status_code") or ("-" if not d_is_reg else "Down")
            d_title = (d.get("title") or "").strip().replace("\n", " ")[:45]
            md.append(f"| `{d_name}` | {d_status} | `{d_ip}` | {d_code} | {d_title} |")
    else:
        md.append("_No domains probed._")

    md.append("\n\n---")
    md.append("_Report compiled automatically by **ExpedUP** Open Source Intelligence Probe._")

    return "\n".join(md)


def export_markdown_file(data: Dict, output_path: str) -> str:
    """Save markdown dossier to file."""
    content = generate_markdown_dossier(data)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


def export_json_file(data: Dict, output_path: str) -> str:
    """Save JSON report to file, ensuring sets are serialized as lists."""
    serializable = dict(data)
    if "entities" in serializable:
        serializable["entities"] = {
            k: list(v) if isinstance(v, set) else v
            for k, v in serializable["entities"].items()
        }
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    return output_path


def export_csv_file(data: Dict, output_path: str) -> str:
    """Save search, social, domain, and entity discoveries to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Category / Key", "Name / URL / Value", "Detail / Snippet / Status"])

        # Business Profile & Clearance
        intel = data.get("intelligence", {})
        bc = intel.get("brand_clearance", {})
        bp = intel.get("business_profile", {})
        if bc:
            writer.writerow(["Brand Clearance", "Uniqueness Score", f"{bc.get('uniqueness_score', 0)}/100", bc.get("clearance_rating", "")])
            writer.writerow(["Brand Clearance", "Verdict", target_name := data.get("target", ""), bc.get("verdict", "")])
        if bp:
            writer.writerow(["Business Profile", "Operating Base", bp.get("operating_base", ""), bp.get("mobility_model", "")])
            for s in bp.get("services", []):
                writer.writerow(["Identified Service", s.get("service", ""), "", s.get("description", "")])

        # Social profiles
        for s in data.get("social_profiles", []):
            if s.get("exists"):
                writer.writerow(["Social Profile", s.get("category", "Social"), s.get("url", ""), s.get("description", "")])

        # Search results
        for r in data.get("search_results", []):
            writer.writerow(["Search Result", r.get("engine", "Search"), r.get("url", ""), r.get("snippet", "")])

        # Domains
        for d in data.get("domains", []):
            status = "Registered" if d.get("is_registered") else "Available"
            writer.writerow(["Domain Record", status, d.get("domain", ""), f"IP: {d.get('resolved_ip')} | HTTP: {d.get('status_code')}"])

        # Harvested Entities
        entities = data.get("entities", {})
        for p in entities.get("phones", []):
            writer.writerow(["Contact Entity", "Phone / WhatsApp", p, "Harvested Phone Number"])
        for e in entities.get("emails", []):
            writer.writerow(["Contact Entity", "Email Address", e, "Harvested Email Address"])
        for m in entities.get("mentions", []):
            writer.writerow(["Contact Entity", "Social Mention", m, "Harvested Handle Mention"])
        for h in entities.get("hashtags", []):
            writer.writerow(["Contact Entity", "Hashtag", h, "Harvested Hashtag"])

    return output_path


def export_expedup_file(data: Dict, output_path: str) -> str:
    """Save full expedition bundle as a native .expedup JSON file."""
    bundle = {
        "app": "ExpedUP",
        "version": "1.0.0",
        "format": "expedition_bundle",
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "payload": data
    }
    serializable = json.dumps(bundle, indent=2, ensure_ascii=False, default=lambda o: list(o) if isinstance(o, set) else str(o))
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(serializable)
    return output_path


def load_expedition_file(filepath: str) -> Dict[str, Any]:
    """
    Load a saved expedition file (.expedup, .json, .md, .txt) into a standard ExpedUP results dict.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Expedition file not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext in [".expedup", ".json"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            raw_data = json.load(f)

        if isinstance(raw_data, dict) and "payload" in raw_data and isinstance(raw_data["payload"], dict):
            data = raw_data["payload"]
        elif isinstance(raw_data, dict):
            data = raw_data
        else:
            raise ValueError("Invalid expedition JSON structure")

        # Convert entities lists back to sets for engine consistency
        entities = data.get("entities", {})
        data["entities"] = {
            "phones": set(entities.get("phones", [])),
            "emails": set(entities.get("emails", [])),
            "mentions": set(entities.get("mentions", [])),
            "hashtags": set(entities.get("hashtags", []))
        }

        # Ensure essential keys exist
        data.setdefault("search_results", [])
        data.setdefault("social_profiles", [])
        data.setdefault("domains", [])
        return data

    elif ext in [".md", ".txt"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Parse target name from markdown header
        m_target = re.search(r"#\s*ExpedUP\s+Intelligence\s+Dossier\s*—\s*([^\n]+)", content, re.IGNORECASE)
        if not m_target:
            m_target = re.search(r"#\s*([^\n]+)", content)
        target_name = m_target.group(1).strip() if m_target else os.path.splitext(os.path.basename(filepath))[0]

        search_results = []
        social_profiles = []
        domains = []

        # 1. Parse Section 7: Web Search Results blocks
        search_blocks = re.findall(
            r'###\s*7\.\d+\.\s*(.*?)\n\s*-\s*\*\*URL:\*\*\s*(?:\[.*?\]\((.*?)\)|(https?://[^\s\)]+))\n\s*-\s*\*\*Source:\*\*\s*(.*?)\n\s*-\s*\*\*Snippet:\*\*\s*>(?:[ \t]*)(.*?)(?=\n\n|\n#|\Z)',
            content, re.DOTALL
        )
        for s_title, s_url1, s_url2, s_src, s_snip in search_blocks:
            url = (s_url1 or s_url2 or "").strip()
            search_results.append({
                "engine": s_src.strip() or "Search Engine",
                "query": target_name,
                "title": s_title.strip(),
                "url": url,
                "snippet": s_snip.strip().replace("\n> ", " ")
            })

        # 2. Parse Section 6: Verified Social Media Profiles table
        social_rows = re.findall(
            r'\|\s*\*\*(.*?)\*\*\s*\|\s*(.*?)\s*\|\s*\[.*?\]\((https?://[^\s\)]+)\)\s*\|\s*(.*?)\s*\|',
            content
        )
        for p_name, p_cat, p_url, p_desc in social_rows:
            social_profiles.append({
                "platform": p_name.strip(),
                "category": p_cat.strip() or "Social",
                "url": p_url.strip(),
                "exists": True,
                "title": p_desc.strip(),
                "description": p_desc.strip()
            })

        # 3. Parse Section 9: Domain & DNS Availability Status table
        domain_rows = re.findall(
            r'\|\s*`?([a-zA-Z0-9_.-]+\.[a-zA-Z]{2,})`?\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(\d{3})\s*\|\s*(.*?)\s*\|',
            content
        )
        for dom_name, status_str, ip_str, code_str, dom_title in domain_rows:
            is_reg = "Registered" in status_str or "Active" in status_str
            domains.append({
                "domain": dom_name.strip(),
                "is_registered": is_reg,
                "resolved_ip": ip_str.strip(),
                "status_code": int(code_str.strip()) if code_str.strip().isdigit() else 200,
                "title": dom_title.strip()
            })

        # Fallback if section parsing yielded empty search & social profiles
        if not search_results and not social_profiles:
            links = re.findall(r'\[(.*?)\]\((https?://[^\s\)]+)\)', content)
            social_domains = ["instagram.com", "tiktok.com", "threads.net", "facebook.com", "twitter.com", "x.com", "linkedin.com", "github.com", "youtube.com", "pinterest.com", "snapchat.com", "reddit.com", "medium.com", "telegram.org", "t.me", "behance.net", "soundcloud.com"]

            for title, url in links:
                is_soc = any(sd in url.lower() for sd in social_domains)
                if is_soc:
                    social_profiles.append({
                        "platform": title or "Social Profile",
                        "category": "Social",
                        "url": url,
                        "exists": True,
                        "title": title or "Verified Profile",
                        "description": "Extracted from saved markdown dossier."
                    })
                else:
                    search_results.append({
                        "engine": "Markdown Dossier",
                        "query": target_name,
                        "title": title or "Indexed Web Finding",
                        "url": url,
                        "snippet": "Extracted from saved dossier link."
                    })

        # Extract phone numbers, emails, mentions, hashtags
        phones = set(re.findall(r'\b0[1-9]\d{8}\b', content) + re.findall(r'\+?\d{1,4}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b', content))
        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content))
        mentions = set(re.findall(r'@[a-zA-Z0-9_.-]{3,30}', content))
        hashtags = set(re.findall(r'#[a-zA-Z0-9_]{3,35}', content))

        results = {
            "target": target_name,
            "location": "",
            "category": "",
            "phone": "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "queries_executed": [],
            "search_results": search_results,
            "social_profiles": social_profiles,
            "domains": [],
            "entities": {
                "phones": phones,
                "emails": emails,
                "mentions": mentions,
                "hashtags": hashtags
            }
        }

        # Synthesize intelligence for parsed markdown
        try:
            from intelligence_synthesizer import synthesize_intelligence
            results["intelligence"] = synthesize_intelligence(target_name, results)
        except Exception:
            pass

        return results

    else:
        raise ValueError(f"Unsupported file format '{ext}'. Expected .expedup, .json, .md, or .txt")


def export_all_formats(data: Dict, output_dir: str = "artifacts/expeditions") -> Dict[str, str]:
    """Export expedition findings into ExpedUP Bundle (.expedup), Markdown, JSON, and CSV simultaneously."""
    clean_target = re.sub(r'[^a-zA-Z0-9_]', '', data.get("target", "expedition")).lower()
    ts = time.strftime("%Y%m%d_%H%M%S")
    base_name = f"ExpedUP_{clean_target}_{ts}"

    os.makedirs(output_dir, exist_ok=True)
    expedup_path = os.path.join(output_dir, f"{base_name}.expedup")
    md_path = os.path.join(output_dir, f"{base_name}.md")
    json_path = os.path.join(output_dir, f"{base_name}.json")
    csv_path = os.path.join(output_dir, f"{base_name}.csv")

    export_expedup_file(data, expedup_path)
    export_markdown_file(data, md_path)
    export_json_file(data, json_path)
    export_csv_file(data, csv_path)

    return {
        "expedup": os.path.abspath(expedup_path),
        "markdown": os.path.abspath(md_path),
        "json": os.path.abspath(json_path),
        "csv": os.path.abspath(csv_path)
    }


