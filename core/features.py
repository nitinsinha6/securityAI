import pandas as pd
import numpy as np
from datetime import datetime, timezone
from .utils import haversine_km, parse_ts, is_off_hours

def add_features(df: pd.DataFrame, business_start=8, business_end=18) -> pd.DataFrame:
    df = df.copy()
    df["ts"] = pd.to_datetime(df["timestamp"], utc=True)
    df["hour"] = df["ts"].dt.hour
    df["dayofweek"] = df["ts"].dt.dayofweek
    df["off_hours"] = df["ts"].apply(lambda x: is_off_hours(x, business_start, business_end)).astype(int)

    # Per-user rolling stats (7d)
    df = df.sort_values(["user_id", "ts"])
    df["amount_roll_mean_7d"] = (
        df.groupby("user_id")["amount"]
        .transform(lambda s: s.rolling(window=50, min_periods=5).mean())
        .fillna(0)
    )
    df["amount_roll_std_7d"] = (
        df.groupby("user_id")["amount"]
        .transform(lambda s: s.rolling(window=50, min_periods=5).std())
        .fillna(0)
    )
    df["login_cnt_24h"] = (
        (df["event_type"] == "login")
        .groupby(df["user_id"])
        .transform(lambda s: s.rolling(window=30, min_periods=1).sum())
        .astype(int)
    )
    # Geo distance from last event per user
    df["prev_lat"] = df.groupby("user_id")["lat"].shift(1)
    df["prev_lon"] = df.groupby("user_id")["lon"].shift(1)
    df["geo_km_from_prev"] = [
        haversine_km(a, b, c, d) if not pd.isna(a) else 0.0
        for a, b, c, d in zip(df["prev_lat"], df["prev_lon"], df["lat"], df["lon"])
    ]
    df["geo_km_from_prev"] = df["geo_km_from_prev"].fillna(0.0)

    # Categorical encodings
    for col in ["event_type", "country", "channel", "role"]:
        df[col + "_code"] = df[col].astype("category").cat.codes

    # Final feature set
    feature_cols = [
        "hour","dayofweek","off_hours",
        "amount","amount_roll_mean_7d","amount_roll_std_7d",
        "login_cnt_24h",
        "geo_km_from_prev",
        "event_type_code","country_code","channel_code","role_code",
        "is_privileged","mfa_success"
    ]
    return df, feature_cols

def apply_rules(row, policy) -> list:
    reasons = []
    if row.get("off_hours") == 1 and row.get("event_type") == "wire_transfer" and row.get("amount",0) > policy.large_transfer_amount:
        reasons.append("OFF_HOURS_LARGE_TRANSFER")
    if row.get("country") in policy.high_risk_countries:
        reasons.append("HIGH_RISK_COUNTRY")
    if row.get("geo_km_from_prev",0) >= policy.geo_jump_km:
        reasons.append("GEO_IMPOSSIBLE_TRAVEL")
    if row.get("is_privileged") == 1 and row.get("event_type") in ("change_beneficiary","password_reset"):
        reasons.append("PRIVILEGED_SENSITIVE_ACTION")
    if row.get("event_type") == "mfa_challenge" and row.get("mfa_success") == 0:
        reasons.append("FAILED_MFA")
    return reasons
