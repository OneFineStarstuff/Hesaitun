"""
Recursive Context Envelope (RCE): EAIP §3 State Management
Implements the distributed state propagation layer for agentic workloads.
"""

import time
import uuid
import json

class RCELayerError(Exception):
    """Custom exception for RCE protocol violations."""
    pass

class RCESlot:
    def __init__(self, slot_id, slot_type, content, immutable=False):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.content = content
        self.immutable = immutable

    def to_dict(self):
        return {
            "id": self.slot_id,
            "type": self.slot_type,
            "content": self.content,
            "immutable": self.immutable
        }

class RCE:
    MAX_DEPTH = 4
    MAX_SLOTS = 32

    def __init__(self, spiffe_id, conversation_id, depth=0, parent_id="",
                 token_budget=8192, tokens_consumed=0, compression_algo="none"):
        self.envelope_id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.depth = depth
        self.created = time.time()
        self.spiffe_id = spiffe_id
        self.conversation_id = conversation_id
        self.token_budget = token_budget
        self.tokens_consumed = tokens_consumed
        self.compression_algo = compression_algo
        self.slots = []
        self.children = []

        # Validate on creation
        self.validate()

    def validate(self):
        """Validates the envelope against EAIP §6 Conformance requirements."""
        # C-R-02: Depth limit
        if self.depth > self.MAX_DEPTH:
            raise RCELayerError(f"EAIP-2001: RCE nesting depth {self.depth} exceeds maximum ({self.MAX_DEPTH})")

        # C-R-03: Token budget logic (usually checked during child creation, but here for safety)
        if self.tokens_consumed > self.token_budget:
            raise RCELayerError("EAIP-2002: Token budget exhausted")

        # C-R-05 (Implicit): Slot limit
        if len(self.slots) > self.MAX_SLOTS:
            raise RCELayerError(f"EAIP-2003: Slot count {len(self.slots)} exceeds maximum ({self.MAX_SLOTS})")

    def add_slot(self, slot_type, content, immutable=False):
        slot_id = len(self.slots)
        slot = RCESlot(slot_id, slot_type, content, immutable)
        self.slots.append(slot)
        self.validate()
        return slot

    def spawn_child(self, child_spiffe_id, child_token_budget):
        """Creates a nested child RCE as per EAIP §3.3."""
        # C-R-03: Child TokenBudget SHALL NOT exceed parent's remaining budget
        remaining_budget = self.token_budget - self.tokens_consumed
        if child_token_budget > remaining_budget:
            raise RCELayerError(f"EAIP-2002: Child budget {child_token_budget} exceeds parent's remaining {remaining_budget}")

        child = RCE(
            spiffe_id=child_spiffe_id,
            conversation_id=self.conversation_id,
            depth=self.depth + 1,
            parent_id=self.envelope_id,
            token_budget=child_token_budget,
            tokens_consumed=0
        )
        self.children.append(child)
        return child

    def to_dict(self):
        return {
            "envelope_id": self.envelope_id,
            "parent_id": self.parent_id,
            "depth": self.depth,
            "created": self.created,
            "origin": {"spiffe_id": self.spiffe_id},
            "state": {
                "conversation_id": self.conversation_id,
                "token_budget": self.token_budget,
                "tokens_consumed": self.tokens_consumed
            },
            "slots": [s.to_dict() for s in self.slots],
            "children": [c.to_dict() for c in self.children]
        }

if __name__ == "__main__":
    try:
        # 1. Create Root RCE
        root = RCE(
            spiffe_id="spiffe://eaip.example.org/gateway",
            conversation_id="conv_123"
        )
        root.add_slot("SystemPrompt", "You are a secure assistant.")
        print(f"Root RCE Created: {root.envelope_id} (Depth: {root.depth})")

        # 2. Spawn Child
        child = root.spawn_child("spiffe://eaip.example.org/retrieval", 2048)
        print(f"Child RCE Created: {child.envelope_id} (Depth: {child.depth})")

        # 3. Test Depth Violation
        current = child
        for i in range(5):
            print(f"Spawning generation {i+3}...")
            current = current.spawn_child("spiffe://eaip.example.org/nested", 100)

    except RCELayerError as e:
        print(f"Caught Expected Protocol Violation: {e}")
