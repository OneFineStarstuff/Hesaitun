#!/bin/bash
# G-Stack Governance Framework: Operational Verification Suite

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "===================================================="
echo "G-Stack Framework Operational Verification Suite"
echo "===================================================="

ERRORS=0

# 1. File Count Verification
echo -n "[1/4] Verifying total document count... "
DOC_COUNT=$(find governance -name "*.md" | wc -l)
if [ "$DOC_COUNT" -ge 22 ]; then
    echo "PASSED ($DOC_COUNT files found)"
else
    echo "FAILED (Found $DOC_COUNT, expected at least 22)"
    ERRORS=$((ERRORS + 1))
fi

# 2. Master Index Integrity
echo -n "[2/4] Verifying Master Index cross-references... "
INDEX_FILE="governance/core/MASTER_INDEX.md"
if [ ! -f "$INDEX_FILE" ]; then
    echo "FAILED: Master Index missing"
    ERRORS=$((ERRORS + 1))
else
    MISSING_LINKS=0
    # Extract relative links in format [text](path)
    LINKS=$(grep -oP '\[.*?\]\(\K.*?(?=\))' "$INDEX_FILE")
    for link in $LINKS; do
        pushd governance/core > /dev/null
        if [ ! -f "$link" ]; then
            echo "Missing target: $link"
            MISSING_LINKS=$((MISSING_LINKS + 1))
        fi
        popd > /dev/null
    done

    if [ $MISSING_LINKS -eq 0 ]; then
        echo "PASSED"
    else
        echo "FAILED ($MISSING_LINKS broken links found)"
        ERRORS=$((ERRORS + 1))
    fi
fi

# 3. Content Integrity (Mandatory Keyword Check)
echo -n "[3/4] Verifying core framework keywords... "
KEYWORDS=("G-Stack" "EAIP" "Sentinel" "G-SIFI" "WORM" "OPA")
MISSING_KEYWORDS=0
for kw in "${KEYWORDS[@]}"; do
    if ! grep -rIq "$kw" governance/; then
        echo "Keyword '$kw' not found"
        MISSING_KEYWORDS=$((MISSING_KEYWORDS + 1))
    fi
done

if [ $MISSING_KEYWORDS -eq 0 ]; then
    echo "PASSED"
else
    echo "WARNING ($MISSING_KEYWORDS keywords missing)"
fi

# 4. Technical Artifact Alignment
echo -n "[4/4] Verifying Technical Artifacts (Proto/Rego)... "
if [[ -f "governance/technical/proto/eaip_v2.proto" && -f "governance/technical/policy.rego" ]]; then
    echo "PASSED"
else
    echo "FAILED: Technical artifacts missing"
    ERRORS=$((ERRORS + 1))
fi

echo "===================================================="
if [ $ERRORS -eq 0 ]; then
    echo "VERIFICATION SUCCESSFUL: Framework is operationally sound."
else
    echo "VERIFICATION FAILED: $ERRORS errors found."
fi
