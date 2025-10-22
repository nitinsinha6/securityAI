import os
import json
import time
from typing import Dict, Any, List
import requests
from urllib.parse import urljoin

class QTestClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/') + '/'
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def create_auto_test_logs(self, project_id: str, payload: Dict[str, Any]):
        endpoint = urljoin(self.base_url, f"api/v3/projects/{project_id}/auto-test-logs")
        resp = self.session.post(endpoint, data=json.dumps(payload), timeout=60)
        return resp

def map_allure_status_to_qtest(status: str) -> str:
    status = (status or "").lower()
    if status in ("passed", "pass"): return "PASS"
    if status in ("failed", "broken", "fail"): return "FAIL"
    if status in ("skipped", "unknown"): return "SKIPPED"
    return "UNDEFINED"

def build_qtest_payload_from_allure(allure_results: List[Dict[str, Any]],
                                    release_id: str = None,
                                    test_cycle_id: str = None,
                                    test_suite_id: str = None) -> Dict[str, Any]:
    test_logs = []
    now_ms = int(time.time() * 1000)

    for test in allure_results:
        if not isinstance(test, dict) or not test.get("status"): 
            continue
        name = test.get("name") or test.get("fullName") or "Unnamed Test"
        status = map_allure_status_to_qtest(test.get("status"))
        duration = (test.get("time") or {}).get("duration") or 0
        external_id = None
        for lbl in test.get("labels", []):
            if lbl.get("name") in ("testcase", "testcase_external_id", "tms"):
                external_id = lbl.get("value"); break

        log = {
            "name": name,
            "status": status,
            "automationContent": test.get("fullName", name),
            "exe_start_date": now_ms - duration,
            "exe_end_date": now_ms,
            "moduleNames": ["Automation"],
            "attachments": [],
            "testCase": {"externalId": external_id} if external_id else None,
        }
        test_logs.append(log)

    payload = {
        "testLogs": test_logs,
        "executionDate": now_ms,
        "testCycle": {"id": test_cycle_id} if test_cycle_id else None,
        "testSuite": {"id": test_suite_id} if test_suite_id else None,
        "release": {"id": release_id} if release_id else None,
    }

    def _prune(obj):
        if isinstance(obj, dict):
            return {k: _prune(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [_prune(x) for x in obj if x is not None]
        return obj
    return _prune(payload)
