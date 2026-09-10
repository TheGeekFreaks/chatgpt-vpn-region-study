"""Loopback-only recorder for private ChatGPT route-study measurements."""

import argparse
import hashlib
import hmac
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

MAX_POST = 1_000_000
SCHEDULE = Path(__file__).resolve().parent.parent / "protocol" / "schedule.json"
PUBLIC_STUDY_ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {
    "run_id", "visit", "arm", "block", "country", "node_code", "start", "end",
    "model_label", "personalization", "response", "response_sha256",
}
OPTIONAL = {"collected_model", "effort", "chat_mode", "prompt_sha256", "status", "deviation_reason"}
TOP_REQUIRED = {"visit", "browser_pre_verified", "browser_post_verified", "observations"}
TOP_ALLOWED = TOP_REQUIRED | {"same_ip_verified"}
SCHEDULE_VISIT = {"visit", "block", "country", "node_code", "safety"}
COUNTRIES = {"DE", "US", "JP", "BR"}
EVIDENCE_IDS = {"baseline", "end-context"}


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def load_schedule(path=SCHEDULE):
    try:
        raw = Path(path).read_bytes()
        source_data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError("invalid schedule") from error
    if not isinstance(source_data, dict) or not all(is_digest(source_data.get(key)) for key in ("main_prompt_sha256", "safety_prompt_sha256")):
        raise ValidationError("schedule prompt hashes are invalid")
    if not isinstance(source_data.get("visits"), list) or len(source_data["visits"]) != 24:
        raise ValidationError("schedule must contain 24 visits")
    visits = {}
    for item in source_data["visits"]:
        if not isinstance(item, dict) or set(item) != SCHEDULE_VISIT:
            raise ValidationError("invalid schedule visit fields")
        visit, block, country, node = item["visit"], item["block"], item["country"], item["node_code"]
        if (type(visit) is not int or type(block) is not int or type(item["safety"]) is not bool or
                not 1 <= visit <= 24 or not 1 <= block <= 6 or not isinstance(country, str) or country not in COUNTRIES or
                not isinstance(node, str) or not node.startswith(country + "-") or visit in visits):
            raise ValidationError("invalid schedule visit")
        visits[visit] = item
    if set(visits) != set(range(1, 25)):
        raise ValidationError("schedule visit numbers are invalid")
    if any({item["country"] for item in visits.values() if item["block"] == block} != COUNTRIES for block in range(1, 7)):
        raise ValidationError("schedule blocks must contain each country")
    for key in ("collected_model", "effort", "chat_mode", "model_label"):
        if key in source_data and (not isinstance(source_data[key], str) or not source_data[key].strip()):
            raise ValidationError("invalid schedule model metadata")
    visits["_main_prompt_sha256"] = source_data.get("main_prompt_sha256")
    visits["_safety_prompt_sha256"] = source_data.get("safety_prompt_sha256")
    visits["_collected_model"] = source_data.get("collected_model", "GPT-5.6 Sol")
    visits["_effort"] = source_data.get("effort", "high")
    visits["_chat_mode"] = source_data.get("chat_mode")
    visits["_model_label"] = source_data.get("model_label", "5.6 Hoch")
    visits["_schedule_sha256"] = hashlib.sha256(raw).hexdigest()
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
                observation["personalization"] != personalization or observation["model_label"] != schedule.get("_model_label", "5.6 Hoch")):
            raise ValidationError("run metadata does not match protocol")
        if type(observation["block"]) is not int or observation["block"] != planned["block"]:
            raise ValidationError("route metadata does not match schedule")
        for key in ("country", "node_code"):
            if not isinstance(observation[key], str) or observation[key] != planned[key]:
                raise ValidationError("route metadata does not match schedule")
        if "collected_model" in observation and observation["collected_model"] != schedule.get("_collected_model", "GPT-5.6 Sol"):
            raise ValidationError("unexpected collected model")
        if "effort" in observation and observation["effort"] != schedule.get("_effort", "high"):
            raise ValidationError("unexpected effort")
        if ("chat_mode" in observation and (not isinstance(observation["chat_mode"], str)
                                            or not isinstance(schedule.get("_chat_mode"), str)
                                            or observation["chat_mode"] != schedule.get("_chat_mode"))):
            raise ValidationError("unexpected chat mode")
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


def _ensure_private_output_paths(out_dir):
    """Keep visits and sibling evidence outside the public study tree."""
    visits_dir = Path(out_dir).resolve()
    evidence_dir = (visits_dir.parent / "evidence").resolve()
    public_root = PUBLIC_STUDY_ROOT.resolve()
    for path in (visits_dir, evidence_dir):
        try:
            path.relative_to(public_root)
        except ValueError:
            continue
        raise ValidationError(
            "recorder visits and sibling evidence must stay outside the public study directory"
        )
    return visits_dir


def save_payload(out_dir, payload):
    out_dir = _ensure_private_output_paths(out_dir)
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


