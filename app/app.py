from flask import Flask, jsonify, request, render_template
import os, pandas as pd, json
from core.model import infer, ai_summary
from core.config import load_policy
from .dashboard import (
    chart_risk_by_event_type, chart_risk_over_time, chart_top_users, chart_rules_bar, chart_risk_by_country
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "events.csv")
INSIGHTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "insights.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
POLICY_PATH = os.path.join(os.path.dirname(__file__), "..", "configs", "policy.yaml")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = Flask(__name__, template_folder="templates", static_folder="static")


def _resolve_logo():
    # Prefer a user-provided real logo if present; fall back to placeholder.
    cand = [
        os.path.join(STATIC_DIR, "brand", "rbc_logo.svg"),
        os.path.join(STATIC_DIR, "brand", "rbc_logo.png"),
        os.path.join(STATIC_DIR, "brand", "logo.svg"),
        os.path.join(STATIC_DIR, "brand", "logo.png"),
        os.path.join(STATIC_DIR, "brand", "placeholder_rbc_logo.svg"),
    ]
    for p in cand:
        if os.path.exists(p):
            return "/static/brand/" + os.path.basename(p)
    return "/static/brand/placeholder_rbc_logo.svg"


@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/insights")
def insights():
    limit = int(request.args.get("limit", 100))
    if not os.path.exists(INSIGHTS_PATH):
        return jsonify({"error":"no insights yet; run the scoring pipeline"}), 404
    df = pd.read_csv(INSIGHTS_PATH)
    payload = df.sort_values("risk_score", ascending=False).head(limit).fillna("").to_dict(orient="records")
    return jsonify({"count": len(payload), "items": payload})

@app.route("/ingest", methods=["POST"])
def ingest():
    body = request.get_json(force=True, silent=True) or {}
    events = body.get("events", [])
    if not events:
        return jsonify({"error":"no events"}), 400
    df_new = pd.DataFrame(events)
    if os.path.exists(DATA_PATH):
        df_old = pd.read_csv(DATA_PATH)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

    try:
        df_sc = infer(df, model_dir=MODEL_DIR, policy_path=POLICY_PATH)
        df_sc["summary"] = df_sc.apply(ai_summary, axis=1)
        df_sc.sort_values("risk_score", ascending=False).to_csv(INSIGHTS_PATH, index=False)
    except Exception as e:
        return jsonify({"status":"ingested", "warning": str(e)}), 202
    return jsonify({"status":"ingested_and_scored", "rows": len(events)})

def _kpis(df: pd.DataFrame):
    total = len(df)
    high = int((df.get("sev","")== "high").sum()) if "sev" in df.columns else int((df["risk_score"]>=0.8).sum())
    med = int((df.get("sev","")== "medium").sum()) if "sev" in df.columns else int((df["risk_score"].between(0.6,0.8)).sum())
    low = int((df.get("sev","")== "low").sum()) if "sev" in df.columns else total - high - med
    avg = float(df["risk_score"].mean()) if "risk_score" in df.columns else 0.0
    return {"total": total, "high": high, "medium": med, "low": low, "avg": round(avg, 3)}

def _charts_for_view(view: str, df: pd.DataFrame):
    charts = []
    if view == "exec":
        chart_risk_over_time(df, os.path.join(STATIC_DIR, "risk_trend.png"), freq="D")
        charts.append(("/static/risk_trend.png", "Risk Trend"))
    elif view == "compliance":
        df_c = df[df["event_type"].isin(["wire_transfer","change_beneficiary","password_reset"])].copy()
        if df_c.empty: df_c = df.copy()
        chart_rules_bar(df_c, os.path.join(STATIC_DIR, "rules.png"))
        chart_risk_by_country(df_c, os.path.join(STATIC_DIR, "risk_by_country.png"))
        charts.extend([("/static/rules.png", "Top Rules"), ("/static/risk_by_country.png", "Risk by Country")])
    elif view == "advisor":
        chart_top_users(df, os.path.join(STATIC_DIR, "top_clients.png"), metric="max", title="Top Clients by Risk")
        chart_risk_by_event_type(df, os.path.join(STATIC_DIR, "risk_by_event.png"))
        charts.extend([("/static/top_clients.png", "Top Clients"), ("/static/risk_by_event.png", "Risk by Event")])
    else:
        chart_risk_over_time(df, os.path.join(STATIC_DIR, "risk_trend.png"), freq="H")
        chart_top_users(df, os.path.join(STATIC_DIR, "top_users.png"))
        chart_rules_bar(df, os.path.join(STATIC_DIR, "rules.png"))
        charts.extend([("/static/risk_trend.png", "Risk Trend (Hourly)"),
                       ("/static/top_users.png", "Top Users"),
                       ("/static/rules.png", "Top Rules")])
    return charts

@app.route("/")
def index():
    if not os.path.exists(INSIGHTS_PATH):
        return "<h3>No insights yet. Run pipelines/train.py and pipelines/score.py first.</h3>"
    view = request.args.get("view", "soc")
    df = pd.read_csv(INSIGHTS_PATH)
    os.makedirs(STATIC_DIR, exist_ok=True)
    charts = _charts_for_view(view, df)
    if view == "exec":
        items = df.sort_values("risk_score", ascending=False).head(25).to_dict(orient="records")
    elif view == "compliance":
        items = df[df["event_type"].isin(["wire_transfer","change_beneficiary","password_reset"])].sort_values("risk_score", ascending=False).head(50).to_dict(orient="records")
    elif view == "advisor":
        items = df.sort_values("risk_score", ascending=False).groupby("user_id").head(1).head(50).to_dict(orient="records")
    else:
        items = df.sort_values("risk_score", ascending=False).head(100).to_dict(orient="records")
    kpis = _kpis(df)
    return render_template("index.html", items=items, charts=charts, view=view, kpis=kpis, brand_name="RBC Wealth Management", logo_url=_resolve_logo())

if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.run(host="127.0.0.1", port=5010, debug=False, threaded=True)
