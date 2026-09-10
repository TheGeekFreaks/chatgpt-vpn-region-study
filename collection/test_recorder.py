import hashlib
import http.client
import json
import socket
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


def evidence(data=None):
    return {"evidence_id": "baseline", "data": {"private": "snapshot"} if data is None else data}


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

    def test_custom_schedule_supports_main_only_visit(self):
        with tempfile.TemporaryDirectory() as directory:
            schedule_path = Path(directory) / "schedule.json"
            v2 = json.loads(recorder.SCHEDULE.read_text(encoding="utf-8"))
            v2.update(collected_model="GPT-6 Astra", effort="pro", chat_mode="regular", model_label="6 Pro")
            for item in v2["visits"]: item["safety"] = False
            schedule_path.write_text(json.dumps(v2), encoding="utf-8")
            main_only = payload(); main_only["observations"].pop()
            loaded = recorder.load_schedule(schedule_path)
            main_only["observations"][0].update(model_label="6 Pro", collected_model="GPT-6 Astra", effort="pro", chat_mode="regular", prompt_sha256=v2["main_prompt_sha256"])
            self.assertEqual(1, len(recorder.validate_payload(main_only, loaded)))
            server = recorder.create_server(directory, 0, schedule_path)
            self.assertEqual("127.0.0.1", server.server_address[0]); server.server_close()
            provenance = json.loads((Path(directory) / "schedule-provenance.json").read_text())
            self.assertEqual(hashlib.sha256(schedule_path.read_bytes()).hexdigest(), provenance["schedule_sha256"])
            v2["seed"] += 1; schedule_path.write_text(json.dumps(v2), encoding="utf-8")
            with self.assertRaises(recorder.ConflictError): recorder.create_server(directory, 0, schedule_path)

    def test_malformed_schedule_fails_before_server_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            broken = json.loads(recorder.SCHEDULE.read_text(encoding="utf-8"))
            del broken["visits"][0]["safety"]
            schedule_path = Path(directory) / "broken.json"
            schedule_path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(recorder.ValidationError): recorder.create_server(directory, 0, schedule_path)

    def test_failed_bind_writes_no_provenance_and_null_chat_mode_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            schedule_path = Path(directory) / "schedule.json"
            schedule_path.write_bytes(recorder.SCHEDULE.read_bytes())
            with socket.socket() as occupied:
                occupied.bind(("127.0.0.1", 0))
                with self.assertRaises(OSError): recorder.create_server(directory, occupied.getsockname()[1], schedule_path)
            self.assertFalse((Path(directory) / "schedule-provenance.json").exists())
            invalid = payload(); invalid["observations"][0]["chat_mode"] = None
            with self.assertRaises(recorder.ValidationError): recorder.validate_payload(invalid, SCHEDULE)

    def test_evidence_is_allowlisted_immutable_and_separate_from_visits(self):
        with tempfile.TemporaryDirectory() as directory:
            visits = Path(directory) / "visits"; visits.mkdir()
            item = evidence(); recorder.validate_evidence(item)
            first = recorder.save_evidence(visits, item)
            second = recorder.save_evidence(visits, json.loads(json.dumps(item)))
            self.assertFalse(first[2]); self.assertTrue(second[2]); self.assertEqual(first[1], second[1])
            self.assertTrue((Path(directory) / "evidence" / "baseline.json").is_file())
            with self.assertRaises(recorder.ConflictError): recorder.save_evidence(visits, evidence({"private": "changed"}))
            with self.assertRaises(recorder.ValidationError): recorder.validate_evidence({"evidence_id": "../baseline", "data": {}})

    def test_recorder_rejects_public_visits_and_sibling_evidence_paths(self):
        public_visits = (
            recorder.PUBLIC_STUDY_ROOT / "test-recorder-public-output" / "visits"
        )
        with self.assertRaises(recorder.ValidationError):
            recorder.create_server(public_visits, 0)
        with self.assertRaises(recorder.ValidationError):
            recorder.save_payload(public_visits, payload())
        with self.assertRaises(recorder.ValidationError):
            recorder.save_evidence(public_visits, evidence())
        self.assertFalse(public_visits.exists())
        self.assertFalse((public_visits.parent / "evidence").exists())

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

    def test_server_saves_evidence_and_rejects_oversize_body(self):
        with tempfile.TemporaryDirectory() as directory:
            visits = Path(directory) / "visits"; visits.mkdir()
            server = recorder.HTTPServer(("127.0.0.1", 0), recorder.make_handler(visits, SCHEDULE))
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                port = server.server_port; headers = {"Content-Type": "application/json", "Origin": "http://127.0.0.1:%d" % port}
                connection = http.client.HTTPConnection("127.0.0.1", port)
                connection.request("POST", "/evidence", json.dumps(evidence()).encode(), headers)
                response = connection.getresponse()
                self.assertEqual(200, response.status); self.assertIn("Gespeichert: evidence/baseline.json", response.read().decode())
                connection.request("POST", "/evidence", b"x" * (recorder.MAX_POST + 1), headers)
                self.assertEqual(400, connection.getresponse().status)
                connection.request("POST", "/evidence", b'{"evidence_id":"end-context","data":"\\ud800"}', headers)
                self.assertEqual(400, connection.getresponse().status)
                self.assertFalse((Path(directory) / "evidence" / "end-context.json").exists())
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == "__main__":
    unittest.main()
