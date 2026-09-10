#!/usr/bin/env python3
"""Create descriptive public-CSV visit diagnostics without inferential claims.

The script reads only public trial rows. It does not inspect private custody
artifacts, timestamps, raw prompts, IP addresses, or VPN-node details.
It visualizes a prevalidated public CSV and does not replace frozen-schedule
validation in the study analyzer.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AXES = (
    "groundedness_calibration",
    "reflective_depth",
    "directness",
    "actionable_usefulness",
)
REQUIRED_COLUMNS = (
    "run_id",
    "arm",
    "block",
    "country",
    "status",
    "visit",
    *AXES,
    "duration_seconds",
)
AXIS_LABELS = {
    "groundedness_calibration": "Belegtreue und Kalibrierung",
    "reflective_depth": "Reflexionstiefe",
    "directness": "Direktheit",
    "actionable_usefulness": "Handlungsnutzen",
}
COUNTRY_STYLES = {
    "DE": ("#4c78a8", "o"),
    "US": ("#f58518", "s"),
    "JP": ("#54a24b", "^"),
    "BR": ("#e45756", "D"),
}
ALLOWED_COUNTRIES = frozenset(COUNTRY_STYLES)


class DiagnosticsError(ValueError):
    """Raised when a public trial CSV cannot support these diagnostics."""


@dataclass(frozen=True)
class PublicMainRow:
    run_id: str
    block: int
    country: str
    visit: int
    scores: dict[str, float | None]
    duration_seconds: float | None


def _required_text(row: dict[str, str], name: str, row_number: int) -> str:
    value = row.get(name)
    if value is None or not value.strip():
        raise DiagnosticsError(f"row {row_number}: {name} is required")
    return value.strip()


def _positive_integer(value: str, name: str, row_number: int) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise DiagnosticsError(
            f"row {row_number}: {name} must be a positive integer"
        ) from error
    if str(result) != value or result < 1:
        raise DiagnosticsError(f"row {row_number}: {name} must be a positive integer")
    return result


def _score(value: str, name: str, row_number: int) -> float | None:
    if not value:
        return None
    try:
        result = float(value)
    except ValueError as error:
        raise DiagnosticsError(
            f"row {row_number}: {name} must be numeric or blank"
        ) from error
    if not math.isfinite(result) or not 0 <= result <= 4:
        raise DiagnosticsError(
            f"row {row_number}: {name} must be a finite score from 0 to 4"
        )
    return result


def _duration(value: str, row_number: int) -> float | None:
    if not value:
        return None
    try:
        result = float(value)
    except ValueError as error:
        raise DiagnosticsError(
            f"row {row_number}: duration_seconds must be numeric or blank"
        ) from error
    if not math.isfinite(result) or result < 0:
        raise DiagnosticsError(
            f"row {row_number}: duration_seconds must be finite and nonnegative"
        )
    return result


def load_public_main_rows(path: Path) -> list[PublicMainRow]:
    """Load valid public main rows and reject schema or numeric ambiguity."""
    try:
        source = path.open(newline="", encoding="utf-8")
    except OSError as error:
        raise DiagnosticsError(f"cannot read {path}: {error}") from error
    with source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise DiagnosticsError("CSV has no header")
        duplicate_headers = sorted(
            {name for name in reader.fieldnames if reader.fieldnames.count(name) > 1}
        )
        if duplicate_headers:
            raise DiagnosticsError(
                "CSV has duplicate headers: " + ", ".join(duplicate_headers)
            )
        missing_columns = [
            name for name in REQUIRED_COLUMNS if name not in reader.fieldnames
        ]
        if missing_columns:
            raise DiagnosticsError(
                "CSV is missing required columns: " + ", ".join(missing_columns)
            )

        records: list[PublicMainRow] = []
        seen_run_ids: set[str] = set()
        seen_visits: set[int] = set()
        seen_country_blocks: set[tuple[str, int]] = set()
        for row_number, row in enumerate(reader, start=2):
            if (
                row.get("arm", "").strip() != "main"
                or row.get("status", "").strip() != "valid"
            ):
                continue
            run_id = _required_text(row, "run_id", row_number)
            if run_id in seen_run_ids:
                raise DiagnosticsError(
                    f"row {row_number}: duplicate valid main run_id {run_id}"
                )
            block = _positive_integer(
                _required_text(row, "block", row_number), "block", row_number
            )
            country = _required_text(row, "country", row_number).upper()
            if country not in ALLOWED_COUNTRIES:
                raise DiagnosticsError(
                    f"row {row_number}: country must be one of DE, US, JP, BR"
                )
            visit = _positive_integer(
                _required_text(row, "visit", row_number), "visit", row_number
            )
            if visit in seen_visits:
                raise DiagnosticsError(
                    f"row {row_number}: duplicate valid main visit {visit}"
                )
            if (country, block) in seen_country_blocks:
                raise DiagnosticsError(
                    f"row {row_number}: duplicate valid main country/block {country}/{block}"
                )
            seen_run_ids.add(run_id)
            seen_visits.add(visit)
            seen_country_blocks.add((country, block))
            scores = {
                axis: _score(row[axis].strip(), axis, row_number) for axis in AXES
            }
            records.append(
                PublicMainRow(
                    run_id=run_id,
                    block=block,
                    country=country,
                    visit=visit,
                    scores=scores,
                    duration_seconds=_duration(
                        row["duration_seconds"].strip(), row_number
                    ),
                )
            )
    if not records:
        raise DiagnosticsError("CSV contains no valid public main rows")
    return sorted(records, key=lambda row: row.visit)


def _country_style(country: str) -> tuple[str, str]:
    return COUNTRY_STYLES[country]


def quality_series(
    rows: list[PublicMainRow], country: str, axis: str, blocks: list[int]
) -> list[float]:
    """Return one country trajectory with NaN gaps that Matplotlib will not join."""
    by_block = {row.block: row.scores[axis] for row in rows if row.country == country}
    series: list[float] = []
    for block in blocks:
        value = by_block.get(block)
        series.append(math.nan if value is None else value)
    return series


def _save_quality_by_block(
    rows: list[PublicMainRow], output_path: Path, plt: Any
) -> None:
    blocks = sorted({row.block for row in rows})
    countries = sorted({row.country for row in rows})
    figure, panels = plt.subplots(
        2, 2, figsize=(10.2, 7.5), sharex=True, sharey=True, squeeze=False
    )
    for panel, axis in zip(panels.flat, AXES):
        for country in countries:
            color, marker = _country_style(country)
            panel.plot(
                blocks,
                quality_series(rows, country, axis, blocks),
                color=color,
                marker=marker,
                linewidth=1.5,
                markersize=5.5,
                label=country,
            )
        panel.set_title(AXIS_LABELS[axis])
        panel.set_xticks(blocks)
        panel.set_ylim(-0.05, 4.15)
        panel.set_yticks([0, 1, 2, 3, 4])
        panel.set_ylabel("Bewertung (0–4)")
        panel.grid(axis="y", alpha=0.25)
    for panel in panels[1]:
        panel.set_xlabel("Block")
    handles, labels = panels[0][0].get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.955),
        ncol=len(countries),
        frameon=False,
    )
    figure.suptitle("Qualitätsbewertungen nach Block (deskriptiv)", y=0.993)
    figure.text(
        0.5,
        0.015,
        "Punkte sind beobachtete Einzelbewertungen; fehlende Werte werden nicht verbunden. "
        "Gleiche Werte können Marker mehrerer Länder überlagern.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.90))
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _save_capture_duration_by_visit(
    rows: list[PublicMainRow], output_path: Path, plt: Any
) -> None:
    figure, panel = plt.subplots(figsize=(10.2, 5.8))
    countries = sorted({row.country for row in rows})
    for country in countries:
        color, marker = _country_style(country)
        country_rows = [
            row
            for row in rows
            if row.country == country and row.duration_seconds is not None
        ]
        panel.scatter(
            [row.visit for row in country_rows],
            [row.duration_seconds for row in country_rows],
            color=color,
            marker=marker,
            s=42,
            label=country,
            zorder=3,
        )
    block_visits: dict[int, list[int]] = {}
    for row in rows:
        block_visits.setdefault(row.block, []).append(row.visit)
    for index, (block, visits) in enumerate(sorted(block_visits.items())):
        left, right = min(visits) - 0.5, max(visits) + 0.5
        panel.axvspan(
            left,
            right,
            color="#d9d9d9",
            alpha=0.18 if index % 2 == 0 else 0.08,
            zorder=0,
        )
        panel.text(
            (left + right) / 2,
            0.985,
            f"Block {block}",
            transform=panel.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=9,
        )
    panel.set_xticks([row.visit for row in rows])
    panel.set_xlabel("Besuchsreihenfolge")
    panel.set_ylabel("Zeit von Absenden bis Erfassung (s)")
    panel.set_title("Erfassungsdauer nach Besuchsreihenfolge (deskriptiv)")
    panel.grid(axis="y", alpha=0.25)
    handles, labels = panel.get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        title="Land",
        ncol=len(countries),
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.965),
    )
    figure.text(
        0.5,
        0.015,
        "Enthält Polling- und manuelle Erfassungszeit; keine Serverlatenz und kein Maß für Länderleistung.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 0.84))
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def create_diagnostic_figures(input_csv: Path, output_dir: Path) -> dict[str, str]:
    """Write the two descriptive figures; the source CSV is opened read-only."""
    try:
        import matplotlib.pyplot as plt  # type: ignore[import-not-found, import-untyped]
    except ImportError as error:
        raise DiagnosticsError(
            "matplotlib is required to create diagnostic figures"
        ) from error
    rows = load_public_main_rows(input_csv)
    quality_path = output_dir / "quality_by_block.png"
    duration_path = output_dir / "capture_duration_by_visit.png"
    if input_csv.resolve() in {quality_path.resolve(), duration_path.resolve()}:
        raise DiagnosticsError("refusing to overwrite the input CSV")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        _save_quality_by_block(rows, quality_path, plt)
        _save_capture_duration_by_visit(rows, duration_path, plt)
    except OSError as error:
        raise DiagnosticsError(
            f"cannot write diagnostic figures to {output_dir}: {error}"
        ) from error
    return {
        "quality_by_block": quality_path.name,
        "capture_duration_by_visit": duration_path.name,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Prevalidated public trial CSV to read without modification.",
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="Directory for the two PNG figures."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        figures = create_diagnostic_figures(arguments.input_csv, arguments.out)
    except DiagnosticsError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for label, filename in figures.items():
        print(f"{label}: {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
