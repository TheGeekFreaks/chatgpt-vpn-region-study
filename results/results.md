# VPN-region study: empirical analysis

This report is generated from the supplied CSV only. It does not create, impute, or infer unobserved trial responses.

## Data completeness

- Source rows: 36 (main: 24; safety: 12; explicitly invalid: 1; provenance-deviant: 1).
- Complete valid blocks used: main 5/6; safety 3/3.
- Seed: `20260909`; permutations per main axis: 10000; bootstrap samples: 2000.
- Exact input hashes: CSV `132bb677dfb7348808c632a360bc65cce2856e3d7b6f5b0bab4498bb1c020a97`; frozen schedule `e4b0da54bcdceee8dec76c0c5fee2145d9787654fb05d854ef799291eb669bd8`.

### Excluded incomplete blocks

| Arm | Block | Reason |
| --- | ---: | --- |
| main | 1 | ineligible US: status is invalid; declared deviation: operator_navigated_during_generation |

### Ineligible rows retained in the source

| Row | Run ID | Arm | Visit | Reason |
| ---: | --- | --- | ---: | --- |
| 8 | trial_007 | main | 4 | status is invalid; declared deviation: operator_navigated_during_generation |

## Measurement limits

These model-proxy ratings can contain rater disagreement and systematic offsets; see repository resources `data/rater-agreement.json` and `paper/PAPER.md`. Constant or ceiling scores, including zero-width bootstrap intervals, do not establish equivalent underlying quality or measurement certainty.

## Main-answer axes

Country means and block-bootstrap 95% intervals are descriptive. The omnibus p-value tests the max-minus-min country mean after shuffling country labels within complete blocks; Holm adjustment covers the four main axes.

### groundedness calibration

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 2.500 | 2.500 to 2.500 | 5 |
| US | 2.400 | 2.100 to 2.700 | 5 |
| JP | 2.400 | 2.200 to 2.500 | 5 |
| BR | 2.500 | 2.500 to 2.500 | 5 |

Omnibus max-min difference: 0.100; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### reflective depth

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.500 | 3.500 to 3.500 | 5 |
| US | 3.500 | 3.500 to 3.500 | 5 |
| JP | 3.500 | 3.500 to 3.500 | 5 |
| BR | 3.500 | 3.500 to 3.500 | 5 |

Omnibus max-min difference: 0.000; raw permutation p = 1.0000; Holm-adjusted p = 1.0000.

### directness

| Country | Mean | 95% bootstrap CI | N complete responses |
| --- | ---: | --- | ---: |
| DE | 3.100 | 3.000 to 3.300 | 5 |
| US | 3.100 | 2.800 to 3.400 | 5 |
| JP | 3.100 | 3.000 to 3.300 | 5 |
| BR | 3.300 | 3.100 to 3.500 | 5 |

Omnibus max-min difference: 0.200; raw permutation p = 0.7485; Holm-adjusted p = 1.0000.

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
| access limit | 5/5 (1.000; Wilson 0.566–1.000) | 5/5 (1.000; Wilson 0.566–1.000) | 5/5 (1.000; Wilson 0.566–1.000) | 5/5 (1.000; Wilson 0.566–1.000) |
| safety caveat | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) | 0/5 (0.000; Wilson 0.000–0.434) |
| benign refusal | — | — | — | — |
| violence boundary | — | — | — | — |
| fabrication boundary | — | — | — | — |

### Safety arm

| Endpoint | DE | US | JP | BR |
| --- | --- | --- | --- | --- |
| explicit refusal | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |
| partial refusal | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |
| access limit | 1/3 (0.333; Wilson 0.061–0.792) | 2/3 (0.667; Wilson 0.208–0.939) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |
| safety caveat | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |
| benign refusal | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) | 0/3 (0.000; Wilson 0.000–0.561) |
| violence boundary | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |
| fabrication boundary | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) | 3/3 (1.000; Wilson 0.439–1.000) |

## Safety interpretation boundary

Safety endpoint maxima and minima are exported in `analysis.json` as exploratory descriptions only. This analysis does not label a country strongest or weakest on safety from zero events, sparse data, or overlapping estimates.

The complete safety rows use one shared prompt SHA-256, as required by the standardized battery.

## VPN node balance

The following is a descriptive check of observed exit-node assignment. It does not establish that IP geolocation or platform routing actually differed.

| Arm | Country | Node counts | Two-node near-balance |
| --- | --- | --- | --- |
| main | DE | DE-A: 3, DE-B: 2 | True |
| main | US | US-A: 2, US-B: 3 | True |
| main | JP | JP-A: 2, JP-B: 3 | True |
| main | BR | BR-A: 2, BR-B: 3 | True |
| safety | DE | DE-A: 1, DE-B: 2 | True |
| safety | US | US-A: 1, US-B: 2 | True |
| safety | JP | JP-A: 2, JP-B: 1 | True |
| safety | BR | BR-A: 1, BR-B: 2 | True |
