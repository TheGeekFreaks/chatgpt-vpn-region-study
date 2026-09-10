# Reproducible derived analyses

This directory contains derived public artifacts. It does not replace the
frozen primary analysis in `../results/`.

## Block-1 sensitivity analysis

`trials-excluding-interrupted-block1.csv` contains the exact public CSV rows
whose `block` field is not `1`, with the original header and all remaining
fields retained. It has 20 rows. The frozen schedule is deliberately retained:
the analyzer therefore records block 1 as an incomplete expected main block,
rather than treating the study as if it had only five scheduled blocks.

The following PowerShell selection and analyzer command reproduce the derived
CSV and its `sensitivity-excluding-interrupted-block1/` output:

```powershell
$source = 'extensions/v2-all-chats/data/trials.csv'
$derived = 'extensions/v2-all-chats/derived'
$selected = Join-Path $derived 'trials-excluding-interrupted-block1.csv'

Import-Csv -LiteralPath $source |
  Where-Object { $_.block -ne '1' } |
  Export-Csv -LiteralPath $selected -NoTypeInformation -Encoding utf8

python analysis/analysis_cli.py $selected `
  --schedule extensions/v2-all-chats/protocol/schedule.json `
  --out extensions/v2-all-chats/derived/sensitivity-excluding-interrupted-block1 `
  --permutations 10000 `
  --bootstrap-samples 2000 `
  --seed 20260909
```

The source CSV SHA-256 is
`af85f3ecb2c76e719f265759684ea6f974aa0d0b7447b32919502ee55e501b67`.
The selected CSV SHA-256 is
`72ece138bc99607adf7e6f80c8e163b0e0a48d188a4957cebe6b0cf7d85d0000`.
The retained frozen schedule SHA-256 is
`9b564fedb0f94f5e85d1012011595e9f9274ee1b77620b4c6737e993bddd360d`.

This sensitivity does **not** remove the documented possibility that M01
remained in account history through M14. It cannot repair carryover, replace the
frozen primary analysis, or trigger the conditional country expansion. See
`../protocol/DEVIATIONS.md`.

## Strict verified-account blocks 5–6 description

`trials-strict-verified-account-blocks5-6.csv` retains exactly the eight public
rows whose `block` field is `5` or `6`. It is summarized in
`strict-verified-account-blocks5-6-descriptive.md` using means and raw endpoint
counts only. No permutation test, bootstrap interval, p-value, Holm adjustment,
or expansion decision is calculated for this two-block descriptive subset.

The selected blocks-5–6 CSV SHA-256 is
`50f47935f01518ed778bdd2971e848881a396a52e6ee563042f68c90e1b7626`.
