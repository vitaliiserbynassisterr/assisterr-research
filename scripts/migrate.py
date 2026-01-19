#!/usr/bin/env python3
"""
Migration script: Extract metadata from current index.html and restructure repo.

Run from repo root:
  python scripts/migrate.py

Actions:
1. Parse current index.html to extract report metadata
2. Create config/reports.json with all metadata
3. Move HTML files to reports/ folder
4. Backup original index.html
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser

BASE_DIR = Path(__file__).parent.parent
REPORTS_DIR = BASE_DIR / "reports"
CONFIG_DIR = BASE_DIR / "config"


class ReportCardParser(HTMLParser):
    """Parse report cards from index.html"""

    def __init__(self):
        super().__init__()
        self.reports = []
        self.current_report = None
        self.in_report_card = False
        self.in_title = False
        self.in_description = False
        self.in_badge = False
        self.current_badges = []
        self.current_badge_colors = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Detect report card link
        if tag == "a" and "report-card" in attrs_dict.get("class", ""):
            self.in_report_card = True
            href = attrs_dict.get("href", "")
            self.current_report = {
                "filename": href,
                "id": href.replace(".html", ""),
                "featured": "featured" in attrs_dict.get("class", ""),
                "badges": [],
                "badge_colors": []
            }
            self.current_badges = []
            self.current_badge_colors = []

        if self.in_report_card:
            if tag == "h3":
                self.in_title = True
            elif tag == "p" and not self.current_report.get("description"):
                self.in_description = True
            elif tag == "span" and "badge" in attrs_dict.get("class", ""):
                classes = attrs_dict.get("class", "").split()
                self.in_badge = True
                # Extract badge color
                for cls in classes:
                    if cls.startswith("badge-") and cls != "badge":
                        color = cls.replace("badge-", "")
                        if color in ["primary", "purple", "blue", "green", "pink"]:
                            self.current_badge_colors.append(color)
                        elif color in ["v1", "v2"]:
                            self.current_report["version"] = color.replace("v", "") + ".0"

    def handle_endtag(self, tag):
        if tag == "a" and self.in_report_card:
            self.in_report_card = False
            if self.current_report and self.current_report.get("filename"):
                self.current_report["badges"] = self.current_badges
                self.current_report["badge_colors"] = self.current_badge_colors[:len(self.current_badges)]
                self.reports.append(self.current_report)
            self.current_report = None

        if tag == "h3":
            self.in_title = False
        if tag == "p":
            self.in_description = False
        if tag == "span":
            self.in_badge = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.in_report_card and self.current_report:
            if self.in_title:
                self.current_report["title"] = data
            elif self.in_description and not self.current_report.get("description"):
                self.current_report["description"] = data
            elif self.in_badge and data not in ["v1.0", "v2.0", "v3.0"]:
                self.current_badges.append(data)


def extract_date_from_filename(filename):
    """Extract date from filename pattern like *-2026-01-19.html"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})\.html$', filename)
    return match.group(1) if match else "2026-01-15"


def determine_category(filename):
    """Determine category from filename prefix"""
    filename_lower = filename.lower()

    if "solana" in filename_lower or filename.startswith("SOLANA-"):
        return "solana"
    elif filename.startswith("SLM-") or "slm" in filename_lower:
        return "slm"
    elif filename.startswith("KYA-") or filename.startswith("X402-"):
        return "kya"
    elif filename.startswith("VC-") or filename.startswith("SERIES-A") or filename.startswith("FUNDING-") or "funding" in filename_lower or "investor" in filename_lower or "benchmark" in filename_lower:
        return "vc"
    elif filename.startswith("VERTICAL-") or "vertical" in filename_lower:
        return "vertical"
    elif "cross-chain" in filename_lower:
        return "cross-chain"
    elif filename.startswith("CEO-DEFI"):
        return "vertical"  # DeFi agents go to vertical
    elif filename.startswith("CEO-RESEARCH"):
        # Check content for category
        if "solana" in filename_lower or "vibe" in filename_lower:
            return "solana"
        elif "cross-chain" in filename_lower:
            return "cross-chain"
        else:
            return "solana"  # Default CEO research to solana
    else:
        return "slm"  # Default


