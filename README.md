# ExpedUP 🚀
### Universal Word, Brand & Name Online Expedition Engine
**Multi-Axis OSINT Reconnaissance, Automated Business Profiling & Brand Clearance Intelligence**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![UI Framework](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Build Status](https://img.shields.io/badge/status-active-success.svg)](#)

---

## 📌 Executive Summary

**ExpedUP** is a publication-grade Open Source Intelligence (OSINT) and brand reconnaissance engine designed to execute deep, multi-source digital expeditions on any word, brand name, developer handle, or business identity. 

ExpedUP is built around **two core value propositions**:

1. **For Brand Creators & Entrepreneurs Seeking Unique Names**:
   Delivers an immediate **Brand Clearance & Name Collision Matrix** featuring a 0–100 Uniqueness Score, handle claim audits across 15+ social networks, domain TLD registration checks, risk classification (`HIGHLY AVAILABLE / CLEAN BRAND IDENTITY` vs `HIGH COLLISION RISK`), and clean alternative brand name recommendations.

2. **For Developers Building Systems for Existing Businesses**:
   Performs deep **Automated Business Profiling** (extracting operating hubs, mobility models, verified phones/WhatsApp contacts, identified service lines) and generates a complete **Developer Digital Roadmap & Architectural Blueprint** (database schema entities, REST API contracts, payment gateways, and automated notification workflows).

---

## 🖼️ Application Visual Tour

> [!NOTE]
> *Place your application screenshots into the `screenshots/` directory using the filenames specified below.*

### 1. Executive Dashboard & Live Recon Metrics
![ExpedUP GUI Executive Overview Dashboard](screenshots/expedup_executive_overview.png)
*Figure 1: The dual-column CustomTkinter GUI featuring real-time KPI metric counters, status pills, and interactive parameter controls.*

### 2. Brand Clearance & Name Collision Matrix
![Brand Clearance & Collision Matrix](screenshots/brand_clearance_matrix.png)
*Figure 2: Brand clearance uniqueness score gauge (0-100), clearance verdict, occupied vs. available social handles, and domain TLD collision audit.*

### 3. Developer Digital Roadmap & Architecture Blueprint
![Developer Digital Roadmap & Architecture Blueprint](screenshots/developer_roadmap_blueprint.png)
*Figure 3: Business profile summary, identified service lines, operational bottlenecks, recommended platform modules, and target database entities.*

### 4. Interactive Network Connection Manager & Tappable Warning Pill
![Network Connection Manager Modal & Tappable Warning Pill](screenshots/network_connection_manager.png)
*Figure 4: Automatic expedition pause modal triggered upon internet degradation with live WAN reachability status, retry, force continue, and tappable progress warning badge.*

### 5. Engine Settings & Staged Configuration Dashboard
![Live Recon Console & Settings Dashboard](screenshots/settings_and_recon_console.png)
*Figure 5: Non-instant staged settings dashboard with dual light/dark themes, text font scale adjustment (100%-120%), delay sliders, and platform matrices.*

### 6. Publication-Grade Markdown Dossier Output
![Publication-Grade Markdown Dossier Output](screenshots/markdown_dossier_report.png)
*Figure 6: The comprehensive 9-section markdown intelligence report auto-generated and exported to disk.*

---

## ✨ Key Features

- **🌐 Resilient Multi-Engine Search Crawling**:
  - **Bing Block & Lineclamp Parsing**: Multi-page HTML extraction with Base64 redirect URL unwrapping (`&u=a1...`) to recover canonical destination URLs (e.g. `https://www.instagram.com/target/`).
  - **DuckDuckGo Lite Scraping**: Block-level link parsing with clean URL unquoting.
  - **Edge Client Hints Parity**: Header simulation (`Sec-Ch-Ua`, `Sec-Fetch-*`) preventing anti-bot blockages on rare or single-word commercial queries.
  - **Adaptive Regional Pivots**: Dynamically detects geographic tags in early search snippets (e.g. `#Takoradi`, `#Lagos`) and executes localized follow-up probes.

- **📱 18 Social Platform Identity Footprint Verification**:
  - Probes Instagram, TikTok (with custom script rehydration JSON parsing), Threads, Twitter/X, Facebook, LinkedIn, GitHub, Dev.to, Hashnode, YouTube, Pinterest, Snapchat, Reddit, Medium, Telegram, Behance, and SoundCloud.
  - Advanced SPA landing page rejection: Prevents false positive claims on generic login authwalls or 404 fallback titles.

- **📡 Network Interruption Manager & Auto-Pause**:
  - Automatic detection of internet connection degradation or consecutive request timeouts.
  - Auto-pauses worker threads safely without losing accumulated OSINT findings.
  - Interactive GUI connection modal with live WAN health monitoring, auto-recovery reconnection loop, manual retry, force continue, and tappable progress warning badge.

- **📄 9-Section Publication-Grade Report Generator**:
  - 1-click export to Markdown (`.md`), JSON (`.json`), CSV (`.csv`), and Plain Text (`.txt`).
  - Structured into 9 executive sections: Reconnaissance Snapshot, Business Profile, Service Lines, Developer Blueprint, Brand Clearance Matrix, Verified Social Footprints, Discovered Web Index, Contact Graph, and Domain TLD Status.

- **🖥️ Modern CustomTkinter GUI + Headless CLI**:
  - Fully responsive GUI with light and dark mode dual-token themes.
  - Adjustable typography font scaling (`100%`, `110%`, `120%`) for maximum legibility.
  - Headless CLI mode for automation scripts, terminal reconnaissance, and CI pipelines.

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+** installed on Windows, macOS, or Linux.
- `git` installed on your system.

### Quickstart

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kwasihenri/ExpedUP.git
   cd ExpedUP
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage Guide

### 1. Launching the GUI Dashboard
To run the interactive desktop application:
```bash
python main.py
```
Or launch directly via the GUI script:
```bash
python gui.py
```

### 2. Running Headless CLI Expeditions
ExpedUP supports powerful command-line reconnaissance:

```bash
# Basic CLI Expedition (Standard Depth)
python main.py --cli --target "acmecorp"

# Deep Multi-Engine Expedition with Auto-Export
python main.py --cli --target "luuksgh" --depth Deep --export-all

# Strict Exact-Match Mode (Disables loose pivots & exact quoted search)
python main.py --cli --target "waitrive" --strict --export-all

# Expedition with Geographic & Industry Anchors
python main.py --cli --target "salonbeauty" --location "London, UK" --category "Cosmetics"
```

### Command-Line Arguments Reference

| Flag / Option | Description | Default |
|---|---|---|
| `--cli` | Run ExpedUP in Headless Command-Line Interface mode. | `False` |
| `--target <name>` | Target word, brand name, handle, or identity to probe. | *Required in CLI mode* |
| `--location <loc>` | Geographic anchor filter (e.g. `Takoradi`, `London`). | `""` |
| `--category <cat>` | Industry / service category filter (e.g. `Wigs`, `Fintech`). | `""` |
| `--phone <num>` | Seed contact phone number for correlation. | `""` |
| `--depth <level>` | Reconnaissance depth mode (`Standard` or `Deep`). | `Deep` |
| `--strict` | Enable **Strict Go By Keyword** mode (exact matches only). | `False` |
| `--export-all` | Automatically export all report formats (`.md`, `.json`, `.csv`, `.txt`). | `False` |

---

## 📁 Exported Dossier Structure

When an expedition completes, reports are saved to `artifacts/expeditions/`:
```
artifacts/expeditions/
├── ExpedUP_targetname_20260911_231434.md   # Publication 9-Section Markdown Dossier
├── ExpedUP_targetname_20260911_231434.json # Raw Structured OSINT Data Object
├── ExpedUP_targetname_20260911_231434.csv  # Web Index & Social Matrix Table
└── ExpedUP_targetname_20260911_231434.txt  # Plain Text Recon Summary
```

---

## 🏗️ Architecture & Component Overview

```
ExpedUP/
├── main.py                     # Primary entry point (CLI argument parser & GUI dispatcher)
├── expedup_engine.py           # Core reconnaissance engine (search crawlers, pause/resume, probes)
├── intelligence_synthesizer.py # Intelligence synthesis engine (Brand Clearance & Developer Blueprint)
├── exporters.py                # Publication dossier formatter and multi-format exporter
├── gui.py                      # CustomTkinter GUI dashboard, modal manager & terminal console
├── settings_manager.py        # Persistent settings loader/saver (settings.json)
├── config.py                   # Centralized configuration tokens, color palettes & user agents
├── icons.py                    # Vector icon manager and tint renderer
└── scratch/                    # Test harnesses and temporary verification scripts
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [Issues page](https://github.com/kwasihenri/ExpedUP/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git checkout -b feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

---

<p center>
Developed with ❤️ by <a href="https://github.com/kwasihenri">Kwasi Henri</a> — ExpedUP Universal Brand Intelligence Engine
</p>
