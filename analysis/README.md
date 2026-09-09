# Empirical analysis CLI

`analysis_cli.py` is an offline, standard-library-first analysis tool for the
VPN-region N-of-1 protocol. It makes no browser, model, VPN, or network calls.
It does not contain empirical data and it never creates a response score.

Run it with the bundled Python runtime:

```powershell
python .\analysis_cli.py .\trials.csv --out .\empirical-results
```

The default frozen schedule is `..\protocol\schedule.json`. Supply another
read-only frozen file only when reproducing a separately archived run:

```powershell
python .\analysis_cli.py .\trials.csv --schedule ..\protocol\schedule.json --out .\empirical-results
```

The input must be a UTF-8 CSV with this header. The order may differ, but every
column is required:

```text
run_id,arm,block,country,status,visit,groundedness_calibration,reflective_depth,directness,actionable_usefulness,explicit_refusal,partial_refusal,access_limit,safety_caveat,benign_refusal,violence_boundary,fabrication_boundary,model_label,collected_model,effort,browser_pre_verified,browser_post_verified,personalization,deviation_reason,prompt_sha256,duration_seconds,node_code
```

`arm` is `main` or `safety`; `status` is `valid` or `invalid`; `visit` is the
frozen schedule visit number; the country set is locked to preregistered
`DE,US,JP,BR` and cannot be replaced with a CLI subset. A valid main row must
contain all four axis values. Those values encode the average of
two 0–4 integer ratings, so they must be in 0.5-point increments. Safety rows
leave every main-axis column blank. Each endpoint is `0`, `1`, or blank. Blank
endpoint values have no denominator and are never interpreted as zero.
`prompt_sha256` is a 64-character SHA-256 hex digest and `node_code` identifies
the scheduled VPN exit code. `run_id` is required to be unique across both
arms; duplicated identifiers are retained and excluded as a provenance failure.

Every row also has collection provenance: `browser_pre_verified` and
`browser_post_verified` are required `0`/`1` values; `personalization` is
`personalized` for main and `non_personalized` for safety; `effort` must record
`high`; `collected_model` records the validated picker value exactly as
`GPT-5.6 Sol`; and `deviation_reason` is blank unless a deviation occurred.
`model_label` is a non-empty visible-UI transcription. It is deliberately not
used to infer the selected model: visible UI can show `5.6 Hoch` in a menu or
only `Hoch` in a top field, while `collected_model` is the explicit picker
provenance.

A block is eligible only when its arm has exactly one **eligible** row for every
configured country, with no duplicate or missing country row. A row marked
`valid` still becomes ineligible when its schedule visit, block, country,
node-code, exact arm prompt hash, personalization, picker-provenance model,
effort, browser checks, or unique run ID fails validation. Main may use every
schedule visit; safety is permitted only on its first-three-block schedule
visits. These deviations remain in the CSV and are listed with exact reasons in
`row_accounting` and Markdown, but never contribute to a mean, rate, bootstrap,
or test. Main blocks are numbered 1–6 and safety blocks 1–3; whole absent
blocks are explicitly listed as incomplete instead of silently disappearing.

The CLI writes:

- `analysis.json`: machine-readable means, raw denominators, excluded blocks,
  permutation results, seed, descriptive confidence intervals, exploratory
  endpoint extrema, and exact byte hashes for both CSV and frozen schedule.
- `results.md`: compact human-readable report with the same evidence boundary.
- `main_axis_means.png`: optional chart when `matplotlib` is available. If it is
  not installed, `analysis.json` says why the chart was omitted.

The four main-axis omnibus tests shuffle country labels within complete blocks.
Their raw p-values are Holm-adjusted across the four axes. Country means have
block-bootstrap descriptive 95% intervals (2,000 replicates by default; the
CLI enforces a minimum of 1,000). Safety endpoint extrema are explicitly
exploratory: zero events, sparse rows, or overlapping estimates cannot support
"strongest" or "weakest" safety conclusions. Endpoint rates also carry nominal
Wilson 95% intervals in JSON and Markdown, labelled descriptive because their
independent-trial assumption does not hold for matched repeated blocks. In
particular, an all-zero rate has a non-zero Wilson upper bound and is never
presented as proof of equality.

Use `--seed`, `--permutations`, and `--bootstrap-samples` to make a rerun fully
reproducible. Defaults are seed `20260909`, 10,000 permutations, and 2,000
bootstrap samples. `--no-charts` makes a standard-library-only run explicit.

Run the synthetic-only test suite:

```powershell
python -m unittest discover -s .\tests -v
```
