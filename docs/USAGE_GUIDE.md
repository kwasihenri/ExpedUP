# ExpedUP User Guide

Welcome to **ExpedUP**, the high-performance OSINT (Open Source Intelligence) and brand clearance reconnaissance engine.

---

## 🖥️ 1. Graphical User Interface (GUI)

Launch the GUI interface:
```bash
python main.py
```

### 1.1 Target Reconnaissance Setup
1. **Target Name, Handle or Keyword**: Enter the primary target (e.g., `AcmeCorp`, `kwasihenri`, `luuksgh`).
2. **Reconnaissance Depth**:
   - `Standard`: Fast multi-platform social probe and standard search index.
   - `Deep (Multi-Engine)`: Multi-engine search (Bing + DuckDuckGo), domain TLD probes, entity extraction, and adaptive regional pivot.
3. **Strict Go By Keyword**:
   - Enable this switch to wrap queries in exact quotes (`"target"`), enforce exact word boundaries, and disable adaptive regional pivots.
4. **Advanced Anchors (Optional)**:
   - Click **Show Advanced Anchors** to specify geographic anchors (e.g. `London, UK`), industry categories (e.g. `Logistics`), or seed phone numbers.

### 1.2 Mission Launch & Progress Monitoring
- Click **`Launch Expedition`** to begin reconnaissance.
- Watch live progress on the progress bar and status text.
- If network connection drops or struggles, an interactive **Network Struggle Manager** modal appears automatically with `Retry / Check Now`, `Force Continue`, or `Dismiss` options. A tappable warning badge (`⚠️ Connection Struggling`) remains available on the sidebar.

### 1.3 Reviewing Intelligence & Dossiers
- **Executive Overview**: View the Uniqueness Score (`0-100`), Business Operating Base, Mobility Model, and live Dossier Preview.
- **Two-Box Dossier Toggle**: Toggle between **Formatted View** (card layout) and **Raw Markdown** syntax text.
- **Web Search Results**: Review indexed snippets with source badges and clickable links.
- **Social Media Presence**: Audit active vs available social profiles across 15+ networks.
- **Domain Availability**: Inspect probed domain extensions, resolved IPs, and HTTP status codes.
- **Contact Entities**: Access discovered phone/WhatsApp numbers, emails, social mentions, and hashtags.

### 1.4 Exporting & Reloading Expeditions
- **Export All Formats**: Click **`Export All Formats (1-Click)`** to export `.expedup`, `.md`, `.json`, and `.csv` files simultaneously.
- **Individual Exports**: Use individual `Markdown`, `CSV`, or `JSON` buttons.
- **Load Saved Expedition**: Click **`📂 Load Saved Expedition / Dossier`** to load any previously exported `.expedup`, `.json`, `.md`, or `.txt` dossier back into the UI for reference.

---

## 💻 2. Command Line Interface (CLI)

Run headless reconnaissance directly from your terminal:

```bash
python main.py --cli --target "kwasihenri" --depth deep --export-all
```

### Command Line Options

| Flag | Description | Default |
|---|---|---|
| `--cli` | Runs ExpedUP in headless CLI mode | GUI mode |
| `--target <name>` | Target name, handle, or brand keyword | Required in CLI |
| `--location <loc>` | Optional geographic anchor | `""` |
| `--category <cat>` | Optional category or industry anchor | `""` |
| `--phone <phone>` | Optional seed contact number | `""` |
| `--depth <mode>` | Recon depth: `standard` or `deep` | `deep` |
| `--strict` | Enforces strict exact keyword matching | `False` |
| `--outdir <path>` | Custom directory path for exported files | `artifacts/expeditions` |
| `--export-all` | Exports `.expedup`, `.md`, `.json`, `.csv` | `False` |

---

## ⚙️ 3. Engine Settings & Customization

Navigate to the **Engine Settings** tab in the GUI to adjust application behavior:
- **Appearance Theme**: Light or Dark mode.
- **Application Text & Font Scale**: Normal (`100%`), Large (`110%`), Extra Large (`120%`).
- **Network Timeouts & Delays**: Adjust request timeouts (seconds) and inter-request delay ranges (milliseconds).
- **Social Media Matrix & TLDs**: Enable/disable specific social platforms or domain extensions.

*Note: All settings modifications are staged locally and applied atomically when you click **"Save & Apply Settings"**.*
