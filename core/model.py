import os, json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
from .features import add_features, apply_rules
from .config import load_policy

def train(df: pd.DataFrame, policy_path="configs/policy.yaml"):
    policy = load_policy(policy_path)
    df_f, feature_cols = add_features(df, policy.business_hours["start"], policy.business_hours["end"])
    X = df_f[feature_cols].to_numpy(dtype=float)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    iso = IsolationForest(n_estimators=250, contamination=0.02, random_state=13)
    iso.fit(Xs)
    return {"model": iso, "scaler": scaler, "feature_cols": feature_cols}

def save_artifacts(art, model_dir="models"):
    os.makedirs(model_dir, exist_ok=True)
    dump(art["model"], os.path.join(model_dir, "iso_model.joblib"))
    dump(art["scaler"], os.path.join(model_dir, "scaler.joblib"))
    with open(os.path.join(model_dir, "features.json"), "w", encoding="utf-8") as f:
        json.dump(art["feature_cols"], f)

def load_artifacts(model_dir="models"):
    model = load(os.path.join(model_dir, "iso_model.joblib"))
    scaler = load(os.path.join(model_dir, "scaler.joblib"))
    with open(os.path.join(model_dir, "features.json"), "r", encoding="utf-8") as f:
        feature_cols = json.load(f)
    return {"model": model, "scaler": scaler, "feature_cols": feature_cols}

def infer(df: pd.DataFrame, model_dir="models", policy_path="configs/policy.yaml"):
    policy = load_policy(policy_path)
    df_f, feature_cols = add_features(df, policy.business_hours["start"], policy.business_hours["end"])
    art = load_artifacts(model_dir)
    assert feature_cols == art["feature_cols"], "Feature mismatch: retrain recommended"
    X = df_f[feature_cols].to_numpy(dtype=float)
    Xs = art["scaler"].transform(X)
    # decision_function: higher is more normal; invert to "anomaly score"
    anomaly_raw = -art["model"].decision_function(Xs)
    # Normalize to 0..1 via min-max within sample (toy normalization)
    min_v, max_v = float(np.min(anomaly_raw)), float(np.max(anomaly_raw))
    eps = 1e-9
    anomaly_prob = (anomaly_raw - min_v) / (max_v - min_v + eps)
    df_out = df_f.copy()
    df_out["anomaly_prob"] = anomaly_prob

    # Apply rules and fuse risk
    fused = []
    reasons_list = []
    for _, r in df_out.iterrows():
        reasons = apply_rules(r, policy)
        score = float(r["anomaly_prob"])
        if len(reasons) >= policy.thresholds.get("rules_alert", 2):
            score = min(1.0, score + 0.2 + 0.1*len(reasons))
        fused.append(score)
        reasons_list.append(reasons)
    df_out["risk_score"] = fused
    df_out["reasons"] = reasons_list
    df_out["sev"] = pd.cut(df_out["risk_score"], bins=[-1,0.6,0.8,1.1], labels=["low","medium","high"])
    return df_out

def ai_summary(row: pd.Series) -> str:
    # Lightweight extractive summary with simple templates (LLM pluggable)
    base = f"User {row['user_id']} triggered {row['event_type']} in {row['country']} at {row['timestamp']}"
    if row.get("event_type") == "wire_transfer":
        base += f" for ${row['amount']:.2f}"
    if row.get("off_hours") == 1:
        base += " outside business hours"
    if row.get("reasons"):
        base += f"; flags: {', '.join(row['reasons'])}"
    base += f". Risk={row['risk_score']:.2f} (sev={row['sev']})."
    return base
