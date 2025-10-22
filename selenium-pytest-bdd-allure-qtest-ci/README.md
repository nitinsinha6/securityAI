# Selenium + pytest-bdd + Allure + qTest (Starter)

End-to-end testing scaffold with:
- **Selenium WebDriver** (Chrome, headless by default)
- **pytest-bdd** for BDD-style scenarios
- **Allure** reporting (via `allure-pytest`)
- **qTest** push script that converts Allure test-cases to qTest auto test logs

## Install
```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests
By default, tests look for the app at `http://127.0.0.1:5010`.
You can override with `--base-url` or env `BASE_URL`.

```bash
pytest --base-url http://127.0.0.1:5010
```

Allure raw results are stored under `reports/allure-results` (per `pytest.ini`).

### Allure HTML
Install the Allure CLI, then:
```bash
allure serve reports/allure-results
# or
allure generate reports/allure-results -o allure-report --clean && allure open allure-report
```

## qTest push
```bash
export QTEST_BASE_URL="https://your-qtest-url"
export QTEST_PROJECT_ID="12345"
export QTEST_TOKEN="YOUR_PERSONAL_ACCESS_TOKEN"
python qtest_integration/qtest_push.py reports/allure-results
```


---

## CI: GitHub Actions (parallel + Allure + PDF + qTest)
- Workflow: `.github/workflows/ci.yml`
- Runs `pytest -n auto` (parallel) and writes Allure results to `reports/allure-results/`
- Generates Allure HTML and a best-effort PDF (`wkhtmltopdf`)
- Uploads artifacts and (optionally) **deploys Allure HTML to GitHub Pages**
- Tries to start the **local RBC demo app** if `rbc-security-insights-ai/` exists.
- If you want qTest push, set these **repository secrets**:
  - `QTEST_BASE_URL`, `QTEST_PROJECT_ID`, `QTEST_TOKEN` (and optional `QTEST_RELEASE_ID`, `QTEST_TEST_CYCLE_ID`, `QTEST_TEST_SUITE_ID`)

### Enable GitHub Pages
1. Go to **Settings → Pages**
2. Set **Source** to “GitHub Actions”
3. After a push to `main`/`master`, the `pages` job will publish the Allure site.

### Custom BASE_URL
- The CI assumes the AUT is at `http://127.0.0.1:5010`.
- Update `env.BASE_URL` in the workflow or pass `--base-url` differently.