def parse_index_html():
    """Parse current index.html and extract report metadata"""
    index_path = BASE_DIR / "index.html"

    with open(index_path, "r") as f:
        content = f.read()

    parser = ReportCardParser()
    parser.feed(content)

    # Deduplicate reports (they appear in both category and date views)
    seen = set()
    unique_reports = []
    for report in parser.reports:
        if report["filename"] not in seen:
            seen.add(report["filename"])
            # Add derived fields
            report["date"] = extract_date_from_filename(report["filename"])
            if "category" not in report:
                report["category"] = determine_category(report["filename"])
            if "version" not in report:
                report["version"] = "1.0" if report["date"] <= "2026-01-15" else "2.0"
            unique_reports.append(report)

    return unique_reports


def create_reports_json(reports):
    """Create config/reports.json from extracted metadata"""

    # Sort by date descending
    reports.sort(key=lambda x: x["date"], reverse=True)

    # Mark top 3 as featured (if not already)
    featured_count = sum(1 for r in reports if r.get("featured"))
    if featured_count < 3:
        for i, report in enumerate(reports[:3]):
            if not report.get("featured"):
                report["featured"] = True

    # Add featured labels
    for i, report in enumerate(reports):
        if report.get("featured"):
            if i == 0:
                report["featured_label"] = "NEW - Latest Research"
            else:
                report["featured_label"] = "Key Document"

    metadata = {
        "system_version": "3.3.0",
        "last_updated": datetime.now().isoformat(),
        "reports": reports,
        "categories": {
            "featured": {"name": "Featured Reports", "order": 0, "auto_select": "latest_3"},
            "solana": {"name": "Solana Ecosystem", "order": 1},
            "slm": {"name": "SLM & Edge AI Research", "order": 2},
            "vertical": {"name": "Vertical AI Agents", "order": 3},
            "kya": {"name": "Trust Infrastructure (KYA)", "order": 4},
            "vc": {"name": "Series A & VC Intelligence", "order": 5},
            "cross-chain": {"name": "Cross-Chain & Multi-Chain", "order": 6}
        },
        "stats": {
            "slm_market": "$64B",
            "ai_agent_market": "$150B",
            "target_valuation": "$50-100M",
            "vc_conflicts": "0"
        }
    }

    # Write to config/reports.json
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_DIR / "reports.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def move_html_files():
    """Move all HTML report files to reports/ folder"""
    REPORTS_DIR.mkdir(exist_ok=True)

    moved = 0
    for html_file in BASE_DIR.glob("*.html"):
        if html_file.name == "index.html":
            continue

        dest = REPORTS_DIR / html_file.name
        shutil.move(str(html_file), str(dest))
        moved += 1
        print(f"  Moved: {html_file.name} -> reports/")

    return moved


def backup_index():
    """Backup original index.html"""
    index_path = BASE_DIR / "index.html"
    backup_path = BASE_DIR / "index.html.backup"
    shutil.copy(str(index_path), str(backup_path))
    print(f"  Backed up: index.html -> index.html.backup")


def main():
    print("=" * 60)
    print("  Assisterr Research Repository Migration")
    print("=" * 60)
    print()

    # Step 1: Backup
    print("1. Backing up index.html...")
    backup_index()
    print()

    # Step 2: Parse current index
    print("2. Parsing current index.html...")
    reports = parse_index_html()
    print(f"  Found {len(reports)} unique reports")
    print()

    # Step 3: Create reports.json
    print("3. Creating config/reports.json...")
    metadata = create_reports_json(reports)
    print(f"  Created with {len(metadata['reports'])} reports")
    print()

    # Step 4: Move HTML files
    print("4. Moving HTML files to reports/...")
    moved = move_html_files()
    print(f"  Moved {moved} files")
    print()

    # Summary
    print("=" * 60)
    print("  Migration Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run: python build/generate-index.py")
    print("  2. Verify index.html looks correct")
    print("  3. Commit changes: git add . && git commit -m 'Restructure for automation'")
    print()

    # Show categories distribution
    print("Reports by category:")
    categories = {}
    for r in reports:
        cat = r.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
