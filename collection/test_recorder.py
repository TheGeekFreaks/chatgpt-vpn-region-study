import hashlib
import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import recorder


SCHEDULE = {1: {"visit": 1, "block": 1, "country": "JP", "node_code": "JP-A", "safety": True}}


def payload(response="private markdown"):
    def observation(run_id, arm, personalization):
        return {
            "run_id": run_id, "visit": 1, "arm": arm, "block": 1, "country": "JP", "node_code": "JP-A",
            "start": "2026-09-09T12:00:00Z", "end": "2026-09-09T12:01:00Z", "model_label": "5.6 Hoch",
            "personalization": personalization, "response": response,
            "response_sha256": hashlib.sha256(response.encode()).hexdigest(),
        }
    return {"visit": 1, "browser_pre_verified": 1, "browser_post_verified": 1,
            "observations": [observation("M01", "main", "personalized"), observation("S01", "safety", "non_personalized")]}


class RecorderTests(unittest.TestCase):
    def test_valid_idempotent_and_conflicting_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            data = payload()
            self.assertEqual(2, len(recorder.validate_payload(data, SCHEDULE)))
            first = recorder.save_payload(directory, data)
            second = recorder.save_payload(directory, json.loads(json.dumps(data)))
            self.assertFalse(first[2]); self.assertTrue(second[2]); self.assertEqual(first[1], second[1])
            with self.assertRaises(recorder.ConflictError):
                recorder.save_payload(directory, payload("different private markdown"))

    def test_rejects_bad_hash_invalid_visit_and_incomplete_runs(self):
        bad_hash = payload(); bad_hash["observations"][0]["response_sha256"] = "0" * 64
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(bad_hash, SCHEDULE)
        invalid_visit = payload(); invalid_visit["visit"] = "../1"
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(invalid_visit, SCHEDULE)
        incomplete = payload(); incomplete["observations"].pop()
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(incomplete, SCHEDULE)

    def test_rejects_boolean_or_float_numeric_coercion(self):
        boolean_check = payload(); boolean_check["browser_pre_verified"] = True
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(boolean_check, SCHEDULE)
        float_block = payload(); float_block["observations"][0]["block"] = 1.0
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(float_block, SCHEDULE)

    def test_valid_record_cannot_use_empty_response_placeholder(self):
        missing = payload("")
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(missing, SCHEDULE)
        missing["observations"][0].update(status="technical_failure", deviation_reason="navigation interrupted")
        missing["observations"][1].update(status="technical_failure", deviation_reason="not attempted after interruption")
        self.assertEqual(2, len(recorder.validate_payload(missing, SCHEDULE)))

    def test_rejects_unexpected_top_field_float_visit_and_whitespace_only_values(self):
        extra = payload(); extra["unplanned"] = True
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(extra, SCHEDULE)
        float_visit = payload(); float_visit["observations"][0]["visit"] = 1.0
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(float_visit, SCHEDULE)
        whitespace_response = payload("   ")
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(whitespace_response, SCHEDULE)
        whitespace_reason = payload(); whitespace_reason["observations"][0].update(
            status="technical_failure", response="", response_sha256=recorder.sha256_text(""), deviation_reason="  ")
        with self.assertRaises(recorder.ValidationError): recorder.validate_payload(whitespace_reason, SCHEDULE)

    def test_server_rejects_remote_origin_and_accepts_local_post(self):
        with tempfile.TemporaryDirectory() as directory:
            server = recorder.HTTPServer(("127.0.0.1", 0), recorder.make_handler(Path(directory), SCHEDULE))
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                port = server.server_port; body = json.dumps(payload()).encode()
                connection = http.client.HTTPConnection("127.0.0.1", port)
                connection.request("POST", "/save", body, {"Content-Type": "application/json", "Origin": "https://elsewhere.example"})
                self.assertEqual(403, connection.getresponse().status)
                connection.request("POST", "/save", body, {"Content-Type": "application/json", "Origin": "http://127.0.0.1:%d" % port})
                response = connection.getresponse()
                self.assertEqual(200, response.status); self.assertIn("Gespeichert: visit-01.json", response.read().decode())
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == "__main__":
    unittest.main()
