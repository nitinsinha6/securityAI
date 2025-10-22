# RBC Wealth Management — Security Insights (AI demo)

> **Educational demo**: This is a generic, non-proprietary project scaffold that shows how a bank like **RBC Wealth Management** could surface AI-driven security insights. It uses synthetic data only. Do **not** deploy to production as-is.

## What it does
- Generates **synthetic** login and transaction events for retail/wealth users.
- Builds per-event features and trains an **IsolationForest** to spot anomalies.
- Adds **rules-based** risk signals (e.g., off-hours large transfer, geo jumps).
- Serves a **Flask** API + **dashboard** with top risky events and explanations.

## Stack
- Python, Flask, pandas, numpy, scikit-learn, matplotlib, YAML configs
- Simple local storage (CSV/Parquet) and `joblib` for model artifacts

## Project layout
```
rbc-security-insights-ai/
├─ app/
│  ├─ app.py                  # Flask API + HTML dashboard
│  ├─ dashboard.py            # Plot helpers
│  └─ templates/index.html    # Dashboard template
├─ core/
│  ├─ synth.py                # Synthetic event generator
│  ├─ features.py             # Feature engineering + rules
│  ├─ model.py                # Train/score (IsolationForest + risk fusion)
│  ├─ utils.py                # Haversine, time utils, etc.
│  └─ config.py               # Loads YAML config
├─ pipelines/
│  ├─ train.py                # Train model on synthetic baseline
│  └─ score.py                # Score new events and produce insights.csv
├─ configs/
│  └─ policy.yaml             # Thresholds, geo, business hours
├─ data/                      # Synthetic data and outputs
├─ models/                    # Saved model + scalers
├─ tests/
│  ├─ test_synth.py
│  ├─ test_features.py
│  └─ test_model.py
├─ requirements.txt
└─ README.md
```

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1) Create synthetic data
```bash
python -m core.synth --days 10 --users 200 --out data/events.csv
```

### 2) Train the AI model on baseline
```bash
python -m pipelines.train --in data/events.csv --model_dir models
```

### 3) Score and produce insights
```bash
python -m pipelines.score --in data/events.csv --model_dir models --out data/insights.csv
```

### 4) Run the dashboard
```bash
python app/app.py
# http://127.0.0.1:5010
```

## API
- `GET /health` → `{"status":"ok"}`
- `GET /insights?limit=100` → top risk events with reasons
- `POST /ingest` → `{ "events": [ ... ] }` to append new events and re-score (toy behavior)

## Notes
- Replace synthetic generator + CSV with your own secure ingestion (SIEM/EDR/streams).
- Evaluate with real labels and governance. Tune thresholds in `configs/policy.yaml`.
- For LLM-based incident summaries, plug a provider in `core/model.py:ai_summary()`.
