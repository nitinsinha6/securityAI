import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend for server-side rendering
import matplotlib.pyplot as plt
import numpy as np
import ast

def _ensure_dir(p):
    os.makedirs(os.path.dirname(p), exist_ok=True)

def _save(fig, out_path):
    _ensure_dir(out_path)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)

def parse_reasons_column(df: pd.DataFrame) -> pd.Series:
    def _parse(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            x = x.strip()
            if x.startswith('[') and x.endswith(']'):
                try:
                    return ast.literal_eval(x)
                except Exception:
                    return [x]
            if x:
                return [x]
        return []
    return df.get("reasons", pd.Series(dtype=object)).apply(_parse)

def chart_risk_by_event_type(df: pd.DataFrame, out_path: str):
    agg = df.groupby("event_type")["risk_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(agg.index, agg.values)
    ax.set_title("Avg Risk by Event Type")
    ax.set_ylabel("Avg risk score")
    ax.set_xlabel("Event type")
    _save(fig, out_path)

def chart_risk_over_time(df: pd.DataFrame, out_path: str, freq="D"):
    dft = df.copy()
    dft["ts"] = pd.to_datetime(dft["timestamp"], utc=True)
    agg = dft.set_index("ts").resample(freq)["risk_score"].mean().fillna(0.0)
    fig, ax = plt.subplots(figsize=(7,3.5))
    ax.plot(agg.index, agg.values)
    ax.set_title(f"Risk Trend ({freq}-avg)")
    ax.set_ylabel("Avg risk score")
    ax.set_xlabel("Time")
    _save(fig, out_path)

def chart_top_users(df: pd.DataFrame, out_path: str, metric="max", top_n=12, title="Top Users by Risk"):
    if metric == "mean":
        agg = df.groupby("user_id")["risk_score"].mean().sort_values(ascending=False).head(top_n)
    else:
        agg = df.groupby("user_id")["risk_score"].max().sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(agg.index.astype(str), agg.values)
    ax.set_title(title)
    ax.set_ylabel("Risk score")
    ax.set_xlabel("User")
    ax.tick_params(axis='x', labelrotation=45)
    _save(fig, out_path)

def chart_rules_bar(df: pd.DataFrame, out_path: str, top_n=10):
    reasons_series = parse_reasons_column(df)
    exploded = pd.Series([r for L in reasons_series for r in (L or [])], dtype=object)
    counts = exploded.value_counts().head(top_n) if not exploded.empty else pd.Series([], dtype=int)
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(counts.index.astype(str), counts.values)
    ax.set_title("Top Rule Triggers")
    ax.set_ylabel("Count")
    ax.set_xlabel("Rule")
    ax.tick_params(axis='x', labelrotation=45)
    _save(fig, out_path)

def chart_risk_by_country(df: pd.DataFrame, out_path: str):
    agg = df.groupby("country")["risk_score"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(agg.index.astype(str), agg.values)
    ax.set_title("Avg Risk by Country")
    ax.set_ylabel("Avg risk score")
    ax.set_xlabel("Country")
    _save(fig, out_path)
