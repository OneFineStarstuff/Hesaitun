import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from governance_engine.rce import RCE, RCELayerError

def test_rce_creation():
    rce = RCE(spiffe_id="spiffe://test", conversation_id="conv1")
    assert rce.depth == 0
    assert rce.token_budget == 8192
    assert rce.spiffe_id == "spiffe://test"

def test_rce_slots():
    rce = RCE(spiffe_id="spiffe://test", conversation_id="conv1")
    rce.add_slot("TestType", "TestData")
    assert len(rce.slots) == 1
    assert rce.slots[0].slot_type == "TestType"

def test_rce_depth_limit():
    root = RCE(spiffe_id="s", conversation_id="c")
    l1 = root.spawn_child("s1", 7000)
    l2 = l1.spawn_child("s2", 6000)
    l3 = l2.spawn_child("s3", 5000)
    l4 = l3.spawn_child("s4", 4000)

    with pytest.raises(RCELayerError) as excinfo:
        l4.spawn_child("s5", 3000)
    assert "depth 5 exceeds maximum" in str(excinfo.value)

def test_rce_token_budget_limit():
    root = RCE(spiffe_id="s", conversation_id="c", token_budget=1000)

    # Valid child
    root.spawn_child("s1", 500)

    # Invalid child (exceeds remaining)
    with pytest.raises(RCELayerError) as excinfo:
        root.spawn_child("s2", 1100)
    assert "exceeds parent's remaining" in str(excinfo.value)

def test_rce_slot_limit():
    rce = RCE(spiffe_id="s", conversation_id="c")
    for i in range(32):
        rce.add_slot(f"Type{i}", "Data")

    with pytest.raises(RCELayerError) as excinfo:
        rce.add_slot("Overflow", "Data")
    assert "Slot count 33 exceeds maximum" in str(excinfo.value)

def test_rce_to_dict():
    rce = RCE(spiffe_id="s", conversation_id="c")
    rce.add_slot("T", "D")
    data = rce.to_dict()
    assert data["origin"]["spiffe_id"] == "s"
    assert data["state"]["conversation_id"] == "c"
    assert len(data["slots"]) == 1
