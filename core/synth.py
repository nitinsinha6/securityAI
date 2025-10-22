import argparse, random
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

COUNTRIES = [
    ("CA", 43.6532, -79.3832),    # Toronto
    ("CA", 49.2827, -123.1207),   # Vancouver
    ("CA", 45.4215, -75.6972),    # Ottawa
    ("US", 40.7128, -74.0060),    # New York
    ("US", 37.7749, -122.4194),   # San Francisco
    ("GB", 51.5074, -0.1278),     # London
    ("IN", 19.0760, 72.8777),     # Mumbai
    ("SG", 1.3521, 103.8198),     # Singapore
]

EVENT_TYPES = ["login", "wire_transfer", "view", "change_beneficiary", "password_reset", "mfa_challenge"]
CHANNELS = ["web", "mobile", "branch"]

def gen_user_id(u): return f"user_{u:05d}"

def synthesize(days=7, users=100, seed=7):
    rng = np.random.default_rng(seed)
    start = datetime.now(timezone.utc) - timedelta(days=days)
    rows = []
    for u in range(users):
        user_id = gen_user_id(u)
        role = "user" if rng.random() > 0.05 else "admin"
        home_idx = rng.integers(0, len(COUNTRIES))
        home = COUNTRIES[home_idx]
        last_lat, last_lon = home[1], home[2]

        events_per_day = rng.integers(5, 20)
        for d in range(days):
            base = start + timedelta(days=d)
            for _ in range(events_per_day):
                et = rng.choice(EVENT_TYPES, p=[0.45, 0.05, 0.35, 0.02, 0.06, 0.07])
                ts = base + timedelta(minutes=int(rng.integers(0, 24*60)))
                if rng.random() < 0.15:  # sometimes travel (geo change)
                    c = COUNTRIES[rng.integers(0, len(COUNTRIES))]
                else:
                    c = home
                lat = float(np.clip(rng.normal(c[1], 0.5), -80, 80))
                lon = float(np.clip(rng.normal(c[2], 0.5), -170, 170))
                amount = 0.0
                if et == "wire_transfer":
                    amount = float(np.abs(rng.normal(15000, 12000)))
                channel = rng.choice(CHANNELS, p=[0.6, 0.35, 0.05])
                is_priv = int(role != "user")
                mfa_success = int(rng.random() > 0.05)

                rows.append({
                    "timestamp": ts.isoformat(),
                    "user_id": user_id,
                    "role": role,
                    "event_type": et,
                    "amount": round(amount, 2),
                    "country": c[0],
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "channel": channel,
                    "is_privileged": is_priv,
                    "mfa_success": mfa_success,
                    "device_id": f"dev_{rng.integers(1, 5000)}",
                    "ip": f"10.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(1,255)}",
                })
    df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)

    # Inject some anomalies
    idx = rng.choice(len(df), size=max(20, len(df)//200), replace=False)
    df.loc[idx, "amount"] = df.loc[idx, "amount"] * 8 + 100000  # very large transfers
    df.loc[idx, "mfa_success"] = 0
    df.loc[idx, "country"] = "RU"

    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--users", type=int, default=100)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=str, default="data/events.csv")
    args = ap.parse_args()

    df = synthesize(days=args.days, users=args.users, seed=args.seed)
    os.makedirs("data", exist_ok=True)
    df.to_csv(args.out, index=False)
    print("Wrote", args.out, "rows=", len(df))

if __name__ == "__main__":
    import os
    main()
