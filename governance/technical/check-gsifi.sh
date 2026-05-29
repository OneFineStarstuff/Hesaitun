#!/bin/bash
# EAIP v3.4.1 Compliance Checker for G-SIFI Governance

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "Starting EAIP v3.4.1 Technical Compliance Check..."

STATUS=0

# 1. Directory Structure Verification
echo -n "Checking Governance Directory Structure... "
REQUIRED_DIRS=("governance/core" "governance/executive" "governance/ops" "governance/readiness" "governance/technical" "governance/communication")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "FAILED: $dir missing"
        STATUS=1
    fi
done
if [ $STATUS -eq 0 ]; then echo "PASSED"; fi

# 2. Proto Definition Verification
echo -n "Verifying EAIP v2 RCE Proto Definition... "
if [ ! -f "governance/technical/proto/eaip_v2.proto" ]; then
    echo "FAILED: eaip_v2.proto missing"
    STATUS=1
fi
if grep -q "MUST NOT exceed 4" "governance/technical/proto/eaip_v2.proto"; then
    echo "PASSED (Depth Constraint Found)"
else
    echo "FAILED: Depth constraint comment missing in proto"
    STATUS=1
fi

# 3. OPA Policy Verification
echo -n "Verifying OPA Authorization Policies... "
if [ ! -f "governance/technical/policy.rego" ]; then
    echo "FAILED: policy.rego missing"
    STATUS=1
fi
if grep -q "input.rce.depth <= 4" "governance/technical/policy.rego"; then
    echo "PASSED (RCE Depth Policy Found)"
else
    echo "FAILED: RCE depth policy missing in Rego"
    STATUS=1
fi

# 4. G-SIFI Practitioner Guide Existence
echo -n "Verifying G-SIFI Practitioner Guide... "
if [ -f "governance/core/GSIFI_PRACTITIONER_GUIDE.md" ]; then
    echo "PASSED"
else
    echo "FAILED: GSIFI_PRACTITIONER_GUIDE.md missing"
    STATUS=1
fi

# 5. Kafka WORM Specification Check
echo -n "Verifying Kafka WORM Architecture Specs... "
if grep -q "Kafka WORM" "governance/technical/ADVANCED_ARCHITECTURE.md"; then
    echo "PASSED"
else
    echo "FAILED: Kafka WORM specs missing"
    STATUS=1
fi

if [ $STATUS -eq 0 ]; then
    echo "ALL GOVERNANCE COMPLIANCE CHECKS PASSED (EAIP v3.4.1)"
else
    echo "GOVERNANCE COMPLIANCE CHECKS FAILED"
fi
