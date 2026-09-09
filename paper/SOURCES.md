# Quellenverzeichnis zum Manuskript

Stand der Prüfung: 09.09.2026. Diese Liste enthält nur die primären, öffentlichen Quellen, auf die sich das Methodenmanuskript stützt. Sie ist keine Quelle für empirische Studienergebnisse.

| Nr. | Quelle | Verwendung im Manuskript | Stabilitätsgrenze |
|---|---|---|---|
| 1 | OpenAI, [*ChatGPT Supported Countries*](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries) | Belegt, dass DE, US, JP und BR in der zum Prüfzeitpunkt veröffentlichten Liste stehen. | Die Liste ist dynamisch; sie belegt weder tatsächliche Behandlung noch Serving-Standort. |
| 2 | OpenAI, [*Temporary Chat FAQ*](https://help.openai.com/en/articles/8914046-temporary-chat-faq) | Belegt die aktuelle Unterscheidung zwischen personalisierten und nicht-personalisierten Temporary Chats sowie die Aussagen zu Verlauf und Memory-Aktualisierung. | Produkt- und Hilfedokumentation kann sich ändern; UI-Zustand wurde zusätzlich pro Durchführung beobachtet. |
| 3 | OpenAI, [*Memory FAQ*](https://help.openai.com/en/articles/8590148-memory-faq) | Belegt, dass sichtbare Memory-Zusammenfassungen und Quellenansichten nicht alle einwirkenden Faktoren abbilden müssen. | Keine vollständige Offenlegung interner Kontextverarbeitung. |
| 4 | NordVPN, [*Connect to NordVPN (Windows) with Command Prompt*](https://support.nordvpn.com/hc/en-us/articles/19919384880145-Connect-to-NordVPN-Windows-with-Command-Prompt) | Belegt die dokumentierte Möglichkeit, nach Ländergruppe oder Servername zu verbinden. | Eine erfolgreiche Verbindung beweist allein keinen Browser-Egress; deshalb verlangt das Protokoll zwei Browserprüfungen vor und nach jedem Besuch. |

## Quellenhierarchie für die Durchführung

Die spezifische aktuelle Temporary-Chat-FAQ [2] hat für die Personalisierungsentscheidung Vorrang vor älteren, allgemeiner formulierten Aussagen in der Memory-FAQ [3]. Sie wird durch den beobachteten, pro Chat gewählten UI-Modus abgesichert. Diese Hierarchie löst keine unzugänglichen Systemzustände auf: Sie dokumentiert nur, welche öffentlich beschriebene Produktsemantik und welche sichtbare Einstellung im Protokoll verwendet wurden.

Die interne methodische Primärquelle ist das vor der Antwortsammlung eingefrorene [Protokoll](../protocol/PROTOCOL.md), ergänzt durch den [Ablaufplan](../protocol/schedule.json) und das [Abweichungsprotokoll](../protocol/DEVIATIONS.md). Diese Dateien legen Design und Auditgrenze fest; sie sind keine externe Evidenz für eine Wirkung.
