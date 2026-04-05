"""
Unit tests for FinTechFuzzer class.
Tests run without a live server — only the fuzzer's internal state and utilities
are exercised here.
"""
import json
import os
import pytest
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_fuzzer(tmp_path):
    """Import FinTechFuzzer with artifacts_dir pointing at tmp_path."""
    import importlib
    import sys

    # Ensure src/ is on the path
    src_root = Path(__file__).parent.parent / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from fuzzer import FinTechFuzzer
    f = FinTechFuzzer(base_url="http://localhost:9999")
    f.artifacts_dir = str(tmp_path)
    os.makedirs(f.artifacts_dir, exist_ok=True)
    return f


# ── Tests ────────────────────────────────────────────────────────────────────

class TestFuzzerInitialState:
    def test_initial_result_counters_are_zero(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        for key in ("total_tests", "crashes", "errors", "warnings", "successful"):
            assert fuzz.results[key] == 0

    def test_initial_artifacts_list_is_empty(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        assert fuzz.results["artifacts"] == []

    def test_base_url_has_no_trailing_slash(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        assert not fuzz.base_url.endswith("/")


class TestSaveArtifact:
    def test_returns_artifact_dict(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        artifact = fuzz.save_artifact("sql_injection", {"id": "1' OR 1=1--"}, None)
        assert isinstance(artifact, dict)
        assert artifact["test_type"] == "sql_injection"
        assert artifact["payload"] == {"id": "1' OR 1=1--"}

    def test_artifact_file_written_to_disk(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        fuzz.save_artifact("overflow", "A" * 10000, None)
        files = list(tmp_path.glob("overflow_*.json"))
        assert len(files) == 1

    def test_artifact_file_is_valid_json(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        fuzz.save_artifact("malformed", {"$key": True}, {"status": 500})
        files = list(tmp_path.glob("malformed_*.json"))
        with open(files[0]) as f:
            data = json.load(f)
        assert data["test_type"] == "malformed"

    def test_artifact_appended_to_results_list(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        fuzz.save_artifact("t1", "payload1", None)
        fuzz.save_artifact("t2", "payload2", None)
        assert len(fuzz.results["artifacts"]) == 2

    def test_artifact_stores_error_field(self, tmp_path):
        fuzz = make_fuzzer(tmp_path)
        artifact = fuzz.save_artifact("error_test", {}, None, error="connection refused")
        assert artifact["error"] == "connection refused"


class TestResultCounters:
    def test_total_tests_incremented_on_endpoint_call(self, tmp_path):
        """save_artifact does NOT increment total_tests; test_endpoint does."""
        from unittest.mock import patch, MagicMock
        fuzz = make_fuzzer(tmp_path)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        with patch("requests.post", return_value=mock_resp):
            fuzz.test_endpoint("/test", method="POST", payload={"amount": 1})
        assert fuzz.results["total_tests"] == 1
