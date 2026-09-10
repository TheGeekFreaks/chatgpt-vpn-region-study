"""Synthetic tests for public-CSV descriptive diagnostics only."""

from __future__ import annotations

import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS_DIR))

from plot_visit_diagnostics import (
    AXES,
    REQUIRED_COLUMNS,
    DiagnosticsError,
    create_diagnostic_figures,
    load_public_main_rows,
    quality_series,
)


def _row(
    *, visit: int, block: int, country: str, duration: str = "12.5", **scores: str
) -> dict[str, str]:
    row = {column: "" for column in REQUIRED_COLUMNS}
    row.update(
        {
            "run_id": f"synthetic-{visit}",
            "arm": "main",
            "block": str(block),
            "country": country,
            "status": "valid",
            "visit": str(visit),
            "duration_seconds": duration,
        }
    )
    row.update({axis: scores.get(axis, "2.0") for axis in AXES})
    return row


def _write_csv(directory: Path, rows: list[dict[str, str]]) -> Path:
    path = directory / "SYNTHETIC_PUBLIC_TRIALS.csv"
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


class VisitDiagnosticsTest(unittest.TestCase):
    def _workspace(self) -> Path:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        return Path(temporary_directory.name)

    def test_creates_public_descriptive_figures_and_preserves_missing_score_gap(
        self,
    ) -> None:
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib is optional")
        workspace = self._workspace()
        rows = [
            _row(visit=1, block=1, country="DE"),
            _row(visit=2, block=1, country="US"),
            _row(visit=3, block=2, country="DE", directness=""),
            _row(visit=4, block=2, country="US", duration=""),
            _row(visit=5, block=3, country="DE"),
        ]
        input_csv = _write_csv(workspace, rows)
        loaded = load_public_main_rows(input_csv)
        directness = quality_series(loaded, "DE", "directness", [1, 2, 3])
        self.assertTrue(math.isnan(directness[1]))
        figures = create_diagnostic_figures(input_csv, workspace / "figures")
        self.assertGreater(
            (workspace / "figures" / figures["quality_by_block"]).stat().st_size, 0
        )
        self.assertGreater(
            (workspace / "figures" / figures["capture_duration_by_visit"])
            .stat()
            .st_size,
            0,
        )

    def test_rejects_missing_columns_and_invalid_duration(self) -> None:
        workspace = self._workspace()
        missing_column_csv = workspace / "MISSING.csv"
        missing_column_csv.write_text("run_id,arm\ntrial,main\n", encoding="utf-8")
        with self.assertRaisesRegex(DiagnosticsError, "missing required columns"):
            load_public_main_rows(missing_column_csv)

        invalid_duration_csv = _write_csv(
            workspace, [_row(visit=1, block=1, country="DE", duration="unknown")]
        )
        with self.assertRaisesRegex(
            DiagnosticsError, "duration_seconds must be numeric or blank"
        ):
            load_public_main_rows(invalid_duration_csv)

        unknown_country_csv = _write_csv(
            workspace, [_row(visit=1, block=1, country="untrusted legend text")]
        )
        with self.assertRaisesRegex(
            DiagnosticsError, "country must be one of DE, US, JP, BR"
        ):
            load_public_main_rows(unknown_country_csv)

        duplicate_run_id_rows = [
            _row(visit=1, block=1, country="DE"),
            _row(visit=2, block=1, country="US"),
        ]
        duplicate_run_id_rows[1]["run_id"] = duplicate_run_id_rows[0]["run_id"]
        duplicate_run_id_csv = _write_csv(workspace, duplicate_run_id_rows)
        with self.assertRaisesRegex(DiagnosticsError, "duplicate valid main run_id"):
            load_public_main_rows(duplicate_run_id_csv)

    def test_reports_output_write_errors_as_diagnostics_errors(self) -> None:
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib is optional")
        workspace = self._workspace()
        input_csv = _write_csv(workspace, [_row(visit=1, block=1, country="DE")])
        with patch.object(
            Path, "mkdir", side_effect=OSError("synthetic denied")
        ), self.assertRaisesRegex(DiagnosticsError, "cannot write diagnostic figures"):
            create_diagnostic_figures(input_csv, workspace / "unwritable")


if __name__ == "__main__":
    unittest.main()
