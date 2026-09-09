"""Loopback-only recorder for private ChatGPT route-study measurements."""

import argparse
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

MAX_POST = 1_000_000
SCHEDULE = Path(__file__).resolve().parent.parent / "protocol" / "schedule.json"
REQUIRED = {
    "run_id", "visit", "arm", "block", "country", "node_code", "start", "end",
    "model_label", "personalization", "response", "response_sha256",
}
OPTIONAL = {"collected_model", "effort", "prompt_sha256", "status", "deviation_reason"}
TOP_REQUIRED = {"visit", "browser_pre_verified", "browser_post_verified", "observations"}
TOP_ALLOWED = TOP_REQUIRED | {"same_ip_verified"}


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_schedule(path=SCHEDULE):
    with Path(path).open(encoding="utf-8") as source:
        source_data = json.load(source)
    visits = {item["visit"]: item for item in source_data["visits"]}
    visits["_main_prompt_sha256"] = source_data.get("main_prompt_sha256")
    visits["_safety_prompt_sha256"] = source_data.get("safety_prompt_sha256")
    return visits


def validate_payload(payload, schedule):
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object")
    if not TOP_REQUIRED.issubset(payload) or not set(payload).issubset(TOP_ALLOWED):
        raise ValidationError("unexpected payload fields")
    visit = payload.get("visit")
    if type(visit) is not int or visit not in schedule or not 1 <= visit <= 24:
        raise ValidationError("invalid visit")
    if (type(payload.get("browser_pre_verified")) is not int or payload["browser_pre_verified"] != 1 or
            type(payload.get("browser_post_verified")) is not int or payload["browser_post_verified"] != 1):
        raise ValidationError("browser verification is incomplete")
    if "same_ip_verified" in payload and (type(payload["same_ip_verified"]) is not int or payload["same_ip_verified"] != 1):
        raise ValidationError("IP verification is incomplete")
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise ValidationError("observations must be a list")
    planned = schedule[visit]
    expected = {"M%02d" % visit}
    if planned["safety"]:
        expected.add("S%02d" % visit)
    seen, hashes = set(), []
    for observation in observations:
        if (not isinstance(observation, dict) or not REQUIRED.issubset(observation)
                or not set(observation).issubset(REQUIRED | OPTIONAL)):
            raise ValidationError("incomplete observation")
        run_id = observation["run_id"]
        if not isinstance(run_id, str) or run_id in seen or run_id not in expected:
            raise ValidationError("unexpected or duplicate run_id")
        seen.add(run_id)
        arm = "main" if run_id.startswith("M") else "safety"
        personalization = "personalized" if arm == "main" else "non_personalized"
        if (type(observation["visit"]) is not int or observation["visit"] != visit or observation["arm"] != arm or
                observation["personalization"] != personalization or
                observation["model_label"] != "5.6 Hoch"):
            raise ValidationError("run metadata does not match protocol")
        if type(observation["block"]) is not int or observation["block"] != planned["block"]:
            raise ValidationError("route metadata does not match schedule")
        for key in ("country", "node_code"):
            if not isinstance(observation[key], str) or observation[key] != planned[key]:
                raise ValidationError("route metadata does not match schedule")
        if "collected_model" in observation and observation["collected_model"] != "GPT-5.6 Sol":
            raise ValidationError("unexpected collected model")
        if "effort" in observation and observation["effort"] != "high":
            raise ValidationError("unexpected effort")
        prompt_hash = schedule.get("_%s_prompt_sha256" % arm)
        if "prompt_sha256" in observation and (not isinstance(observation["prompt_sha256"], str)
                                                or prompt_hash is not None and not hmac.compare_digest(observation["prompt_sha256"], prompt_hash)):
            raise ValidationError("prompt hash does not match protocol")
        if not all(isinstance(observation[key], str) for key in ("start", "end", "response")):
            raise ValidationError("response and timestamps must be strings")
        status = observation.get("status", "valid")
        reason = observation.get("deviation_reason", "")
        if status not in ("valid", "technical_failure") or not isinstance(reason, str):
            raise ValidationError("invalid observation status")
        if status == "technical_failure" and (observation["response"] != "" or not reason.strip()):
            raise ValidationError("technical failure requires an empty response and reason")
        if status == "valid" and (not observation["response"].strip() or reason):
            raise ValidationError("valid observation requires a response and no deviation")
        claimed = observation["response_sha256"]
        actual = sha256_text(observation["response"])
        if not isinstance(claimed, str) or not hmac.compare_digest(claimed, actual):
            raise ValidationError("response hash mismatch")
        hashes.append(actual)
    if seen != expected:
        raise ValidationError("missing planned observation")
    return hashes


