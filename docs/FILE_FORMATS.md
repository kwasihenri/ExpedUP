# ExpedUP File Formats Specification

ExpedUP supports exporting and re-loading reconnaissance dossiers across multiple standardized formats.

---

## 📦 1. ExpedUP Native Bundle (`.expedup`)

The `.expedup` file is an JSON bundle containing full raw findings, target parameters, and synthesized intelligence payloads.

### JSON Structure

```json
{
  "format": "expedition_bundle",
  "version": "1.0.0",
  "timestamp": "2026-09-12 00:00:00",
  "payload": {
    "target": "kwasihenri",
    "location": "Accra, Ghana",
    "category": "Software Engineer",
    "phone": "+233200000000",
    "timestamp": "2026-09-12 00:00:00",
    "search_results": [
      {
        "title": "kwasihenri (Kwasi Henri) · GitHub",
        "url": "https://github.com/kwasihenri",
        "snippet": "Software Developer & Open Source Contributor.",
        "engine": "DuckDuckGo"
      }
    ],
    "social_profiles": [
      {
        "platform": "GitHub",
        "url": "https://github.com/kwasihenri",
        "exists": true,
        "status_code": 200,
        "category": "Developer"
      }
    ],
    "domains": [
      {
        "domain": "kwasihenri.com",
        "is_registered": true,
        "resolved_ip": "104.21.55.12",
        "status_code": 200,
        "title": "Kwasi Henri Official Portfolio"
      }
    ],
    "entities": {
      "phones": ["+233200000000"],
      "emails": ["dev@kwasihenri.com"],
      "mentions": ["@kwasihenri"],
      "hashtags": ["#ExpedUP"]
    },
    "intelligence": {
      "developer_roadmap": { ... },
      "brand_clearance": { ... }
    }
  }
}
```

---

## 📝 2. Publication-Grade 9-Section Markdown Dossier (`.md`)

The Markdown dossier is a formatted report designed for human review, executive summary presentations, and version control archiving.

### 9-Section Architecture

1. **Section 1: Executive Reconnaissance & Brand Clearance Snapshot**
   - Uniqueness score gauge (`0-100`), clearance verdict, collision metrics.
2. **Section 2: Business Profile & Operational Model**
   - Operating base, mobility model, detected industry categories, primary contacts.
3. **Section 3: Core Service & Product Lines Identified**
   - Detailed breakdown of identified offerings.
4. **Section 4: Developer Digital Roadmap & Architecture Blueprint**
   - Current state, operational bottlenecks, 5 recommended platform modules, database entities, integrations.
5. **Section 5: Brand Clearance & Name Collision Matrix**
   - Occupied vs available social handle claims, registered vs available domain extensions, recommended alternative brand variations.
6. **Section 6: Verified Social Media & Digital Footprints**
   - Markdown table of active social profiles.
7. **Section 7: Discovered Web Index & Search Evidence**
   - Numbered index of web hits with title, URL link, search engine source, and snippet blockquote.
8. **Section 8: Discovered Contact Entities & Social Graph**
   - Lists of phone/WhatsApp numbers, email addresses, mentions, and hashtags.
9. **Section 9: Domain & DNS Availability Status**
   - Table of probed TLDs with registration status, resolved IP, and HTTP status code.

---

## 📊 3. Standard Data Exports (`.json` and `.csv`)

- **Raw JSON (`.json`)**: Contains standard JSON dictionary structure compatible with automated data pipelines.
- **Structured CSV (`.csv`)**: Contains tabular rows categorizing findings into `Search Result`, `Social Profile`, `Domain`, `Phone Entity`, `Email Entity`, `Mention Entity`, and `Hashtag Entity`.

---

## 🔄 4. Universal Importer Compatibility Matrix

The ExpedUP Universal Loader (`load_expedition_file`) accepts:

| Extension | Parsing Method | Target & Payload Recovery |
|---|---|---|
| **`.expedup`** | Direct JSON bundle deserialization | Complete (All fields, sets, and intelligence payload) |
| **`.json`** | Direct JSON deserialization | Complete (All fields, sets, and intelligence payload) |
| **`.md`** | Section-aware regex parser | Complete (Extracts target, Section 7 search items, Section 6 social table, Section 9 domain table, entities, and re-synthesizes intelligence) |
| **`.txt`** | Text & section regex parser | Complete (Extracts target, links, search items, social profiles, and contact entities) |
