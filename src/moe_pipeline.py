"""
MoE Pipeline: Retail-facing Inference Simulator
Demonstrates EAIP-compliant governance integration with RCE propagation.
"""

import time
import json
import random
from governance_engine.orchestrator import GovernanceOrchestrator
from governance_engine.rce import RCE, RCELayerError

class MoEPipeline:
    def __init__(self):
        self.orchestrator = GovernanceOrchestrator(worm_path="moe_audit.worm")
        self.experts = ["retail_loan_v1", "fraud_detection_v2", "customer_service_v1"]

    def process_inference_request(self, user_id, request_payload, rce=None):
        """
        Simulates a gRPC request processing lifecycle as per EAIP Spec.
        """
        print(f"[*] Processing request for User: {user_id}")

        # 0. EAIP §3.1: Ensure Root RCE exists
        if rce is None:
            print("[+] Initializing Root RCE (Depth 0)")
            rce = RCE(
                spiffe_id="spiffe://eaip.example.org/inference-gateway",
                conversation_id=f"conv_{user_id}"
            )
            rce.add_slot("SystemPrompt", "Adhere to EAIP §3.3 regulations.")
            rce.add_slot("UserMessage", request_payload.get("purpose", "none"))

        # 1. Routing (MoE Logic)
        expert = "retail_loan_v1"
        print(f"[>] Routed to Expert: {expert}")

        # 2. EAIP §3.3: Spawn Child RCE for the Expert Sub-call
        child_rce = None
        try:
            print(f"[+] Spawning Child RCE for {expert} (Depth: {rce.depth + 1})")
            child_rce = rce.spawn_child(
                child_spiffe_id=f"spiffe://eaip.example.org/expert/{expert}",
                child_token_budget=min(2048, rce.token_budget - rce.tokens_consumed)
            )
        except RCELayerError as e:
            print(f"[-] RCE Propagation Failed: {e}")
            # If protocol limits are reached, we simulate a "rogue" bypass for the demonstration
            child_rce = rce
            # We use a non-standard way to modify depth to trigger the orchestrator's check
            # In Python, we can modify private-ish members if we really want to
            child_rce.__dict__['depth'] = rce.depth + 1

        # 3. Expert Processing (Simulated)
        demographics = ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"]
        predictions = [random.randint(0, 1) for _ in range(10)]

        # 4. Action Execution (Simulated)
        action_id = "loan_eligibility_check"
        context = request_payload.get("purpose", "unknown")
        attributions = {
            "debt_to_income": 0.55,
            "employment_length": 0.25,
            "region": 0.20
        }

        # 5. Governance Enforcement (EAIP Mandated)
        print("[!] Executing Governance Orchestrator with RCE Attestation...")
        try:
            gov_result = self.orchestrator.validate_and_log_action(
                expert_id=expert,
                demographics=demographics,
                predictions=predictions,
                action_id=action_id,
                context=context,
                attributions=attributions,
                rce=child_rce
            )
        except Exception as e:
            # Re-raise if orchestrator terminated the process (e.g. kill switch)
            raise e

        return {
            "request_id": f"req_{int(time.time())}",
            "status": "PROCESSED",
            "expert": expert,
            "governance_summary": {
                "rce_status": gov_result["rce_status"],
                "fairness_status": gov_result["fairness"]["verification_status"],
                "gsri_score": gov_result["risk_index"],
                "pqc_attestation": gov_result["log_attestation"][:16] + "..."
            },
            "rce_id": child_rce.envelope_id
        }

if __name__ == "__main__":
    pipeline = MoEPipeline()
    request = {"purpose": "Home Improvement Loan", "amount": 50000}

    print("--- SCENARIO 1: NORMAL OPERATION ---")
    response = pipeline.process_inference_request("user_88", request)
    print(json.dumps(response, indent=2))

    print("\n--- SCENARIO 2: PROTOCOL VIOLATION (DEPTH > 4) ---")
    # Create an RCE already at max depth
    root = RCE("spiffe://eaip.org/gateway", "conv_99", token_budget=10000)
    level1 = root.spawn_child("s1", 9000)
    level2 = level1.spawn_child("s2", 8000)
    level3 = level2.spawn_child("s3", 7000)
    level4 = level3.spawn_child("s4", 6000)

    print("[!] Attempting to process request with Depth 4 RCE (Expert call will push to 5)")
    try:
        response = pipeline.process_inference_request("user_adversary", request, rce=level4)
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Pipeline Terminated by Governance: {e}")
