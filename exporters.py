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
    md.append(f"| **Identified Contacts** | {len(phones)} phone(s), {len(emails)} email(s) |\n")

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


def export_all_formats(data: Dict, output_dir: str = "artifacts/expeditions") -> Dict[str, str]:
    """Export expedition findings into Markdown, JSON, and CSV simultaneously."""
    clean_target = re.sub(r'[^a-zA-Z0-9_]', '', data.get("target", "expedition")).lower()
    ts = time.strftime("%Y%m%d_%H%M%S")
    base_name = f"ExpedUP_{clean_target}_{ts}"

    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, f"{base_name}.md")
    json_path = os.path.join(output_dir, f"{base_name}.json")
    csv_path = os.path.join(output_dir, f"{base_name}.csv")

    export_markdown_file(data, md_path)
    export_json_file(data, json_path)
    export_csv_file(data, csv_path)

    return {
        "markdown": os.path.abspath(md_path),
        "json": os.path.abspath(json_path),
        "csv": os.path.abspath(csv_path)
    }


