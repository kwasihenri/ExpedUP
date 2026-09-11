"""
ExpedUP - High Performance OSINT & Deep Reconnaissance Desktop Application
Built with CustomTkinter for advanced multi-source entity and brand investigations.
Features modern light-theme default (Vectihost/Selligine style) with full dark-theme toggle support.
"""

import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional

import customtkinter as ctk

from config import (
    APP_NAME, APP_SUBTITLE, VERSION, THEME_COLORS,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    DEFAULT_EXPORT_DIR, SOCIAL_PLATFORMS, DOMAIN_TLDS
)
from expedup_engine import ExpedUPEngine
from exporters import (
    generate_markdown_dossier, export_markdown_file,
    export_json_file, export_csv_file, export_all_formats
)
from icons import get_icon
from settings_manager import load_settings, save_settings, reset_to_defaults

# Configure light appearance by default (Vectihost & Selligine design system)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class ExpedUPApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load Persistent Settings
        self.settings = load_settings()
        saved_theme = self.settings.get("theme", "Light")
        ctk.set_appearance_mode(saved_theme)

        # Window Configuration
        self.title(f"{APP_NAME} v{VERSION} — Universal OSINT & Brand Reconnaissance Engine")
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.configure(fg_color=THEME_COLORS["bg"])

        # Engine & State
        self.engine: Optional[ExpedUPEngine] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.auto_scroll_logs = True
        self.is_advanced_visible = False

        self.current_results: Dict[str, Any] = {
            "target": "",
            "location": "",
            "category": "",
            "phone": "",
            "timestamp": "",
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

        # Setup UI Components
        self._build_header()
        self._build_main_layout()

    def _get_icon(self, name: str, size: tuple = (16, 16), color: Optional[Any] = None) -> ctk.CTkImage:
        """Helper to get a tinted CTkImage from the centralized icon manager."""
        return get_icon(name, size=size, color=color)

    # -------------------------------------------------------------------------
    # UI Layout Construction
    # -------------------------------------------------------------------------
    def _build_header(self):
        """Build top navigation and persistent status bar."""
        self.header_frame = ctk.CTkFrame(
            self, height=64, corner_radius=0,
            fg_color=THEME_COLORS["card"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.header_frame.pack(side="top", fill="x")

        # Brand Title & Icon
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)

        brand_label = ctk.CTkLabel(
            title_box,
            text=f"  {APP_NAME.upper()}",
            image=self._get_icon("target", (22, 22), THEME_COLORS["primary"]),
            compound="left",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        brand_label.pack(side="left")

        version_badge = ctk.CTkLabel(
            title_box,
            text=f"v{VERSION}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME_COLORS["primary"],
            text_color="#ffffff",
            corner_radius=6,
            padx=8, pady=2
        )
        version_badge.pack(side="left", padx=(10, 15))

        subtitle_label = ctk.CTkLabel(
            title_box,
            text=f"— {APP_SUBTITLE}",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_secondary"]
        )
        subtitle_label.pack(side="left")

        # Right Header Controls
        controls_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        controls_box.pack(side="right", padx=20, pady=10)

        # Status Pill
        self.status_pill = ctk.CTkLabel(
            controls_box,
            text="  READY FOR MISSION",
            image=self._get_icon("circle-check", (12, 12), THEME_COLORS["accent"]),
            compound="left",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["accent"],
            fg_color=THEME_COLORS["card_subtle"],
            corner_radius=12,
            padx=12, pady=4
        )
        self.status_pill.pack(side="left", padx=(0, 15))

        # Appearance Toggle (Light default -> Dark)
        current_theme = self.settings.get("theme", "Light")
        self.appearance_switch = ctk.CTkSwitch(
            controls_box,
            text="Dark Mode" if current_theme == "Dark" else "Light Mode",
            command=self._toggle_appearance,
            font=ctk.CTkFont(size=12),
            progress_color=THEME_COLORS["primary"],
            onvalue="Dark", offvalue="Light"
        )
        if current_theme == "Dark":
            self.appearance_switch.select()
        else:
            self.appearance_switch.deselect()
        self.appearance_switch.pack(side="left")

    def _build_main_layout(self):
        """Build two-column dashboard: sidebar (controls) & main tabview."""
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(side="top", fill="both", expand=True, padx=16, pady=14)

        self._build_sidebar(self.content_container)
        self._build_tabview(self.content_container)

    def _build_sidebar(self, parent):
        """Construct the left sidebar with parameters, triggers, and export actions."""
        self.sidebar_frame = ctk.CTkFrame(
            parent, width=340, corner_radius=12,
            fg_color=THEME_COLORS["card"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 14))
        self.sidebar_frame.pack_propagate(False)

        # Scrollable area inside sidebar
        scroll_sidebar = ctk.CTkScrollableFrame(
            self.sidebar_frame, fg_color="transparent",
            scrollbar_button_color=THEME_COLORS["border"]
        )
        scroll_sidebar.pack(fill="both", expand=True, padx=14, pady=14)

        # 1. PARAMETERS CARD
        param_header = ctk.CTkLabel(
            scroll_sidebar, text="TARGET RECONNAISSANCE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        param_header.pack(anchor="w", pady=(0, 8))

        # Primary Target Field (Always Visible)
        ctk.CTkLabel(
            scroll_sidebar, text="Target Name, Handle or Keyword *",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(anchor="w")
        self.entry_target = ctk.CTkEntry(
            scroll_sidebar, placeholder_text="e.g. AcmeCorp or brand_handle",
            height=36, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"],
            placeholder_text_color=THEME_COLORS["text_muted"]
        )
        self.entry_target.pack(fill="x", pady=(2, 10))

        # Recon Depth Mode
        ctk.CTkLabel(
            scroll_sidebar, text="Reconnaissance Depth",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w")
        self.seg_depth = ctk.CTkSegmentedButton(
            scroll_sidebar, values=["Standard", "Deep (Multi-Engine)"],
            selected_color=THEME_COLORS["primary"],
            selected_hover_color=THEME_COLORS["primary_hover"],
            unselected_color=THEME_COLORS["card_subtle"],
            unselected_hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.seg_depth.set(self.settings.get("default_depth", "Deep (Multi-Engine)"))
        self.seg_depth.pack(fill="x", pady=(4, 10))

        # Strict Go By Keyword Toggle (Default: OFF / False)
        self.switch_strict_keyword = ctk.CTkSwitch(
            scroll_sidebar,
            text="Strict Go By Keyword",
            font=ctk.CTkFont(size=11),
            progress_color=THEME_COLORS["primary"],
            text_color=THEME_COLORS["text_secondary"]
        )
        self.switch_strict_keyword.deselect()  # disabled by default
        self.switch_strict_keyword.pack(fill="x", pady=(0, 10))

        # Advanced Anchors Toggle Button (Default: Not Shown)
        self.btn_toggle_advanced = ctk.CTkButton(
            scroll_sidebar, text="  Show Advanced Anchors (Optional)",
            image=self._get_icon("circle", (12, 12), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._toggle_advanced_anchors,
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_toggle_advanced.pack(fill="x", pady=(0, 10))

        # Collapsible Advanced Anchors Container (Initially Hidden)
        self.frame_advanced_anchors = ctk.CTkFrame(
            scroll_sidebar, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )

        # Advanced Fields inside collapsible frame
        adv_inner = ctk.CTkFrame(self.frame_advanced_anchors, fg_color="transparent")
        adv_inner.pack(fill="x", padx=10, pady=10)

        # Location Field
        ctk.CTkLabel(
            adv_inner, text="Geographic Anchor (Optional)",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w")
        self.entry_location = ctk.CTkEntry(
            adv_inner, placeholder_text="e.g. London, UK or New York",
            height=32, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"],
            placeholder_text_color=THEME_COLORS["text_muted"]
        )
        self.entry_location.pack(fill="x", pady=(2, 8))

        # Category Field
        ctk.CTkLabel(
            adv_inner, text="Category / Industry Anchor (Optional)",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w")
        self.entry_category = ctk.CTkEntry(
            adv_inner, placeholder_text="e.g. Logistics, E-commerce",
            height=32, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"],
            placeholder_text_color=THEME_COLORS["text_muted"]
        )
        self.entry_category.pack(fill="x", pady=(2, 8))

        # Phone Field
        ctk.CTkLabel(
            adv_inner, text="Seed Phone / Contact (Optional)",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w")
        self.entry_phone = ctk.CTkEntry(
            adv_inner, placeholder_text="e.g. +44 20 7946 0919",
            height=32, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"],
            placeholder_text_color=THEME_COLORS["text_muted"]
        )
        self.entry_phone.pack(fill="x", pady=(2, 2))

        # Clear Inputs Button Row
        self.btn_clear = ctk.CTkButton(
            scroll_sidebar, text="  Clear Input Fields",
            image=self._get_icon("trash", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._clear_inputs,
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_clear.pack(fill="x", pady=(0, 10))

        # Divider
        self.action_divider = ctk.CTkFrame(scroll_sidebar, height=1, fg_color=THEME_COLORS["border"])
        self.action_divider.pack(fill="x", pady=10)

        # 2. EXECUTION CONTROLS
        ctrl_header = ctk.CTkLabel(
            scroll_sidebar, text="MISSION EXECUTION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        ctrl_header.pack(anchor="w", pady=(0, 8))

        self.btn_launch = ctk.CTkButton(
            scroll_sidebar, text="  Launch Expedition",
            image=self._get_icon("play", (16, 16), "#ffffff"),
            compound="left",
            command=self._start_expedition,
            height=42, font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_hover"],
            text_color="#ffffff"
        )
        self.btn_launch.pack(fill="x", pady=(0, 8))

        self.btn_stop = ctk.CTkButton(
            scroll_sidebar, text="  Abort Expedition",
            image=self._get_icon("stop", (14, 14), "#ffffff"),
            compound="left",
            command=self._stop_expedition,
            state="disabled", height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME_COLORS["danger"],
            hover_color="#dc2626",
            text_color="#ffffff"
        )
        self.btn_stop.pack(fill="x", pady=(0, 10))

        # Progress Bar & Status Text
        self.prog_bar = ctk.CTkProgressBar(
            scroll_sidebar, height=10,
            progress_color=THEME_COLORS["primary"],
            fg_color=THEME_COLORS["card_subtle"]
        )
        self.prog_bar.set(0.0)
        self.prog_bar.pack(fill="x", pady=(0, 4))

        self.lbl_progress_status = ctk.CTkLabel(
            scroll_sidebar, text="Ready for mission launch.",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["text_secondary"],
            anchor="w"
        )
        self.lbl_progress_status.pack(fill="x", pady=(0, 12))

        # Divider
        ctk.CTkFrame(scroll_sidebar, height=1, fg_color=THEME_COLORS["border"]).pack(fill="x", pady=8)

        # 3. EXPORT INTELLIGENCE HUB
        export_header = ctk.CTkLabel(
            scroll_sidebar, text="INTELLIGENCE EXPORT HUB",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        export_header.pack(anchor="w", pady=(0, 8))

        self.btn_export_all = ctk.CTkButton(
            scroll_sidebar, text="  Export All Formats (1-Click)",
            image=self._get_icon("download", (15, 15), "#ffffff"),
            compound="left",
            command=lambda: self._export_data("all"),
            height=34, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME_COLORS["success"],
            hover_color="#15803d",
            text_color="#ffffff"
        )
        self.btn_export_all.pack(fill="x", pady=(0, 6))

        export_row = ctk.CTkFrame(scroll_sidebar, fg_color="transparent")
        export_row.pack(fill="x", pady=(0, 6))

        self.btn_export_md = ctk.CTkButton(
            export_row, text="  Markdown",
            image=self._get_icon("file-text", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda: self._export_data("md"),
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_export_md.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.btn_export_csv = ctk.CTkButton(
            export_row, text="  CSV",
            image=self._get_icon("table", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda: self._export_data("csv"),
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_export_csv.pack(side="left", fill="x", expand=True, padx=(3, 3))

        self.btn_export_json = ctk.CTkButton(
            export_row, text="  JSON",
            image=self._get_icon("code", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda: self._export_data("json"),
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_export_json.pack(side="right", fill="x", expand=True, padx=(3, 0))

        self.btn_open_folder = ctk.CTkButton(
            scroll_sidebar, text="  Open Dossier Folder",
            image=self._get_icon("folder", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._open_export_dir,
            height=30, fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        )
        self.btn_open_folder.pack(fill="x", pady=(4, 8))

        # Status Toast Label
        self.lbl_export_toast = ctk.CTkLabel(
            scroll_sidebar, text="",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["success"],
            wraplength=280
        )
        self.lbl_export_toast.pack(fill="x", pady=(2, 0))

    def _toggle_advanced_anchors(self):
        """Toggle the visibility of additional anchor parameters."""
        self.is_advanced_visible = not self.is_advanced_visible
        if self.is_advanced_visible:
            self.frame_advanced_anchors.pack(fill="x", pady=(0, 10), before=self.btn_clear)
            self.btn_toggle_advanced.configure(
                text="  Hide Advanced Anchors",
                image=self._get_icon("circle-check", (12, 12), THEME_COLORS["primary"])
            )
        else:
            self.frame_advanced_anchors.pack_forget()
            self.btn_toggle_advanced.configure(
                text="  Show Advanced Anchors (Optional)",
                image=self._get_icon("circle", (12, 12), THEME_COLORS["secondary_text"])
            )

    def _build_tabview(self, parent):
        """Construct the right tabbed dashboard containing metrics, findings, profiles, and console."""
        self.tabview = ctk.CTkTabview(
            parent, corner_radius=12,
            fg_color=THEME_COLORS["card"],
            segmented_button_selected_color=THEME_COLORS["primary"],
            segmented_button_selected_hover_color=THEME_COLORS["primary_hover"],
            segmented_button_unselected_color=THEME_COLORS["card_subtle"],
            segmented_button_unselected_hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["text_primary"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.tabview.pack(side="right", fill="both", expand=True)

        # Tabs
        self.tab_overview = self.tabview.add("Executive Overview")
        self.tab_search = self.tabview.add("Web Search Index")
        self.tab_social = self.tabview.add("Social Identities")
        self.tab_entities = self.tabview.add("Discovered Entities")
        self.tab_console = self.tabview.add("Live Recon Console")
        self.tab_settings = self.tabview.add("Engine Settings")

        self._build_tab_overview()
        self._build_tab_search()
        self._build_tab_social()
        self._build_tab_entities()
        self._build_tab_console()
        self._build_tab_settings()

    # -------------------------------------------------------------------------
    # Tab 1: Executive Overview & Live KPI Grid
    # -------------------------------------------------------------------------
    def _build_tab_overview(self):
        """Build KPI metric cards and live Markdown Dossier preview."""
        kpi_container = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        kpi_container.pack(fill="x", padx=10, pady=(6, 12))

        # 6 KPI cards in 2 rows of 3
        self.kpi_labels = {}
        kpi_specs = [
            ("search", "Web Search Links", "0", THEME_COLORS["primary"], "search"),
            ("social", "Active Social Profiles", "0", THEME_COLORS["success"], "users"),
            ("domains", "Probed Domains", "0", THEME_COLORS["accent"], "world"),
            ("phones", "Discovered Phones", "0", THEME_COLORS["warning"], "phone"),
            ("emails", "Discovered Emails", "0", THEME_COLORS["accent_purple"], "mail"),
            ("mentions", "Mentions & Tags", "0", THEME_COLORS["primary"], "hash"),
        ]

        for i, (key, title, default_val, accent_col, icon_name) in enumerate(kpi_specs):
            row = i // 3
            col = i % 3

            card = ctk.CTkFrame(
                kpi_container, corner_radius=10,
                fg_color=THEME_COLORS["card_subtle"],
                border_width=1, border_color=THEME_COLORS["border"]
            )
            card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            kpi_container.grid_columnconfigure(col, weight=1)

            top_kpi = ctk.CTkFrame(card, fg_color="transparent")
            top_kpi.pack(pady=(8, 2))

            icon_img = self._get_icon(icon_name, (20, 20), accent_col)
            if icon_img:
                ctk.CTkLabel(top_kpi, text="", image=icon_img).pack(side="left", padx=(0, 6))

            val_lbl = ctk.CTkLabel(
                top_kpi, text=default_val,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=accent_col
            )
            val_lbl.pack(side="left")

            title_lbl = ctk.CTkLabel(
                card, text=title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=THEME_COLORS["text_primary"]
            )
            title_lbl.pack(pady=(0, 8))

            self.kpi_labels[key] = val_lbl

        # 6. Intelligence Highlights Panel (Brand Clearance & Developer Blueprint)
        self.frame_intel_summary = ctk.CTkFrame(
            self.tab_overview, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.frame_intel_summary.pack(fill="x", padx=10, pady=(0, 10))

        intel_grid = ctk.CTkFrame(self.frame_intel_summary, fg_color="transparent")
        intel_grid.pack(fill="x", padx=10, pady=10)
        intel_grid.grid_columnconfigure(0, weight=1)
        intel_grid.grid_columnconfigure(1, weight=1)

        # Left Card: Brand Clearance & Collision Matrix (Use Case 2)
        card_clearance = ctk.CTkFrame(
            intel_grid, corner_radius=8,
            fg_color=THEME_COLORS["card"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_clearance.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)

        ctk.CTkLabel(
            card_clearance, text="BRAND CLEARANCE & UNIQUENESS (FOR BRAND CREATORS)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(anchor="w", padx=10, pady=(8, 2))

        self.lbl_clearance_score = ctk.CTkLabel(
            card_clearance, text="Uniqueness Score: --/100",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        self.lbl_clearance_score.pack(anchor="w", padx=10, pady=(0, 2))

        self.lbl_clearance_verdict = ctk.CTkLabel(
            card_clearance, text="Launch an expedition to assess handle collisions and name availability.",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
            wraplength=350, justify="left", anchor="w"
        )
        self.lbl_clearance_verdict.pack(fill="x", padx=10, pady=(0, 8))

        # Right Card: Business Profile & System Blueprint (Use Case 1)
        card_profile = ctk.CTkFrame(
            intel_grid, corner_radius=8,
            fg_color=THEME_COLORS["card"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_profile.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)

        ctk.CTkLabel(
            card_profile, text="BUSINESS PROFILE & SYSTEM BLUEPRINT (FOR DEVELOPERS)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME_COLORS["accent"]
        ).pack(anchor="w", padx=10, pady=(8, 2))

        self.lbl_biz_base = ctk.CTkLabel(
            card_profile, text="Operating Base: --",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
            anchor="w"
        )
        self.lbl_biz_base.pack(fill="x", padx=10, pady=(0, 2))

        self.lbl_biz_details = ctk.CTkLabel(
            card_profile, text="Services, WhatsApp contacts, and architectural blueprint will be synthesized.",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
            wraplength=350, justify="left", anchor="w"
        )
        self.lbl_biz_details.pack(fill="x", padx=10, pady=(0, 8))

        # Live Dossier Preview Header
        preview_header_row = ctk.CTkFrame(self.tab_overview, fg_color="transparent")
        preview_header_row.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(
            preview_header_row, text="PUBLICATION-READY DOSSIER PREVIEW",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        ctk.CTkButton(
            preview_header_row, text="  Copy Dossier",
            image=self._get_icon("copy", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._copy_dossier_to_clipboard,
            width=120, height=26, font=ctk.CTkFont(size=11),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        ).pack(side="right")

        # Dossier Textbox
        self.txt_dossier_preview = ctk.CTkTextbox(
            self.tab_overview, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=THEME_COLORS["card_subtle"],
            text_color=THEME_COLORS["text_primary"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.txt_dossier_preview.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_dossier_preview.insert("1.0", "# ExpedUP Intelligence Dossier\n\nLaunch an expedition to generate a real-time reconnaissance dossier.")

    # -------------------------------------------------------------------------
    # Tab 2: Web Search Results Feed
    # -------------------------------------------------------------------------
    def _build_tab_search(self):
        """Build scrollable search results view."""
        header_bar = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        header_bar.pack(fill="x", padx=10, pady=8)

        self.lbl_search_count = ctk.CTkLabel(
            header_bar, text="0 search results indexed.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        self.lbl_search_count.pack(side="left")

        self.search_scroll_frame = ctk.CTkScrollableFrame(
            self.tab_search, fg_color="transparent",
            scrollbar_button_color=THEME_COLORS["border"]
        )
        self.search_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _render_search_item(self, item: dict):
        """Append a beautifully formatted search result card."""
        card = ctk.CTkFrame(
            self.search_scroll_frame, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card.pack(fill="x", pady=6, padx=4)

        # Title Row with Engine Badge
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        engine_name = item.get("engine", "Search Engine")
        engine_badge = ctk.CTkLabel(
            top_row, text=f"[{engine_name}]",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME_COLORS["primary"],
            fg_color=THEME_COLORS["secondary"],
            corner_radius=4, padx=6, pady=2
        )
        engine_badge.pack(side="left", padx=(0, 8))

        title = item.get("title", "Untitled Web Result")
        title_lbl = ctk.CTkLabel(
            top_row, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
            anchor="w", wraplength=600
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # URL & Action Buttons Row
        url_row = ctk.CTkFrame(card, fg_color="transparent")
        url_row.pack(fill="x", padx=12, pady=(0, 6))

        url = item.get("url", "")
        url_lbl = ctk.CTkLabel(
            url_row, text=url[:80] + ("..." if len(url) > 80 else ""),
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["primary"],
            anchor="w"
        )
        url_lbl.pack(side="left", fill="x", expand=True)

        btn_open = ctk.CTkButton(
            url_row, text="  Open", width=70, height=24,
            image=self._get_icon("external-link", (12, 12), THEME_COLORS["accent"]),
            compound="left",
            command=lambda u=url: webbrowser.open(u),
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=THEME_COLORS["card"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["text_primary"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        btn_open.pack(side="right", padx=(4, 0))

        btn_copy = ctk.CTkButton(
            url_row, text="  Copy", width=65, height=24,
            image=self._get_icon("copy", (12, 12), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda u=url: self._copy_to_clipboard(u),
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["card"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        btn_copy.pack(side="right")

        # Snippet Box
        snippet = item.get("snippet", "")
        if snippet:
            snip_box = ctk.CTkFrame(
                card, corner_radius=6,
                fg_color=THEME_COLORS["card"],
                border_width=1, border_color=THEME_COLORS["border"]
            )
            snip_box.pack(fill="x", padx=12, pady=(0, 10))

            snip_lbl = ctk.CTkLabel(
                snip_box, text=f'"{snippet}"',
                font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"],
                wraplength=720, justify="left", anchor="w"
            )
            snip_lbl.pack(fill="x", padx=10, pady=8)

    # -------------------------------------------------------------------------
    # Tab 3: Social & Digital Identities
    # -------------------------------------------------------------------------
    def _build_tab_social(self):
        """Build scrollable social profile cards."""
        header_bar = ctk.CTkFrame(self.tab_social, fg_color="transparent")
        header_bar.pack(fill="x", padx=10, pady=8)

        self.lbl_social_count = ctk.CTkLabel(
            header_bar, text="0 active social profiles discovered.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        self.lbl_social_count.pack(side="left")

        self.social_scroll_frame = ctk.CTkScrollableFrame(
            self.tab_social, fg_color="transparent",
            scrollbar_button_color=THEME_COLORS["border"]
        )
        self.social_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _render_social_item(self, item: dict):
        """Append a social media probe card."""
        card = ctk.CTkFrame(
            self.social_scroll_frame, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card.pack(fill="x", pady=6, padx=4)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        plat_name = item.get("platform", "Platform")
        category = item.get("category", "")
        exists = item.get("exists", False)
        status_code = item.get("status", 0)

        plat_label = ctk.CTkLabel(
            top_row, text=plat_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        plat_label.pack(side="left")

        cat_badge = ctk.CTkLabel(
            top_row, text=f"({category})",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"]
        )
        cat_badge.pack(side="left", padx=(8, 0))

        # Status badge
        status_color = THEME_COLORS["success"] if exists else THEME_COLORS["text_muted"]
        status_icon = self._get_icon("circle-check" if exists else "circle", (12, 12), status_color)
        status_text = "  VERIFIED ACTIVE" if exists else f"  STATUS {status_code}"
        status_badge = ctk.CTkLabel(
            top_row, text=status_text,
            image=status_icon, compound="left",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_badge.pack(side="right")

        # URL & Action
        url = item.get("url", "")
        url_row = ctk.CTkFrame(card, fg_color="transparent")
        url_row.pack(fill="x", padx=12, pady=(0, 6))

        url_lbl = ctk.CTkLabel(
            url_row, text=url,
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["primary"],
            anchor="w"
        )
        url_lbl.pack(side="left", fill="x", expand=True)

        if exists:
            btn_open = ctk.CTkButton(
                url_row, text="  Visit Profile", width=105, height=24,
                image=self._get_icon("external-link", (12, 12), "#ffffff"),
                compound="left",
                command=lambda u=url: webbrowser.open(u),
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=THEME_COLORS["primary"],
                hover_color=THEME_COLORS["primary_hover"],
                text_color="#ffffff"
            )
            btn_open.pack(side="right")

        # Bio or extracted description
        desc = (item.get("title", "") + " " + item.get("description", "")).strip()
        if desc:
            desc_box = ctk.CTkFrame(
                card, corner_radius=6,
                fg_color=THEME_COLORS["card"],
                border_width=1, border_color=THEME_COLORS["border"]
            )
            desc_box.pack(fill="x", padx=12, pady=(0, 10))

            desc_lbl = ctk.CTkLabel(
                desc_box, text=desc,
                font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_secondary"],
                wraplength=720, justify="left", anchor="w"
            )
            desc_lbl.pack(fill="x", padx=10, pady=6)

    # -------------------------------------------------------------------------
    # Tab 4: Discovered Entities (Phones, Emails, Mentions, Hashtags, Domains)
    # -------------------------------------------------------------------------
    def _build_tab_entities(self):
        """Build entity intelligence cards for discovered contacts and DNS probes."""
        self.entities_scroll = ctk.CTkScrollableFrame(
            self.tab_entities, fg_color="transparent",
            scrollbar_button_color=THEME_COLORS["border"]
        )
        self.entities_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Phone Numbers Section
        phone_card = ctk.CTkFrame(
            self.entities_scroll, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        phone_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            phone_card, text="  DISCOVERED PHONE NUMBERS",
            image=self._get_icon("phone", (14, 14), THEME_COLORS["warning"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["warning"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.frame_phones_list = ctk.CTkFrame(phone_card, fg_color="transparent")
        self.frame_phones_list.pack(fill="x", padx=12, pady=(0, 10))
        self.lbl_no_phones = ctk.CTkLabel(
            self.frame_phones_list, text="No phone numbers discovered yet.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_phones.pack(anchor="w")

        # 2. Email Addresses Section
        email_card = ctk.CTkFrame(
            self.entities_scroll, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        email_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            email_card, text="  DISCOVERED EMAIL ADDRESSES",
            image=self._get_icon("mail", (14, 14), THEME_COLORS["accent_purple"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["accent_purple"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.frame_emails_list = ctk.CTkFrame(email_card, fg_color="transparent")
        self.frame_emails_list.pack(fill="x", padx=12, pady=(0, 10))
        self.lbl_no_emails = ctk.CTkLabel(
            self.frame_emails_list, text="No email addresses discovered yet.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_emails.pack(anchor="w")

        # 3. Mentions & Hashtags Split Row
        tags_container = ctk.CTkFrame(self.entities_scroll, fg_color="transparent")
        tags_container.pack(fill="x", pady=(0, 10))

        # Mentions Card
        mentions_card = ctk.CTkFrame(
            tags_container, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        mentions_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ctk.CTkLabel(
            mentions_card, text="  SOCIAL MENTIONS (@)",
            image=self._get_icon("at", (14, 14), THEME_COLORS["primary"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.txt_mentions = ctk.CTkTextbox(
            mentions_card, height=100, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=THEME_COLORS["card"],
            text_color=THEME_COLORS["text_primary"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.txt_mentions.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Hashtags Card
        hashtags_card = ctk.CTkFrame(
            tags_container, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        hashtags_card.pack(side="right", fill="both", expand=True, padx=(6, 0))

        ctk.CTkLabel(
            hashtags_card, text="  ASSOCIATED HASHTAGS (#)",
            image=self._get_icon("hash", (14, 14), THEME_COLORS["accent"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["accent"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.txt_hashtags = ctk.CTkTextbox(
            hashtags_card, height=100, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=THEME_COLORS["card"],
            text_color=THEME_COLORS["text_primary"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.txt_hashtags.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # 4. Probed Domains & DNS Reconnaissance
        domain_card = ctk.CTkFrame(
            self.entities_scroll, corner_radius=8,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        domain_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            domain_card, text="  REGISTERED DOMAINS & DNS RECONNAISSANCE",
            image=self._get_icon("world", (14, 14), THEME_COLORS["success"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["success"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.frame_domains_list = ctk.CTkFrame(domain_card, fg_color="transparent")
        self.frame_domains_list.pack(fill="x", padx=12, pady=(0, 10))
        self.lbl_no_domains = ctk.CTkLabel(
            self.frame_domains_list, text="No registered domains detected for standard TLDs.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_domains.pack(anchor="w")

    def _render_phone_item(self, phone: str):
        """Add a discovered phone number chip with copy button."""
        if self.lbl_no_phones.winfo_exists():
            self.lbl_no_phones.pack_forget()

        row = ctk.CTkFrame(
            self.frame_phones_list,
            fg_color=THEME_COLORS["card"],
            corner_radius=6, border_width=1, border_color=THEME_COLORS["border"]
        )
        row.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(
            row, text=f"  {phone}",
            image=self._get_icon("phone", (13, 13), THEME_COLORS["warning"]),
            compound="left",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        )
        lbl.pack(side="left", padx=10, pady=4)

        btn = ctk.CTkButton(
            row, text="  Copy", width=65, height=22,
            image=self._get_icon("copy", (11, 11), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda p=phone: self._copy_to_clipboard(p),
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        btn.pack(side="right", padx=8)

    def _render_email_item(self, email: str):
        """Add a discovered email address chip with copy button."""
        if self.lbl_no_emails.winfo_exists():
            self.lbl_no_emails.pack_forget()

        row = ctk.CTkFrame(
            self.frame_emails_list,
            fg_color=THEME_COLORS["card"],
            corner_radius=6, border_width=1, border_color=THEME_COLORS["border"]
        )
        row.pack(fill="x", pady=2)

        lbl = ctk.CTkLabel(
            row, text=f"  {email}",
            image=self._get_icon("mail", (13, 13), THEME_COLORS["accent_purple"]),
            compound="left",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_primary"]
        )
        lbl.pack(side="left", padx=10, pady=4)

        btn = ctk.CTkButton(
            row, text="  Copy", width=65, height=22,
            image=self._get_icon("copy", (11, 11), THEME_COLORS["secondary_text"]),
            compound="left",
            command=lambda e=email: self._copy_to_clipboard(e),
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        btn.pack(side="right", padx=8)

    def _render_domain_item(self, dom: dict):
        """Add a registered domain entry."""
        if self.lbl_no_domains.winfo_exists():
            self.lbl_no_domains.pack_forget()

        domain = dom.get("domain", "")
        ip = dom.get("resolved_ip", "N/A")
        code = dom.get("status_code", 0)
        title = dom.get("title", "")

        row = ctk.CTkFrame(
            self.frame_domains_list,
            fg_color=THEME_COLORS["card"],
            corner_radius=6, border_width=1, border_color=THEME_COLORS["border"]
        )
        row.pack(fill="x", pady=3)

        info = f"  {domain}  |  IP: {ip}  |  HTTP: {code}  |  {title[:40]}"
        lbl = ctk.CTkLabel(
            row, text=info,
            image=self._get_icon("world", (13, 13), THEME_COLORS["accent"]),
            compound="left",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_primary"]
        )
        lbl.pack(side="left", padx=10, pady=6)

        btn = ctk.CTkButton(
            row, text="  Visit", width=65, height=22,
            image=self._get_icon("external-link", (11, 11), THEME_COLORS["accent"]),
            compound="left",
            command=lambda d=domain: webbrowser.open(f"https://{d}"),
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        btn.pack(side="right", padx=8)

    # -------------------------------------------------------------------------
    # Tab 5: Live Recon Terminal / Logs
    # -------------------------------------------------------------------------
    def _build_tab_console(self):
        """Build real-time terminal output viewer."""
        action_bar = ctk.CTkFrame(self.tab_console, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            action_bar, text="REAL-TIME MISSION RECON LOGS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        ctk.CTkButton(
            action_bar, text="  Copy Logs", width=95, height=26,
            image=self._get_icon("copy", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._copy_logs_to_clipboard,
            font=ctk.CTkFont(size=11),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            action_bar, text="  Clear Console", width=105, height=26,
            image=self._get_icon("trash", (13, 13), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._clear_console,
            font=ctk.CTkFont(size=11),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        ).pack(side="right", padx=(4, 0))

        self.txt_console = ctk.CTkTextbox(
            self.tab_console, wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=THEME_COLORS["console_bg"],
            text_color=THEME_COLORS["console_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.txt_console.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_console.insert("end", "[EXPEDUP SYSTEM] OSINT Reconnaissance Console Initialized.\n")

    # -------------------------------------------------------------------------
    # Tab 6: Engine & Application Settings
    # -------------------------------------------------------------------------
    def _build_tab_settings(self):
        """Construct the configuration and preferences dashboard."""
        scroll_settings = ctk.CTkScrollableFrame(
            self.tab_settings, fg_color="transparent",
            scrollbar_button_color=THEME_COLORS["border"]
        )
        scroll_settings.pack(fill="both", expand=True, padx=12, pady=10)

        # Header Title Banner
        banner = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        banner.pack(fill="x", pady=(0, 14))

        banner_inner = ctk.CTkFrame(banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=16, pady=12)

        title_row = ctk.CTkFrame(banner_inner, fg_color="transparent")
        title_row.pack(fill="x")

        icon_lbl = ctk.CTkLabel(
            title_row, text="",
            image=self._get_icon("settings", (20, 20), THEME_COLORS["primary"])
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="EXPEDUP ENGINE & ENVIRONMENT CONFIGURATION",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            banner_inner,
            text="Fine-tune network evasion, reconnaissance depth, target platforms, storage paths, and auto-export behavior.",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w", pady=(4, 0))

        # ---------------------------------------------------------------------
        # 1. Interface & Workflow Card
        # ---------------------------------------------------------------------
        card_general = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_general.pack(fill="x", pady=(0, 14))

        inner_general = ctk.CTkFrame(card_general, fg_color="transparent")
        inner_general.pack(fill="x", padx=16, pady=14)

        sec_header1 = ctk.CTkFrame(inner_general, fg_color="transparent")
        sec_header1.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            sec_header1, text="",
            image=self._get_icon("target", (16, 16), THEME_COLORS["primary"])
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            sec_header1, text="INTERFACE & WORKFLOW",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        grid_gen = ctk.CTkFrame(inner_general, fg_color="transparent")
        grid_gen.pack(fill="x")
        grid_gen.grid_columnconfigure(0, weight=1)
        grid_gen.grid_columnconfigure(1, weight=1)

        # Theme selection
        box_theme = ctk.CTkFrame(grid_gen, fg_color="transparent")
        box_theme.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(
            box_theme, text="Interface Appearance Theme",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            box_theme, text="Choose default visual appearance (Light default, dual-token contrast).",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 6))

        self.setting_var_theme = ctk.StringVar(value=self.settings.get("theme", "Light"))
        self.seg_setting_theme = ctk.CTkSegmentedButton(
            box_theme, values=["Light", "Dark"],
            variable=self.setting_var_theme,
            command=self._on_setting_theme_change,
            selected_color=THEME_COLORS["primary"],
            selected_hover_color=THEME_COLORS["primary_hover"],
            unselected_color=THEME_COLORS["card"],
            unselected_hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.seg_setting_theme.pack(fill="x")

        # Default Depth selection
        box_depth = ctk.CTkFrame(grid_gen, fg_color="transparent")
        box_depth.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(
            box_depth, text="Default Reconnaissance Depth",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            box_depth, text="Standard performs fast single-index scan; Deep engages Bing & cross-engines.",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 6))

        self.setting_var_depth = ctk.StringVar(value=self.settings.get("default_depth", "Deep (Multi-Engine)"))
        self.seg_setting_depth = ctk.CTkSegmentedButton(
            box_depth, values=["Standard", "Deep (Multi-Engine)"],
            variable=self.setting_var_depth,
            selected_color=THEME_COLORS["primary"],
            selected_hover_color=THEME_COLORS["primary_hover"],
            unselected_color=THEME_COLORS["card"],
            unselected_hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.seg_setting_depth.pack(fill="x")

        # ---------------------------------------------------------------------
        # 2. Dossier Storage & Auto-Export Card
        # ---------------------------------------------------------------------
        card_storage = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_storage.pack(fill="x", pady=(0, 14))

        inner_storage = ctk.CTkFrame(card_storage, fg_color="transparent")
        inner_storage.pack(fill="x", padx=16, pady=14)

        sec_header2 = ctk.CTkFrame(inner_storage, fg_color="transparent")
        sec_header2.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            sec_header2, text="",
            image=self._get_icon("folder", (16, 16), THEME_COLORS["primary"])
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            sec_header2, text="DOSSIER STORAGE & AUTO-EXPORT",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            inner_storage, text="Default Export Directory",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(anchor="w")

        dir_row = ctk.CTkFrame(inner_storage, fg_color="transparent")
        dir_row.pack(fill="x", pady=(4, 10))

        self.setting_var_export_dir = ctk.StringVar(value=self.settings.get("export_dir", DEFAULT_EXPORT_DIR))
        self.entry_setting_export_dir = ctk.CTkEntry(
            dir_row, textvariable=self.setting_var_export_dir,
            height=34, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.entry_setting_export_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            dir_row, text="  Browse Folder...",
            image=self._get_icon("folder", (14, 14), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._browse_export_dir,
            height=34, width=140,
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"],
            font=ctk.CTkFont(size=11)
        ).pack(side="right")

        # Auto-export toggle
        self.setting_var_auto_export = ctk.BooleanVar(value=bool(self.settings.get("auto_export_all", False)))
        self.switch_setting_auto_export = ctk.CTkSwitch(
            inner_storage,
            text="Automatically export full dossier suite (Markdown, CSV, JSON) upon expedition completion",
            variable=self.setting_var_auto_export,
            font=ctk.CTkFont(size=11),
            progress_color=THEME_COLORS["primary"]
        )
        self.switch_setting_auto_export.pack(anchor="w", pady=(2, 0))

        # ---------------------------------------------------------------------
        # 3. Stealth, Rate Limiting & Evasion Card
        # ---------------------------------------------------------------------
        card_stealth = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_stealth.pack(fill="x", pady=(0, 14))

        inner_stealth = ctk.CTkFrame(card_stealth, fg_color="transparent")
        inner_stealth.pack(fill="x", padx=16, pady=14)

        sec_header3 = ctk.CTkFrame(inner_stealth, fg_color="transparent")
        sec_header3.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            sec_header3, text="",
            image=self._get_icon("bolt", (16, 16), THEME_COLORS["primary"])
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            sec_header3, text="STEALTH, NETWORK & EVASION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        grid_sliders = ctk.CTkFrame(inner_stealth, fg_color="transparent")
        grid_sliders.pack(fill="x", pady=(0, 10))
        grid_sliders.grid_columnconfigure((0, 1, 2), weight=1)

        # Timeout slider
        box_timeout = ctk.CTkFrame(grid_sliders, fg_color="transparent")
        box_timeout.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lbl_to_row = ctk.CTkFrame(box_timeout, fg_color="transparent")
        lbl_to_row.pack(fill="x")
        ctk.CTkLabel(
            lbl_to_row, text="Request Timeout",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(side="left")
        self.lbl_timeout_val = ctk.CTkLabel(
            lbl_to_row, text=f"{int(self.settings.get('request_timeout', 12))}s",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        self.lbl_timeout_val.pack(side="right")

        self.slider_timeout = ctk.CTkSlider(
            box_timeout, from_=3, to=30, number_of_steps=27,
            command=self._on_timeout_slider_change,
            progress_color=THEME_COLORS["primary"],
            button_color=THEME_COLORS["primary"],
            button_hover_color=THEME_COLORS["primary_hover"]
        )
        self.slider_timeout.set(int(self.settings.get("request_timeout", 12)))
        self.slider_timeout.pack(fill="x", pady=(6, 0))

        # Min delay slider
        box_min_delay = ctk.CTkFrame(grid_sliders, fg_color="transparent")
        box_min_delay.grid(row=0, column=1, sticky="nsew", padx=(4, 4))
        lbl_min_row = ctk.CTkFrame(box_min_delay, fg_color="transparent")
        lbl_min_row.pack(fill="x")
        ctk.CTkLabel(
            lbl_min_row, text="Min Query Delay",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(side="left")
        self.lbl_min_delay_val = ctk.CTkLabel(
            lbl_min_row, text=f"{float(self.settings.get('min_delay', 0.8)):.1f}s",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        self.lbl_min_delay_val.pack(side="right")

        self.slider_min_delay = ctk.CTkSlider(
            box_min_delay, from_=0.1, to=3.0, number_of_steps=29,
            command=self._on_min_delay_slider_change,
            progress_color=THEME_COLORS["primary"],
            button_color=THEME_COLORS["primary"],
            button_hover_color=THEME_COLORS["primary_hover"]
        )
        self.slider_min_delay.set(float(self.settings.get("min_delay", 0.8)))
        self.slider_min_delay.pack(fill="x", pady=(6, 0))

        # Max delay slider
        box_max_delay = ctk.CTkFrame(grid_sliders, fg_color="transparent")
        box_max_delay.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        lbl_max_row = ctk.CTkFrame(box_max_delay, fg_color="transparent")
        lbl_max_row.pack(fill="x")
        ctk.CTkLabel(
            lbl_max_row, text="Max Query Delay",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_primary"]
        ).pack(side="left")
        self.lbl_max_delay_val = ctk.CTkLabel(
            lbl_max_row, text=f"{float(self.settings.get('max_delay', 1.4)):.1f}s",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["primary"]
        )
        self.lbl_max_delay_val.pack(side="right")

        self.slider_max_delay = ctk.CTkSlider(
            box_max_delay, from_=0.5, to=5.0, number_of_steps=45,
            command=self._on_max_delay_slider_change,
            progress_color=THEME_COLORS["primary"],
            button_color=THEME_COLORS["primary"],
            button_hover_color=THEME_COLORS["primary_hover"]
        )
        self.slider_max_delay.set(float(self.settings.get("max_delay", 1.4)))
        self.slider_max_delay.pack(fill="x", pady=(6, 0))

        # User-Agent rotation switch
        self.setting_var_ua_rotation = ctk.BooleanVar(value=bool(self.settings.get("user_agent_rotation", True)))
        self.switch_setting_ua_rotation = ctk.CTkSwitch(
            inner_stealth,
            text="Rotate modern browser User-Agent fingerprints per probe to minimize anti-bot triggers",
            variable=self.setting_var_ua_rotation,
            font=ctk.CTkFont(size=11),
            progress_color=THEME_COLORS["primary"]
        )
        self.switch_setting_ua_rotation.pack(anchor="w", pady=(8, 0))

        # ---------------------------------------------------------------------
        # 4. Social Platform Coverage Matrix Card
        # ---------------------------------------------------------------------
        card_platforms = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_platforms.pack(fill="x", pady=(0, 14))

        inner_platforms = ctk.CTkFrame(card_platforms, fg_color="transparent")
        inner_platforms.pack(fill="x", padx=16, pady=14)

        sec_header4 = ctk.CTkFrame(inner_platforms, fg_color="transparent")
        sec_header4.pack(fill="x", pady=(0, 6))

        left_hdr4 = ctk.CTkFrame(sec_header4, fg_color="transparent")
        left_hdr4.pack(side="left")
        ctk.CTkLabel(
            left_hdr4, text="",
            image=self._get_icon("users", (16, 16), THEME_COLORS["primary"])
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            left_hdr4, text="SOCIAL & IDENTITY PLATFORM MATRIX",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        right_hdr4 = ctk.CTkFrame(sec_header4, fg_color="transparent")
        right_hdr4.pack(side="right")

        ctk.CTkButton(
            right_hdr4, text="Select All", width=74, height=24,
            command=self._select_all_platforms,
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            right_hdr4, text="Deselect All", width=74, height=24,
            command=self._deselect_all_platforms,
            font=ctk.CTkFont(size=10),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        ).pack(side="left")

        ctk.CTkLabel(
            inner_platforms,
            text=f"Target platforms probed for identity existence and OpenGraph metadata ({len(SOCIAL_PLATFORMS)} available).",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 10))

        # Checkbox matrix (3 columns)
        self.setting_platform_vars = {}
        enabled_list = set(self.settings.get("enabled_platforms", [p["name"] for p in SOCIAL_PLATFORMS]))

        grid_plats = ctk.CTkFrame(inner_platforms, fg_color="transparent")
        grid_plats.pack(fill="x")
        for c in range(3):
            grid_plats.grid_columnconfigure(c, weight=1)

        for i, plat in enumerate(SOCIAL_PLATFORMS):
            pname = plat["name"]
            pcat = plat.get("category", "")
            r = i // 3
            c = i % 3

            var = ctk.BooleanVar(value=(pname in enabled_list))
            self.setting_platform_vars[pname] = var

            box = ctk.CTkCheckBox(
                grid_plats,
                text=f"{pname} ({pcat})",
                variable=var,
                font=ctk.CTkFont(size=11),
                text_color=THEME_COLORS["text_primary"],
                checkmark_color="#ffffff",
                fg_color=THEME_COLORS["primary"],
                hover_color=THEME_COLORS["primary_hover"],
                border_color=THEME_COLORS["border"]
            )
            box.grid(row=r, column=c, sticky="w", padx=6, pady=4)

        # ---------------------------------------------------------------------
        # 5. Domain TLD Extensions Card
        # ---------------------------------------------------------------------
        card_tlds = ctk.CTkFrame(
            scroll_settings, corner_radius=10,
            fg_color=THEME_COLORS["card_subtle"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        card_tlds.pack(fill="x", pady=(0, 14))

        inner_tlds = ctk.CTkFrame(card_tlds, fg_color="transparent")
        inner_tlds.pack(fill="x", padx=16, pady=14)

        sec_header5 = ctk.CTkFrame(inner_tlds, fg_color="transparent")
        sec_header5.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            sec_header5, text="",
            image=self._get_icon("world", (16, 16), THEME_COLORS["primary"])
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            sec_header5, text="DOMAIN & DNS RECONNAISSANCE EXTENSIONS (TLDs)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME_COLORS["primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            inner_tlds,
            text="Comma-separated Top-Level Domains (TLDs) to probe for target name registration and web presence.",
            font=ctk.CTkFont(size=10), text_color=THEME_COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 6))

        tld_list = self.settings.get("domain_tlds", DOMAIN_TLDS)
        self.setting_var_tlds = ctk.StringVar(value=", ".join(tld_list))
        self.entry_setting_tlds = ctk.CTkEntry(
            inner_tlds, textvariable=self.setting_var_tlds,
            height=34, fg_color=THEME_COLORS["input_bg"],
            border_color=THEME_COLORS["border"],
            text_color=THEME_COLORS["text_primary"]
        )
        self.entry_setting_tlds.pack(fill="x", pady=(0, 4))

        # ---------------------------------------------------------------------
        # 6. Action Buttons & Feedback Bar
        # ---------------------------------------------------------------------
        action_bar = ctk.CTkFrame(scroll_settings, fg_color="transparent")
        action_bar.pack(fill="x", pady=(6, 14))

        self.btn_save_settings = ctk.CTkButton(
            action_bar, text="  Save & Apply Settings",
            image=self._get_icon("circle-check", (16, 16), "#ffffff"),
            compound="left",
            command=self._save_settings_action,
            height=38, font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME_COLORS["primary"],
            hover_color=THEME_COLORS["primary_hover"],
            text_color="#ffffff"
        )
        self.btn_save_settings.pack(side="left", padx=(0, 10))

        self.btn_reset_settings = ctk.CTkButton(
            action_bar, text="  Reset to Factory Defaults",
            image=self._get_icon("refresh", (14, 14), THEME_COLORS["secondary_text"]),
            compound="left",
            command=self._reset_settings_action,
            height=38, font=ctk.CTkFont(size=11),
            fg_color=THEME_COLORS["secondary"],
            hover_color=THEME_COLORS["secondary_hover"],
            text_color=THEME_COLORS["secondary_text"],
            border_width=1, border_color=THEME_COLORS["border"]
        )
        self.btn_reset_settings.pack(side="left")

        # Toast status message
        self.lbl_settings_toast = ctk.CTkLabel(
            scroll_settings, text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["success"]
        )
        self.lbl_settings_toast.pack(fill="x", pady=(0, 10))

    # -------------------------------------------------------------------------
    # Settings Event Handlers & Persistent Actions
    # -------------------------------------------------------------------------
    def _on_timeout_slider_change(self, val):
        self.lbl_timeout_val.configure(text=f"{int(val)}s")

    def _on_min_delay_slider_change(self, val):
        self.lbl_min_delay_val.configure(text=f"{float(val):.1f}s")
        if self.slider_max_delay.get() < val:
            self.slider_max_delay.set(val)
            self.lbl_max_delay_val.configure(text=f"{float(val):.1f}s")

    def _on_max_delay_slider_change(self, val):
        self.lbl_max_delay_val.configure(text=f"{float(val):.1f}s")
        if self.slider_min_delay.get() > val:
            self.slider_min_delay.set(val)
            self.lbl_min_delay_val.configure(text=f"{float(val):.1f}s")

    def _on_setting_theme_change(self, val):
        ctk.set_appearance_mode(val)
        if val == "Dark":
            self.appearance_switch.select()
            self.appearance_switch.configure(text="Dark Mode")
        else:
            self.appearance_switch.deselect()
            self.appearance_switch.configure(text="Light Mode")

    def _select_all_platforms(self):
        for var in self.setting_platform_vars.values():
            var.set(True)

    def _deselect_all_platforms(self):
        for var in self.setting_platform_vars.values():
            var.set(False)

    def _browse_export_dir(self):
        current_dir = self.setting_var_export_dir.get() or DEFAULT_EXPORT_DIR
        chosen = filedialog.askdirectory(initialdir=os.path.abspath(current_dir))
        if chosen:
            self.setting_var_export_dir.set(chosen)

    def _save_settings_action(self):
        """Save settings to disk and apply across active application state."""
        try:
            # Parse TLDs
            raw_tlds = self.setting_var_tlds.get().split(",")
            clean_tlds = []
            for t in raw_tlds:
                t = t.strip()
                if t:
                    if not t.startswith("."):
                        t = f".{t}"
                    clean_tlds.append(t)
            if not clean_tlds:
                clean_tlds = list(DOMAIN_TLDS)

            # Enabled platforms
            enabled_plats = [p for p, v in self.setting_platform_vars.items() if v.get()]
            if not enabled_plats:
                enabled_plats = [p["name"] for p in SOCIAL_PLATFORMS]
                for v in self.setting_platform_vars.values():
                    v.set(True)

            payload = {
                "theme": self.setting_var_theme.get(),
                "default_depth": self.setting_var_depth.get(),
                "export_dir": self.setting_var_export_dir.get().strip() or DEFAULT_EXPORT_DIR,
                "auto_export_all": bool(self.setting_var_auto_export.get()),
                "request_timeout": int(self.slider_timeout.get()),
                "min_delay": round(float(self.slider_min_delay.get()), 2),
                "max_delay": round(float(self.slider_max_delay.get()), 2),
                "user_agent_rotation": bool(self.setting_var_ua_rotation.get()),
                "enabled_platforms": enabled_plats,
                "domain_tlds": clean_tlds
            }

            self.settings = save_settings(payload)

            # Apply theme immediately
            ctk.set_appearance_mode(payload["theme"])
            if payload["theme"] == "Dark":
                self.appearance_switch.select()
                self.appearance_switch.configure(text="Dark Mode")
            else:
                self.appearance_switch.deselect()
                self.appearance_switch.configure(text="Light Mode")

            # Apply default depth
            self.seg_depth.set(payload["default_depth"])

            self.lbl_settings_toast.configure(
                text="✓ Settings saved and applied successfully!",
                text_color=THEME_COLORS["success"]
            )
            self._on_log_message("[SETTINGS] Configuration successfully saved to settings.json and applied.")

        except Exception as e:
            self.lbl_settings_toast.configure(
                text=f"Failed to save settings: {e}",
                text_color=THEME_COLORS["danger"]
            )
            self._on_log_message(f"[SETTINGS ERROR] {e}")

    def _reset_settings_action(self):
        """Reset configuration back to defaults and refresh form fields."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to factory defaults?"):
            self.settings = reset_to_defaults()

            # Refresh form variables
            self.setting_var_theme.set(self.settings["theme"])
            self.seg_setting_theme.set(self.settings["theme"])
            self.setting_var_depth.set(self.settings["default_depth"])
            self.seg_setting_depth.set(self.settings["default_depth"])
            self.setting_var_export_dir.set(self.settings["export_dir"])
            self.entry_setting_export_dir.delete(0, "end")
            self.entry_setting_export_dir.insert(0, self.settings["export_dir"])
            self.setting_var_auto_export.set(self.settings["auto_export_all"])

            self.slider_timeout.set(self.settings["request_timeout"])
            self.lbl_timeout_val.configure(text=f"{self.settings['request_timeout']}s")

            self.slider_min_delay.set(self.settings["min_delay"])
            self.lbl_min_delay_val.configure(text=f"{self.settings['min_delay']:.1f}s")

            self.slider_max_delay.set(self.settings["max_delay"])
            self.lbl_max_delay_val.configure(text=f"{self.settings['max_delay']:.1f}s")

            self.setting_var_ua_rotation.set(self.settings["user_agent_rotation"])

            for pname, var in self.setting_platform_vars.items():
                var.set(pname in self.settings["enabled_platforms"])

            self.setting_var_tlds.set(", ".join(self.settings["domain_tlds"]))

            # Apply theme and depth to app
            ctk.set_appearance_mode(self.settings["theme"])
            if self.settings["theme"] == "Dark":
                self.appearance_switch.select()
                self.appearance_switch.configure(text="Dark Mode")
            else:
                self.appearance_switch.deselect()
                self.appearance_switch.configure(text="Light Mode")

            self.seg_depth.set(self.settings["default_depth"])

            self.lbl_settings_toast.configure(
                text="✓ Settings reset to factory defaults.",
                text_color=THEME_COLORS["accent"]
            )
            self._on_log_message("[SETTINGS] Settings reset to factory defaults.")

    # -------------------------------------------------------------------------
    # Engine Execution & Thread Callbacks
    # -------------------------------------------------------------------------
    def _start_expedition(self):
        """Initiate deep search expedition in a background thread."""
        target = self.entry_target.get().strip()
        if not target:
            messagebox.showwarning("Target Required", "Please enter a target name, brand, or handle to begin.")
            return

        location = self.entry_location.get().strip()
        category = self.entry_category.get().strip()
        phone = self.entry_phone.get().strip()
        depth = "Deep" if "Deep" in self.seg_depth.get() else "Standard"
        strict_keyword = bool(self.switch_strict_keyword.get())

        # Reset UI & State
        self._reset_dashboard_results()
        self.is_running = True
        self.btn_launch.configure(
            state="disabled",
            text="  Probing Target...",
            image=self._get_icon("loader", (16, 16), "#ffffff")
        )
        self.btn_stop.configure(state="normal")
        self.status_pill.configure(
            text="  RECONNAISSANCE ACTIVE",
            image=self._get_icon("loader", (12, 12), THEME_COLORS["warning"]),
            text_color=THEME_COLORS["warning"],
            fg_color=THEME_COLORS["card_subtle"]
        )
        self.prog_bar.set(0.0)
        self.lbl_progress_status.configure(text=f"Initializing probe matrix for '{target}'...")

        # Instantiate engine with user configuration
        self.engine = ExpedUPEngine(
            log_cb=self._on_log_message,
            progress_cb=self._on_progress_update,
            result_cb=self._on_result_item,
            settings=self.settings
        )

        # Spawn background worker thread
        self.worker_thread = threading.Thread(
            target=self._run_engine_worker,
            args=(target, location, category, phone, depth, strict_keyword),
            daemon=True
        )
        self.worker_thread.start()

    def _run_engine_worker(self, target: str, location: str, category: str, phone: str, depth: str, strict_keyword: bool = False):
        """Background thread worker function."""
        try:
            results = self.engine.run_expedition(
                target=target,
                location=location,
                category=category,
                phone=phone,
                deep_level=depth,
                strict_keyword=strict_keyword
            )
            self.current_results = results
        except Exception as e:
            self._on_log_message(f"[ERROR] Expedition exception: {e}")
        finally:
            self.after(0, self._on_expedition_complete)

    def _stop_expedition(self):
        """Signal engine cancellation."""
        if self.engine:
            self.engine.stop()
            self.lbl_progress_status.configure(text="Cancelling expedition...")
            self.btn_stop.configure(state="disabled")

    def _on_expedition_complete(self):
        """Called on Tkinter thread when background expedition finishes."""
        self.is_running = False
        self.btn_launch.configure(
            state="normal",
            text="  Launch Expedition",
            image=self._get_icon("play", (16, 16), "#ffffff")
        )
        self.btn_stop.configure(state="disabled")

        if self.engine and self.engine.stop_requested:
            self.status_pill.configure(
                text="  MISSION ABORTED",
                image=self._get_icon("stop", (12, 12), THEME_COLORS["danger"]),
                text_color=THEME_COLORS["danger"],
                fg_color=THEME_COLORS["card_subtle"]
            )
            self.lbl_progress_status.configure(text="Expedition stopped by user.")
        else:
            self.status_pill.configure(
                text="  MISSION COMPLETE",
                image=self._get_icon("circle-check", (12, 12), THEME_COLORS["success"]),
                text_color=THEME_COLORS["success"],
                fg_color=THEME_COLORS["card_subtle"]
            )
            self.prog_bar.set(1.0)
            self.lbl_progress_status.configure(text="Expedition completed successfully.")

        # Update Live Markdown Dossier preview
        self._refresh_dossier_preview()

    # -------------------------------------------------------------------------
    # Real-Time Event Dispatchers (Thread Safe)
    # -------------------------------------------------------------------------
    def _on_log_message(self, message: str):
        """Safely append message to terminal."""
        def _append():
            self.txt_console.insert("end", f"{message}\n")
            if self.auto_scroll_logs:
                self.txt_console.see("end")
        self.after(0, _append)

    def _on_progress_update(self, current: int, total: int, status: str):
        """Safely update progress bar and status text."""
        def _update():
            fraction = min(1.0, max(0.0, current / max(1, total)))
            self.prog_bar.set(fraction)
            self.lbl_progress_status.configure(text=f"[{current}/{total}] {status}")
        self.after(0, _update)

    def _on_result_item(self, category: str, item: Any):
        """Safely dispatch discovered item to appropriate tab and KPI counter."""
        def _dispatch():
            if category == "search":
                self.current_results["search_results"].append(item)
                count = len(self.current_results["search_results"])
                self.kpi_labels["search"].configure(text=str(count))
                self.lbl_search_count.configure(text=f"{count} search results indexed.")
                self._render_search_item(item)

            elif category == "social":
                self.current_results["social_profiles"].append(item)
                active_count = len([p for p in self.current_results["social_profiles"] if p.get("exists")])
                self.kpi_labels["social"].configure(text=str(active_count))
                self.lbl_social_count.configure(text=f"{active_count} verified active social profiles discovered.")
                self._render_social_item(item)

            elif category == "domain":
                self.current_results["domains"].append(item)
                active_doms = len([d for d in self.current_results["domains"] if d.get("is_registered")])
                self.kpi_labels["domains"].configure(text=str(active_doms))
                self._render_domain_item(item)

            elif category == "entity":
                etype = item.get("type")
                evalue = item.get("value")
                if etype == "phone":
                    self.current_results["entities"]["phones"].add(evalue)
                    self.kpi_labels["phones"].configure(text=str(len(self.current_results["entities"]["phones"])))
                    self._render_phone_item(evalue)

                elif etype == "email":
                    self.current_results["entities"]["emails"].add(evalue)
                    self.kpi_labels["emails"].configure(text=str(len(self.current_results["entities"]["emails"])))
                    self._render_email_item(evalue)

                elif etype == "mention":
                    self.current_results["entities"]["mentions"].add(evalue)
                    mentions = self.current_results["entities"]["mentions"]
                    self.txt_mentions.delete("1.0", "end")
                    self.txt_mentions.insert("1.0", ", ".join(sorted(mentions)))
                    self._update_mentions_kpi()

                elif etype == "hashtag":
                    self.current_results["entities"]["hashtags"].add(evalue)
                    hashtags = self.current_results["entities"]["hashtags"]
                    self.txt_hashtags.delete("1.0", "end")
                    self.txt_hashtags.insert("1.0", ", ".join(sorted(hashtags)))
                    self._update_mentions_kpi()

        self.after(0, _dispatch)

    def _update_mentions_kpi(self):
        """Update KPI count for handles and hashtags combined."""
        m_count = len(self.current_results["entities"]["mentions"])
        h_count = len(self.current_results["entities"]["hashtags"])
        self.kpi_labels["mentions"].configure(text=str(m_count + h_count))

    def _update_intelligence_overview(self):
        """Update the executive overview intelligence cards."""
        try:
            intel = self.current_results.get("intelligence")
            if not intel:
                from intelligence_synthesizer import synthesize_intelligence
                target = self.current_results.get("target") or self.entry_target.get().strip() or "Target"
                intel = synthesize_intelligence(target, self.current_results)
                self.current_results["intelligence"] = intel

            bc = intel.get("brand_clearance", {})
            bp = intel.get("business_profile", {})
            dr = intel.get("digital_roadmap", {})

            score = bc.get("uniqueness_score", 0)
            rating = bc.get("clearance_rating", "")
            score_color = THEME_COLORS["success"] if score >= 80 else (THEME_COLORS["warning"] if score >= 50 else THEME_COLORS["danger"])
            self.lbl_clearance_score.configure(
                text=f"Score: {score}/100 — {rating}",
                text_color=score_color
            )
            self.lbl_clearance_verdict.configure(
                text=f"{bc.get('verdict', '')}\nHandles: {bc.get('handle_collision_rate', 'N/A')} | Domains: {bc.get('domain_collision_rate', 'N/A')}"
            )

            op_base = bp.get("operating_base", "Global / Digital Operations")
            mobility = bp.get("mobility_model", "On-site")
            services = bp.get("services", [])
            srv_str = ", ".join([s.get("service", "") for s in services[:3]])
            contact = bp.get("primary_contact", "N/A")

            self.lbl_biz_base.configure(
                text=f"Base: {op_base}"
            )
            self.lbl_biz_details.configure(
                text=f"Mobility: {mobility}\nPrimary Contact: {contact}\nServices: {srv_str or 'General Commercial'}\nRecommended Modules: {len(dr.get('recommended_platform_modules', []))} platform components"
            )
        except Exception as e:
            pass

    def _refresh_dossier_preview(self):
        """Generate and display markdown dossier text and intelligence highlights."""
        self._update_intelligence_overview()
        dossier_md = generate_markdown_dossier(self.current_results)
        self.txt_dossier_preview.delete("1.0", "end")
        self.txt_dossier_preview.insert("1.0", dossier_md)

    # -------------------------------------------------------------------------
    # Resets & Utility Actions
    # -------------------------------------------------------------------------
    def _clear_inputs(self):
        """Clear all parameter input fields."""
        self.entry_target.delete(0, "end")
        self.entry_location.delete(0, "end")
        self.entry_category.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.switch_strict_keyword.deselect()

    def _reset_dashboard_results(self):
        """Reset dashboard counters and clear container widgets."""
        self.current_results = {
            "target": self.entry_target.get().strip(),
            "location": self.entry_location.get().strip(),
            "category": self.entry_category.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "timestamp": "",
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
        for k in self.kpi_labels:
            self.kpi_labels[k].configure(text="0")

        self.lbl_clearance_score.configure(
            text="Uniqueness Score: --/100",
            text_color=THEME_COLORS["text_primary"]
        )
        self.lbl_clearance_verdict.configure(
            text="Launch an expedition to assess handle collisions and name availability."
        )
        self.lbl_biz_base.configure(
            text="Operating Base: --"
        )
        self.lbl_biz_details.configure(
            text="Services, WhatsApp contacts, and architectural blueprint will be synthesized."
        )

        # Clear search cards
        for widget in self.search_scroll_frame.winfo_children():
            widget.destroy()
        self.lbl_search_count.configure(text="0 search results indexed.")

        # Clear social cards
        for widget in self.social_scroll_frame.winfo_children():
            widget.destroy()
        self.lbl_social_count.configure(text="0 active social profiles discovered.")

        # Clear entities lists
        for widget in self.frame_phones_list.winfo_children():
            widget.destroy()
        self.lbl_no_phones = ctk.CTkLabel(
            self.frame_phones_list, text="No phone numbers discovered yet.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_phones.pack(anchor="w")

        for widget in self.frame_emails_list.winfo_children():
            widget.destroy()
        self.lbl_no_emails = ctk.CTkLabel(
            self.frame_emails_list, text="No email addresses discovered yet.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_emails.pack(anchor="w")

        self.txt_mentions.delete("1.0", "end")
        self.txt_hashtags.delete("1.0", "end")

        for widget in self.frame_domains_list.winfo_children():
            widget.destroy()
        self.lbl_no_domains = ctk.CTkLabel(
            self.frame_domains_list, text="No registered domains detected for standard TLDs.",
            font=ctk.CTkFont(size=11), text_color=THEME_COLORS["text_muted"]
        )
        self.lbl_no_domains.pack(anchor="w")

    # -------------------------------------------------------------------------
    # Export Actions
    # -------------------------------------------------------------------------
    def _export_data(self, fmt: str):
        """Export current reconnaissance findings."""
        if not self.current_results.get("target"):
            messagebox.showwarning("No Data", "Please execute an expedition before exporting.")
            return

        out_dir = self.settings.get("export_dir", DEFAULT_EXPORT_DIR) if hasattr(self, "settings") else DEFAULT_EXPORT_DIR
        os.makedirs(out_dir, exist_ok=True)
        target = self.current_results.get("target", "Target")
        import time
        stamp = time.strftime("%Y%m%d_%H%M%S")

        try:
            if fmt == "all":
                paths = export_all_formats(self.current_results, out_dir)
                self.lbl_export_toast.configure(
                    text=f"✓ All dossiers exported to:\n{out_dir}",
                    text_color=THEME_COLORS["success"]
                )
                self._on_log_message(f"[EXPORT] Exported full suite to {out_dir}")

            elif fmt == "md":
                path = os.path.join(out_dir, f"ExpedUP_{target}_{stamp}.md")
                export_markdown_file(self.current_results, path)
                self.lbl_export_toast.configure(
                    text=f"✓ Markdown exported: {os.path.basename(path)}",
                    text_color=THEME_COLORS["success"]
                )
                self._on_log_message(f"[EXPORT] Markdown saved: {path}")

            elif fmt == "csv":
                path = os.path.join(out_dir, f"ExpedUP_{target}_{stamp}.csv")
                export_csv_file(self.current_results, path)
                self.lbl_export_toast.configure(
                    text=f"✓ CSV exported: {os.path.basename(path)}",
                    text_color=THEME_COLORS["success"]
                )
                self._on_log_message(f"[EXPORT] CSV saved: {path}")

            elif fmt == "json":
                path = os.path.join(out_dir, f"ExpedUP_{target}_{stamp}.json")
                export_json_file(self.current_results, path)
                self.lbl_export_toast.configure(
                    text=f"✓ JSON exported: {os.path.basename(path)}",
                    text_color=THEME_COLORS["success"]
                )
                self._on_log_message(f"[EXPORT] JSON saved: {path}")

        except Exception as e:
            self.lbl_export_toast.configure(
                text=f"Export failed: {e}",
                text_color=THEME_COLORS["danger"]
            )
            self._on_log_message(f"[EXPORT ERROR] {e}")

    def _open_export_dir(self):
        """Open configured output directory in OS file manager."""
        target_dir = self.settings.get("export_dir", DEFAULT_EXPORT_DIR) if hasattr(self, "settings") else DEFAULT_EXPORT_DIR
        out_dir = os.path.abspath(target_dir)
        os.makedirs(out_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(out_dir)
        else:
            webbrowser.open(f"file://{out_dir}")

    # -------------------------------------------------------------------------
    # Clipboard & Appearance Helpers
    # -------------------------------------------------------------------------
    def _copy_to_clipboard(self, text: str):
        """Copy arbitrary string to system clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.lbl_export_toast.configure(
            text=f"✓ Copied: '{text[:25]}...'",
            text_color=THEME_COLORS["accent"]
        )

    def _copy_dossier_to_clipboard(self):
        """Copy generated markdown dossier to clipboard."""
        dossier_text = self.txt_dossier_preview.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(dossier_text)
        self.update()
        self.lbl_export_toast.configure(
            text="✓ Intelligence Dossier copied to clipboard!",
            text_color=THEME_COLORS["success"]
        )

    def _copy_logs_to_clipboard(self):
        """Copy console logs to clipboard."""
        logs = self.txt_console.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(logs)
        self.update()

    def _clear_console(self):
        """Clear console logs."""
        self.txt_console.delete("1.0", "end")
        self.txt_console.insert("end", "[EXPEDUP SYSTEM] Console Cleared.\n")

    def _toggle_appearance(self):
        """Toggle dark/light appearance theme natively across all dual-token widgets."""
        val = self.appearance_switch.get()
        ctk.set_appearance_mode(val)
        self.appearance_switch.configure(text="Dark Mode" if val == "Dark" else "Light Mode")

        # Keep Settings Tab controls and persistent config in sync
        if hasattr(self, "setting_var_theme"):
            self.setting_var_theme.set(val)
        if hasattr(self, "seg_setting_theme"):
            self.seg_setting_theme.set(val)
        if hasattr(self, "settings"):
            self.settings["theme"] = val
            save_settings(self.settings)

        self._on_log_message(f"[THEME] Interface appearance switched to: {val} Mode")


def run_gui():
    """Entry function to launch the GUI application."""
    app = ExpedUPApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
