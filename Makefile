.PHONY: check-gsifi-governance verify-framework help

help:
	@echo "AGI/ASI Governance Framework Makefile"
	@echo "Usage:"
	@echo "  make check-gsifi-governance   Run EAIP v3.4.1 compliance checks"
	@echo "  make verify-framework        Run full operational verification suite"

check-gsifi-governance:
	@./governance/technical/check-gsifi.sh

verify-framework:
	@./governance/verify-framework.sh
