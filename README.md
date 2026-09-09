# ChatGPT VPN Region Study

An exploratory, single-account study of response quality and boundary behavior across verified VPN exit countries. The central question is whether observed ChatGPT answers vary with the tested network route while prompt, visible model, effort and personalization are held fixed.

**Collection in progress. No final regional effect or safety ranking is claimed here.**

The main experiment uses the same German personal-history introspection prompt in 24 personalized temporary chats: Germany, United States, Japan and Brazil, six randomized sequential blocks. A separate fixed four-item battery is planned in 12 non-personalized temporary chats. It combines benign controls with a nonspecific violent-intent probe and a request to fabricate personal knowledge. Battery items are not treated as independent response trials.

Four model-rated quality axes are specified in advance: groundedness/calibration, reflective depth, directness and actionable usefulness. Refusals, epistemic access limits, benign over-refusal and protective boundaries are separate endpoints. Low refusal on a benign question does not mean weak safety. One prompt, one account and a short window cannot establish a country's general safety policy.

## Reproducibility package

- [Prospectively specified protocol](protocol/PROTOCOL.md)
- [Frozen randomized schedule and prompt hashes](protocol/schedule.json)
- [Main prompt](protocol/prompts/main.de.txt) and [boundary battery](protocol/prompts/safety.de.txt)
- [Acquisition notes and deviations](protocol/DEVIATIONS.md)
- [Offline analysis CLI](analysis/README.md)
- [Reusable Codex skill](skill/chatgpt-vpn-region-audit/SKILL.md)

The protocol was committed locally before response collection (`2fe04a2903725d1aa357a70f5090d841778cd294`). This is not an externally registered or independently timestamp-certified preregistration. Original responses, custom instructions, memory summaries, IP addresses and account/session identifiers stay outside the public repository. Only anonymized ratings, aggregate results and non-sensitive methods are intended for publication.

## Technical evidence boundary

VPN egress is verified in the actual browser before and after each route visit with two separate services. A terminal IP, a selected VPN country or a CLI success does not prove the ChatGPT browser route. Preflight found that the browser's friendly provider label was Chrome while its actual process was Thorium, which was excluded by NordVPN split tunneling. The exception was temporarily disabled and browser egress reverified before any prompt was submitted.

The visible model is GPT-5.6 Sol with High effort. The interface resets model choice on navigation, so the picker is checked for each chat. A visible label does not reveal backend weights, hidden system instructions or the provider's serving region. Personalized Temporary Chat behavior is checked against the actual UI and the [current dedicated OpenAI FAQ](https://help.openai.com/en/articles/8914046-temporary-chat-faq).

## Run the offline checks

Python 3.10+ is required. The numerical core uses the standard library; matplotlib is optional for figures.

```sh
python -m unittest discover -s analysis/tests -v
python analysis/analysis_cli.py data/trials.csv --out results
```

The empirical CSV will be added after collection and masked coding. Tests use explicitly synthetic fixtures inside temporary directories; synthetic values must never be presented as study observations. The analyzer checks the frozen schedule, both prompt hashes, model/mode provenance and browser verification. Invalid/incomplete blocks remain documented and are excluded from randomized contrasts.

## Interpretation

Results apply only to this account, the tested routes, model label and study window. The study cannot isolate country from exit-node effects, IP reputation, network routing, time, memory synthesis or product changes. Observed country extrema are exploratory descriptions. Sparse or zero events, ties and wide uncertainty do not identify a strongest or weakest national safety system.

## License

Original code and documentation in this repository are provided under the MIT license. Publicly linked third-party documentation remains under its respective terms. No license is granted to undisclosed private account data.
