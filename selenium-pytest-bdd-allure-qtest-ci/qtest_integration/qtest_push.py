import os, sys, json, glob
from qtest_client import QTestClient, build_qtest_payload_from_allure

def load_allure_testcases(results_dir: str):
    data = []
    for fp in glob.glob(os.path.join(results_dir, "*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, dict) and obj.get("status") and obj.get("name"):
                data.append(obj)
        except Exception:
            continue
    return data

def main():
    if len(sys.argv) < 2:
        print("Usage: python qtest_push.py <path-to-allure-results-dir>")
        sys.exit(2)

    results_dir = sys.argv[1]
    base_url = os.environ.get("Qhttps://analytics1.qtestnet.com/")
    project_id = os.environ.get("23149")
    token = os.environ.get("Bearer c5314029-ea1b-466d-adf2-62fdba5da189")
    release_id = os.environ.get("R4")
    test_cycle_id = os.environ.get("QTEST_TEST_CYCLE_ID")
    test_suite_id = os.environ.get("8988185")

    if not all([base_url, project_id, token]):
        print("Missing env vars. Set QTEST_BASE_URL, QTEST_PROJECT_ID, QTEST_TOKEN."); sys.exit(3)

    allure_cases = load_allure_testcases(results_dir)
    if not allure_cases:
        print("No Allure test-case JSON files found in", results_dir); sys.exit(4)

    client = QTestClient(base_url, token)
    payload = build_qtest_payload_from_allure(allure_cases,
                                              release_id=release_id,
                                              test_cycle_id=test_cycle_id,
                                              test_suite_id=test_suite_id)
    resp = client.create_auto_test_logs(project_id, payload)
    print("qTest response status:", resp.status_code)
    try:
        print("qTest response body:", resp.json())
    except Exception:
        print("qTest response text:", resp.text)

if __name__ == "__main__":
    main()
