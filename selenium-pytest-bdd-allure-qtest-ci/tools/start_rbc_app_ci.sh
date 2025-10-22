#!/usr/bin/env bash
set -euo pipefail
if [ -d "rbc-security-insights-ai" ]; then
  echo "[CI] Starting local RBC app..."
  pushd rbc-security-insights-ai >/dev/null
  python -m pip install -r requirements.txt
  python -m core.synth --days 2 --users 60 --out data/events.csv
  python -m pipelines.train --in data/events.csv --model_dir models
  python -m pipelines.score --in data/events.csv --model_dir models --out data/insights.csv
  nohup python -m app.app > rbc_app.log 2>&1 &
  popd >/dev/null
else
  echo "[CI] rbc-security-insights-ai directory not found; tests may skip if BASE_URL not reachable."
fi

# wait for http health
for i in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:5010/health >/dev/null 2>&1; then
    echo "[CI] App is up."; exit 0
  fi
  sleep 1
done

echo "[CI] App did not become healthy in time." >&2
exit 1
