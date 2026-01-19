#!/usr/bin/env python3
"""
Validate reports.json and HTML files before deployment.

Run from repo root:
  python build/validate-reports.py

Exit codes:
  0 - All validations passed
  1 - Validation errors found
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("WARNING: jsonschema not installed. Run: pip install jsonschema")
    validate = None
    ValidationError = Exception

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
REPORTS_DIR = BASE_DIR / "reports"

errors = []
warnings = []


def error(msg):
    errors.append(f"ERROR: {msg}")


def warn(msg):
    warnings.append(f"WARNING: {msg}")


def validate_reports_json():
    """Load and validate reports.json"""
    reports_path = CONFIG_DIR / "reports.json"

    if not reports_path.exists():
        error(f"Missing {reports_path}")
        return None

    try:
        with open(reports_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in reports.json: {e}")
        return None

    return data


def validate_schema(data):
    """Validate against JSON schema"""
    if validate is None:
        warn("jsonschema not installed, skipping schema validation")
        return

    schema_path = CONFIG_DIR / "reports.schema.json"
    if not schema_path.exists():
        warn("Schema file not found, skipping validation")
        return

    with open(schema_path, "r") as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        error(f"Schema validation failed: {e.message}")


def validate_html_files(reports):
    """Check all referenced HTML files exist"""
    for report in reports:
        filename = report.get("filename")
        if not filename:
            error(f"Report missing filename: {report.get('id', 'unknown')}")
            continue

        html_path = REPORTS_DIR / filename
        if not html_path.exists():
            error(f"Missing HTML file: reports/{filename}")


def validate_report_fields(reports):
    """Validate required fields in each report"""
    required = ["id", "filename", "title", "date", "category"]

    for report in reports:
        report_id = report.get("id", "unknown")

        for field in required:
            if not report.get(field):
                error(f"Report '{report_id}' missing required field: {field}")

        # Validate date format
        date = report.get("date", "")
        if date and not (len(date) == 10 and date[4] == "-" and date[7] == "-"):
            error(f"Report '{report_id}' has invalid date format: {date} (expected YYYY-MM-DD)")

        # Validate category
        valid_categories = ["solana", "slm", "vertical", "kya", "vc", "cross-chain"]
        cat = report.get("category", "")
        if cat and cat not in valid_categories:
            warn(f"Report '{report_id}' has unknown category: {cat}")


def validate_duplicates(reports):
    """Check for duplicate IDs or filenames"""
    ids = {}
    filenames = {}

    for report in reports:
        report_id = report.get("id", "")
        filename = report.get("filename", "")

        if report_id in ids:
            error(f"Duplicate report ID: {report_id}")
        ids[report_id] = True

        if filename in filenames:
            error(f"Duplicate filename: {filename}")
        filenames[filename] = True


def validate_orphan_files():
    """Check for HTML files not listed in reports.json"""
    if not REPORTS_DIR.exists():
        return

    data = validate_reports_json()
    if not data:
        return

    listed_files = {r.get("filename") for r in data.get("reports", [])}

    for html_file in REPORTS_DIR.glob("*.html"):
        if html_file.name not in listed_files:
            warn(f"Orphan HTML file not in reports.json: reports/{html_file.name}")


def main():
    print("=" * 60)
    print("  Assisterr Research Validation")
    print("=" * 60)
    print()

    # Load reports.json
    print("1. Loading config/reports.json...")
    data = validate_reports_json()
    if not data:
        print("   FAILED")
    else:
        print(f"   Found {len(data.get('reports', []))} reports")
    print()

    if data:
        # Validate schema
        print("2. Validating JSON schema...")
        validate_schema(data)
        print()

        # Validate HTML files
        print("3. Checking HTML files...")
        validate_html_files(data.get("reports", []))
        print()

        # Validate report fields
        print("4. Validating report fields...")
        validate_report_fields(data.get("reports", []))
        print()

        # Check for duplicates
        print("5. Checking for duplicates...")
        validate_duplicates(data.get("reports", []))
        print()

        # Check for orphans
        print("6. Checking for orphan files...")
        validate_orphan_files()
        print()

    # Summary
    print("=" * 60)

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print()
        print("VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\nVALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
