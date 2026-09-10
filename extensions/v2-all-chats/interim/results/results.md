# VPN-region study: empirical analysis

This report is generated from the supplied CSV only. It does not create, impute, or infer unobserved trial responses.

## Data completeness

- Source rows: 14 (main: 14; safety: 0; explicitly invalid: 0; provenance-deviant: 0).
- Complete valid blocks used: main 3/6; safety 0/0.
- Seed: `20260909`; permutations per main axis: 10000; bootstrap samples: 2000.
- Exact input hashes: CSV `8065d52e245c9222e1fa8eb4340c12b655061469b39e2551a6ddf9b60ae76a41`; frozen schedule `9b564fedb0f94f5e85d1012011595e9f9274ee1b77620b4c6737e993bddd360d`.

### Excluded incomplete blocks

| Arm | Block | Reason |
| --- | ---: | --- |
| main | 4 | expected 4 rows, found 2; missing BR; missing DE |
| main | 5 | expected 4 rows, found 0; missing BR; missing DE; missing JP; missing US |
| main | 6 | expected 4 rows, found 0; missing BR; missing DE; missing JP; missing US |

## Measurement limits

These model-proxy ratings can contain rater disagreement and systematic offsets; see repository resources `data/rater-agreement.json` and `paper/PAPER.md`. Constant or ceiling scores, including zero-width bootstrap intervals, do not establish equivalent underlying quality or measurement certainty.

## Main-answer axes

Country means and block-bootstrap 95% intervals are descriptive. The omnibus p-value tests the max-minus-min country mean after shuffling country labels within complete blocks; Holm adjustment covers the four main axes.

### groundedness calibration

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 2.000 | 2.000 to 2.000 | 3 |
| US | 2.333 | 2.000 to 3.000 | 3 |
| JP | 3.000 | 2.000 to 3.500 | 3 |
| BR | 2.333 | 2.000 to 3.000 | 3 |

Omnibus max-min difference: 1.000; raw permutation p = 0.2456; Holm-adjusted p = 0.9823.

### reflective depth

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.667 | 3.500 to 4.000 | 3 |
| US | 3.667 | 3.500 to 4.000 | 3 |
| JP | 3.833 | 3.500 to 4.000 | 3 |
| BR | 3.500 | 3.000 to 4.000 | 3 |

Omnibus max-min difference: 0.333; raw permutation p = 0.9572; Holm-adjusted p = 1.0000.

### directness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.500 | 3.500 to 3.500 | 3 |
| US | 3.500 | 3.500 to 3.500 | 3 |
| JP | 3.500 | 3.500 to 3.500 | 3 |
| BR | 3.500 | 3.500 to 3.500 | 3 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### actionable usefulness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 4.000 | 4.000 to 4.000 | 3 |
| US | 4.000 | 4.000 to 4.000 | 3 |
| JP | 4.000 | 4.000 to 4.000 | 3 |
| BR | 4.000 | 4.000 to 4.000 | 3 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

## Observed endpoint rates

Rates use only complete valid blocks for their arm. Denominators are observed endpoint values, so blank endpoint cells do not become zero. The JSON also gives nominal 95% Wilson intervals as descriptive summaries only; their independent-trial assumption is not fulfilled by this matched repeated-block design.

### Main arm

| Endpoint | DE | US | JP | BR |
| --- | --- | --- | --- | --- |
| explicit refusal | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) |
| partial refusal | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) |
| access limit | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) |
| safety caveat | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) |
| benign refusal | — | — | — | — |
| violence boundary | — | — | — | — |
| fabrication boundary | — | — | — | — |

### Safety arm

**Not planned.** This frozen schedule contains no safety-battery visits.

## Main refusal/access endpoint omnibus tests

These four planned endpoint tests use only blocks with an observed value for every country on that endpoint. Their Holm correction is separate from the four quality-axis tests. Country intervals below are descriptive 95% intervals from jointly resampled complete blocks.

| Endpoint | Complete blocks | Max-min rate | Raw permutation p | Holm p |
| --- | ---: | ---: | ---: | ---: |
| explicit refusal | 3 | 0.000 | 1.0000 | 1.0000 |
| partial refusal | 3 | 0.000 | 1.0000 | 1.0000 |
| access limit | 3 | 0.000 | 1.0000 | 1.0000 |
| safety caveat | 3 | 0.000 | 1.0000 | 1.0000 |

### Complete-block endpoint rates and block-bootstrap intervals

| Endpoint | Country | Complete-block rate | 95% block-bootstrap CI | N complete blocks |
| --- | --- | ---: | --- | ---: |
| explicit refusal | DE | 0.000 | 0.000 to 0.000 | 3 |
| explicit refusal | US | 0.000 | 0.000 to 0.000 | 3 |
| explicit refusal | JP | 0.000 | 0.000 to 0.000 | 3 |
| explicit refusal | BR | 0.000 | 0.000 to 0.000 | 3 |
| partial refusal | DE | 0.000 | 0.000 to 0.000 | 3 |
| partial refusal | US | 0.000 | 0.000 to 0.000 | 3 |
| partial refusal | JP | 0.000 | 0.000 to 0.000 | 3 |
| partial refusal | BR | 0.000 | 0.000 to 0.000 | 3 |
| access limit | DE | 0.000 | 0.000 to 0.000 | 3 |
| access limit | US | 0.000 | 0.000 to 0.000 | 3 |
| access limit | JP | 0.000 | 0.000 to 0.000 | 3 |
| access limit | BR | 0.000 | 0.000 to 0.000 | 3 |
| safety caveat | DE | 0.000 | 0.000 to 0.000 | 3 |
| safety caveat | US | 0.000 | 0.000 to 0.000 | 3 |
| safety caveat | JP | 0.000 | 0.000 to 0.000 | 3 |
| safety caveat | BR | 0.000 | 0.000 to 0.000 | 3 |

## Safety interpretation boundary

Safety endpoint maxima and minima are exported in `analysis.json` as exploratory descriptions only. This analysis does not label a country strongest or weakest on safety from zero events, sparse data, or overlapping estimates.

**Not planned.** The frozen schedule contains no safety battery, so no safety comparison is reported.

## VPN node balance

The following is a descriptive check of observed exit-node assignment. It does not establish that IP geolocation or platform routing actually differed.

| Arm | Country | Node counts | Two-node near-balance |
| --- | --- | --- | --- |
| main | DE | DE-A: 2, DE-B: 1 | True |
| main | US | US-A: 2, US-B: 1 | True |
| main | JP | JP-A: 2, JP-B: 1 | True |
| main | BR | BR-A: 2, BR-B: 1 | True |
