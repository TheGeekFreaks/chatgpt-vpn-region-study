# Quellenverzeichnis zum Manuskript

Stand der Prüfung: 09.09.2026. Diese Liste enthält nur die primären, öffentlichen Quellen, auf die sich das Methodenmanuskript stützt. Sie ist keine Quelle für empirische Studienergebnisse.

| Nr. | Quelle | Verwendung im Manuskript | Stabilitätsgrenze |
|---|---|---|---|
| 1 | OpenAI, [*ChatGPT Supported Countries*](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries) | Belegt, dass DE, US, JP und BR in der zum Prüfzeitpunkt veröffentlichten Liste stehen. | Die Liste ist dynamisch; sie belegt weder tatsächliche Behandlung noch Serving-Standort. |
| 2 | OpenAI, [*Temporary Chat FAQ*](https://help.openai.com/en/articles/8914046-temporary-chat-faq) | Belegt die aktuelle Unterscheidung zwischen personalisierten und nicht-personalisierten Temporary Chats sowie die Aussagen zu Verlauf und Memory-Aktualisierung. | Produkt- und Hilfedokumentation kann sich ändern; UI-Zustand wurde zusätzlich pro Durchführung beobachtet. |
| 3 | OpenAI, [*Memory FAQ*](https://help.openai.com/en/articles/8590148-memory-faq) | Belegt, dass sichtbare Memory-Zusammenfassungen und Quellenansichten nicht alle einwirkenden Faktoren abbilden müssen. | Keine vollständige Offenlegung interner Kontextverarbeitung. |
| 4 | NordVPN, [*Connect to NordVPN (Windows) with Command Prompt*](https://support.nordvpn.com/hc/en-us/articles/19919384880145-Connect-to-NordVPN-Windows-with-Command-Prompt) | Belegt die dokumentierte Möglichkeit, nach Ländergruppe oder Servername zu verbinden. | Eine erfolgreiche Verbindung beweist allein keinen Browser-Egress; deshalb verlangt das Protokoll zwei Browserprüfungen vor und nach jedem Besuch. |
| 5 | Phipson, B. & Smyth, G. K. (2010), [*Permutation P-values Should Never Be Zero*](https://doi.org/10.2202/1544-6115.1585); [korrigierte Autorenfassung, 2011](https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf) | Begründet für zufällig gezogene Permutationen den diskreten p-Wert `(b + 1) / (B + 1)` anstelle von `b / B`. | Die Quelle begründet die Monte-Carlo-p-Wertberechnung; sie erweitert weder die kleine Stichprobe noch die kausale Reichweite dieser Studie. |

## Quellenhierarchie für die Durchführung

Die spezifische aktuelle Temporary-Chat-FAQ [2] hat für die Personalisierungsentscheidung Vorrang vor älteren, allgemeiner formulierten Aussagen in der Memory-FAQ [3]. Sie wird durch den beobachteten, pro Chat gewählten UI-Modus abgesichert. Diese Hierarchie löst keine unzugänglichen Systemzustände auf: Sie dokumentiert nur, welche öffentlich beschriebene Produktsemantik und welche sichtbare Einstellung im Protokoll verwendet wurden.

Die Analysequelle [5] wird eng verwendet: Der Offline-Analyzer zählt Zufallsstatistiken, die mindestens so extrem wie die beobachtete sind, und berechnet daraus `(b + 1) / (B + 1)`. Sie ist keine Rechtfertigung, die Ergebnisse als Länderwirkung oder als präzise Sicherheitsrangfolge zu deuten.

Die interne methodische Primärquelle ist das vor der Antwortsammlung eingefrorene [Protokoll](../protocol/PROTOCOL.md), ergänzt durch den [Ablaufplan](../protocol/schedule.json) und das [Abweichungsprotokoll](../protocol/DEVIATIONS.md). Diese Dateien legen Design und Auditgrenze fest; sie sind keine externe Evidenz für eine Wirkung.
