import pytest
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from governance_engine.zkml_pipeline_verifier import ZKFairnessVerifier
from governance_engine.asa_drift_monitor import ASADriftMonitor
from governance_engine.gsri_scoring_engine import GSRIScoringEngine
from governance_engine.pqc_worm_logger import PQCWORMLogger
from governance_engine.omega_actual_switch import OmegaActualSwitch

def test_zk_fairness_verifier():
    verifier = ZKFairnessVerifier(demographic_parity_threshold=0.1)
    expert = "test_expert"
    # Perfectly fair data
    demographics = ["A", "B", "A", "B"]
    predictions = [1, 1, 0, 0]
    proof = verifier.generate_fairness_proof(expert, demographics, predictions)
    assert proof["verification_status"] == "PASSED"
    assert proof["parity_gap"] == 0.0
    assert verifier.verify_expert_node(proof) is True

    # Unfair data
    demographics = ["A", "A", "B", "B"]
    predictions = [1, 1, 0, 0] # A rate = 1.0, B rate = 0.0, gap = 1.0
    proof = verifier.generate_fairness_proof(expert, demographics, predictions)
    assert proof["verification_status"] == "FAILED"
    assert proof["parity_gap"] == 1.0
    assert verifier.verify_expert_node(proof) is False

def test_asa_drift_monitor():
    monitor = ASADriftMonitor()
    action = "test_action"
    context = "test_context"
    attributions = {"f1": 0.5, "f2": 0.5}

    cae = monitor.record_action(action, context, attributions)
    assert cae.action_id == action
    assert len(monitor.envelopes) == 1

    # Test insufficient data for drift
    assert "Insufficient data" in monitor.analyze_drift()

    # Add another and check drift
    monitor.record_action(action, context, attributions)
    assert "HKMA Compliance: PASSED" in monitor.analyze_drift()

def test_gsri_scoring_engine():
    engine = GSRIScoringEngine(threshold=40.0)
    # High maturity = Low SRI
    mock_maturity = {"C1": 5, "C2": 5} # 10/10 = 100% maturity -> 0 SRI
    sri = engine.calculate_sri(mock_maturity)
    assert sri == 0.0
    assert "GREEN" in engine.get_status(sri)

    # Low maturity = High SRI
    mock_maturity = {"C1": 0, "C2": 0} # 0/10 = 0% maturity -> 100 SRI
    sri = engine.calculate_sri(mock_maturity)
    assert sri == 100.0
    assert "RED" in engine.get_status(sri)

def test_pqc_worm_logger():
    logger = PQCWORMLogger(storage_path="test_audit.worm")
    event = {"msg": "hello"}
    entry1 = logger.log_event("TEST", event)
    assert entry1["event_type"] == "TEST"
    assert entry1["prev_hash"] == "0" * 64

    entry2 = logger.log_event("TEST2", event)
    assert entry2["prev_hash"] == entry1["attestation"]

    if os.path.exists("test_audit.worm"):
        os.remove("test_audit.worm")

def test_omega_actual_switch():
    switch = OmegaActualSwitch()
    assert switch.state == "OPERATIONAL"

    # Execute without arming
    res = switch.execute_kill_switch("drift")
    assert "NOT ARMED" in res
    assert switch.state == "OPERATIONAL"

    # Arm and execute
    switch.arm()
    assert switch.is_armed is True
    res = switch.execute_kill_switch("drift")
    assert "SUCCESSFUL" in res
    assert switch.state == "TERMINATED"
