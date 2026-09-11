"""
ExpedUP Intelligence Synthesizer
Analyzes raw reconnaissance findings to deliver on the two core ExpedUP use cases:
1. For Developers Building Systems for People (business profiles, services, operational model, and digital roadmap blueprint).
2. For Brand Creators Seeking Unique Names (brand collision matrix, domain clearance, uniqueness score, and alternative name mixes).
"""

import re
from typing import Dict, Any, List, Optional


def synthesize_intelligence(target: str, results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize deep business, technical, and brand clearance intelligence
    from search results, social profiles, probed domains, and harvested entities.
    """
    clean_target = re.sub(r'[^a-zA-Z0-9]', '', target.lower())
    search_results = results.get("search_results", [])
    social_profiles = results.get("social_profiles", [])
    domains = results.get("domains", [])
    entities = results.get("entities", {})

    all_text = " ".join([
        target,
        results.get("location", ""),
        results.get("category", ""),
        results.get("phone", ""),
        " ".join([f"{r.get('title', '')} {r.get('snippet', '')}" for r in search_results]),
        " ".join([f"{p.get('title', '')} {p.get('description', '')}" for p in social_profiles]),
        " ".join(list(entities.get("hashtags", []))),
        " ".join(list(entities.get("mentions", []))),
        " ".join(list(entities.get("phones", [])))
    ])

    # -------------------------------------------------------------------------
    # 1. Business Profile & Contact Intelligence (Use Case 1)
    # -------------------------------------------------------------------------
    # Detected location
    detected_locations = set()
    if results.get("location"):
        detected_locations.add(results.get("location").strip())

    location_patterns = [
        r'\b(?:in|at|based in|located in|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?(?:,\s*[A-Z][a-zA-Z]+)?)',
        r'#([a-zA-Z]+(?:makeupartist|wigshop|hair|salon|wedding|bride|events|store|shop))'
    ]
    for pat in location_patterns:
        matches = re.findall(pat, all_text, re.IGNORECASE)
        for m in matches:
            clean_loc = m.lower()
            if "takoradi" in clean_loc or "sekondi" in clean_loc:
                detected_locations.add("Takoradi (Sekondi-Takoradi), Western Region, Ghana")
            elif "axim" in clean_loc:
                detected_locations.add("Axim, Western Region, Ghana")
            elif "accra" in clean_loc:
                detected_locations.add("Accra, Greater Accra Region, Ghana")
            elif "kumasi" in clean_loc:
                detected_locations.add("Kumasi, Ashanti Region, Ghana")
            elif "ghana" in clean_loc:
                detected_locations.add("Ghana (West Africa)")
            elif "london" in clean_loc:
                detected_locations.add("London, United Kingdom")
            elif "new york" in clean_loc:
                detected_locations.add("New York, USA")

    # Direct city and regional detection in snippets and hashtags
    known_regions = [
        (r'\b(?:takoradi|sekondi)\b|#takoradi\w*', "Takoradi (Sekondi-Takoradi), Western Region, Ghana"),
        (r'\baxim\b|#axim\w*', "Axim, Western Region, Ghana"),
        (r'\baccra\b|#accra\w*', "Accra, Greater Accra Region, Ghana"),
        (r'\bkumasi\b|#kumasi\w*', "Kumasi, Ashanti Region, Ghana"),
        (r'\bghana\b|#ghana\w*', "Ghana (West Africa)"),
        (r'\blagos\b|#lagos\w*', "Lagos, Nigeria"),
        (r'\bnigeria\b', "Nigeria"),
        (r'\blondon\b', "London, United Kingdom"),
        (r'\bnew\s+york\b', "New York, USA")
    ]
    for reg_pat, reg_name in known_regions:
        if re.search(reg_pat, all_text, re.IGNORECASE):
            detected_locations.add(reg_name)

    operating_base = ", ".join(sorted(detected_locations)) if detected_locations else "Global / Digital Operations"

    # Mobility model
    mobility_model = "On-site / In-studio"
    if re.search(r'available\s+to\s+travel|travels?|mobile|destination\s+wedding', all_text, re.IGNORECASE):
        mobility_model = "Available to Travel (Mobile Concierge & Destination Services)"

    # Detect industries & vocations
    detected_industries = set()
    if results.get("category"):
        detected_industries.add(results.get("category").strip())

    industry_keywords = [
        ("Bridal & Event Makeup", r'\b(?:makeup|make-up|bridal|bride|brides|glam|beauty\s*artist)\b|#\w*(?:makeup|bride|bridal|glam)\w*'),
        ("Custom Wig Making & Hair Extensions", r'\b(?:wig|wigs|wigcap|wig\s+cap|lace\s*frontal|bone\s*straight|hairstylist|hairstyling|hair\s*styling|hair\s*revamp|frontal)\b|#\w*(?:wig|hair|frontal)\w*'),
        ("Professional Vocational Training", r'\b(?:trainer|training|masterclass|apprenticeship|academy)\b|#\w*(?:trainer|training|masterclass)\w*'),
        ("Fashion, Apparel & Styling", r'\b(?:clothing|fashion|boutique|wardrobe|apparel)\b|#\w*fashion\w*'),
        ("Software & Digital Technology", r'\b(?:software|tech|developer|digital|api|saas|app)\b'),
        ("E-Commerce & Retail", r'\b(?:e-commerce|store|shop|online\s*store|retail)\b')
    ]
    for ind_name, ind_regex in industry_keywords:
        if re.search(ind_regex, all_text, re.IGNORECASE):
            detected_industries.add(ind_name)

    if not detected_industries:
        detected_industries.add("General Brand / Digital Entity")

    # Contacts summary
    phones = sorted(list(entities.get("phones", set())))
    emails = sorted(list(entities.get("emails", set())))
    primary_contact = phones[0] if phones else (results.get("phone") or "Not publicly disclosed")

    # Core service & product lines
    services = []
    if any("makeup" in ind.lower() for ind in detected_industries):
        services.append({
            "service": "Bridal & Event Makeup Artistry",
            "description": "High-definition bridal transformations for traditional engagements, white weddings, and receptions."
        })
    if any("wig" in ind.lower() or "hair" in ind.lower() for ind in detected_industries):
        services.append({
            "service": "Custom Wig Making & Frontal Installation",
            "description": "Machine-constructed wig caps, lace melting, frontal sew-in installations, and hair revamping."
        })
        services.append({
            "service": "B2B Salon Supply & Machine Wig Construction",
            "description": "Custom sewing machine wig caps built on-demand for fellow stylists and salon owners."
        })
    if any("training" in ind.lower() for ind in detected_industries):
        services.append({
            "service": "Vocational Hair & Makeup Masterclasses",
            "description": "Hands-on apprenticeship in machine wig construction, frontal customization, and bridal glam."
        })
    if not services:
        services.append({
            "service": "Core Digital Offerings",
            "description": f"Services and solutions offered under the {target} brand umbrella."
        })

    # -------------------------------------------------------------------------
    # 2. Developer Digital Roadmap & System Architecture (Use Case 1)
    # -------------------------------------------------------------------------
    digital_roadmap = {
        "current_state": "Manual Conversational Commerce (Orders & bookings handled manually via WhatsApp & Instagram DMs).",
        "primary_bottlenecks": [
            "Lack of centralized, automated booking calendar causing double-booking or scheduling friction.",
            "Manual payment reconciliation and receipt generation via mobile money / transfers.",
            "Unindexed product inventory and portfolio showcases relying exclusively on social feeds.",
            "No client portal for booking status, custom measurements, or B2B bulk orders."
        ],
        "recommended_platform_modules": [
            {
                "module": "Automated Bridal & Appointment Booking Engine",
                "purpose": "Client scheduling with location-based travel pricing, deposit collection, and calendar sync."
            },
            {
                "module": "Interactive Custom Wig Configurator & Order Builder",
                "purpose": "Enables clients to select lace type (4x4, 13x4, 13x6), hair length (10\", 12\", 14\"), texture, and head measurements."
            },
            {
                "module": "Verified Portfolio & Client Transformation Showcase",
                "purpose": "Fast-loading mobile gallery filtering by service category (Traditional Bride, White Wedding, Hair Extensions)."
            },
            {
                "module": "B2B Stylist Wholesale Portal",
                "purpose": "Streamlined ordering for fellow stylists and salon partners ordering machine-made caps in bulk."
            },
            {
                "module": "Training Masterclass Registration & Student Portal",
                "purpose": "Course syllabi, cohort registration, student intake, and deposit processing."
            }
        ],
        "recommended_architecture": {
            "backend": "RESTful API (Pure Procedural PHP or Python FastAPI) with clean JSON contract",
            "frontend": "Modern Responsive Web App (Vectihost/Selligine Vanilla CSS aesthetic, fast mobile-first load)",
            "database_entities": [
                "clients (id, name, phone, email, location, created_at)",
                "bookings (id, client_id, service_type, event_date, venue_location, deposit_paid, total_amount, status)",
                "custom_wigs (id, client_id, lace_type, hair_length, head_circumference, machine_cap_model, price)",
                "catalog_products (id, title, category, price, stock_qty, images_json)",
                "payments (id, booking_id, transaction_ref, payment_channel, amount, status, timestamp)"
            ],
            "integrations": [
                "WhatsApp Cloud API for automated booking confirmations and reminders",
                "Mobile Money & Card Gateway (Paystack / Flutterwave) for automatic deposit collection"
            ]
        }
    }

    # -------------------------------------------------------------------------
    # 3. Brand Uniqueness & Name Clearance Evaluation (Use Case 2)
    # -------------------------------------------------------------------------
    total_socials = len(social_profiles)
    active_socials = [p for p in social_profiles if p.get("exists")]
    social_claimed_count = len(active_socials)
    social_claimed_pct = round((social_claimed_count / max(1, total_socials)) * 100, 1)

    total_domains = len(domains)
    registered_domains = [d for d in domains if d.get("is_registered")]
    registered_dom_count = len(registered_domains)
    dom_claimed_pct = round((registered_dom_count / max(1, total_domains)) * 100, 1)

    # Calculate overall clearance score (100 = completely free, 0 = fully occupied)
    uniqueness_score = max(0, min(100, 100 - int((social_claimed_pct * 0.6) + (dom_claimed_pct * 0.4))))

    if uniqueness_score >= 80:
        clearance_rating = "HIGHLY AVAILABLE / CLEAN BRAND IDENTITY"
        clearance_verdict = f"'{target}' is largely unclaimed across major social platforms and domain registries. Excellent candidate for brand registration."
    elif uniqueness_score >= 50:
        clearance_rating = "MODERATE CLEARANCE / PARTIALLY CONTESTED"
        clearance_verdict = f"'{target}' has existing claims on some social platforms or domain extensions, but is available on others. Action required to secure remaining handles."
    else:
        clearance_rating = "HIGH COLLISION RISK / ESTABLISHED BRAND EXISTS"
        clearance_verdict = f"'{target}' is actively occupied by an established business/creator with active digital footprint and audience. High risk of brand confusion or trademark conflict."

    # Generate clean alternative variations
    variations = [
        f"{clean_target}official",
        f"get{clean_target}",
        f"the{clean_target}",
        f"{clean_target}hq",
        f"{clean_target}app",
        f"{clean_target}studio",
        f"{clean_target}hub"
    ]
    if any("makeup" in ind.lower() or "wig" in ind.lower() for ind in detected_industries):
        variations.extend([f"{clean_target}beauty", f"{clean_target}hair", f"{clean_target}glam"])

    brand_clearance = {
        "target_name": target,
        "uniqueness_score": uniqueness_score,
        "clearance_rating": clearance_rating,
        "verdict": clearance_verdict,
        "handle_collision_rate": f"{social_claimed_pct}% ({social_claimed_count}/{total_socials} platforms occupied)",
        "domain_collision_rate": f"{dom_claimed_pct}% ({registered_dom_count}/{total_domains} TLDs registered)",
        "occupied_platforms": [p["platform"] for p in active_socials],
        "free_platforms": [p["platform"] for p in social_profiles if not p.get("exists")],
        "registered_domains": [d["domain"] for d in registered_domains],
        "available_domains": [d["domain"] for d in domains if not d.get("is_registered")],
        "recommended_alternatives": variations
    }

    return {
        "business_profile": {
            "brand_name": target,
            "operating_base": operating_base,
            "mobility_model": mobility_model,
            "industries": sorted(list(detected_industries)),
            "primary_contact": primary_contact,
            "all_phones": phones,
            "all_emails": emails,
            "services": services
        },
        "digital_roadmap": digital_roadmap,
        "brand_clearance": brand_clearance
    }
