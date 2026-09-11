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
    active_socials = [p for p in social_profiles if p.get("exists")]
    is_virgin_brand = (len(search_results) == 0 and len(active_socials) == 0)

    # Contacts summary
    phones = sorted(list(entities.get("phones", set())))
    emails = sorted(list(entities.get("emails", set())))
    primary_contact = phones[0] if phones else (results.get("phone") or "Not publicly disclosed")

    if is_virgin_brand:
        operating_base = "Unclaimed / Pristine Digital Identity"
        mobility_model = "N/A (Brand not yet operating publicly)"
        detected_industries = ["Unoccupied Brand Name (No Digital Traces Found)"]
        primary_contact = "N/A"
        services = []

        digital_roadmap = {
            "current_state": "Unoccupied Brand Space — Pristine Digital Canvas ready for initial brand launch.",
            "primary_bottlenecks": [
                f"Brand namespace '{target}' is currently unregistered across primary web & social registries.",
                "Zero public digital presence or indexed search engine authority (virgin keyword).",
                "No primary domain, DNS infrastructure, or corporate email secured.",
                "High susceptibility to name-squatting once public brand promotion begins."
            ],
            "recommended_platform_modules": [
                {
                    "module": "Namespace Securitization & Social Handle Squat-Defense",
                    "purpose": "Reserve and protect exact-match handles (@target) across key social and developer channels (X/Twitter, Instagram, TikTok, GitHub, LinkedIn)."
                },
                {
                    "module": "Primary Domain Registration & DNS Hardening",
                    "purpose": f"Register {clean_target}.com and key regional extensions, configuring DNSSEC, Cloudflare CDN, and SSL/TLS certificates."
                },
                {
                    "module": "High-Performance Modern Web Landing Page & Lead Capture",
                    "purpose": "Deploy a clean, mobile-first responsive landing page (Vectihost/Selligine style) with early subscriber waitlist capture."
                },
                {
                    "module": "Unified Inbound Communication (Domain Email & MX Routing)",
                    "purpose": f"Provision Google Workspace or Proton business email (e.g. contact@{clean_target}.com) for professional stakeholder inquiries."
                },
                {
                    "module": "Search Engine Console Indexing & Schema Entity Registration",
                    "purpose": f"Submit XML sitemap and Schema.org Organization markup to Google Search Console and Bing Webmaster Tools to anchor '{target}'."
                }
            ],
            "recommended_architecture": {
                "backend": "RESTful API (Python FastAPI or Node.js) with clean OpenAPI specification",
                "frontend": "Modern Responsive Web App (Vectihost/Selligine Vanilla CSS aesthetic, fast mobile-first load)",
                "database_entities": [
                    "users (id, email, password_hash, full_name, role, created_at)",
                    "profiles (id, user_id, display_name, bio, avatar_url, preferences_json)",
                    "waitlist_leads (id, email, full_name, source, status, created_at)",
                    "audit_logs (id, user_id, action, ip_address, timestamp)"
                ],
                "integrations": [
                    "Transactional Email Gateway (Resend / SendGrid) for automated verification and onboarding",
                    "Payment Processing Gateway (Paystack / Stripe) for subscription and order collection"
                ]
            }
        }

    else:
        # Detected location
        detected_locations = set()
        if results.get("location"):
            detected_locations.add(results.get("location").strip())

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

        # Extract specific physical address/landmark if found in bio or text
        m_landmark = re.search(r'([A-Za-z]+,\s*(?:adjacent|opposite|behind|near|next to)\s+[A-Za-z0-9\s]+)', all_text, re.IGNORECASE)
        if m_landmark:
            landmark_text = m_landmark.group(1).strip().title()
            detected_locations.add(landmark_text)

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
            ("Bridal & Event Makeup", r'\b(?:makeup|make-up|bridal|bride|brides|glam|beauty\s*artist|makeup\s*artistry)\b|#\w*(?:makeup|bride|bridal|glam)\w*'),
            ("Custom Wig Making & Hair Extensions", r'\b(?:wig|wigs|wigcap|wig\s+cap|lace\s*frontal|bone\s*straight|hairstylist|hairstyling|hair\s*styling|hair\s*revamp|frontal)\b|#\w*(?:wig|hair|frontal)\w*'),
            ("Professional Vocational Training", r'\b(?:trainer|training|masterclass|apprenticeship|academy|educator|beauty\s*educator)\b|#\w*(?:trainer|training|masterclass|educator)\w*'),
            ("Fashion, Apparel & Styling", r'\b(?:clothing|fashion|boutique|wardrobe|apparel)\b|#\w*fashion\w*'),
            ("Software & Digital Technology", r'\b(?:software|tech|developer|digital|api|saas|app)\b'),
            ("E-Commerce & Retail", r'\b(?:e-commerce|store|shop|online\s*store|retail)\b')
        ]
        for ind_name, ind_regex in industry_keywords:
            if re.search(ind_regex, all_text, re.IGNORECASE):
                detected_industries.add(ind_name)

        if not detected_industries:
            detected_industries.add("General Brand / Digital Entity")

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
        if any("tech" in ind.lower() or "software" in ind.lower() for ind in detected_industries):
            services.append({
                "service": "Custom Software & Web Application Development",
                "description": "Modern API development, client portals, and scalable cloud solutions."
            })
        if not services:
            services.append({
                "service": "Core Digital Offerings",
                "description": f"Services and solutions offered under the {target} brand umbrella."
            })

        # -------------------------------------------------------------------------
        # 2. Developer Digital Roadmap & System Architecture (Use Case 1)
        # -------------------------------------------------------------------------
        if any("makeup" in ind.lower() or "wig" in ind.lower() for ind in detected_industries):
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
        elif any("tech" in ind.lower() or "software" in ind.lower() for ind in detected_industries):
            digital_roadmap = {
                "current_state": "Developer / Tech Operations (Product APIs, service documentation, and cloud architecture).",
                "primary_bottlenecks": [
                    "Manual client onboarding and contract management.",
                    "Dispersed documentation and API developer guides.",
                    "Absence of self-service billing and license key generation."
                ],
                "recommended_platform_modules": [
                    {
                        "module": "Developer API & Documentation Portal",
                        "purpose": "Interactive OpenAPI documentation, SDK libraries, and sandbox testing."
                    },
                    {
                        "module": "Self-Service Client Dashboard & Analytics",
                        "purpose": "Real-time usage metrics, license provisioning, and account settings."
                    },
                    {
                        "module": "Automated Billing & Subscription Lifecycle Engine",
                        "purpose": "Recurring subscription billing, tiered licensing, and automated invoicing."
                    }
                ],
                "recommended_architecture": {
                    "backend": "Python FastAPI or Node.js with asynchronous worker queues",
                    "frontend": "Modern Single Page Application (Light Theme, high data-density dashboard)",
                    "database_entities": [
                        "organizations (id, name, plan_tier, created_at)",
                        "users (id, org_id, email, role, api_key_hash)",
                        "subscriptions (id, org_id, status, renewal_date, amount)",
                        "usage_events (id, org_id, endpoint, response_time, timestamp)"
                    ],
                    "integrations": [
                        "Stripe / Paystack for global and local subscription billing",
                        "Transactional Email & Webhook Dispatchers"
                    ]
                }
            }
        else:
            digital_roadmap = {
                "current_state": "Direct Conversational & Social Engagement (Inquiries received across social channels).",
                "primary_bottlenecks": [
                    "Manual lead intake and response latency across uncentralized channels.",
                    "No integrated deposit collection or formal quote generation.",
                    "Limited digital authority outside of third-party platforms."
                ],
                "recommended_platform_modules": [
                    {
                        "module": "Automated Client Inquiry & Consultation Engine",
                        "purpose": "Centralized intake form capturing project scope, budget, and contact info."
                    },
                    {
                        "module": "Dynamic Portfolio & Trust Showcase",
                        "purpose": "Fast-loading mobile showcase with client testimonials and case studies."
                    },
                    {
                        "module": "Online Invoicing & Payment Reconciliation",
                        "purpose": "Instant receipt generation and automated mobile money/card settlement."
                    }
                ],
                "recommended_architecture": {
                    "backend": "RESTful API (Python FastAPI or PHP) with clean MVC structure",
                    "frontend": "Modern Responsive Web App (Vectihost/Selligine style, mobile-first)",
                    "database_entities": [
                        "clients (id, name, phone, email, status, created_at)",
                        "inquiries (id, client_id, subject, requirements, status)",
                        "invoices (id, client_id, total_amount, paid_amount, status, due_date)"
                    ],
                    "integrations": [
                        "Mobile Money & Card Gateway (Paystack / Flutterwave)",
                        "Automated SMS/Email Notification Gateway"
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

    # -------------------------------------------------------------------------
    # Multi-Dimensional Collision & Clearance Scoring Model:
    # A virgin name (like 'waitrive') with 0 web hits, 0 socials, 0 domains, 0 contacts -> 100/100 (Pristine).
    # An active real-world operating brand (like 'luuksgh') with dozens of indexed search hits,
    # active Tier-1 socials (Instagram, TikTok), verified contact numbers, and physical operations
    # must score as HIGH COLLISION RISK (~5 to 20/100).
    # -------------------------------------------------------------------------

    # 1. Search Engine Footprint Collision (Weight: up to 35 pts)
    search_count = len(search_results)
    if search_count == 0:
        search_collision = 0
    elif search_count <= 2:
        search_collision = 8
    elif search_count <= 6:
        search_collision = 16
    elif search_count <= 15:
        search_collision = 24
    elif search_count <= 30:
        search_collision = 30
    else:
        search_collision = 35  # Established online search footprint (e.g. 70+ results)

    # 2. Social Handle Collision (Weight: up to 40 pts)
    # Tier-1 creator/commercial platforms have higher collision impact than niche sites
    tier1_names = {"instagram", "tiktok", "twitter / x", "facebook", "youtube", "linkedin company", "threads"}
    tier1_active = [p for p in active_socials if p.get("platform", "").lower() in tier1_names]
    other_active = [p for p in active_socials if p.get("platform", "").lower() not in tier1_names]

    if not tier1_active and not other_active:
        social_collision = 0
    else:
        if len(tier1_active) == 1:
            tier1_pts = 20
        elif len(tier1_active) == 2:
            tier1_pts = 32
        elif len(tier1_active) >= 3:
            tier1_pts = 40
        else:
            tier1_pts = 0

        other_pts = len(other_active) * 5
        social_collision = min(40, tier1_pts + other_pts)

    # 3. Active Commercial Operations & Direct Contact Collision (Weight: up to 25 pts)
    commercial_collision = 0
    if phones:
        commercial_collision += 15  # Active trading business with direct public phone/WhatsApp lines
    if emails:
        commercial_collision += 5
    if operating_base and "unclaimed" not in operating_base.lower() and "pristine" not in operating_base.lower() and operating_base != "Global / Digital Operations":
        commercial_collision += 5
    commercial_collision = min(25, commercial_collision)

    # 4. Domain Name Space Collision (Weight: up to 20 pts)
    domain_collision = 0
    has_com = any(d.get("domain", "").endswith(".com") and d.get("is_registered") for d in registered_domains)
    if has_com:
        domain_collision += 14
        other_doms = len(registered_domains) - 1
        domain_collision += min(6, max(0, other_doms) * 2)
    else:
        domain_collision += min(20, len(registered_domains) * 4)

    # Total Collision Penalty (0 to 100)
    total_collision_penalty = min(100, search_collision + social_collision + commercial_collision + domain_collision)
    uniqueness_score = max(0, min(100, 100 - total_collision_penalty))

    if uniqueness_score >= 80:
        clearance_rating = "HIGHLY AVAILABLE / CLEAN BRAND IDENTITY"
        clearance_verdict = f"'{target}' is largely unclaimed across major web search indexes, social platforms, and domain registries. Pristine candidate for brand registration."
    elif uniqueness_score >= 50:
        clearance_rating = "MODERATE CLEARANCE / PARTIALLY CONTESTED"
        occupied_names = ", ".join([p["platform"] for p in active_socials]) or "partial web traces"
        clearance_verdict = f"'{target}' has existing claims on {occupied_names}, but remains available across other channels. Action required to secure remaining namespace or evaluate trademark."
    else:
        clearance_rating = "HIGH COLLISION RISK / ESTABLISHED BRAND EXISTS"
        occupied_names = ", ".join([p["platform"] for p in active_socials]) or "multiple web channels"
        clearance_verdict = f"'{target}' is actively occupied by an established entity with {search_count} indexed web citations, active presence on {occupied_names}, and direct commercial contact channels. High risk of brand collision or trademark conflict."

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
    if any("makeup" in ind.lower() or "wig" in ind.lower() or "beauty" in ind.lower() for ind in detected_industries):
        variations.extend([f"{clean_target}beauty", f"{clean_target}hair", f"{clean_target}glam"])

    brand_clearance = {
        "target_name": target,
        "uniqueness_score": uniqueness_score,
        "clearance_rating": clearance_rating,
        "verdict": clearance_verdict,
        "handle_collision_rate": f"{social_claimed_pct}% ({social_claimed_count}/{total_socials} platforms occupied)",
        "domain_collision_rate": f"{dom_claimed_pct}% ({registered_dom_count}/{total_domains} TLDs registered)",
        "search_collision_impact": f"{search_collision}/35 pts ({search_count} indexed web entries)",
        "social_collision_impact": f"{social_collision}/40 pts ({len(active_socials)} active channels: {', '.join([p['platform'] for p in active_socials]) or 'None'})",
        "commercial_collision_impact": f"{commercial_collision}/25 pts ({len(phones)} phone(s), base: {operating_base})",
        "domain_collision_impact": f"{domain_collision}/20 pts ({len(registered_domains)} registered TLDs)",
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
