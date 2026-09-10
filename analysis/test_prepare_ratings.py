"""Synthetic tests for private blinded-rating preparation; no empirical text."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ANALYSIS_DIR))

from analysis_cli import load_schedule
from prepare_ratings import (
    EXPECTED_VISITS,
    PreparationError,
    build_blinded_artifacts,
    load_attempts,
    write_artifacts,
)


def synthetic_response(visit: int, arm: str) -> str:
    return f"synthetic response for visit {visit} arm {arm}"


def observation(
    visit: int, arm: str, *, status: str | None = None, response: str | None = None
) -> dict[str, object]:
    text = synthetic_response(visit, arm) if response is None else response
    item: dict[str, object] = {
        "arm": arm,
        "block": (visit - 1) // 4 + 1,
        "collected_model": "GPT-5.6 Sol",
        "country": "ZZ",
        "effort": "high",
        "end": "2026-01-01T00:00:01Z",
        "model_label": "Synthetic",
        "node_code": "ZZ-A",
        "personalization": "personalized" if arm == "main" else "non_personalized",
        "prompt_sha256": hashlib.sha256(arm.encode()).hexdigest(),
        "response": text,
        "response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "run_id": f"synthetic-{visit:02d}-{arm}",
        "start": "2026-01-01T00:00:00Z",
        "visit": visit,
    }
    if status is not None:
        item["status"] = status
    if status == "technical_failure":
        item["deviation_reason"] = "synthetic navigation during generation"
    return item


def write_complete_envelopes(
    directory: Path, *, failed_main_visit: int | None = None
) -> Path:
    visits_dir = directory / "visits"
    visits_dir.mkdir(parents=True)
    for visit in EXPECTED_VISITS:
        observations = [observation(visit, "main")]
        if visit <= 12:
            observations.append(observation(visit, "safety"))
        if visit == failed_main_visit:
            observations[0] = observation(
                visit, "main", status="technical_failure", response=""
            )
        envelope = {
            "visit": visit,
            "browser_pre_verified": True,
            "browser_post_verified": True,
            "same_ip_verified": True,
            "observations": observations,
        }
        (visits_dir / f"visit-{visit:02d}.json").write_text(
            json.dumps(envelope), encoding="utf-8"
        )
    return visits_dir


def write_v2_schedule(directory: Path) -> Path:
    path = directory / "SYNTHETIC_V2_SCHEDULE.json"
    visits = [
        {
            "visit": visit,
            "block": (visit - 1) // 4 + 1,
            "country": ("DE", "US", "JP", "BR")[(visit - 1) % 4],
            "node_code": "SYN-A",
            "safety": False,
        }
        for visit in EXPECTED_VISITS
    ]
    path.write_text(
        json.dumps(
            {
                "main_prompt_sha256": hashlib.sha256(b"synthetic-main").hexdigest(),
                "safety_prompt_sha256": hashlib.sha256(b"synthetic-safety").hexdigest(),
                "collected_model": "GPT-6 Astra",
                "effort": "pro",
                "endpoint_inference": True,
                "visits": visits,
            }
        ),
        encoding="utf-8",
    )
    return path


def write_v2_main_only_envelopes(directory: Path) -> Path:
    visits_dir = directory / "v2-visits"
    visits_dir.mkdir(parents=True)
    for visit in EXPECTED_VISITS:
        item = observation(visit, "main")
        item["collected_model"] = "GPT-6 Astra"
        item["effort"] = "pro"
        envelope = {
            "visit": visit,
            "browser_pre_verified": True,
            "browser_post_verified": True,
            "same_ip_verified": True,
            "observations": [item],
        }
        (visits_dir / f"visit-{visit:02d}.json").write_text(json.dumps(envelope), encoding="utf-8")
    return visits_dir


class PrepareRatingsTests(unittest.TestCase):
    def _workspace(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def test_hash_integrity_rejects_changed_response(self) -> None:
        workspace = self._workspace()
        visits_dir = write_complete_envelopes(workspace)
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["response"] = "tampered synthetic text"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(PreparationError, "response_sha256 does not match"):
            load_attempts(visits_dir)

    def test_pack_is_blinded_and_mapping_retains_linkage(self) -> None:
        workspace = self._workspace()
        attempts = load_attempts(write_complete_envelopes(workspace))
        pack, mapping = build_blinded_artifacts(attempts, seed=81)
        self.assertEqual(len(pack["records"]), 36)
        self.assertEqual(len(mapping["attempts"]), 36)
        self.assertEqual(
            [record["label"] for record in pack["records"]],
            [f"R{value:03d}" for value in range(1, 37)],
        )
        self.assertEqual(set(pack), {"format", "records", "rating_instructions"})
        self.assertTrue(
            all(
                set(record) == {"label", "arm", "response"}
                for record in pack["records"]
            )
        )
        serialized = json.dumps(pack)
        for forbidden in (
            "country",
            "block",
            "visit",
            "node_code",
            "run_id",
            "prompt_sha256",
            "response_sha256",
            "start",
            "end",
            "model_label",
        ):
            self.assertNotIn(f'"{forbidden}"', serialized)
        mapped = next(item for item in mapping["attempts"] if item["label"] == "R001")
        self.assertIn("country", mapped)
        self.assertIn("response_sha256", mapped)

    def test_mapping_retains_failed_attempt_but_pack_excludes_empty_response(
        self,
    ) -> None:
        workspace = self._workspace()
        attempts = load_attempts(
            write_complete_envelopes(workspace, failed_main_visit=4)
        )
        pack, mapping = build_blinded_artifacts(attempts, seed=21)
        self.assertEqual(len(mapping["attempts"]), 36)
        self.assertEqual(len(pack["records"]), 35)
        failed = next(
            item
            for item in mapping["attempts"]
            if item["status"] == "technical_failure"
        )
        self.assertIsNone(failed["label"])
        self.assertEqual(
            failed["deviation_reason"], "synthetic navigation during generation"
        )

    def test_complete_collection_has_stable_seeded_labels(self) -> None:
        workspace = self._workspace()
        attempts = load_attempts(write_complete_envelopes(workspace))
        first_pack, first_mapping = build_blinded_artifacts(attempts, seed=909)
        second_pack, second_mapping = build_blinded_artifacts(attempts, seed=909)
        self.assertEqual(first_pack["records"], second_pack["records"])
        self.assertEqual(first_mapping["attempts"], second_mapping["attempts"])
        reversed_pack, reversed_mapping = build_blinded_artifacts(
            reversed(attempts), seed=909
        )
        self.assertEqual(first_pack["records"], reversed_pack["records"])
        self.assertEqual(first_mapping["attempts"], reversed_mapping["attempts"])

    def test_v2_schedule_accepts_exactly_twenty_four_main_attempts(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        attempts = load_attempts(write_v2_main_only_envelopes(workspace), schedule=schedule)
        pack, mapping = build_blinded_artifacts(attempts, seed=1)
        self.assertEqual(len(attempts), 24)
        self.assertTrue(all(attempt.observation["arm"] == "main" for attempt in attempts))
        self.assertEqual(len(pack["records"]), 24)
        self.assertTrue(
            all(
                not ({"country", "visit", "block", "order", "model_label", "collected_model", "effort"} & set(record))
                for record in pack["records"]
            )
        )
        self.assertEqual(mapping["attempt_count"], 24)

    def test_v2_schedule_rejects_wrong_collected_model(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        visits_dir = write_v2_main_only_envelopes(workspace)
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["collected_model"] = "GPT-5.6 Sol"
        path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(
            PreparationError, "collected_model does not match frozen schedule"
        ):
            load_attempts(visits_dir, schedule=schedule)

    def test_v2_schedule_rejects_wrong_effort(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        visits_dir = write_v2_main_only_envelopes(workspace)
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["effort"] = "high"
        path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(PreparationError, "effort does not match frozen schedule"):
            load_attempts(visits_dir, schedule=schedule)

    def test_wrong_block_or_unverified_valid_attempt_is_rejected(self) -> None:
        workspace = self._workspace()
        visits_dir = write_complete_envelopes(workspace)
        path = visits_dir / "visit-05.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["block"] = 6
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            PreparationError, "does not match frozen visit block"
        ):
            load_attempts(visits_dir)

        visits_dir = write_complete_envelopes(workspace / "unverified")
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["browser_pre_verified"] = 0
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(PreparationError, "require browser_pre_verified=1"):
            load_attempts(visits_dir)

    def test_noncanonical_prompt_or_response_digest_is_rejected(self) -> None:
        workspace = self._workspace()
        visits_dir = write_complete_envelopes(workspace)
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["prompt_sha256"] = "not-a-sha256"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            PreparationError, "prompt_sha256 must be a lowercase"
        ):
            load_attempts(visits_dir)

        visits_dir = write_complete_envelopes(workspace / "uppercase")
        path = visits_dir / "visit-01.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["observations"][0]["response_sha256"] = payload["observations"][0][
            "response_sha256"
        ].upper()
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(
            PreparationError, "response_sha256 must be a lowercase"
        ):
            load_attempts(visits_dir)

    def test_incomplete_collection_requires_explicit_exploratory_flag(self) -> None:
        workspace = self._workspace()
        visits_dir = write_complete_envelopes(workspace)
        (visits_dir / "visit-24.json").unlink()
        with self.assertRaisesRegex(PreparationError, "requires visits 1 through 24"):
            load_attempts(visits_dir)
        partial = load_attempts(visits_dir, allow_partial=True)
        self.assertEqual(len(partial), 35)

    def test_write_rejects_public_study_directory(self) -> None:
        workspace = self._workspace()
        attempts = load_attempts(write_complete_envelopes(workspace))
        pack, mapping = build_blinded_artifacts(attempts, seed=1)
        public_child = ANALYSIS_DIR.parent / "test-private-output"
        with self.assertRaisesRegex(PreparationError, "must not be written"):
            write_artifacts(pack, mapping, public_child)


if __name__ == "__main__":
    unittest.main()
