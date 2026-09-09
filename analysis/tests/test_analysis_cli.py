"""Synthetic fixtures only. No fixture value may be used as an empirical result."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ANALYSIS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS_DIR))

from analysis_cli import (  # noqa: E402
    AXES,
    DEFAULT_COUNTRIES,
    ENDPOINTS,
    REQUIRED_COLUMNS,
    SchemaError,
    analyze,
    load_schedule,
    load_trials,
)


SYNTHETIC_MAIN_HASH = hashlib.sha256(b"synthetic-main-prompt-only").hexdigest()
SYNTHETIC_SAFETY_HASH = hashlib.sha256(b"synthetic-safety-prompt-only").hexdigest()


def visit_for(block: int, country: str) -> int:
    return (block - 1) * len(DEFAULT_COUNTRIES) + DEFAULT_COUNTRIES.index(country) + 1


def node_for(block: int, country: str) -> str:
    return f"{country}-{'A' if block % 2 else 'B'}"


def write_synthetic_schedule(directory: Path) -> Path:
    path = directory / "SYNTHETIC_SCHEDULE_ONLY.json"
    visits = [
        {
            "visit": visit_for(block, country),
            "block": block,
            "country": country,
            "node_code": node_for(block, country),
            "safety": block <= 3,
        }
        for block in range(1, 7)
        for country in DEFAULT_COUNTRIES
    ]
    payload = {
        "main_prompt_sha256": SYNTHETIC_MAIN_HASH,
        "safety_prompt_sha256": SYNTHETIC_SAFETY_HASH,
        "visits": visits,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def synthetic_row(
    *,
    run_id: str,
    arm: str = "main",
    block: int,
    country: str,
    status: str = "valid",
    score: float | None = 2.0,
    endpoint: int | None = 0,
    **overrides: str,
) -> dict[str, str]:
    row = {column: "" for column in REQUIRED_COLUMNS}
    row.update(
        {
            "run_id": run_id,
            "arm": arm,
            "block": str(block),
            "country": country,
            "status": status,
            "visit": str(visit_for(block, country)),
            "model_label": "Synthetic visible label",
            "collected_model": "GPT-5.6 Sol",
            "effort": "high",
            "browser_pre_verified": "1",
            "browser_post_verified": "1",
            "personalization": "personalized" if arm == "main" else "non_personalized",
            "deviation_reason": "",
            "prompt_sha256": SYNTHETIC_MAIN_HASH if arm == "main" else SYNTHETIC_SAFETY_HASH,
            "duration_seconds": "1.25",
            "node_code": node_for(block, country),
        }
    )
    if arm == "main" and score is not None:
        for axis in AXES:
            row[axis] = str(score)
    for field in ENDPOINTS:
        row[field] = "" if endpoint is None else str(endpoint)
    row.update(overrides)
    return row


def all_main_rows(score_by_country: dict[str, float] | None = None) -> list[dict[str, str]]:
    return [
        synthetic_row(
            run_id=f"synthetic-main-{block}-{country}",
            block=block,
            country=country,
            score=(score_by_country or {}).get(country, 2.0),
        )
        for block in range(1, 7)
        for country in DEFAULT_COUNTRIES
    ]


def write_synthetic_csv(directory: Path, rows: list[dict[str, str]]) -> Path:
    path = directory / "SYNTHETIC_FIXTURE_ONLY.csv"
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def load_synthetic_data(directory: Path, rows: list[dict[str, str]]):
    schedule = load_schedule(write_synthetic_schedule(directory))
    return load_trials(write_synthetic_csv(directory, rows), schedule)


class AnalysisTests(unittest.TestCase):
    def _workspace(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name)

    def test_all_zero_scores_have_no_spurious_effect(self) -> None:
        data = load_synthetic_data(self._workspace(), all_main_rows({country: 0.0 for country in DEFAULT_COUNTRIES}))
        result = analyze(data, permutations=1_000, bootstrap_samples=1_000, seed=77)
        for axis in AXES:
            details = result["main_axes"][axis]
            self.assertEqual(details["permutation"]["observed_statistic"], 0.0)
            self.assertEqual(details["permutation"]["p_value"], 1.0)
            self.assertEqual(details["holm_adjusted_p_value"], 1.0)
        rate = result["observed_endpoint_rates"]["main"]["explicit_refusal"]["DE"]
        self.assertEqual(rate["events"], 0)
        self.assertGreater(rate["wilson_interval_95_descriptive"]["upper_95"], 0.0)

    def test_clear_shifted_synthetic_outcome_is_detected(self) -> None:
        data = load_synthetic_data(
            self._workspace(), all_main_rows({"DE": 4.0, "US": 0.0, "JP": 0.0, "BR": 0.0})
        )
        result = analyze(data, permutations=2_000, bootstrap_samples=1_000, seed=12)
        details = result["main_axes"]["directness"]
        self.assertEqual(details["permutation"]["observed_statistic"], 4.0)
        self.assertLess(details["permutation"]["p_value"], 0.05)
        self.assertLess(details["holm_adjusted_p_value"], 0.05)

    def test_incomplete_block_is_retained_and_excluded(self) -> None:
        rows = [row for row in all_main_rows() if not (row["block"] == "2" and row["country"] == "BR")]
        data = load_synthetic_data(self._workspace(), rows)
        result = analyze(data, permutations=1_000, bootstrap_samples=1_000, seed=3)
        self.assertEqual(result["row_accounting"]["total_rows"], 23)
        self.assertEqual(result["row_accounting"]["complete_main_blocks"], 5)
        exclusion = next(item for item in result["row_accounting"]["incomplete_blocks"] if item["arm"] == "main" and item["block"] == 2)
        self.assertIn("missing BR", exclusion["reason"])

    def test_seeded_resampling_is_deterministic(self) -> None:
        rows = [
            synthetic_row(
                run_id=f"synthetic-main-{block}-{country}",
                block=block,
                country=country,
                score=((block + index) % 5) * 0.5,
            )
            for block in range(1, 7)
            for index, country in enumerate(DEFAULT_COUNTRIES)
        ]
        data = load_synthetic_data(self._workspace(), rows)
        first = analyze(data, permutations=1_000, bootstrap_samples=1_000, seed=909)
        second = analyze(data, permutations=1_000, bootstrap_samples=1_000, seed=909)
        for axis in AXES:
            self.assertEqual(first["main_axes"][axis], second["main_axes"][axis])

    def test_invalid_numeric_labels_are_rejected(self) -> None:
        row = synthetic_row(run_id="synthetic-bad-binary", block=1, country="DE", explicit_refusal="2")
        workspace = self._workspace()
        schedule = load_schedule(write_synthetic_schedule(workspace))
        with self.assertRaisesRegex(SchemaError, "explicit_refusal must be 0, 1, or blank"):
            load_trials(write_synthetic_csv(workspace, [row]), schedule)

    def test_uniform_wrong_prompt_is_excluded_against_frozen_arm_hash(self) -> None:
        wrong_uniform_hash = hashlib.sha256(b"uniform-but-wrong").hexdigest()
        rows = all_main_rows()
        for row in rows:
            row["prompt_sha256"] = wrong_uniform_hash
        data = load_synthetic_data(self._workspace(), rows)
        self.assertTrue(all("schedule prompt_sha256 mismatch for main arm" in row.protocol_issues for row in data.trials))
        result = analyze(data, permutations=1_000, bootstrap_samples=1_000, seed=2)
        self.assertEqual(result["row_accounting"]["complete_main_blocks"], 0)

    def test_duplicate_run_id_excludes_affected_block(self) -> None:
        rows = all_main_rows()
        rows[1]["run_id"] = rows[0]["run_id"]
        data = load_synthetic_data(self._workspace(), rows)
        duplicate_rows = [row for row in data.trials if row.run_id == rows[0]["run_id"]]
        self.assertEqual(len(duplicate_rows), 2)
        self.assertTrue(all(any("duplicate run_id" in reason for reason in row.protocol_issues) for row in duplicate_rows))
        self.assertEqual(analyze(data, permutations=1_000, bootstrap_samples=1_000)["row_accounting"]["complete_main_blocks"], 5)

    def test_schedule_mapping_mismatch_is_excluded_with_reason(self) -> None:
        rows = all_main_rows()
        rows[0]["node_code"] = "WRONG-NODE"
        data = load_synthetic_data(self._workspace(), rows)
        self.assertTrue(any("schedule node_code mismatch" in reason for reason in data.trials[0].protocol_issues))
        result = analyze(data, permutations=1_000, bootstrap_samples=1_000)
        self.assertEqual(result["row_accounting"]["complete_main_blocks"], 5)

    def test_missing_required_provenance_column_is_rejected(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_synthetic_schedule(workspace))
        path = workspace / "SYNTHETIC_MISSING_PROVENANCE.csv"
        fields = [field for field in REQUIRED_COLUMNS if field != "browser_post_verified"]
        with path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=fields)
            writer.writeheader()
            writer.writerow({key: value for key, value in synthetic_row(run_id="one", block=1, country="DE").items() if key in fields})
        with self.assertRaisesRegex(SchemaError, "browser_post_verified"):
            load_trials(path, schedule)

    def test_duplicate_csv_header_names_are_rejected(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_synthetic_schedule(workspace))
        path = workspace / "SYNTHETIC_DUPLICATE_HEADER.csv"
        with path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.writer(destination)
            writer.writerow([*REQUIRED_COLUMNS, "run_id"])
            row = synthetic_row(run_id="one", block=1, country="DE")
            writer.writerow([row[field] for field in REQUIRED_COLUMNS] + ["shadow-id"])
        with self.assertRaisesRegex(SchemaError, "duplicate header names: run_id"):
            load_trials(path, schedule)

    def test_excess_csv_row_fields_are_rejected(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_synthetic_schedule(workspace))
        path = workspace / "SYNTHETIC_EXCESS_FIELD.csv"
        with path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.writer(destination)
            writer.writerow(REQUIRED_COLUMNS)
            row = synthetic_row(run_id="one", block=1, country="DE")
            writer.writerow([row[field] for field in REQUIRED_COLUMNS] + ["ambiguous-extra"])
        with self.assertRaisesRegex(SchemaError, "more fields than the CSV header"):
            load_trials(path, schedule)

    def test_schedule_country_set_must_remain_preregistered_four(self) -> None:
        workspace = self._workspace()
        schedule_path = write_synthetic_schedule(workspace)
        payload = json.loads(schedule_path.read_text(encoding="utf-8"))
        for visit in payload["visits"]:
            if visit["country"] == "JP":
                visit["country"] = "DE"  # Remove JP without adding an unregistered code.
        schedule_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(SchemaError, "declared country set must equal DE, US, JP, BR"):
            load_schedule(schedule_path)

    def test_raw_hash_binds_scores_and_endpoints(self) -> None:
        workspace = self._workspace()
        schedule = load_schedule(write_synthetic_schedule(workspace))
        path = write_synthetic_csv(workspace, all_main_rows())
        first = load_trials(path, schedule)
        rows = all_main_rows()
        rows[0]["directness"] = "3.0"
        rows[0]["explicit_refusal"] = "1"
        write_synthetic_csv(workspace, rows)
        second = load_trials(path, schedule)
        self.assertNotEqual(first.csv_sha256, second.csv_sha256)
        self.assertEqual(first.schedule.sha256, second.schedule.sha256)


if __name__ == "__main__":
    unittest.main()
