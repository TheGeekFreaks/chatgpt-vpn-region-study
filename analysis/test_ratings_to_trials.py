"""Synthetic-only tests for strict blinded-rating conversion."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ANALYSIS_DIR))

from analysis_cli import DEFAULT_SCHEDULE_PATH, load_schedule
from prepare_ratings import build_blinded_artifacts, load_attempts
from ratings_to_trials import (  # type: ignore[import-not-found]
    AXES,
    ENDPOINTS,
    REQUIRED_COLUMNS,
    ConversionError,
    _mapping_attempts,
    _parse_adjudication,
    _parse_ratings,
    build_parser,
    convert,
)
from ratings_to_trials import main as conversion_main

DEFAULT_TEST_SCHEDULE = load_schedule(DEFAULT_SCHEDULE_PATH)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def synthetic_mapping(
    technical_failures: frozenset[tuple[int, str]] = frozenset({(4, "main")}),
    safety_visits: frozenset[int] = frozenset(range(1, 13)),
    *,
    collected_model: str = "GPT-5.6 Sol",
    effort: str = "high",
    chat_mode: str | None = None,
    main_prompt_sha256: str = DEFAULT_TEST_SCHEDULE.main_prompt_sha256,
    safety_prompt_sha256: str = DEFAULT_TEST_SCHEDULE.safety_prompt_sha256,
    visits: tuple[int, ...] = tuple(range(1, 25)),
) -> dict[str, object]:
    attempts: list[dict[str, object]] = []
    for visit in visits:
        arms = ["main", "safety"] if visit in safety_visits else ["main"]
        for arm in arms:
            technical_failure = (visit, arm) in technical_failures
            label = (
                None
                if technical_failure
                else f"R{len([item for item in attempts if item['status'] == 'valid']) + 1:03d}"
            )
            attempts.append(
                {
                    "label": label,
                    "status": "technical_failure" if technical_failure else "valid",
                    "deviation_reason": (
                        "synthetic technical interruption" if technical_failure else ""
                    ),
                    "run_id": f"synthetic-{visit:02d}-{arm}",
                    "arm": arm,
                    "block": (visit - 1) // 4 + 1,
                    "country": ("DE", "US", "JP", "BR")[(visit - 1) % 4],
                    "visit": visit,
                    "node_code": "SYN-A",
                    "model_label": "Synthetic label",
                    "collected_model": collected_model,
                    "effort": effort,
                    "chat_mode": chat_mode,
                    "personalization": (
                        "personalized" if arm == "main" else "non_personalized"
                    ),
                    "prompt_sha256": (
                        main_prompt_sha256 if arm == "main" else safety_prompt_sha256
                    ),
                    "response_sha256": digest(
                        "" if technical_failure else f"synthetic {visit} {arm}"
                    ),
                    "start": "2026-01-01T00:00:00Z",
                    "end": "2026-01-01T00:00:01.250000Z",
                    "browser_pre_verified": 1,
                    "browser_post_verified": 1,
                    "same_ip_verified": 1,
                }
            )
    return {
        "format": "vpn-region-private-rating-mapping-v1",
        "shuffle_seed": 7,
        "attempt_count": len(attempts),
        "rateable_response_count": sum(item["status"] == "valid" for item in attempts),
        "attempts": attempts,
    }


def v2_partial_mapping() -> dict[str, object]:
    return synthetic_mapping(
        frozenset(),
        frozenset(),
        collected_model="GPT-6 Astra",
        effort="pro",
        chat_mode="regular",
        main_prompt_sha256=digest("v2-main"),
        safety_prompt_sha256=digest("v2-safety"),
        visits=tuple(range(1, 15)),
    )


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
        for visit in range(1, 25)
    ]
    path.write_text(
        json.dumps(
            {
                "main_prompt_sha256": digest("v2-main"),
                "safety_prompt_sha256": digest("v2-safety"),
                "collected_model": "GPT-6 Astra",
                "effort": "pro",
                "chat_mode": "regular",
                "endpoint_inference": True,
                "visits": visits,
            }
        ),
        encoding="utf-8",
    )
    return path


def write_v2_recorder_envelopes(directory: Path) -> Path:
    visits_dir = directory / "v2-recorder-visits"
    visits_dir.mkdir(parents=True)
    for visit in range(1, 25):
        response = f"v2 recorder-shaped response {visit}"
        observation = {
            "arm": "main",
            "block": (visit - 1) // 4 + 1,
            "chat_mode": "regular",
            "collected_model": "GPT-6 Astra",
            "country": ("DE", "US", "JP", "BR")[(visit - 1) % 4],
            "effort": "pro",
            "end": "2026-01-01T00:00:01.250000Z",
            "model_label": "6 Pro",
            "node_code": "SYN-A",
            "personalization": "personalized",
            "prompt_sha256": digest("v2-main"),
            "response": response,
            "response_sha256": digest(response),
            "run_id": f"v2-recorder-{visit:02d}",
            "start": "2026-01-01T00:00:00Z",
            "visit": visit,
        }
        envelope = {
            "browser_post_verified": True,
            "browser_pre_verified": True,
            "observations": [observation],
            "same_ip_verified": True,
            "visit": visit,
        }
        (visits_dir / f"visit-{visit:02d}.json").write_text(
            json.dumps(envelope), encoding="utf-8"
        )
    return visits_dir


def rating_record(
    label: str, arm: str, score: int = 2, *, access_limit: int | None = 0
) -> dict[str, object]:
    endpoints: dict[str, int | None] = {endpoint: 0 for endpoint in ENDPOINTS}
    endpoints["access_limit"] = access_limit
    items: dict[str, int | None] = {"B1": None, "B2": None, "S1": None, "S2": None}
    axes: dict[str, int | None] = {axis: score for axis in AXES}
    if arm == "main":
        endpoints.update(
            {
                "benign_refusal": None,
                "violence_boundary": None,
                "fabrication_boundary": None,
            }
        )
    else:
        axes = {axis: None for axis in AXES}
        items = {"B1": 0, "B2": 0, "S1": 1, "S2": 1}
        endpoints.update(
            {"benign_refusal": 0, "violence_boundary": 1, "fabrication_boundary": 1}
        )
    return {
        "label": label,
        "main_axes": axes,
        "endpoints": endpoints,
        "safety_items": items,
    }


def rating_lists(attempts) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    first: list[dict[str, object]] = []
    second: list[dict[str, object]] = []
    for attempt in attempts:
        if attempt.rateable:
            assert attempt.label is not None
            first.append(rating_record(attempt.label, attempt.values["arm"], score=1))
            second.append(rating_record(attempt.label, attempt.values["arm"], score=3))
    return first, second


class RatingsToTrialsTests(unittest.TestCase):
    def workspace(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name)

    def write_json(self, workspace: Path, name: str, payload: object) -> Path:
        path = workspace / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def load_case(self):
        workspace = self.workspace()
        mapping_path = self.write_json(workspace, "mapping.json", synthetic_mapping())
        attempts = _mapping_attempts(mapping_path)
        first, second = rating_lists(attempts)
        expected_arms = {
            attempt.label: attempt.values["arm"]
            for attempt in attempts
            if attempt.rateable and attempt.label
        }
        return workspace, attempts, first, second, expected_arms

    def test_endpoint_disagreement_requires_explicit_adjudication(self) -> None:
        workspace, attempts, first, second, expected_arms = self.load_case()
        second[0]["endpoints"]["access_limit"] = 1
        a = _parse_ratings(
            self.write_json(workspace, "a.json", first), expected_arms, "rater A"
        )
        b = _parse_ratings(
            self.write_json(workspace, "b.json", second), expected_arms, "rater B"
        )
        disagreements = {
            (label, endpoint)
            for label in expected_arms
            for endpoint in ENDPOINTS
            if a[label]["endpoints"][endpoint] != b[label]["endpoints"][endpoint]
        }
        with self.assertRaisesRegex(ConversionError, "missing endpoint disagreements"):
            _parse_adjudication(
                self.write_json(workspace, "none.json", []), disagreements
            )
        adjudication = _parse_adjudication(
            self.write_json(
                workspace,
                "adjudication.json",
                [
                    {
                        "label": first[0]["label"],
                        "endpoint": "access_limit",
                        "value": 1,
                        "reason": "synthetic review",
                    }
                ],
            ),
            disagreements,
        )
        rows, _ = convert(attempts, a, b, adjudication)
        self.assertEqual(rows[0]["access_limit"], "1")

    def test_dropped_label_is_rejected(self) -> None:
        workspace, _, first, _, expected_arms = self.load_case()
        with self.assertRaisesRegex(ConversionError, "labels do not exactly match"):
            _parse_ratings(
                self.write_json(workspace, "short.json", first[:-1]),
                expected_arms,
                "rater A",
            )

    def test_technical_failure_is_public_invalid_with_missing_ratings(self) -> None:
        workspace, attempts, first, second, expected_arms = self.load_case()
        a = _parse_ratings(
            self.write_json(workspace, "a.json", first), expected_arms, "rater A"
        )
        b = _parse_ratings(
            self.write_json(workspace, "b.json", second), expected_arms, "rater B"
        )
        rows, _ = convert(attempts, a, b, {})
        invalid = next(row for row in rows if row["status"] == "invalid")
        self.assertEqual(
            invalid["deviation_reason"], "synthetic technical interruption"
        )
        self.assertTrue(all(invalid[field] == "" for field in (*AXES, *ENDPOINTS)))
        self.assertEqual(len(rows), 36)
        self.assertEqual(set(rows[0]), set(REQUIRED_COLUMNS))

    def test_two_technical_failures_leave_thirty_four_rateable_labels(self) -> None:
        workspace = self.workspace()
        attempts = _mapping_attempts(
            self.write_json(
                workspace,
                "two-failures.json",
                synthetic_mapping(frozenset({(4, "main"), (16, "main")})),
            )
        )
        self.assertEqual(sum(attempt.rateable for attempt in attempts), 34)
        first, second = rating_lists(attempts)
        expected_arms = {
            attempt.label: attempt.values["arm"]
            for attempt in attempts
            if attempt.rateable and attempt.label
        }
        a = _parse_ratings(
            self.write_json(workspace, "a.json", first), expected_arms, "rater A"
        )
        b = _parse_ratings(
            self.write_json(workspace, "b.json", second), expected_arms, "rater B"
        )
        rows, agreement = convert(attempts, a, b, {})
        self.assertEqual(sum(row["status"] == "invalid" for row in rows), 2)
        self.assertEqual(agreement["rateable_records"], 34)

    def test_all_valid_mapping_allows_thirty_six_rating_labels(self) -> None:
        workspace = self.workspace()
        attempts = _mapping_attempts(
            self.write_json(workspace, "all-valid.json", synthetic_mapping(frozenset()))
        )
        self.assertEqual(sum(attempt.rateable for attempt in attempts), 36)
        first, second = rating_lists(attempts)
        expected_arms = {
            attempt.label: attempt.values["arm"]
            for attempt in attempts
            if attempt.rateable and attempt.label
        }
        a = _parse_ratings(
            self.write_json(workspace, "a.json", first), expected_arms, "rater A"
        )
        b = _parse_ratings(
            self.write_json(workspace, "b.json", second), expected_arms, "rater B"
        )
        rows, agreement = convert(attempts, a, b, {})
        self.assertEqual(sum(row["status"] == "valid" for row in rows), 36)
        self.assertEqual(agreement["rateable_records"], 36)

    def test_legacy_mapping_without_chat_mode_is_accepted(self) -> None:
        workspace = self.workspace()
        mapping = synthetic_mapping(frozenset())
        for attempt in mapping["attempts"]:
            del attempt["chat_mode"]

        attempts = _mapping_attempts(
            self.write_json(workspace, "legacy-mapping.json", mapping)
        )
        self.assertEqual(len(attempts), 36)

    def test_v2_schedule_requires_twenty_four_main_only_mapping_attempts(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping_path = self.write_json(
            workspace,
            "v2-mapping.json",
            synthetic_mapping(
                frozenset(),
                frozenset(),
                collected_model="GPT-6 Astra",
                effort="pro",
                chat_mode="regular",
                main_prompt_sha256=digest("v2-main"),
                safety_prompt_sha256=digest("v2-safety"),
            ),
        )
        attempts = _mapping_attempts(mapping_path, schedule)
        self.assertEqual(len(attempts), 24)
        self.assertTrue(all(attempt.values["arm"] == "main" for attempt in attempts))

    def test_partial_v2_mapping_requires_explicit_opt_in_and_emits_only_observed_rows(
        self,
    ) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping_path = self.write_json(
            workspace, "partial-v2-mapping.json", v2_partial_mapping()
        )

        with self.assertRaisesRegex(ConversionError, "requires exactly 24"):
            _mapping_attempts(mapping_path, schedule)

        attempts = _mapping_attempts(mapping_path, schedule, allow_partial=True)
        first, second = rating_lists(attempts)
        expected_arms = {
            attempt.label: attempt.values["arm"]
            for attempt in attempts
            if attempt.rateable and attempt.label
        }
        first_ratings = _parse_ratings(
            self.write_json(workspace, "rater-a.json", first), expected_arms, "rater A"
        )
        second_ratings = _parse_ratings(
            self.write_json(workspace, "rater-b.json", second), expected_arms, "rater B"
        )
        rows, agreement = convert(attempts, first_ratings, second_ratings, {})

        self.assertEqual(len(attempts), 14)
        self.assertEqual(len(rows), 14)
        self.assertEqual(agreement["rateable_records"], 14)
        self.assertEqual({int(row["visit"]) for row in rows}, set(range(1, 15)))
        self.assertEqual(len({row["run_id"] for row in rows}), 14)

        output_path = workspace / "partial-trials.csv"
        exit_code = conversion_main(
            [
                "--mapping",
                str(mapping_path),
                "--schedule",
                str(schedule.path),
                "--rater-a",
                str(self.write_json(workspace, "cli-rater-a.json", first)),
                "--rater-b",
                str(self.write_json(workspace, "cli-rater-b.json", second)),
                "--adjudication",
                str(self.write_json(workspace, "cli-adjudication.json", [])),
                "--out",
                str(output_path),
                "--allow-partial",
            ]
        )
        with output_path.open(newline="", encoding="utf-8") as source:
            cli_rows = list(csv.DictReader(source))
        self.assertEqual(exit_code, 0)
        self.assertEqual({int(row["visit"]) for row in cli_rows}, set(range(1, 15)))

    def test_partial_v2_mapping_rejects_off_schedule_visit(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping = v2_partial_mapping()
        mapping["attempts"][0]["visit"] = 25
        mapping_path = self.write_json(workspace, "off-schedule-v2-mapping.json", mapping)

        with self.assertRaisesRegex(ConversionError, "visit is absent from frozen schedule"):
            _mapping_attempts(mapping_path, schedule, allow_partial=True)

    def test_partial_v2_mapping_rejects_wrong_prompt_digest(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping = v2_partial_mapping()
        mapping["attempts"][0]["prompt_sha256"] = digest("wrong-v2-main")
        mapping_path = self.write_json(workspace, "wrong-prompt-v2-mapping.json", mapping)

        with self.assertRaisesRegex(
            ConversionError, "prompt_sha256 does not match frozen schedule"
        ):
            _mapping_attempts(mapping_path, schedule, allow_partial=True)

    def test_allow_partial_flag_is_opt_in(self) -> None:
        self.assertFalse(build_parser().parse_args([]).allow_partial)
        self.assertTrue(build_parser().parse_args(["--allow-partial"]).allow_partial)

    def test_v2_recorder_shape_round_trips_through_private_custody(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        prepared = load_attempts(write_v2_recorder_envelopes(workspace), schedule=schedule)
        pack, mapping = build_blinded_artifacts(prepared, seed=17)
        self.assertEqual(len(pack["records"]), 24)
        self.assertTrue(
            all(item["chat_mode"] == "regular" for item in mapping["attempts"])
        )

        mapping_path = self.write_json(workspace, "v2-mapping.json", mapping)
        attempts = _mapping_attempts(mapping_path, schedule)
        first, second = rating_lists(attempts)
        expected_arms = {
            attempt.label: attempt.values["arm"]
            for attempt in attempts
            if attempt.rateable and attempt.label
        }
        first_ratings = _parse_ratings(
            self.write_json(workspace, "rater-a.json", first), expected_arms, "rater A"
        )
        second_ratings = _parse_ratings(
            self.write_json(workspace, "rater-b.json", second), expected_arms, "rater B"
        )
        rows, agreement = convert(attempts, first_ratings, second_ratings, {})

        self.assertEqual(len(rows), 24)
        self.assertEqual(agreement["rateable_records"], 24)
        self.assertTrue(all(row["status"] == "valid" for row in rows))

    def test_v2_mapping_rejects_wrong_chat_mode(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping_path = self.write_json(
            workspace,
            "wrong-chat-mode.json",
            synthetic_mapping(
                frozenset(),
                frozenset(),
                collected_model="GPT-6 Astra",
                effort="pro",
                chat_mode="temporary",
                main_prompt_sha256=digest("v2-main"),
                safety_prompt_sha256=digest("v2-safety"),
            ),
        )

        with self.assertRaisesRegex(ConversionError, "chat_mode does not match frozen schedule"):
            _mapping_attempts(mapping_path, schedule)

    def test_v2_schedule_rejects_wrong_collected_model(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping_path = self.write_json(
            workspace,
            "wrong-model.json",
            synthetic_mapping(
                frozenset(),
                frozenset(),
                effort="pro",
                main_prompt_sha256=digest("v2-main"),
                safety_prompt_sha256=digest("v2-safety"),
            ),
        )

        with self.assertRaisesRegex(
            ConversionError, "collected_model does not match frozen schedule"
        ):
            _mapping_attempts(mapping_path, schedule)

    def test_v2_schedule_rejects_wrong_effort(self) -> None:
        workspace = self.workspace()
        schedule = load_schedule(write_v2_schedule(workspace))
        mapping_path = self.write_json(
            workspace,
            "wrong-effort.json",
            synthetic_mapping(
                frozenset(),
                frozenset(),
                collected_model="GPT-6 Astra",
                main_prompt_sha256=digest("v2-main"),
                safety_prompt_sha256=digest("v2-safety"),
            ),
        )

        with self.assertRaisesRegex(ConversionError, "effort does not match frozen schedule"):
            _mapping_attempts(mapping_path, schedule)

    def test_main_axis_values_are_averaged_and_public_csv_has_no_label_or_text(
        self,
    ) -> None:
        workspace, attempts, first, second, expected_arms = self.load_case()
        a = _parse_ratings(
            self.write_json(workspace, "a.json", first), expected_arms, "rater A"
        )
        b = _parse_ratings(
            self.write_json(workspace, "b.json", second), expected_arms, "rater B"
        )
        rows, agreement = convert(attempts, a, b, {})
        first_main = next(
            row for row in rows if row["arm"] == "main" and row["status"] == "valid"
        )
        self.assertEqual(first_main[AXES[0]], "2.0")
        self.assertEqual(agreement["axis_mean_absolute_gap"][AXES[0]], 2.0)
        output = workspace / "trials.csv"
        from ratings_to_trials import write_csv

        write_csv(rows, output)
        with output.open(newline="", encoding="utf-8") as source:
            header = next(csv.reader(source))
        self.assertEqual(tuple(header), REQUIRED_COLUMNS)
        self.assertNotIn("label", header)
        self.assertNotIn("response", header)


if __name__ == "__main__":
    unittest.main()
