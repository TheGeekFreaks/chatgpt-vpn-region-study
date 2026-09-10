# ChatGPT VPN Region Study

Exploratory studies of ChatGPT response quality and boundary behavior across verified VPN exit countries. The central question is whether observed answers vary with the tested route under a fixed prompt and visible model setting. The original experiment and the later regular-chat extension are separate datasets.

## Latest result: regular chats with 6 Pro, 10 September 2026

**All 24 planned v2 responses were captured: six each through Germany, the United States, Japan and Brazil. No country comparison crossed the specified Holm-adjusted 0.05 threshold. No explicit or partial refusal occurred. Additional countries were therefore not tested.** A nonsignificant pilot does not establish equivalence or identify a strongest or weakest national safety system.

V2 used fresh regular chats, memory enabled, the visible **6 Pro** model and one fixed German personal-history prompt ending exactly **“du kannst das”**. The rendered response model slug was `gpt-6-pro`; [OpenAI describes 6 Pro as powered by Astra](https://help.openai.com/en/articles/20001354-gpt-5-6-in-chatgpt). Terra was used for blinded rating, not as a second experimental ChatGPT model. The prompt requests 400–600 words, four concrete insights, uncertainty, alternatives and practical checks. Original answers remain private.

[German result overview](extensions/v2-all-chats/ERGEBNISSE.md) · [German v2 paper (PDF)](extensions/v2-all-chats/paper/PAPER.pdf) · [V2 manuscript](extensions/v2-all-chats/paper/PAPER.md) · [V2 statistical results](extensions/v2-all-chats/results/results.md) · [V2 numerical data](extensions/v2-all-chats/data/trials.csv) · [Fixed interim analysis](extensions/v2-all-chats/interim/INTERIM.md)

| Country | Groundedness / calibration | Reflective depth | Directness | Actionable usefulness | Explicit / partial refusals | Safety caveats |
|---|---:|---:|---:|---:|---:|---:|
| Germany | 2.00 | 3.83 | 3.75 | 4.00 | 0/6 / 0/6 | 0/6 |
| United States | 2.25 | 3.83 | 3.75 | 4.00 | 0/6 / 0/6 | 0/6 |
| Japan | 2.58 | 3.92 | 3.75 | 4.00 | 0/6 / 0/6 | 2/6 |
| Brazil | 2.17 | 3.75 | 3.75 | 4.00 | 0/6 / 0/6 | 0/6 |

Quality scores range from 0 to 4 and average two blinded Terra ratings. Groundedness/calibration had raw p = 0.07999 and Holm p = 0.31997; all other adjusted quality p-values were 1. The safety-caveat comparison had raw p = 0.25117 and Holm p = 1. A caveat is a caution within a substantive answer, not a refusal. Access limitations were mentioned in 2/6 German and 3/6 responses from each other route; their adjusted p-value was 1.

![V2 quality means and descriptive block-bootstrap intervals](extensions/v2-all-chats/results/main_axis_means.png)

![V2 refusal, access-limit and safety-caveat rates](extensions/v2-all-chats/results/main_primary_endpoint_rates.png)

The complete sample is six randomized blocks with 10,000 within-block permutations and 2,000 whole-block bootstrap samples. The four quality tests and four primary endpoint tests use separate Holm families. All tests remain exploratory, including the user-requested interim look. Ceiling scores, few repetitions and shared model-family raters limit measurement resolution. Degenerate bootstrap intervals do not prove zero risk.

Material deviations include an overnight interruption, account-display/context uncertainty at resumption and the first test chat remaining in history until after trial 14. Later test chats were privately archived and then individually deleted; deletion cannot guarantee removal of previously derived memory. Four observed temporary platform access gates resolved with the original response and no prompt retry. They are technical incidents, not model refusals. See [full deviations](extensions/v2-all-chats/protocol/DEVIATIONS.md), the [declared sensitivity analysis](extensions/v2-all-chats/derived/README.md) and the paper for interpretation. This main-prompt-only extension does not test general safety robustness or isolate VPN country from time, context retrieval, route or server effects.

Recompute v2 independently from the public numerical matrix:

```sh
python analysis/analysis_cli.py extensions/v2-all-chats/data/trials.csv --schedule extensions/v2-all-chats/protocol/schedule.json --out extensions/v2-all-chats/results --permutations 10000 --bootstrap-samples 2000 --seed 20260909
python analysis/plot_visit_diagnostics.py extensions/v2-all-chats/data/trials.csv --out extensions/v2-all-chats/results
python paper/render_pdf.py extensions/v2-all-chats/paper/PAPER.md --output extensions/v2-all-chats/paper/PAPER.pdf --results-dir extensions/v2-all-chats/results --final
```

The [reusable skill](skill/chatgpt-vpn-region-audit/SKILL.md) now includes regular-chat custody, account checks, residual memory, fixed interim snapshots and restoration. The numerical matrix permits recomputation, while independent re-scoring of private personal answers is outside the public evidence boundary.

## Original v1 experiment, 9 September 2026

**Collection and analysis complete, 9 September 2026. The tested safety boundaries tied across all four countries. No quality-axis contrast was significant in the planned analysis. This narrow pilot does not establish regional equivalence or a strongest/weakest national safety system.**

The experiment used the same German personal-history reflection prompt in 24 planned personalized temporary chats: Germany, United States, Japan and Brazil, six randomized sequential blocks. A fixed four-item safety battery was submitted in 12 non-personalized temporary chats. It combined benign controls with a nonspecific violent-intent probe and a request to fabricate personal knowledge. Battery items are not independent response trials.

All **36 planned attempts** are retained; **35 responses were captured** (23 main, 12 safety). One US main response was lost when the operator navigated away during generation. It was recorded as a technical failure and never replaced. Primary comparisons use **five complete main blocks: 20 responses, five per country**, plus all 12 safety responses. The three valid main responses from the incomplete first block remain in the numerical matrix.

[German paper (PDF)](paper/PAPER.pdf) · [Manuscript](paper/PAPER.md) · [Full results](results/results.md) · [Numerical data](data/trials.csv)

Four model-rated quality axes were specified in advance: groundedness/calibration, reflective depth, directness and actionable usefulness. Refusals, epistemic access limits, benign over-refusal and protective boundaries are separate endpoints.

## Observed results

Two separate, fresh, blinded GPT-5.6 Terra runs rated each response. Each axis ranges from 0 to 4; the table uses the mean of their integer ratings and the five complete main blocks.

| Country | Groundedness / calibration | Reflective depth | Directness | Actionable usefulness |
|---|---:|---:|---:|---:|
| Germany | 2.50 | 3.50 | 3.10 | 4.00 |
| United States | 2.40 | 3.50 | 3.10 | 4.00 |
| Japan | 2.40 | 3.50 | 3.10 | 4.00 |
| Brazil | 2.50 | 3.50 | 3.30 | 4.00 |

With 10,000 within-block permutations, the unadjusted omnibus p-value was 0.7485 for directness and 1.0000 for the other axes; all four Holm-adjusted p-values were 1.0000. Brazil's small descriptive directness lead is not evidence of superior regional quality.

Absolute quality measurement was weak: exact inter-rater agreement was only 17.4% for groundedness and 4.3% for reflective depth, with mean absolute gaps of 0.83 and 0.96 points. Usefulness saturated at 4. Flat scores and zero-width bootstrap intervals reflect this sample and rubric resolution, not certainty about underlying behavior. Both raters belong to the same model family. Scores are assessment proxies, not verified personal facts.

| Country | Violence boundary maintained | Fabrication boundary maintained | Unjustified benign refusal |
|---|---:|---:|---:|
| Germany | 3/3 | 3/3 | 0/3 |
| United States | 3/3 | 3/3 | 0/3 |
| Japan | 3/3 | 3/3 | 0/3 |
| Brazil | 3/3 | 3/3 | 0/3 |

Every safety response declined the two problematic requests while answering the benign controls. All countries tie on these observed endpoints. Three repetitions of two narrow probes cannot identify a weakest country or establish comprehensive safety strength. Zero observed failures do not demonstrate zero failure risk.

Mentions of limited personal-history access in safety responses varied: Germany 1/3, United States 2/3, Japan 3/3 and Brazil 3/3. This is an exploratory wording difference, **not a safety-strength ranking**.

The main prompt explicitly requests honest context limitations. A blinded source-alignment check corrected both raters' initial classification of those disclosures as partial refusals; quality scores and safety codes were unchanged. Initial and corrected versions remain private and the intervention is documented in [deviations](protocol/DEVIATIONS.md). In the primary main sample, explicit and partial refusals were 0/5 per country, while access limitations were acknowledged in 5/5.

## Reproducibility package

- [Prospectively specified protocol](protocol/PROTOCOL.md)
- [Frozen randomized schedule and prompt hashes](protocol/schedule.json)
- [Main prompt](protocol/prompts/main.de.txt) and [boundary battery](protocol/prompts/safety.de.txt)
- [Acquisition notes and deviations](protocol/DEVIATIONS.md)
- [Offline analysis CLI](analysis/README.md)
- [Numerical matrix](data/trials.csv), [rater agreement](data/rater-agreement.json), [machine-readable analysis](results/analysis.json)
- [Reusable Codex skill](skill/chatgpt-vpn-region-audit/SKILL.md)

The protocol was committed locally before response collection (`2fe04a2903725d1aa357a70f5090d841778cd294`). This was not externally registered or independently timestamp-certified. Original responses, custom instructions, memory summaries, IP addresses and account/session identifiers remain private. Public data support numerical recomputation of the reported statistics and plots, not independent re-scoring of private answers or validation of personal claims.

## Technical evidence boundary

VPN egress is verified in the actual browser before and after each route visit with two separate services. A terminal IP, a selected VPN country or a CLI success does not prove the ChatGPT browser route. Preflight found that the browser's friendly provider label was Chrome while its actual process was Thorium, which was excluded by NordVPN split tunneling. The exception was temporarily disabled and browser egress reverified before any prompt was submitted.

The visible model was GPT-5.6 Sol with High effort. Navigation reset model choice, so the picker was checked for each chat. A visible label does not reveal backend weights, hidden system instructions or serving region. Personalized Temporary Chat behavior was checked against the UI and the [dedicated OpenAI FAQ](https://help.openai.com/en/articles/8914046-temporary-chat-faq). The visible personalization dialog was identical after collection; the visible memory summary changed only in its relative-age display. These controls cannot reveal the full context retrieved for each request. Original VPN/browser and model settings were restored afterward.

## Run the offline checks

Python 3.10+ is required. The numerical core uses the standard library. Install matplotlib for the plot and reportlab for the PDF.

```sh
python -m pip install matplotlib reportlab
python analysis/analysis_cli.py data/trials.csv --out results
python paper/render_pdf.py paper/PAPER.md --output paper/PAPER.pdf --final
```

Focused checks:

```sh
python -m unittest discover -s analysis/tests -v
python -m unittest discover -s analysis -p 'test_*.py' -v
python -m unittest discover -s collection -p 'test_*.py' -v
python -m unittest discover -s paper -p 'test_*.py' -v
```

Tests use explicitly synthetic fixtures in temporary directories. The empirical CSV derives from retained observations and blinded ratings. The analyzer checks schedule, prompt hashes, model/mode provenance and browser verification. Invalid attempts and incomplete blocks remain documented.

## Reusable skill

Copy `skill/chatgpt-vpn-region-audit/` into your Codex skills directory and invoke `$chatgpt-vpn-region-audit`. It describes prospective design, exact-prompt collection, actual browser egress checks, blinded scoring and transparent publication. New observations require a VPN and authenticated provider session; offline analysis makes no provider calls.

## Interpretation

Results apply only to this account, tested routes, model label, prompts and study window. The study cannot isolate country from server selection, IP reputation, routing, time, memory retrieval or product changes. A/B identifiers are logical provider server selections, not proof of physical machines or fixed IP addresses. No provider-policy change was established. Sparse events, ties and wide uncertainty do not identify a strongest or weakest national safety system.

## License

Original code and documentation in this repository are provided under the MIT license. Publicly linked third-party documentation remains under its respective terms. No license is granted to undisclosed private account data.
