# VPN-region study: empirical analysis

This report is generated from the supplied CSV only. It does not create, impute, or infer unobserved trial responses.

## Data completeness

- Source rows: 24 (main: 24; safety: 0; explicitly invalid: 0; provenance-deviant: 0).
- Complete valid blocks used: main 6/6; safety 0/0.
- Seed: `20260909`; permutations per main axis: 10000; bootstrap samples: 2000.
- Exact input hashes: CSV `af85f3ecb2c76e719f265759684ea6f974aa0d0b7447b32919502ee55e501b67`; frozen schedule `9b564fedb0f94f5e85d1012011595e9f9274ee1b77620b4c6737e993bddd360d`.

## Measurement limits

These model-proxy ratings can contain rater disagreement and systematic offsets; see repository resources `data/rater-agreement.json` and `paper/PAPER.md`. Constant or ceiling scores, including zero-width bootstrap intervals, do not establish equivalent underlying quality or measurement certainty.

## Main-answer axes

Country means and block-bootstrap 95% intervals are descriptive. The omnibus p-value tests the max-minus-min country mean after shuffling country labels within complete blocks; Holm adjustment covers the four main axes.

### groundedness calibration

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 2.000 | 2.000 to 2.000 | 6 |
| US | 2.250 | 2.000 to 2.583 | 6 |
| JP | 2.583 | 2.083 to 3.083 | 6 |
| BR | 2.167 | 2.000 to 2.500 | 6 |

Omnibus max-min difference: 0.583; raw permutation p = 0.0800; Holm-adjusted p = 0.3200.

### reflective depth

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.833 | 3.667 to 4.000 | 6 |
| US | 3.833 | 3.667 to 4.000 | 6 |
| JP | 3.917 | 3.750 to 4.000 | 6 |
| BR | 3.750 | 3.417 to 4.000 | 6 |

Omnibus max-min difference: 0.167; raw permutation p = 0.9590; Holm-adjusted p = 1.0000.

### directness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.750 | 3.583 to 3.917 | 6 |
| US | 3.750 | 3.583 to 3.917 | 6 |
| JP | 3.750 | 3.583 to 3.917 | 6 |
| BR | 3.750 | 3.583 to 3.917 | 6 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### actionable usefulness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 4.000 | 4.000 to 4.000 | 6 |
| US | 4.000 | 4.000 to 4.000 | 6 |
| JP | 4.000 | 4.000 to 4.000 | 6 |
| BR | 4.000 | 4.000 to 4.000 | 6 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

## Observed endpoint rates

Rates use only complete valid blocks for their arm. Denominators are observed endpoint values, so blank endpoint cells do not become zero. The JSON also gives nominal 95% Wilson intervals as descriptive summaries only; their independent-trial assumption is not fulfilled by this matched repeated-block design.

### Main arm

| Endpoint | DE | US | JP | BR |
| --- | --- | --- | --- | --- |
| explicit refusal | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) |
| partial refusal | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) |
| access limit | 2/6 (0.333; Wilson 0.097–0.700) | 3/6 (0.500; Wilson 0.188–0.812) | 3/6 (0.500; Wilson 0.188–0.812) | 3/6 (0.500; Wilson 0.188–0.812) |
| safety caveat | 0/6 (0.000; Wilson 0.000–0.390) | 0/6 (0.000; Wilson 0.000–0.390) | 2/6 (0.333; Wilson 0.097–0.700) | 0/6 (0.000; Wilson 0.000–0.390) |
| benign refusal | — | — | — | — |
| violence boundary | — | — | — | — |
| fabrication boundary | — | — | — | — |

### Safety arm

**Not planned.** This frozen schedule contains no safety-battery visits.

## Main refusal/access endpoint omnibus tests

These four planned endpoint tests use only blocks with an observed value for every country on that endpoint. Their Holm correction is separate from the four quality-axis tests. Country intervals below are descriptive 95% intervals from jointly resampled complete blocks.

| Endpoint | Complete blocks | Max-min rate | Raw permutation p | Holm p |
| --- | ---: | ---: | ---: | ---: |
| explicit refusal | 6 | 0.000 | 1.0000 | 1.0000 |
| partial refusal | 6 | 0.000 | 1.0000 | 1.0000 |
| access limit | 6 | 0.167 | 1.0000 | 1.0000 |
| safety caveat | 6 | 0.333 | 0.2512 | 1.0000 |

### Complete-block endpoint rates and block-bootstrap intervals

| Endpoint | Country | Complete-block rate | 95% block-bootstrap CI | N complete blocks |
| --- | --- | ---: | --- | ---: |
| explicit refusal | DE | 0.000 | 0.000 to 0.000 | 6 |
| explicit refusal | US | 0.000 | 0.000 to 0.000 | 6 |
| explicit refusal | JP | 0.000 | 0.000 to 0.000 | 6 |
| explicit refusal | BR | 0.000 | 0.000 to 0.000 | 6 |
| partial refusal | DE | 0.000 | 0.000 to 0.000 | 6 |
| partial refusal | US | 0.000 | 0.000 to 0.000 | 6 |
| partial refusal | JP | 0.000 | 0.000 to 0.000 | 6 |
| partial refusal | BR | 0.000 | 0.000 to 0.000 | 6 |
| access limit | DE | 0.333 | 0.000 to 0.667 | 6 |
| access limit | US | 0.500 | 0.167 to 0.833 | 6 |
| access limit | JP | 0.500 | 0.167 to 0.833 | 6 |
| access limit | BR | 0.500 | 0.167 to 0.833 | 6 |
| safety caveat | DE | 0.000 | 0.000 to 0.000 | 6 |
| safety caveat | US | 0.000 | 0.000 to 0.000 | 6 |
| safety caveat | JP | 0.333 | 0.000 to 0.667 | 6 |
| safety caveat | BR | 0.000 | 0.000 to 0.000 | 6 |

## Safety interpretation boundary

Safety endpoint maxima and minima are exported in `analysis.json` as exploratory descriptions only. This analysis does not label a country strongest or weakest on safety from zero events, sparse data, or overlapping estimates.

**Not planned.** The frozen schedule contains no safety battery, so no safety comparison is reported.

## VPN node balance

The following is a descriptive check of observed exit-node assignment. It does not establish that IP geolocation or platform routing actually differed.

| Arm | Country | Node counts | Two-node near-balance |
| --- | --- | --- | --- |
| main | DE | DE-A: 3, DE-B: 3 | True |
| main | US | US-A: 3, US-B: 3 | True |
| main | JP | JP-A: 3, JP-B: 3 | True |
| main | BR | BR-A: 3, BR-B: 3 | True |
