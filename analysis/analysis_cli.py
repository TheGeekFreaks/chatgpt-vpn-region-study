#!/usr/bin/env python3
"""Offline analysis for the prospectively specified N-of-1 VPN-region study.

This module deliberately contains no network, browser, VPN, or model calls.  It
only consumes a CSV collected by the protocol and writes transparent, derived
artifacts.  Empty measurements stay empty: invalid rows and incomplete blocks
are accounted for but never converted into zeros.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean
from typing import Any, Optional


DEFAULT_COUNTRIES = ("DE", "US", "JP", "BR")
EXPECTED_MAIN_BLOCKS = tuple(range(1, 7))
EXPECTED_COLLECTED_MODEL = "GPT-5.6 Sol"
EXPECTED_EFFORT = "high"
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEDULE_PATH = REPOSITORY_ROOT / "protocol" / "schedule.json"
AXES = (
    "groundedness_calibration",
    "reflective_depth",
    "directness",
    "actionable_usefulness",
)
ENDPOINTS = (
    "explicit_refusal",
    "partial_refusal",
    "access_limit",
    "safety_caveat",
    "benign_refusal",
    "violence_boundary",
    "fabrication_boundary",
)
PRIMARY_ENDPOINTS = (
    "explicit_refusal",
    "partial_refusal",
    "access_limit",
    "safety_caveat",
)
REQUIRED_COLUMNS = (
    "run_id",
    "arm",
    "block",
    "country",
    "status",
    "visit",
    *AXES,
    *ENDPOINTS,
    "model_label",
    "collected_model",
    "effort",
    "browser_pre_verified",
    "browser_post_verified",
    "personalization",
    "deviation_reason",
    "prompt_sha256",
    "duration_seconds",
    "node_code",
)
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class SchemaError(ValueError):
    """Raised when the input cannot represent a protocol-compliant trial."""


@dataclass(frozen=True)
class Trial:
    row_number: int
    run_id: str
    arm: str
    block: int
    country: str
    status: str
    visit: int
    scores: dict[str, Optional[float]]
    endpoints: dict[str, Optional[int]]
    model_label: str
    collected_model: str
    effort: str
    browser_pre_verified: int
    browser_post_verified: int
    personalization: str
    deviation_reason: str
    prompt_sha256: str
    duration_seconds: Optional[float]
    node_code: str
    protocol_issues: tuple[str, ...] = ()

    @property
    def eligible(self) -> bool:
        return self.status == "valid" and not self.protocol_issues


@dataclass(frozen=True)
class ScheduleVisit:
    visit: int
    block: int
    country: str
    node_code: str
    safety: bool


@dataclass(frozen=True)
class Schedule:
    path: Path
    sha256: str
    main_prompt_sha256: str
    safety_prompt_sha256: str
    collected_model: str
    effort: str
    chat_mode: str | None
    endpoint_inference: bool
    visits: dict[int, ScheduleVisit]

    @property
    def expected_arms_by_visit(self) -> dict[int, tuple[str, ...]]:
        return {
            visit: ("main", "safety") if entry.safety else ("main",)
            for visit, entry in self.visits.items()
        }

    @property
    def expected_main_blocks(self) -> tuple[int, ...]:
        return tuple(sorted({entry.block for entry in self.visits.values()}))

    @property
    def expected_safety_blocks(self) -> tuple[int, ...]:
        return tuple(sorted({entry.block for entry in self.visits.values() if entry.safety}))


@dataclass(frozen=True)
class StudyData:
    trials: list[Trial]
    csv_path: Path
    csv_sha256: str
    schedule: Schedule


def publication_path(path: Path) -> str:
    """Return a location that cannot disclose a host path in public output."""
    try:
        return path.resolve().relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return path.name


def _text(row: dict[str, str], name: str, row_number: int) -> str:
    value = row.get(name)
    if value is None:
        raise SchemaError(f"row {row_number}: missing {name!r}")
    return value.strip()


def _optional_float(value: str, field: str, row_number: int) -> Optional[float]:
    if value == "":
        return None
    try:
        result = float(value)
    except ValueError as error:
        raise SchemaError(f"row {row_number}: {field} must be numeric or blank") from error
    if not math.isfinite(result):
        raise SchemaError(f"row {row_number}: {field} must be finite")
    return result


def _binary(value: str, field: str, row_number: int) -> Optional[int]:
    if value == "":
        return None
    if value not in {"0", "1"}:
        raise SchemaError(f"row {row_number}: {field} must be 0, 1, or blank")
    return int(value)


def _positive_int(value: str, field: str, row_number: int) -> int:
    try:
        result = int(value)
    except ValueError as error:
        raise SchemaError(f"row {row_number}: {field} must be a positive integer") from error
    if str(result) != value or result < 1:
        raise SchemaError(f"row {row_number}: {field} must be a positive integer")
    return result


def load_schedule(path: Path) -> Schedule:
    """Load the frozen randomization schedule and bind the analysis to its bytes."""
    try:
        raw_bytes = path.read_bytes()
        payload = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SchemaError(f"cannot load frozen schedule {path}: {error}") from error
    try:
        main_prompt = str(payload["main_prompt_sha256"]).lower()
        safety_prompt = str(payload["safety_prompt_sha256"]).lower()
        collected_model = payload.get("collected_model", EXPECTED_COLLECTED_MODEL)
        effort = payload.get("effort", EXPECTED_EFFORT)
        chat_mode = payload.get("chat_mode")
        endpoint_inference = payload.get("endpoint_inference", False)
        raw_visits = payload["visits"]
    except (KeyError, TypeError) as error:
        raise SchemaError("schedule must include main_prompt_sha256, safety_prompt_sha256, and visits") from error
    if not SHA256_RE.fullmatch(main_prompt) or not SHA256_RE.fullmatch(safety_prompt):
        raise SchemaError("schedule prompt hashes must be 64-character hexadecimal SHA-256 values")
    if not isinstance(collected_model, str) or not collected_model:
        raise SchemaError("schedule collected_model must be a nonempty string")
    if not isinstance(effort, str) or not effort:
        raise SchemaError("schedule effort must be a nonempty string")
    if chat_mode is not None and (not isinstance(chat_mode, str) or not chat_mode):
        raise SchemaError("schedule chat_mode must be a nonempty string when present")
    if not isinstance(endpoint_inference, bool):
        raise SchemaError("schedule endpoint_inference must be boolean when present")
    if not isinstance(raw_visits, list):
        raise SchemaError("schedule visits must be a list")
    visits: dict[int, ScheduleVisit] = {}
    for item in raw_visits:
        if not isinstance(item, dict):
            raise SchemaError("each schedule visit must be an object")
        try:
            visit = item["visit"]
            block = item["block"]
            country = str(item["country"]).upper()
            node_code = str(item["node_code"])
            safety = item["safety"]
        except KeyError as error:
            raise SchemaError(f"schedule visit is missing {error.args[0]!r}") from error
        if not isinstance(visit, int) or visit < 1 or not isinstance(block, int):
            raise SchemaError("schedule visit and block must be positive integers")
        if block not in EXPECTED_MAIN_BLOCKS or country not in DEFAULT_COUNTRIES or not node_code:
            raise SchemaError(f"schedule visit {visit} has invalid block, country, or node_code")
        if not isinstance(safety, bool):
            raise SchemaError(f"schedule visit {visit}: safety must be boolean")
        if visit in visits:
            raise SchemaError(f"schedule contains duplicate visit {visit}")
        visits[visit] = ScheduleVisit(visit, block, country, node_code, safety)
    expected_visits = set(range(1, 25))
    if set(visits) != expected_visits:
        raise SchemaError("schedule must contain exactly visits 1 through 24")
    if {entry.country for entry in visits.values()} != set(DEFAULT_COUNTRIES):
        raise SchemaError("schedule declared country set must equal DE, US, JP, BR")
    for block in EXPECTED_MAIN_BLOCKS:
        scheduled_countries = [entry.country for entry in visits.values() if entry.block == block]
        if sorted(scheduled_countries) != sorted(DEFAULT_COUNTRIES):
            raise SchemaError(f"schedule block {block} must contain each configured country exactly once")
        safety_values = {entry.safety for entry in visits.values() if entry.block == block}
        if len(safety_values) != 1:
            raise SchemaError(f"schedule block {block} must use one safety setting for all countries")
    return Schedule(
        path=path,
        sha256=hashlib.sha256(raw_bytes).hexdigest(),
        main_prompt_sha256=main_prompt,
        safety_prompt_sha256=safety_prompt,
        collected_model=collected_model,
        effort=effort,
        chat_mode=chat_mode,
        endpoint_inference=endpoint_inference,
        visits=visits,
    )


def _parse_trial(row: dict[str, str], row_number: int, schedule: Schedule) -> Trial:
    run_id = _text(row, "run_id", row_number)
    arm = _text(row, "arm", row_number)
    country = _text(row, "country", row_number)
    status = _text(row, "status", row_number)
    if not run_id:
        raise SchemaError(f"row {row_number}: run_id cannot be blank")
    if arm not in {"main", "safety"}:
        raise SchemaError(f"row {row_number}: arm must be 'main' or 'safety'")
    if status not in {"valid", "invalid"}:
        raise SchemaError(f"row {row_number}: status must be 'valid' or 'invalid'")
    if country not in DEFAULT_COUNTRIES:
        raise SchemaError(
            f"row {row_number}: country {country!r} is not in the preregistered countries {DEFAULT_COUNTRIES}"
        )
    block = _positive_int(_text(row, "block", row_number), "block", row_number)
    if block not in EXPECTED_MAIN_BLOCKS:
        raise SchemaError(f"row {row_number}: block must be one of 1 through 6")
    visit = _positive_int(_text(row, "visit", row_number), "visit", row_number)

    scores: dict[str, Optional[float]] = {}
    for axis in AXES:
        score = _optional_float(_text(row, axis, row_number), axis, row_number)
        if score is not None and (not 0 <= score <= 4 or not math.isclose(score * 2, round(score * 2))):
            raise SchemaError(
                f"row {row_number}: {axis} must be between 0 and 4 in 0.5-point increments"
            )
        scores[axis] = score
    if arm == "main" and status == "valid" and any(scores[axis] is None for axis in AXES):
        raise SchemaError(f"row {row_number}: valid main rows require all four axis scores")
    if arm == "safety" and any(scores[axis] is not None for axis in AXES):
        raise SchemaError(f"row {row_number}: safety rows must leave all main axis scores blank")

    endpoints = {
        endpoint: _binary(_text(row, endpoint, row_number), endpoint, row_number)
        for endpoint in ENDPOINTS
    }
    duration = _optional_float(_text(row, "duration_seconds", row_number), "duration_seconds", row_number)
    if duration is not None and duration < 0:
        raise SchemaError(f"row {row_number}: duration_seconds cannot be negative")
    model_label = _text(row, "model_label", row_number)
    collected_model = _text(row, "collected_model", row_number)
    effort = _text(row, "effort", row_number)
    browser_pre_verified = _binary(_text(row, "browser_pre_verified", row_number), "browser_pre_verified", row_number)
    browser_post_verified = _binary(_text(row, "browser_post_verified", row_number), "browser_post_verified", row_number)
    personalization = _text(row, "personalization", row_number)
    deviation_reason = _text(row, "deviation_reason", row_number)
    prompt_sha256 = _text(row, "prompt_sha256", row_number)
    node_code = _text(row, "node_code", row_number)
    if not model_label:
        raise SchemaError(f"row {row_number}: model_label cannot be blank")
    if not collected_model:
        raise SchemaError(f"row {row_number}: collected_model cannot be blank")
    if not effort:
        raise SchemaError(f"row {row_number}: effort cannot be blank")
    if browser_pre_verified is None or browser_post_verified is None:
        raise SchemaError(f"row {row_number}: browser verification fields must be 0 or 1, not blank")
    if personalization not in {"personalized", "non_personalized"}:
        raise SchemaError(
            f"row {row_number}: personalization must be 'personalized' or 'non_personalized'"
        )
    if not SHA256_RE.fullmatch(prompt_sha256):
        raise SchemaError(f"row {row_number}: prompt_sha256 must be a 64-character hexadecimal SHA-256")
    if not node_code:
        raise SchemaError(f"row {row_number}: node_code cannot be blank")
    issues: list[str] = []
    scheduled = schedule.visits.get(visit)
    if scheduled is None:
        issues.append(f"visit {visit} is absent from frozen schedule")
    else:
        if block != scheduled.block:
            issues.append(f"schedule block mismatch (expected {scheduled.block}, got {block})")
        if country != scheduled.country:
            issues.append(f"schedule country mismatch (expected {scheduled.country}, got {country})")
        if node_code != scheduled.node_code:
            issues.append(f"schedule node_code mismatch (expected {scheduled.node_code}, got {node_code})")
        if arm not in schedule.expected_arms_by_visit[visit]:
            issues.append(f"{arm} arm is not planned for visit {visit}")
    expected_prompt = schedule.main_prompt_sha256 if arm == "main" else schedule.safety_prompt_sha256
    if prompt_sha256.lower() != expected_prompt:
        issues.append(f"schedule prompt_sha256 mismatch for {arm} arm")
    expected_personalization = "personalized" if arm == "main" else "non_personalized"
    if personalization != expected_personalization:
        issues.append(
            f"personalization mismatch for {arm} arm (expected {expected_personalization})"
        )
    if collected_model != schedule.collected_model:
        issues.append(
            f"collected_model mismatch (expected {schedule.collected_model}, got {collected_model})"
        )
    if effort != schedule.effort:
        issues.append(f"effort mismatch (expected {schedule.effort}, got {effort})")
    if browser_pre_verified != 1:
        issues.append("browser_pre_verified is not 1")
    if browser_post_verified != 1:
        issues.append("browser_post_verified is not 1")
    if deviation_reason:
        issues.append(f"declared deviation: {deviation_reason}")
    return Trial(
        row_number=row_number,
        run_id=run_id,
        arm=arm,
        block=block,
        country=country,
        status=status,
        visit=visit,
        scores=scores,
        endpoints=endpoints,
        model_label=model_label,
        collected_model=collected_model,
        effort=effort,
        browser_pre_verified=browser_pre_verified,
        browser_post_verified=browser_post_verified,
        personalization=personalization,
        deviation_reason=deviation_reason,
        prompt_sha256=prompt_sha256.lower(),
        duration_seconds=duration,
        node_code=node_code,
        protocol_issues=tuple(issues),
    )


def load_trials(path: Path, schedule: Schedule) -> StudyData:
    """Parse the complete raw CSV without dropping protocol-deviant measurements."""
    try:
        raw_bytes = path.read_bytes()
        text = raw_bytes.decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise SchemaError(f"cannot read CSV {path}: {error}") from error
    with io.StringIO(text, newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise SchemaError("CSV has no header row")
        duplicate_headers = sorted(
            header for header, count in Counter(reader.fieldnames).items() if count > 1
        )
        if duplicate_headers:
            raise SchemaError("CSV has duplicate header names: " + ", ".join(duplicate_headers))
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise SchemaError("CSV is missing required columns: " + ", ".join(missing))
        trials: list[Trial] = []
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise SchemaError(f"row {row_number}: has more fields than the CSV header")
            trials.append(_parse_trial(row, row_number, schedule))
    duplicates = Counter(trial.run_id for trial in trials)
    trials = [
        replace(
            trial,
            protocol_issues=trial.protocol_issues
            + ((f"duplicate run_id: {trial.run_id}",) if duplicates[trial.run_id] > 1 else ()),
        )
        for trial in trials
    ]
    return StudyData(
        trials=trials,
        csv_path=path,
        csv_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        schedule=schedule,
    )


def _block_membership(trials: list[Trial], arm: str) -> dict[int, list[Trial]]:
    grouped: dict[int, list[Trial]] = defaultdict(list)
    for trial in trials:
        if trial.arm == arm:
            grouped[trial.block].append(trial)
    return dict(grouped)


def complete_blocks(
    trials: list[Trial], arm: str, countries: tuple[str, ...], expected_blocks: tuple[int, ...]
) -> tuple[dict[int, dict[str, Trial]], list[dict[str, Any]]]:
    """Return structurally complete blocks and auditable reasons for exclusions."""
    complete: dict[int, dict[str, Trial]] = {}
    exclusions: list[dict[str, Any]] = []
    membership = _block_membership(trials, arm)
    for block in expected_blocks:
        block_trials = membership.get(block, [])
        by_country: dict[str, list[Trial]] = defaultdict(list)
        for trial in block_trials:
            by_country[trial.country].append(trial)
        reasons: list[str] = []
        for country in countries:
            rows = by_country.get(country, [])
            if len(rows) == 0:
                reasons.append(f"missing {country}")
            elif len(rows) > 1:
                reasons.append(f"duplicate {country}")
            elif not rows[0].eligible:
                row_reasons = list(rows[0].protocol_issues)
                if rows[0].status != "valid":
                    row_reasons.insert(0, "status is invalid")
                reasons.append(f"ineligible {country}: " + "; ".join(row_reasons))
        if len(block_trials) != len(countries):
            reasons.append(f"expected {len(countries)} rows, found {len(block_trials)}")
        if reasons:
            exclusions.append({"arm": arm, "block": block, "reason": "; ".join(sorted(set(reasons)))})
            continue
        complete[block] = {country: by_country[country][0] for country in countries}
    return complete, exclusions


def _quantile(sorted_values: list[float], probability: float) -> Optional[float]:
    if not sorted_values:
        return None
    index = (len(sorted_values) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_values[lower]
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (index - lower)


def _axis_means(blocks: dict[int, dict[str, Trial]], countries: tuple[str, ...], axis: str) -> dict[str, float]:
    return {
        country: fmean(float(row[country].scores[axis]) for row in blocks.values())
        for country in countries
    }


def _max_min(values: dict[str, float]) -> float:
    return max(values.values()) - min(values.values())


def permutation_test(
    blocks: dict[int, dict[str, Trial]],
    countries: tuple[str, ...],
    axis: str,
    permutations: int,
    seed: int,
) -> dict[str, Any]:
    if not blocks:
        return {
            "status": "insufficient",
            "reason": "No complete valid main blocks are available for this axis.",
        }
    observed_means = _axis_means(blocks, countries, axis)
    observed = _max_min(observed_means)
    rng = random.Random(seed)
    at_least_as_extreme = 0
    ordered_blocks = [blocks[block] for block in sorted(blocks)]
    for _ in range(permutations):
        sums = dict.fromkeys(countries, 0.0)
        for block in ordered_blocks:
            shuffled_labels = list(countries)
            rng.shuffle(shuffled_labels)
            for source_country, assigned_country in zip(countries, shuffled_labels):
                sums[assigned_country] += float(block[source_country].scores[axis])
        permuted_statistic = max(sums.values()) / len(ordered_blocks) - min(sums.values()) / len(ordered_blocks)
        if permuted_statistic >= observed - 1e-12:
            at_least_as_extreme += 1
    return {
        "status": "computed",
        "statistic": "max_country_mean_minus_min_country_mean",
        "observed_statistic": observed,
        "permutations": permutations,
        "exceedances": at_least_as_extreme,
        "p_value": (at_least_as_extreme + 1) / (permutations + 1),
    }


def endpoint_complete_blocks(
    blocks: dict[int, dict[str, Trial]], countries: tuple[str, ...], endpoint: str
) -> dict[int, dict[str, float]]:
    """Keep only blocks with a recorded binary endpoint for every country."""
    complete: dict[int, dict[str, float]] = {}
    for block, rows in blocks.items():
        values: dict[str, int | None] = {
            country: rows[country].endpoints[endpoint] for country in countries
        }
        if all(value is not None for value in values.values()):
            endpoint_values: dict[str, float] = {}
            for country, value in values.items():
                assert value is not None
                endpoint_values[country] = float(value)
            complete[block] = endpoint_values
    return complete


def endpoint_permutation_test(
    blocks: dict[int, dict[str, float]], countries: tuple[str, ...], permutations: int, seed: int
) -> dict[str, Any]:
    if not blocks:
        return {
            "status": "insufficient",
            "reason": "No complete main blocks have observed values for this endpoint.",
        }
    observed_means = {
        country: fmean(values[country] for values in blocks.values()) for country in countries
    }
    observed = _max_min(observed_means)
    rng = random.Random(seed)
    exceedances = 0
    ordered_blocks = [blocks[block] for block in sorted(blocks)]
    for _ in range(permutations):
        sums = dict.fromkeys(countries, 0.0)
        for block in ordered_blocks:
            shuffled_labels = list(countries)
            rng.shuffle(shuffled_labels)
            for source_country, assigned_country in zip(countries, shuffled_labels):
                sums[assigned_country] += block[source_country]
        statistic = max(sums.values()) / len(ordered_blocks) - min(sums.values()) / len(ordered_blocks)
        if statistic >= observed - 1e-12:
            exceedances += 1
    return {
        "status": "computed",
        "statistic": "max_country_rate_minus_min_country_rate",
        "observed_statistic": observed,
        "country_rates": observed_means,
        "n_endpoint_complete_blocks": len(ordered_blocks),
        "permutations": permutations,
        "exceedances": exceedances,
        "p_value": (exceedances + 1) / (permutations + 1),
    }


def bootstrap_cis(
    blocks: dict[int, dict[str, Trial]],
    countries: tuple[str, ...],
    axis: str,
    bootstrap_samples: int,
    seed: int,
) -> dict[str, Optional[dict[str, float]]]:
    if not blocks:
        return {country: None for country in countries}
    rng = random.Random(seed)
    ordered_blocks = [blocks[block] for block in sorted(blocks)]
    samples: dict[str, list[float]] = {country: [] for country in countries}
    for _ in range(bootstrap_samples):
        selection = [rng.choice(ordered_blocks) for _ in ordered_blocks]
        for country in countries:
            samples[country].append(fmean(float(block[country].scores[axis]) for block in selection))
    return {
        country: {
            "lower_95": _quantile(sorted(values), 0.025),
            "upper_95": _quantile(sorted(values), 0.975),
        }
        for country, values in samples.items()
    }


def holm_adjust(p_values: dict[str, Optional[float]]) -> dict[str, Optional[float]]:
    """Holm adjusted p-values, preserving unavailable axes as None."""
    ranked = sorted((p, name) for name, p in p_values.items() if p is not None)
    adjusted: dict[str, Optional[float]] = {name: None for name in p_values}
    previous = 0.0
    total = len(ranked)
    for index, (p_value, name) in enumerate(ranked):
        value = max(previous, min(1.0, p_value * (total - index)))
        adjusted[name] = value
        previous = value
    return adjusted


def wilson_interval(events: int, observations: int) -> Optional[dict[str, float]]:
    """Nominal Wilson interval; descriptive only for the repeated block design."""
    if observations == 0:
        return None
    z = 1.959963984540054
    proportion = events / observations
    denominator = 1 + z * z / observations
    centre = (proportion + z * z / (2 * observations)) / denominator
    half_width = z * math.sqrt(
        proportion * (1 - proportion) / observations + z * z / (4 * observations * observations)
    ) / denominator
    return {"lower_95": max(0.0, centre - half_width), "upper_95": min(1.0, centre + half_width)}


def endpoint_rates(
    blocks: dict[int, dict[str, Trial]], countries: tuple[str, ...]
) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    rows = list(blocks.values())
    for endpoint in ENDPOINTS:
        by_country: dict[str, dict[str, Any]] = {}
        for country in countries:
            observed = [block[country].endpoints[endpoint] for block in rows]
            numeric = [value for value in observed if value is not None]
            by_country[country] = {
                "events": sum(numeric),
                "n_observed": len(numeric),
                "rate": (sum(numeric) / len(numeric)) if numeric else None,
                "wilson_interval_95_descriptive": wilson_interval(sum(numeric), len(numeric)),
            }
        result[endpoint] = by_country
    return result


def endpoint_extrema(rates: dict[str, dict[str, dict[str, Any]]], countries: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    """Descriptive extrema only; this deliberately performs no safety hypothesis test."""
    summary: dict[str, dict[str, Any]] = {}
    for endpoint, country_rates in rates.items():
        observed = {
            country: details["rate"]
            for country, details in country_rates.items()
            if details["rate"] is not None
        }
        if not observed:
            summary[endpoint] = {"status": "insufficient", "reason": "No observed endpoint values."}
        else:
            high = max(observed.values())
            low = min(observed.values())
            summary[endpoint] = {
                "status": "exploratory_only",
                "max_rate": high,
                "max_countries": [country for country in countries if observed.get(country) == high],
                "min_rate": low,
                "min_countries": [country for country in countries if observed.get(country) == low],
                "note": "Descriptive endpoint extrema only. Zero events or overlapping estimates do not establish country differences.",
            }
    return summary


def node_balance(blocks: dict[int, dict[str, Trial]], countries: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for country in countries:
        counts = Counter(block[country].node_code for block in blocks.values())
        output[country] = {
            "node_counts": dict(sorted(counts.items())),
            "distinct_nodes": len(counts),
            "balanced_if_feasible": len(counts) >= 2 and max(counts.values()) - min(counts.values()) <= 1,
        }
    return output


def safety_prompt_check(blocks: dict[int, dict[str, Trial]], safety_planned: bool) -> dict[str, Any]:
    """Expose whether the safety battery actually used one prompt digest."""
    hashes = sorted({trial.prompt_sha256 for block in blocks.values() for trial in block.values()})
    if not safety_planned:
        return {"status": "not_planned", "reason": "Safety battery is not part of this frozen schedule."}
    if not hashes:
        return {"status": "insufficient", "reason": "No complete valid safety blocks are available."}
    if len(hashes) == 1:
        return {"status": "consistent", "prompt_sha256": hashes[0]}
    return {
        "status": "protocol_deviation",
        "prompt_sha256_values": hashes,
        "reason": "Complete safety rows contain more than one prompt SHA-256; do not treat them as one standardized battery.",
    }


def analyze(
    data: StudyData,
    permutations: int = 10_000,
    bootstrap_samples: int = 2_000,
    seed: int = 20_260_909,
) -> dict[str, Any]:
    if permutations < 1:
        raise ValueError("permutations must be at least 1")
    if bootstrap_samples < 1_000:
        raise ValueError("bootstrap_samples must be at least 1000")
    countries = DEFAULT_COUNTRIES
    trials = data.trials
    main_blocks, main_exclusions = complete_blocks(
        trials, "main", countries, data.schedule.expected_main_blocks
    )
    safety_blocks, safety_exclusions = complete_blocks(
        trials, "safety", countries, data.schedule.expected_safety_blocks
    )
    axis_results: dict[str, Any] = {}
    raw_p_values: dict[str, Optional[float]] = {}
    for axis_index, axis in enumerate(AXES):
        if not main_blocks:
            axis_results[axis] = {
                "status": "insufficient",
                "reason": "No complete valid main blocks are available.",
                "country_means": {country: None for country in countries},
                "n_complete_block_responses": {country: 0 for country in countries},
                "bootstrap_ci_95": {country: None for country in countries},
                "permutation": permutation_test(main_blocks, countries, axis, permutations, seed + axis_index),
            }
            raw_p_values[axis] = None
            continue
        means = _axis_means(main_blocks, countries, axis)
        test = permutation_test(main_blocks, countries, axis, permutations, seed + axis_index)
        axis_results[axis] = {
            "status": "computed",
            "country_means": means,
            "n_complete_block_responses": {country: len(main_blocks) for country in countries},
            "bootstrap_ci_95": bootstrap_cis(
                main_blocks, countries, axis, bootstrap_samples, seed + 10_000 + axis_index
            ),
            "permutation": test,
        }
        raw_p_values[axis] = test["p_value"]
    adjusted = holm_adjust(raw_p_values)
    for axis, p_value in adjusted.items():
        axis_results[axis]["holm_adjusted_p_value"] = p_value

    endpoint_inference: dict[str, Any] = {"status": "not_planned", "endpoints": {}}
    if data.schedule.endpoint_inference:
        endpoint_results: dict[str, Any] = {}
        endpoint_p_values: dict[str, Optional[float]] = {}
        for endpoint_index, endpoint in enumerate(PRIMARY_ENDPOINTS):
            test = endpoint_permutation_test(
                endpoint_complete_blocks(main_blocks, countries, endpoint),
                countries,
                permutations,
                seed + 20_000 + endpoint_index,
            )
            endpoint_results[endpoint] = test
            endpoint_p_values[endpoint] = test.get("p_value")
        for endpoint, adjusted_p_value in holm_adjust(endpoint_p_values).items():
            endpoint_results[endpoint]["holm_adjusted_p_value"] = adjusted_p_value
        endpoint_inference = {
            "status": "computed",
            "family": "four_main_refusal_access_flags",
            "method": "within-block country-label max-min permutation with separate Holm correction",
            "endpoints": endpoint_results,
        }

    all_invalid = [trial for trial in trials if trial.status == "invalid"]
    provenance_deviations = [trial for trial in trials if trial.protocol_issues]
    return {
        "analysis_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "design": {
            "countries": list(countries),
            "main_axes": list(AXES),
            "endpoint_fields": list(ENDPOINTS),
            "main_complete_blocks": sorted(main_blocks),
            "safety_complete_blocks": sorted(safety_blocks),
            "expected_main_blocks": list(data.schedule.expected_main_blocks),
            "expected_safety_blocks": list(data.schedule.expected_safety_blocks),
            "safety_planned": bool(data.schedule.expected_safety_blocks),
            "endpoint_inference_planned": data.schedule.endpoint_inference,
            "permutations": permutations,
            "bootstrap_samples": bootstrap_samples,
            "seed": seed,
            "inference": "Country-label permutation is restricted within complete blocks. Bootstrap confidence intervals are descriptive.",
            "frozen_schedule": {
                "path": publication_path(data.schedule.path),
                "sha256": data.schedule.sha256,
                "main_prompt_sha256": data.schedule.main_prompt_sha256,
                "safety_prompt_sha256": data.schedule.safety_prompt_sha256,
                "collected_model": data.schedule.collected_model,
                "effort": data.schedule.effort,
            },
        },
        "row_accounting": {
            "total_rows": len(trials),
            "main_rows": sum(trial.arm == "main" for trial in trials),
            "safety_rows": sum(trial.arm == "safety" for trial in trials),
            "invalid_rows": len(all_invalid),
            "rows_with_provenance_deviations": len(provenance_deviations),
            "complete_main_blocks": len(main_blocks),
            "complete_safety_blocks": len(safety_blocks),
            "incomplete_blocks": main_exclusions + safety_exclusions,
            "ineligible_rows_retained_but_excluded": [
                {
                    "row_number": trial.row_number,
                    "run_id": trial.run_id,
                    "arm": trial.arm,
                    "visit": trial.visit,
                    "block": trial.block,
                    "country": trial.country,
                    "status": trial.status,
                    "reasons": (["status is invalid"] if trial.status != "valid" else [])
                    + list(trial.protocol_issues),
                }
                for trial in trials
                if not trial.eligible
            ],
            "csv_sha256_exact_bytes": data.csv_sha256,
            "schedule_sha256_exact_bytes": data.schedule.sha256,
        },
        "main_axes": axis_results,
        "primary_endpoint_omnibus": endpoint_inference,
        "observed_endpoint_rates": {
            "main": endpoint_rates(main_blocks, countries),
            "safety": endpoint_rates(safety_blocks, countries),
        },
        "safety_endpoint_extrema": endpoint_extrema(endpoint_rates(safety_blocks, countries), countries),
        "node_balance": {
            "main": node_balance(main_blocks, countries),
            "safety": node_balance(safety_blocks, countries)
            if data.schedule.expected_safety_blocks
            else {},
        },
        "safety_battery_prompt_check": safety_prompt_check(
            safety_blocks, bool(data.schedule.expected_safety_blocks)
        ),
        "limitations": [
            "This is an N-of-1 account study; it does not estimate population-level regional behavior.",
            "Invalid rows and incomplete blocks are retained in accounting and excluded from all estimands; missing values are never recoded to zero.",
            "Safety endpoint extrema and nominal Wilson intervals are descriptive only. Zero events, sparse rows, or overlapping estimates do not support strongest/weakest country conclusions.",
        ],
    }


def _format_number(value: Optional[float], digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def render_markdown(result: dict[str, Any]) -> str:
    design = result["design"]
    accounting = result["row_accounting"]
    lines = [
        "# VPN-region study: empirical analysis",
        "",
        "This report is generated from the supplied CSV only. It does not create, impute, or infer unobserved trial responses.",
        "",
        "## Data completeness",
        "",
        f"- Source rows: {accounting['total_rows']} (main: {accounting['main_rows']}; safety: {accounting['safety_rows']}; explicitly invalid: {accounting['invalid_rows']}; provenance-deviant: {accounting['rows_with_provenance_deviations']}).",
        f"- Complete valid blocks used: main {accounting['complete_main_blocks']}/{len(design['expected_main_blocks'])}; safety {accounting['complete_safety_blocks']}/{len(design['expected_safety_blocks'])}.",
        f"- Seed: `{design['seed']}`; permutations per main axis: {design['permutations']}; bootstrap samples: {design['bootstrap_samples']}.",
        f"- Exact input hashes: CSV `{accounting['csv_sha256_exact_bytes']}`; frozen schedule `{accounting['schedule_sha256_exact_bytes']}`.",
        "",
    ]
    if accounting["incomplete_blocks"]:
        lines.extend(["### Excluded incomplete blocks", "", "| Arm | Block | Reason |", "| --- | ---: | --- |"])
        lines.extend(
            f"| {item['arm']} | {item['block']} | {item['reason']} |" for item in accounting["incomplete_blocks"]
        )
        lines.append("")
    if accounting["ineligible_rows_retained_but_excluded"]:
        lines.extend(["### Ineligible rows retained in the source", "", "| Row | Run ID | Arm | Visit | Reason |", "| ---: | --- | --- | ---: | --- |"])
        lines.extend(
            f"| {item['row_number']} | {item['run_id']} | {item['arm']} | {item['visit']} | {'; '.join(item['reasons'])} |"
            for item in accounting["ineligible_rows_retained_but_excluded"]
        )
        lines.append("")

    lines.extend([
        "## Measurement limits",
        "",
        "These model-proxy ratings can contain rater disagreement and systematic offsets; see repository resources `data/rater-agreement.json` and `paper/PAPER.md`. Constant or ceiling scores, including zero-width bootstrap intervals, do not establish equivalent underlying quality or measurement certainty.",
        "",
    ])

    lines.extend([
        "## Main-answer axes",
        "",
        "Country means and block-bootstrap 95% intervals are descriptive. The omnibus p-value tests the max-minus-min country mean after shuffling country labels within complete blocks; Holm adjustment covers the four main axes.",
        "",
    ])
    for axis, details in result["main_axes"].items():
        title = axis.replace("_", " ")
        lines.extend([f"### {title}", ""])
        if details["status"] == "insufficient":
            lines.extend([f"**Insufficient data.** {details['reason']}", ""])
            continue
        lines.extend(["| Country | Mean | 95% bootstrap CI | N complete responses |", "| --- | ---: | --- | ---: |"])
        for country in design["countries"]:
            ci = details["bootstrap_ci_95"][country]
            lines.append(
                f"| {country} | {_format_number(details['country_means'][country])} | "
                f"{_format_number(ci['lower_95'])} to {_format_number(ci['upper_95'])} | "
                f"{details['n_complete_block_responses'][country]} |"
            )
        test = details["permutation"]
        lines.extend([
            "",
            f"Omnibus max-min difference: {_format_number(test['observed_statistic'])}; raw permutation p = {_format_number(test['p_value'], 4)}; Holm-adjusted p = {_format_number(details['holm_adjusted_p_value'], 4)}.",
            "",
        ])

    lines.extend([
        "## Observed endpoint rates",
        "",
        "Rates use only complete valid blocks for their arm. Denominators are observed endpoint values, so blank endpoint cells do not become zero. The JSON also gives nominal 95% Wilson intervals as descriptive summaries only; their independent-trial assumption is not fulfilled by this matched repeated-block design.",
        "",
    ])
    for arm, endpoints in result["observed_endpoint_rates"].items():
        lines.extend([f"### {arm.title()} arm", ""])
        if arm == "safety" and not result["design"]["safety_planned"]:
            lines.extend(["**Not planned.** This frozen schedule contains no safety-battery visits.", ""])
            continue
        if not result["design"][f"{arm}_complete_blocks"]:
            lines.extend(["**Insufficient data.** No complete valid blocks are available for this arm.", ""])
            continue
        lines.extend(["| Endpoint | " + " | ".join(design["countries"]) + " |", "| --- | " + " | ".join("---" for _ in design["countries"]) + " |"])
        for endpoint, country_rates in endpoints.items():
            cells = [
                "—" if country_rates[country]["rate"] is None else (
                    f"{country_rates[country]['events']}/{country_rates[country]['n_observed']} "
                    f"({country_rates[country]['rate']:.3f}; Wilson "
                    f"{country_rates[country]['wilson_interval_95_descriptive']['lower_95']:.3f}–"
                    f"{country_rates[country]['wilson_interval_95_descriptive']['upper_95']:.3f})"
                )
                for country in design["countries"]
            ]
            lines.append(f"| {endpoint.replace('_', ' ')} | " + " | ".join(cells) + " |")
        lines.append("")

    endpoint_omnibus = result["primary_endpoint_omnibus"]
    if endpoint_omnibus["status"] == "computed":
        lines.extend([
            "## Main refusal/access endpoint omnibus tests",
            "",
            "These four planned endpoint tests use only blocks with an observed value for every country on that endpoint. Their Holm correction is separate from the four quality-axis tests.",
            "",
            "| Endpoint | Complete blocks | Max-min rate | Raw permutation p | Holm p |",
            "| --- | ---: | ---: | ---: | ---: |",
        ])
        for endpoint, details in endpoint_omnibus["endpoints"].items():
            if details["status"] == "computed":
                lines.append(
                    f"| {endpoint.replace('_', ' ')} | {details['n_endpoint_complete_blocks']} | "
                    f"{_format_number(details['observed_statistic'])} | {_format_number(details['p_value'], 4)} | "
                    f"{_format_number(details['holm_adjusted_p_value'], 4)} |"
                )
            else:
                lines.append(f"| {endpoint.replace('_', ' ')} | 0 | — | — | — |")
        lines.append("")

    lines.extend([
        "## Safety interpretation boundary",
        "",
        "Safety endpoint maxima and minima are exported in `analysis.json` as exploratory descriptions only. This analysis does not label a country strongest or weakest on safety from zero events, sparse data, or overlapping estimates.",
        "",
    ])
    prompt_check = result["safety_battery_prompt_check"]
    if prompt_check["status"] == "not_planned":
        lines.extend(["**Not planned.** The frozen schedule contains no safety battery, so no safety comparison is reported.", ""])
    elif prompt_check["status"] == "consistent":
        lines.extend(["The complete safety rows use one shared prompt SHA-256, as required by the standardized battery.", ""])
    elif prompt_check["status"] == "protocol_deviation":
        lines.extend([f"**Protocol deviation:** {prompt_check['reason']}", ""])
    else:
        lines.extend([f"**Safety battery check unavailable:** {prompt_check['reason']}", ""])
    lines.extend([
        "## VPN node balance",
        "",
        "The following is a descriptive check of observed exit-node assignment. It does not establish that IP geolocation or platform routing actually differed.",
        "",
        "| Arm | Country | Node counts | Two-node near-balance |",
        "| --- | --- | --- | --- |",
    ])
    for arm, country_data in result["node_balance"].items():
        for country, info in country_data.items():
            node_counts = ", ".join(f"{node}: {count}" for node, count in info["node_counts"].items()) or "—"
            lines.append(f"| {arm} | {country} | {node_counts} | {info['balanced_if_feasible']} |")
    lines.append("")
    return "\n".join(lines)


def create_charts(result: dict[str, Any], output_dir: Path) -> dict[str, str]:
    """Create a single compact main-axis chart when matplotlib is installed."""
    try:
        import matplotlib.pyplot as plt  # type: ignore[import-not-found]
    except ImportError:
        return {"status": "omitted", "reason": "matplotlib is not installed; no charts were produced."}
    computed = [
        (axis, details) for axis, details in result["main_axes"].items() if details["status"] == "computed"
    ]
    if not computed:
        return {"status": "omitted", "reason": "No complete valid main blocks are available for charting."}
    countries = result["design"]["countries"]
    figure, panels = plt.subplots(1, len(computed), figsize=(4.0 * len(computed), 4.2), squeeze=False)
    for panel, (axis, details) in zip(panels[0], computed):
        means = [details["country_means"][country] for country in countries]
        cis = [details["bootstrap_ci_95"][country] for country in countries]
        lower = [means[index] - cis[index]["lower_95"] for index in range(len(countries))]
        upper = [cis[index]["upper_95"] - means[index] for index in range(len(countries))]
        panel.bar(countries, means, yerr=[lower, upper], capsize=4, color="#4c78a8")
        panel.set_ylim(0, 4)
        panel.set_title(axis.replace("_", " ").title())
        panel.set_ylabel("Mean score (0–4)")
        panel.grid(axis="y", alpha=0.25)
    figure.suptitle("Main answers: descriptive country means with block-bootstrap 95% CIs")
    figure.tight_layout()
    chart_path = output_dir / "main_axis_means.png"
    figure.savefig(chart_path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return {"status": "created", "path": chart_path.name}


def write_outputs(result: dict[str, Any], output_dir: Path, charts: bool = True) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_status = create_charts(result, output_dir) if charts else {"status": "omitted", "reason": "Charts disabled by CLI flag."}
    result["charts"] = chart_status
    (output_dir / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "results.md").write_text(render_markdown(result), encoding="utf-8")
    return chart_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Empirical protocol CSV (never a synthetic fixture).")
    parser.add_argument("--out", type=Path, required=True, help="Directory for analysis.json, results.md, and optional charts.")
    parser.add_argument(
        "--schedule",
        type=Path,
        default=DEFAULT_SCHEDULE_PATH,
        help="Frozen schedule JSON (default: ../protocol/schedule.json).",
    )
    parser.add_argument("--permutations", type=int, default=10_000, help="Within-block permutations per main axis (default: 10000).")
    parser.add_argument("--bootstrap-samples", type=int, default=2_000, help="Block bootstrap samples per main axis (minimum: 1000).")
    parser.add_argument("--seed", type=int, default=20_260_909, help="Random seed for reproducible resampling.")
    parser.add_argument("--no-charts", action="store_true", help="Do not attempt optional matplotlib charts.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        schedule = load_schedule(arguments.schedule)
        data = load_trials(arguments.input_csv, schedule)
        result = analyze(
            data,
            permutations=arguments.permutations,
            bootstrap_samples=arguments.bootstrap_samples,
            seed=arguments.seed,
        )
        chart_status = write_outputs(result, arguments.out, charts=not arguments.no_charts)
    except (OSError, SchemaError, ValueError) as error:
        print(f"analysis failed: {error}", file=sys.stderr)
        return 2
    print(f"Wrote {arguments.out / 'analysis.json'} and {arguments.out / 'results.md'}")
    if chart_status["status"] == "omitted":
        print(f"Charts omitted: {chart_status['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
