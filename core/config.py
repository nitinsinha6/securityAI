import yaml

class Policy:
    def __init__(self, d: dict):
        self.thresholds = d.get("thresholds", {})
        self.business_hours = d.get("business_hours", {"start": 8, "end": 18})
        self.high_risk_countries = set(d.get("high_risk_countries", []))
        self.geo_jump_km = d.get("geo_jump_km", 1500)
        self.large_transfer_amount = d.get("large_transfer_amount", 50000)
        self.privileged_roles = set(d.get("privileged_roles", ["admin","ops","supervisor"]))

def load_policy(path: str) -> Policy:
    with open(path, "r", encoding="utf-8") as f:
        return Policy(yaml.safe_load(f))