def validate_evidence(payload):
    if not isinstance(payload, dict) or set(payload) != {"evidence_id", "data"}:
        raise ValidationError("invalid evidence fields")
    evidence_id = payload["evidence_id"]
    if not isinstance(evidence_id, str) or not (evidence_id in EVIDENCE_IDS or re.fullmatch(r"visit-(0[1-9]|1[0-9]|2[0-4])-(pre|post|deletion)", evidence_id)):
        raise ValidationError("invalid evidence id")
    try:
        json.dumps(payload["data"], allow_nan=False)
        canonical(payload)
    except (TypeError, UnicodeEncodeError, ValueError) as error:
        raise ValidationError("invalid evidence data") from error


def save_evidence(out_dir, payload):
    visits_dir = _ensure_private_output_paths(out_dir)
    evidence_dir = visits_dir.parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = "%s.json" % payload["evidence_id"]
    target, data = evidence_dir / filename, canonical(payload)
    saved_sha = hashlib.sha256(data).hexdigest()
    try:
        with target.open("xb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    except FileExistsError:
        if target.read_bytes() != data:
            raise ConflictError("existing evidence differs")
        return filename, saved_sha, True
    return filename, saved_sha, False


def save_schedule_provenance(out_dir, schedule):
    out_dir = _ensure_private_output_paths(out_dir)
    target = out_dir / "schedule-provenance.json"
    data = canonical({"schedule_sha256": schedule["_schedule_sha256"]})
    try:
        with target.open("xb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
    except FileExistsError:
        if target.read_bytes() != data:
            raise ConflictError("existing schedule provenance differs")
    return schedule["_schedule_sha256"]


PAGE = b'''<!doctype html><meta charset="utf-8"><title>Lokaler Messrekorder</title>
<form id="record"><label for="data">Messdaten JSON</label><br><textarea id="data" rows="24" cols="90" required></textarea><br><button>Lokal sichern</button></form><p id="status" aria-live="polite"></p>
<form id="evidence"><label for="evidence-data">Evidenz JSON</label><br><textarea id="evidence-data" rows="16" cols="90" required></textarea><br><button>Evidenz lokal sichern</button></form><p id="evidence-status" aria-live="polite"></p>
<script>for(let x of [['record','data','/save','status'],['evidence','evidence-data','/evidence','evidence-status']])document.getElementById(x[0]).onsubmit=async e=>{e.preventDefault();let r=await fetch(x[2],{method:'POST',headers:{'Content-Type':'application/json'},body:document.getElementById(x[1]).value});document.getElementById(x[3]).textContent=await r.text()};</script>'''


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
            if self.path not in ("/save", "/evidence"):
                self.reply(404, "Nicht gefunden.")
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= MAX_POST:
                    raise ValidationError("invalid content length")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if self.path == "/save":
                    response_hashes = validate_payload(payload, schedule)
                    filename, saved_sha, replay = save_payload(out_dir, payload)
                else:
                    validate_evidence(payload)
                    filename, saved_sha, replay = save_evidence(out_dir, payload)
            except ConflictError:
                self.reply(409, "Dieser Besuch ist bereits anders gespeichert.")
            except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, OSError):
                self.reply(400, "Ungültige Messdaten.")
            else:
                prefix = "Bereits gespeichert" if replay else "Gespeichert"
                if self.path == "/save":
                    self.reply(200, "%s: %s\nAntwort-Hashes: %s\nKanonischer Datensatz-Hash: %s" %
                               (prefix, filename, ", ".join(response_hashes), saved_sha))
                else:
                    self.reply(200, "%s: evidence/%s\nKanonischer Evidenz-Hash: %s" % (prefix, filename, saved_sha))

    return Recorder


def create_server(out_dir, port=43127, schedule_path=SCHEDULE):
    out_dir = _ensure_private_output_paths(out_dir)
    schedule = load_schedule(schedule_path)
    provenance = out_dir / "schedule-provenance.json"
    if not provenance.exists() and any(out_dir.glob("visit-*.json")):
        raise ConflictError("existing visits lack schedule provenance")
    if provenance.exists():
        save_schedule_provenance(out_dir, schedule)
    server = HTTPServer(("127.0.0.1", port), make_handler(out_dir, schedule))
    try:
        save_schedule_provenance(out_dir, schedule)
    except Exception:
        server.server_close()
        raise
    return server


def main():
    parser = argparse.ArgumentParser(description="Private loopback measurement recorder")
    parser.add_argument(
        "--out",
        required=True,
        help=(
            "absolute private visits directory; evidence is written to its sibling "
            "../evidence directory"
        ),
    )
    parser.add_argument("--port", type=int, default=43127)
    parser.add_argument("--schedule", default=str(SCHEDULE), help="frozen schedule JSON path")
    args = parser.parse_args()
    requested = Path(args.out)
    if not requested.is_absolute():
        parser.error("--out must be an absolute directory")
    try:
        requested = _ensure_private_output_paths(requested)
    except ValidationError as error:
        parser.error(str(error))
    requested.mkdir(parents=True, exist_ok=True)
    try:
        server = create_server(requested, args.port, args.schedule)
    except (ConflictError, ValidationError, OSError) as error:
        parser.error(str(error))
    print("Recorder listens only on http://127.0.0.1:%d/" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
