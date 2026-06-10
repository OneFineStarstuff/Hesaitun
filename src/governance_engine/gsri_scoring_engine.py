"""
GSRI Scoring Engine: Systemic Risk Assessment
Calculates the Governance Systemic Risk Index (G-SRI).
"""

import json

class GSRIScoringEngine:
    def __init__(self, threshold=40.0):
        self.threshold = threshold

    def calculate_sri(self, components):
        """
        Calculates SRI based on framework component maturity.
        components: dict of component_name -> maturity_score (0-5)
        """
        if not components:
            return 0.0

        total_maturity = sum(components.values())
        max_possible = len(components) * 5

        # Simple weighted inverse scale: Higher maturity = Lower systemic risk
        maturity_index = (total_maturity / max_possible) * 100
        sri = 100 - maturity_index

        return sri

    def get_status(self, sri):
        if sri < self.threshold:
            return "GREEN (PASS)"
        elif sri < self.threshold + 20:
            return "YELLOW (WARNING)"
        else:
            return "RED (FAIL)"

if __name__ == "__main__":
    engine = GSRIScoringEngine()
    # Mock data based on 18-Component Model
    mock_maturity = {
        "Board Oversight": 4,
        "Ethics Policy": 3,
        "Risk Registry": 4,
        "Kafka WORM Logging": 5,
        "OPA Policy Engine": 5,
        "RCE Integration": 4
    }

    sri = engine.calculate_sri(mock_maturity)
    status = engine.get_status(sri)
    print(f"Governance Systemic Risk Index (G-SRI): {sri:.2f}")
    print(f"System Status: {status}")
