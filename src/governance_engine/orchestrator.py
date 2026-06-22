"""
Governance Orchestrator: Unified Compliance Layer
Integrates ZK-Fairness, CAE Interpretability, G-SRI Scoring, and PQC-WORM logging.
"""

import os
import sys

# Ensure components are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from zkml_pipeline_verifier import ZKFairnessVerifier
    from asa_drift_monitor import ASADriftMonitor
    from gsri_scoring_engine import GSRIScoringEngine
    from pqc_worm_logger import PQCWORMLogger
    from omega_actual_switch import OmegaActualSwitch
    from rce import RCE, RCELayerError
except ImportError:
    from .zkml_pipeline_verifier import ZKFairnessVerifier
    from .asa_drift_monitor import ASADriftMonitor
    from .gsri_scoring_engine import GSRIScoringEngine
    from .pqc_worm_logger import PQCWORMLogger
    from .omega_actual_switch import OmegaActualSwitch
    from .rce import RCE, RCELayerError

class GovernanceOrchestrator:
    def __init__(self, worm_path="production_audit.worm"):
        self.fairness_verifier = ZKFairnessVerifier()
        self.drift_monitor = ASADriftMonitor()
        self.risk_engine = GSRIScoringEngine()
        self.worm_logger = PQCWORMLogger(storage_path=worm_path)
        self.kill_switch = OmegaActualSwitch()

    def validate_and_log_action(self, expert_id, demographics, predictions, action_id, context, attributions, rce=None):
        """
        Executes a full governance check cycle for a single agent action.
        """
        # 0. EAIP §3: RCE Validation
        rce_status = "NOT_PROVIDED"
        if rce:
            try:
                rce.validate()
                rce_status = "VALID"
            except RCELayerError as e:
                rce_status = f"INVALID: {str(e)}"
                print(f"PROTOCOL VIOLATION: {rce_status}")
                # Protocol violation triggers immediate risk escalation
                self.kill_switch.arm()
                self.kill_switch.execute_kill_switch(f"RCE Protocol Violation: {str(e)}")

        # 1. MAS FEAT: ZK-Fairness Proof
        fairness_proof = self.fairness_verifier.generate_fairness_proof(expert_id, demographics, predictions)

        # 2. HKMA Ethics: CAE Recording
        cae = self.drift_monitor.record_action(action_id, context, attributions)

        # 3. GSRI Calculation (Periodic/On-demand)
        mock_maturity = {
            "ZKML Fairness": 5 if fairness_proof["verification_status"] == "PASSED" else 2,
            "ASA Interpretability": 4,
            "PQC-WORM Audit": 5,
            "RCE Integration": 5 if rce_status == "VALID" else 1
        }
        sri = self.risk_engine.calculate_sri(mock_maturity)
        risk_status = self.risk_engine.get_status(sri)

        # 4. PQC-WORM Immutable Audit
        audit_event = {
            "rce_status": rce_status,
            "rce_id": rce.envelope_id if rce else None,
            "fairness_proof": fairness_proof,
            "cae": cae.to_dict(),
            "gsri": sri,
            "risk_status": risk_status
        }
        log_entry = self.worm_logger.log_event("GOVERNANCE_CHECK", audit_event)

        # 5. Safety Check
        if fairness_proof["verification_status"] == "FAILED":
            print(f"CRITICAL: Fairness check FAILED for {expert_id}")
            if sri > 75:
                self.kill_switch.arm()
                self.kill_switch.execute_kill_switch("Systemic Risk threshold exceeded")

        return {
            "rce_status": rce_status,
            "fairness": fairness_proof,
            "interpretability": cae.to_dict(),
            "risk_index": sri,
            "log_attestation": log_entry["attestation"]
        }

if __name__ == "__main__":
    orchestrator = GovernanceOrchestrator(worm_path="demo.worm")

    # 1. Valid RCE Case
    root_rce = RCE(spiffe_id="spiffe://eaip.org/gateway", conversation_id="c1")

    result = orchestrator.validate_and_log_action(
        expert_id="retail_loan_moe_01",
        demographics=["A", "B", "A", "B"],
        predictions=[1, 1, 0, 0],
        action_id="loan_approval",
        context="Standard retail application",
        attributions={"income": 0.6, "credit_score": 0.4},
        rce=root_rce
    )

    print("\n--- GOVERNANCE ORCHESTRATION RESULT (VALID RCE) ---")
    import json
    print(json.dumps(result, indent=2))

    # 2. Invalid RCE Case (Simulated violation)
    bad_rce = RCE(spiffe_id="spiffe://eaip.org/attacker", conversation_id="c2")
    bad_rce.depth = 10 # Manual violation

    print("\n--- TESTING PROTOCOL VIOLATION ---")
    try:
        orchestrator.validate_and_log_action(
            expert_id="rogue_expert",
            demographics=["A"],
            predictions=[1],
            action_id="bypass_security",
            context="Malicious request",
            attributions={},
            rce=bad_rce
        )
    except Exception as e:
        print(f"Process terminated: {e}")
