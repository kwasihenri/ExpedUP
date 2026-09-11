"""
ExpedUP - Entry Point & Application Launcher
Supports both rich interactive CustomTkinter desktop GUI and headless CLI execution.
"""

import os
import sys
import argparse
import time

from config import (
    APP_NAME, APP_SUBTITLE, VERSION, DEFAULT_EXPORT_DIR
)
from expedup_engine import ExpedUPEngine
from exporters import export_all_formats, generate_markdown_dossier


def run_cli(args):
    """Run headless command-line expedition."""
    target = args.target
    location = args.location or ""
    category = args.category or ""
    phone = args.phone or ""
    deep_level = "Deep" if args.deep else "Standard"

    if not target:
        print("[!] Error: Target is required. Use --target <name_or_brand>.")
        sys.exit(1)

    print("=" * 65)
    print(f"  {APP_NAME} v{VERSION} — CLI Reconnaissance Mode")
    print(f"  {APP_SUBTITLE}")
    print("=" * 65)
    print(f"Target: {target}")
    if location:
        print(f"Location: {location}")
    if category:
        print(f"Category: {category}")
    if phone:
        print(f"Contact Anchor: {phone}")
    print(f"Depth: {deep_level}")
    print("-" * 65)

    def log_cb(msg):
        print(msg)

    def progress_cb(curr, tot, desc):
        print(f"[{curr}/{tot}] {desc}")

    engine = ExpedUPEngine(log_cb=log_cb, progress_cb=progress_cb)
    results = engine.run_expedition(
        target=target,
        location=location,
        category=category,
        phone=phone,
        deep_level=deep_level
    )

    print("\n" + "=" * 65)
    print("  EXECUTIVE SUMMARY & RECON COUNTERS")
    print("=" * 65)
    print(f"Total Web Links:        {len(results.get('search_results', []))}")
    print(f"Active Social Profiles: {len([p for p in results.get('social_profiles', []) if p.get('exists')])}")
    print(f"Registered Domains:     {len([d for d in results.get('domains', []) if d.get('is_registered')])}")
    print(f"Discovered Phones:      {len(results.get('entities', {}).get('phones', []))}")
    print(f"Discovered Emails:      {len(results.get('entities', {}).get('emails', []))}")
    print(f"Mentions & Hashtags:    {len(results.get('entities', {}).get('mentions', [])) + len(results.get('entities', {}).get('hashtags', []))}")

    intel = results.get("intelligence", {})
    bc = intel.get("brand_clearance", {})
    bp = intel.get("business_profile", {})
    dr = intel.get("digital_roadmap", {})

    print("\n" + "=" * 65)
    print("  SYNTHESIZED INTELLIGENCE (CORE FUNCTIONALITY)")
    print("=" * 65)
    print(f"Brand Clearance Score:  {bc.get('uniqueness_score', 0)}/100 ({bc.get('clearance_rating', '')})")
    print(f"Verdict:                {bc.get('verdict', '')}")
    print(f"Operating Base:         {bp.get('operating_base', 'Undetected')}")
    print(f"Mobility Model:         {bp.get('mobility_model', '')}")
    print(f"Primary Contact:        {bp.get('primary_contact', 'N/A')}")
    srv_list = [s.get('service', '') for s in bp.get('services', [])]
    print(f"Identified Services:    {', '.join(srv_list) if srv_list else 'General Commercial'}")
    print(f"Digital Blueprint:      {len(dr.get('recommended_platform_modules', []))} platform modules recommended")

    if args.export_all:
        out_dir = args.output or DEFAULT_EXPORT_DIR
        paths = export_all_formats(results, out_dir)
        print("\n" + "-" * 65)
        print(f"[✓] Artifacts saved to: {out_dir}")
        print(f"    - Markdown: {paths['markdown']}")
        print(f"    - JSON:     {paths['json']}")
        print(f"    - CSV:      {paths['csv']}")
        print("-" * 65)


def main():
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} — {APP_SUBTITLE}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--cli", action="store_true", help="Launch in headless CLI mode instead of GUI.")
    parser.add_argument("--target", type=str, help="Target name, handle, brand or keyword.")
    parser.add_argument("--location", type=str, help="Geographic anchor (e.g. 'London, UK').")
    parser.add_argument("--category", type=str, help="Industry / category anchor (e.g. 'Logistics').")
    parser.add_argument("--phone", type=str, help="Seed phone number (e.g. '+44 20 7946 0919').")
    parser.add_argument("--deep", action="store_true", help="Execute multi-engine deep search (DuckDuckGo + Bing).")
    parser.add_argument("--export-all", action="store_true", help="Export Markdown, JSON, and CSV upon completion.")
    parser.add_argument("--output", type=str, default=DEFAULT_EXPORT_DIR, help="Custom export output directory.")

    args = parser.parse_args()

    # Ensure artifacts directory exists
    os.makedirs(DEFAULT_EXPORT_DIR, exist_ok=True)

    if args.cli or args.target:
        run_cli(args)
    else:
        from gui import run_gui
        run_gui()



if __name__ == "__main__":
    main()
