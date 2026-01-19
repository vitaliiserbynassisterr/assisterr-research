#!/bin/bash
#
# Add a new report to the Assisterr Research Hub
#
# Usage:
#   ./scripts/add-report.sh reports/NEW-REPORT.html
#   ./scripts/add-report.sh /path/to/report.html --copy
#
# Options:
#   --copy    Copy the file to reports/ (use when file is outside repo)
#   --featured Mark as featured report
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$BASE_DIR/reports"
CONFIG_FILE="$BASE_DIR/config/reports.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
HTML_FILE=""
DO_COPY=false
FEATURED=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --copy)
            DO_COPY=true
            shift
            ;;
        --featured)
            FEATURED=true
            shift
            ;;
        *)
            HTML_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$HTML_FILE" ]; then
    echo -e "${RED}Error: No HTML file specified${NC}"
    echo "Usage: $0 <path-to-report.html> [--copy] [--featured]"
    exit 1
fi

# Resolve full path
if [[ ! "$HTML_FILE" = /* ]]; then
    HTML_FILE="$(pwd)/$HTML_FILE"
fi

if [ ! -f "$HTML_FILE" ]; then
    echo -e "${RED}Error: File not found: $HTML_FILE${NC}"
    exit 1
fi

FILENAME=$(basename "$HTML_FILE")

# Copy file if requested or if outside reports/
if [ "$DO_COPY" = true ] || [[ ! "$HTML_FILE" == "$REPORTS_DIR"* ]]; then
    echo -e "${BLUE}Copying to reports/${NC}"
    cp "$HTML_FILE" "$REPORTS_DIR/$FILENAME"
fi

# Extract metadata from filename
# Pattern: PREFIX-title-words-YYYY-MM-DD.html
echo -e "${BLUE}Extracting metadata from filename...${NC}"

# Extract date (last YYYY-MM-DD before .html)
DATE=$(echo "$FILENAME" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | tail -1)
if [ -z "$DATE" ]; then
    DATE=$(date +%Y-%m-%d)
    echo -e "${YELLOW}No date in filename, using today: $DATE${NC}"
fi

# Generate ID (filename without .html)
ID="${FILENAME%.html}"

# Determine category from prefix
CATEGORY="slm"
case "$FILENAME" in
    SOLANA-*|solana-*)
        CATEGORY="solana"
        ;;
    SLM-*|slm-*)
        CATEGORY="slm"
        ;;
    KYA-*|kya-*|X402-*)
        CATEGORY="kya"
        ;;
    VC-*|SERIES-*|FUNDING-*|*funding*|*investor*)
        CATEGORY="vc"
        ;;
    VERTICAL-*|*vertical*)
        CATEGORY="vertical"
        ;;
    *cross-chain*)
        CATEGORY="cross-chain"
        ;;
    CEO-DEFI*)
        CATEGORY="vertical"
        ;;
    CEO-RESEARCH*)
        CATEGORY="solana"
        ;;
esac

# Extract title from HTML <title> tag
TITLE=$(grep -oP '(?<=<title>)[^<]+' "$REPORTS_DIR/$FILENAME" 2>/dev/null | head -1)
if [ -z "$TITLE" ]; then
    # Fallback: generate from filename
    TITLE=$(echo "$ID" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
fi

# Truncate title if too long
if [ ${#TITLE} -gt 80 ]; then
    TITLE="${TITLE:0:77}..."
fi

# Extract description from meta tag or first <p>
DESCRIPTION=$(grep -oP '(?<=<meta name="description" content=")[^"]+' "$REPORTS_DIR/$FILENAME" 2>/dev/null | head -1)
if [ -z "$DESCRIPTION" ]; then
    DESCRIPTION="Research report from $DATE"
fi

echo -e "${GREEN}Extracted metadata:${NC}"
echo "  ID: $ID"
echo "  Title: $TITLE"
echo "  Date: $DATE"
echo "  Category: $CATEGORY"
echo "  Featured: $FEATURED"

# Create JSON entry
FEATURED_JSON="false"
if [ "$FEATURED" = true ]; then
    FEATURED_JSON="true"
fi

NEW_ENTRY=$(cat <<EOF
{
    "id": "$ID",
    "filename": "$FILENAME",
    "title": "$TITLE",
    "description": "$DESCRIPTION",
    "date": "$DATE",
    "category": "$CATEGORY",
    "badges": [],
    "badge_colors": [],
    "featured": $FEATURED_JSON,
    "version": "2.0"
}
EOF
)

# Check if jq is available
if command -v jq &> /dev/null; then
    # Use jq to add to reports array
    echo -e "${BLUE}Adding to config/reports.json...${NC}"

    # Check if report already exists
    EXISTING=$(jq -r ".reports[] | select(.id == \"$ID\") | .id" "$CONFIG_FILE" 2>/dev/null)
    if [ -n "$EXISTING" ]; then
        echo -e "${YELLOW}Report already exists in config. Updating...${NC}"
        # Remove existing and add new
        jq "(.reports |= map(select(.id != \"$ID\"))) | .reports = [${NEW_ENTRY}] + .reports | .last_updated = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    else
        # Add to beginning of reports array
        jq ".reports = [${NEW_ENTRY}] + .reports | .last_updated = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    fi

    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    echo -e "${GREEN}Updated config/reports.json${NC}"
else
    echo -e "${YELLOW}jq not found. Please manually add to config/reports.json:${NC}"
    echo "$NEW_ENTRY"
fi

# Regenerate index
echo -e "${BLUE}Regenerating index.html...${NC}"
python3 "$BASE_DIR/build/generate-index.py"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Report added successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git add . && git commit -m 'Add report: $ID'"
echo "  3. Push: git push"
echo ""
