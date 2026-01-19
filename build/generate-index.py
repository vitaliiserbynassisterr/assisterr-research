#!/usr/bin/env python3
"""
Generate index.html from config/reports.json and Jinja2 template.

Run from repo root:
  python build/generate-index.py

This script:
1. Loads config/reports.json (metadata registry)
2. Validates against config/reports.schema.json
3. Verifies all HTML files exist in reports/
4. Organizes reports by category and date
5. Renders the Jinja2 template
6. Writes index.html to repo root
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("ERROR: Jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("WARNING: jsonschema not installed. Skipping validation.")
    validate = None
    ValidationError = Exception

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_reports_json():
    """Load the reports registry"""
    reports_path = CONFIG_DIR / "reports.json"

    if not reports_path.exists():
        print(f"ERROR: {reports_path} not found. Run migration first.")
        sys.exit(1)

    with open(reports_path, "r") as f:
        return json.load(f)


def validate_schema(data):
    """Validate reports.json against schema"""
    if validate is None:
        return True

    schema_path = CONFIG_DIR / "reports.schema.json"
    if not schema_path.exists():
        print("WARNING: Schema file not found, skipping validation")
        return True

    with open(schema_path, "r") as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        print(f"ERROR: Schema validation failed: {e.message}")
        return False


def verify_html_files(reports):
    """Verify all referenced HTML files exist"""
    missing = []

    for report in reports:
        html_path = REPORTS_DIR / report["filename"]
        if not html_path.exists():
            missing.append(report["filename"])

    if missing:
        print(f"ERROR: Missing HTML files in reports/:")
        for f in missing:
            print(f"  - {f}")
        return False

    return True


def organize_by_category(reports, categories):
    """Group reports by category"""
    by_category = defaultdict(list)

    for report in reports:
        cat = report.get("category", "other")
        by_category[cat].append(report)

    # Sort categories by order
    sorted_categories = {}
    for cat_id, cat_info in sorted(categories.items(), key=lambda x: x[1].get("order", 99)):
        if cat_id in by_category:
            sorted_categories[cat_id] = {
                "info": cat_info,
                "reports": by_category[cat_id]
            }

    return sorted_categories


def organize_by_date(reports):
    """Group reports by date"""
    by_date = defaultdict(list)

    for report in reports:
        date = report.get("date", "Unknown")
        by_date[date].append(report)

    # Sort by date descending
    return dict(sorted(by_date.items(), reverse=True))


def get_featured_reports(reports):
    """Get featured reports (top 3 or manually marked)"""
    featured = [r for r in reports if r.get("featured")]

    # If not enough marked, take most recent
    if len(featured) < 3:
        remaining = [r for r in reports if not r.get("featured")]
        remaining.sort(key=lambda x: x.get("date", ""), reverse=True)
        featured.extend(remaining[:3 - len(featured)])

    # Set featured labels
    for i, report in enumerate(featured[:3]):
        if not report.get("featured_label"):
            if i == 0:
                report["featured_label"] = "NEW - Latest Research"
            else:
                report["featured_label"] = "Key Document"
        report["featured"] = True

    return featured[:3]


def format_date_label(date_str):
    """Format date string to display label like 'January 19, 2026'"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.strftime("%B %d, %Y")
    except:
        return date_str


def generate_index(data):
    """Generate index.html from template"""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True
    )

    # Add custom filters
    env.filters["format_date"] = format_date_label

    template = env.get_template("index.template.html")

    reports = data.get("reports", [])
    categories = data.get("categories", {})

    # Prepare template context
    featured_reports = get_featured_reports(reports)
    reports_by_category = organize_by_category(reports, categories)
    reports_by_date = organize_by_date(reports)

    context = {
        "total_reports": len(reports),
        "system_version": data.get("system_version", "3.3.0"),
        "last_updated": data.get("last_updated", datetime.now().isoformat()),
        "stats": data.get("stats", {}),
        "categories": categories,
        "featured_reports": featured_reports,
        "reports_by_category": reports_by_category,
        "reports_by_date": reports_by_date,
        "all_reports": reports,
    }

    return template.render(**context)


def main():
    print("=" * 60)
    print("  Assisterr Research Index Generator")
    print("=" * 60)
    print()

    # Step 1: Load reports.json
    print("1. Loading config/reports.json...")
    data = load_reports_json()
    print(f"   Found {len(data.get('reports', []))} reports")
    print()

    # Step 2: Validate schema
    print("2. Validating against schema...")
    if not validate_schema(data):
        sys.exit(1)
    print("   Schema valid")
    print()

    # Step 3: Verify HTML files
    print("3. Verifying HTML files exist...")
    if not verify_html_files(data.get("reports", [])):
        sys.exit(1)
    print("   All files found")
    print()

    # Step 4: Generate index
    print("4. Generating index.html...")
    html = generate_index(data)
    print()

    # Step 5: Write output
    output_path = BASE_DIR / "index.html"
    print(f"5. Writing {output_path}...")
    with open(output_path, "w") as f:
        f.write(html)
    print(f"   Wrote {len(html):,} bytes")
    print()

    # Summary
    print("=" * 60)
    print("  Index Generation Complete!")
    print("=" * 60)
    print()
    print(f"Output: {output_path}")
    print(f"Reports: {len(data.get('reports', []))}")
    print(f"Categories: {len(data.get('categories', {}))}")
    print(f"System Version: {data.get('system_version', 'unknown')}")
    print()
    print("Next: Commit and push to deploy")


if __name__ == "__main__":
    main()