def save_payload(out_dir, payload):
    out_dir = Path(out_dir)
    filename = "visit-%02d.json" % payload["visit"]
    target = out_dir / filename
    data = canonical(payload)
    saved_sha = hashlib.sha256(data).hexdigest()
    try:
        with target.open("xb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    except FileExistsError:
        if target.read_bytes() != data:
            raise ConflictError("existing visit differs")
        return filename, saved_sha, True
    return filename, saved_sha, False


PAGE = b'''<!doctype html><meta charset="utf-8"><title>Lokaler Messrekorder</title>
<form id="record"><label for="data">Messdaten JSON</label><br><textarea id="data" rows="24" cols="90" required></textarea><br><button>Lokal sichern</button></form><p id="status" aria-live="polite"></p>
<script>document.getElementById('record').onsubmit=async e=>{e.preventDefault();let r=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:document.getElementById('data').value});document.getElementById('status').textContent=await r.text()};</script>'''


def make_handler(out_dir, schedule):
    class Recorder(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Never write request bodies or browser metadata to a log.

        def allowed(self):
            host = "127.0.0.1:%d" % self.server.server_port
            origin = self.headers.get("Origin")
            return self.headers.get("Host") == host and (origin is None or origin == "http://" + host)

        def reply(self, status, body, content_type="text/plain; charset=utf-8"):
            encoded = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            if not self.allowed():
                self.reply(403, "Verbindung abgelehnt.")
            elif self.path == "/":
                self.reply(200, PAGE, "text/html; charset=utf-8")
            else:
                self.reply(404, "Nicht gefunden.")

        def do_POST(self):
            if not self.allowed():
                self.reply(403, "Verbindung abgelehnt.")
                return
            if self.path != "/save":
                self.reply(404, "Nicht gefunden.")
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= MAX_POST:
                    raise ValidationError("invalid content length")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                response_hashes = validate_payload(payload, schedule)
                filename, saved_sha, replay = save_payload(out_dir, payload)
            except ConflictError:
                self.reply(409, "Dieser Besuch ist bereits anders gespeichert.")
            except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, OSError):
                self.reply(400, "Ungültige Messdaten.")
            else:
                prefix = "Bereits gespeichert" if replay else "Gespeichert"
                self.reply(200, "%s: %s\nAntwort-Hashes: %s\nKanonischer Datensatz-Hash: %s" %
                           (prefix, filename, ", ".join(response_hashes), saved_sha))

    return Recorder


def create_server(out_dir, port=43127, schedule_path=SCHEDULE):
    return HTTPServer(("127.0.0.1", port), make_handler(Path(out_dir), load_schedule(schedule_path)))


def main():
    parser = argparse.ArgumentParser(description="Private loopback measurement recorder")
    parser.add_argument("--out", required=True, help="absolute private output directory")
    parser.add_argument("--port", type=int, default=43127)
    args = parser.parse_args()
    requested = Path(args.out)
    if not requested.is_absolute():
        parser.error("--out must be an absolute directory")
    requested.mkdir(parents=True, exist_ok=True)
    server = create_server(requested, args.port)
    print("Recorder listens only on http://127.0.0.1:%d/" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
