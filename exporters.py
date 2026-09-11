"""
ExpedUP Exporters - Intelligence Dossier & Data Exporters
Outputs findings into Markdown Dossiers, JSON, and CSV formats.
"""

import os
import json
import csv
from typing import Dict


def generate_markdown_dossier(data: Dict) -> str:
    """Generate a clean, publication-ready Markdown dossier from expedition data."""
    target = data.get("target", "Target")
    timestamp = data.get("timestamp", "N/A")
    location = data.get("location", "Not specified")
    category = data.get("category", "Not specified")
    phone = data.get("phone", "Not specified")

    search_res = data.get("search_results", [])
    social_res = [s for s in data.get("social_profiles", []) if s.get("exists")]
    domains = [d for d in data.get("domains", []) if d.get("is_registered")]
    entities = data.get("entities", {})

    phones = list(entities.get("phones", []))
    emails = list(entities.get("emails", []))
    mentions = list(entities.get("mentions", []))
    hashtags = list(entities.get("hashtags", []))

    md = []
    md.append(f"# ExpedUP Intelligence Dossier — {target}")
    md.append(f"**Generated:** {timestamp} | **Engine:** ExpedUP v1.0.0\n")
    md.append("---")
    md.append("## 1. Target Overview & Anchors")
    md.append(f"- **Target Keyword / Name:** `{target}`")
    md.append(f"- **Geographic Anchor:** `{location}`")
    md.append(f"- **Industry / Category:** `{category}`")
    md.append(f"- **Seed Contact Anchor:** `{phone}`\n")

    md.append("---")
    md.append("## 2. Executive Reconnaissance Snapshot")
    md.append("| Metric | Count |")
    md.append("|---|---|")
    md.append(f"| **Active Social Profiles** | {len(social_res)} |")
    md.append(f"| **Registered Web Domains** | {len(domains)} |")
    md.append(f"| **Harvested Search Results** | {len(search_res)} |")
    md.append(f"| **Discovered Phone Numbers** | {len(phones)} |")
    md.append(f"| **Discovered Email Addresses** | {len(emails)} |")
    md.append(f"| **Detected Social Mentions** | {len(mentions)} |")
    md.append(f"| **Related Hashtags** | {len(hashtags)} |\n")

    md.append("---")
    md.append("## 3. Verified Social Media & Digital Footprints")
    if social_res:
        md.append("| Platform | Category | URL | Title / Description |")
        md.append("|---|---|---|---|")
        for s in social_res:
            p_name = s.get("platform", "")
            p_cat = s.get("category", "")
            p_url = s.get("url", "")
            p_desc = (s.get("title", "") + " " + s.get("description", "")).strip().replace("\n", " ")[:140]
            md.append(f"| **{p_name}** | {p_cat} | [{p_url}]({p_url}) | {p_desc} |")
    else:
        md.append("_No verified active social profiles detected for this handle._")
    md.append("\n")

    md.append("---")
    md.append("## 4. Discovered Web Index & Search Results")
    if search_res:
        for idx, item in enumerate(search_res[:30], 1):
            title = item.get("title", "No Title")
            url = item.get("url", "#")
            snip = item.get("snippet", "No snippet available.")
            engine = item.get("engine", "Search Engine")
            md.append(f"### {idx}. {title}")
            md.append(f"- **URL:** [{url}]({url})")
            md.append(f"- **Source:** {engine}")
            md.append(f"- **Snippet:** > {snip}\n")
    else:
        md.append("_No direct web search snippets indexed._\n")

    md.append("---")
    md.append("## 5. Harvested Entities & Contact Intelligence")
    md.append("### Phone Numbers")
    if phones:
        for p in phones:
            md.append(f"- Phone: `{p}`")
    else:
        md.append("_No phone numbers discovered._")

    md.append("\n### Email Addresses")
    if emails:
        for e in emails:
            md.append(f"- Email: `{e}`")
    else:
        md.append("_No email addresses discovered._")

    md.append("\n### Key Mentions & Collaborators")
    if mentions:
        md.append(", ".join([f"`{m}`" for m in mentions[:25]]))
    else:
        md.append("_No social mentions detected._")

    md.append("\n### Recurring Hashtags & Tags")
    if hashtags:
        md.append(", ".join([f"`{h}`" for h in hashtags[:25]]))
    else:
        md.append("_No hashtags detected._")

    md.append("\n\n---")
    md.append("## 6. Domain & DNS Status")
    if domains:
        md.append("| Domain | Resolved IP | Status Code | Web Title |")
        md.append("|---|---|---|---|")
        for d in domains:
            d_name = d.get("domain", "")
            d_ip = d.get("resolved_ip", "N/A")
            d_code = d.get("status_code", 0)
            d_title = d.get("title", "").strip().replace("\n", " ")[:60]
            md.append(f"| `{d_name}` | `{d_ip}` | {d_code or 'Down'} | {d_title} |")
    else:
        md.append("_No matching registered web domains found for standard TLDs._")

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
    """Save search and social discoveries to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Name / Title", "URL / Value", "Detail / Snippet"])

        for s in data.get("social_profiles", []):
            if s.get("exists"):
                writer.writerow(["Social Profile", s.get("platform"), s.get("url"), s.get("description", "")])

        for r in data.get("search_results", []):
            writer.writerow(["Search Result", r.get("title"), r.get("url"), r.get("snippet", "")])

        entities = data.get("entities", {})
        for p in entities.get("phones", []):
            writer.writerow(["Phone Number", p, "", "Discovered contact"])
        for e in entities.get("emails", []):
            writer.writerow(["Email Address", e, "", "Discovered contact"])

    return output_path


def export_all_formats(data: Dict, output_dir: str = "artifacts/expeditions") -> Dict[str, str]:
    """Export expedition findings into Markdown, JSON, and CSV simultaneously."""
    import re
    import time

    target = data.get("target", "Target")
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target).strip('_') or "expedition"
    stamp = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)

    md_path = os.path.join(output_dir, f"ExpedUP_{clean_name}_{stamp}.md")
    json_path = os.path.join(output_dir, f"ExpedUP_{clean_name}_{stamp}.json")
    csv_path = os.path.join(output_dir, f"ExpedUP_{clean_name}_{stamp}.csv")

    export_markdown_file(data, md_path)
    export_json_file(data, json_path)
    export_csv_file(data, csv_path)

    return {
        "markdown": os.path.abspath(md_path),
        "json": os.path.abspath(json_path),
        "csv": os.path.abspath(csv_path)
    }

