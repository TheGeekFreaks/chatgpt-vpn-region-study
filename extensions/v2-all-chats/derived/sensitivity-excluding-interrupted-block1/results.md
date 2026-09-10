# VPN-region study: empirical analysis

This report is generated from the supplied CSV only. It does not create, impute, or infer unobserved trial responses.

## Data completeness

- Source rows: 20 (main: 20; safety: 0; explicitly invalid: 0; provenance-deviant: 0).
- Complete valid blocks used: main 5/6; safety 0/0.
- Seed: `20260909`; permutations per main axis: 10000; bootstrap samples: 2000.
- Exact input hashes: CSV `72ece138bc99607adf7e6f80c8e163b0e0a48d188a4957cebe6b0cf7d85d0000`; frozen schedule `9b564fedb0f94f5e85d1012011595e9f9274ee1b77620b4c6737e993bddd360d`.

### Excluded incomplete blocks

| Arm | Block | Reason |
| --- | ---: | --- |
| main | 1 | expected 4 rows, found 0; missing BR; missing DE; missing JP; missing US |

## Measurement limits

These model-proxy ratings can contain rater disagreement and systematic offsets; see repository resources `data/rater-agreement.json` and `paper/PAPER.md`. Constant or ceiling scores, including zero-width bootstrap intervals, do not establish equivalent underlying quality or measurement certainty.

## Main-answer axes

Country means and block-bootstrap 95% intervals are descriptive. The omnibus p-value tests the max-minus-min country mean after shuffling country labels within complete blocks; Holm adjustment covers the four main axes.

### groundedness calibration

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 2.000 | 2.000 to 2.000 | 5 |
| US | 2.100 | 2.000 to 2.300 | 5 |
| JP | 2.400 | 2.000 to 3.000 | 5 |
| BR | 2.000 | 2.000 to 2.000 | 5 |

Omnibus max-min difference: 0.400; raw permutation p = 0.5048; Holm-adjusted p = 1.0000.

### reflective depth

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.900 | 3.700 to 4.000 | 5 |
| US | 3.800 | 3.600 to 4.000 | 5 |
| JP | 3.900 | 3.700 to 4.000 | 5 |
| BR | 3.800 | 3.400 to 4.000 | 5 |

Omnibus max-min difference: 0.100; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### directness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.800 | 3.600 to 4.000 | 5 |
| US | 3.800 | 3.600 to 4.000 | 5 |
| JP | 3.800 | 3.600 to 4.000 | 5 |
| BR | 3.800 | 3.600 to 4.000 | 5 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### actionable usefulness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 4.000 | 4.000 to 4.000 | 5 |
| US | 4.000 | 4.000 to 4.000 | 5 |
| JP | 4.000 | 4.000 to 4.000 | 5 |
| BR | 4.000 | 4.000 to 4.000 | 5 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

## Observed endpoint rates

Rates use only complete valid blocks for their arm. Denominators are observed endpoint values, so blank endpoint cells do not become zero. The JSON also gives nominal 95% Wilson intervals as descriptive summaries only; their independent-trial assumption is not fulfilled by this matched repeated-block design.

### Main arm

| Endpoint | DE | US | JP | BR |
| --- | --- | --- | --- | --- |
| explicit refusal | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) |
| partial refusal | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) |
| access limit | 2/5 (0.400; Wilson 0.118–0.769) | 3/5 (0.600; Wilson 0.231–0.882) | 3/5 (0.600; Wilson 0.231–0.882) | 3/5 (0.600; Wilson 0.231–0.882) |
| safety caveat | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 2/5 (0.400; Wilson 0.118–0.769) | 0/5 (0.000; Wilson 0.000–0.434) |
| benign refusal | — | — | — | — |
| violence boundary | — | — | — | — |
| fabrication boundary | — | — | — | — |

### Safety arm

**Not planned.** This frozen schedule contains no safety-battery visits.

## Main refusal/access endpoint omnibus tests

These four planned endpoint tests use only blocks with an observed value for every country on that endpoint. Their Holm correction is separate from the four quality-axis tests. Country intervals below are descriptive 95% intervals from jointly resampled complete blocks.

| Endpoint | Complete blocks | Max-min rate | Raw permutation p | Holm p |
| --- | ---: | ---: | ---: | ---: |
| explicit refusal | 5 | 0.000 | 1.0000 | 1.0000 |
| partial refusal | 5 | 0.000 | 1.0000 | 1.0000 |
| access limit | 5 | 0.200 | 1.0000 | 1.0000 |
| safety caveat | 5 | 0.400 | 0.2454 | 0.9815 |

### Complete-block endpoint rates and block-bootstrap intervals

| Endpoint | Country | Complete-block rate | 95% block-bootstrap CI | N complete blocks |
| --- | --- | ---: | --- | ---: |
| explicit refusal | DE | 0.000 | 0.000 to 0.000 | 5 |
| explicit refusal | US | 0.000 | 0.000 to 0.000 | 5 |
| explicit refusal | JP | 0.000 | 0.000 to 0.000 | 5 |
| explicit refusal | BR | 0.000 | 0.000 to 0.000 | 5 |
| partial refusal | DE | 0.000 | 0.000 to 0.000 | 5 |
| partial refusal | US | 0.000 | 0.000 to 0.000 | 5 |
| partial refusal | JP | 0.000 | 0.000 to 0.000 | 5 |
| partial refusal | BR | 0.000 | 0.000 to 0.000 | 5 |
| access limit | DE | 0.400 | 0.000 to 0.800 | 5 |
| access limit | US | 0.600 | 0.200 to 1.000 | 5 |
| access limit | JP | 0.600 | 0.200 to 1.000 | 5 |
| access limit | BR | 0.600 | 0.200 to 1.000 | 5 |
| safety caveat | DE | 0.000 | 0.000 to 0.000 | 5 |
| safety caveat | US | 0.000 | 0.000 to 0.000 | 5 |
| safety caveat | JP | 0.400 | 0.000 to 0.800 | 5 |
| safety caveat | BR | 0.000 | 0.000 to 0.000 | 5 |

## Safety interpretation boundary

Safety endpoint maxima and minima are exported in `analysis.json` as exploratory descriptions only. This analysis does not label a country strongest or weakest on safety from zero events, sparse data, or overlapping estimates.

**Not planned.** The frozen schedule contains no safety battery, so no safety comparison is reported.

## VPN node balance

The following is a descriptive check of observed exit-node assignment. It does not establish that IP geolocation or platform routing actually differed.

| Arm | Country | Node counts | Two-node near-balance |
| --- | --- | --- | --- |
| main | DE | DE-A: 2, DE-B: 3 | True |
| main | US | US-A: 3, US-B: 2 | True |
| main | JP | JP-A: 2, JP-B: 3 | True |
| main | BR | BR-A: 2, BR-B: 3 | True |
