# Codex Astra: VPN-Region, Sprache und verfügbarer Kontext

**Abgeschlossener Pilot: zehn Antworten, fünf VPN-Routen, zwei unabhängige modellgestützte Bewertungen.** Die definierten Kennwerte zeigen weder zwischen den deutschen Länderantworten noch innerhalb der Sprachpaare einen Unterschied. Das ist kein Gleichheitsnachweis: Memory-Fragen lagen am unteren, die übrigen strukturierten Aufgaben nahe am oberen Ende der Skalen.

| Befund | Beobachtung |
|---|---|
| Korrekt beantwortete historische Kernfragen | 0 von 8 in jeder Antwort; überwiegend ausdrücklich benannte Informationslücken |
| H/G-Bearbeitungsqualität | Bewerter A immer 3,667/4, Bewerter B immer 4/4; Mittel 3,833/4 |
| Nichtgrafische Erwachsenenthemen N1–N4 | Alle vier in jeder der zehn Antworten vollständig bearbeitet |
| Verweigerungen bei Gegenposition G und N1–N4 | Keine der beiden Bewertungen codierte eine Teil- oder Vollverweigerung |
| Deutsch–Landessprache-Differenzen | Alle vier vorab definierten numerischen Differenzen gleich 0 |
| Beobachtete Memory-Zusammenfassung | Neun erhaltene Prüfsummen identisch; beim ersten Lauf fehlt diese Prüfung |
| Laufzeit pro Modellantwort | Median 74,966 Sekunden; Bereich 67,042–98,280 Sekunden |

Die letzte Zeile erfasst die Modellantwort und nicht den gesamten Bedien-, VPN- oder Auswertungsaufwand. Ein Geschwindigkeitsvorteil gegenüber ChatGPT Web wurde nicht kontrolliert getestet.

## Was sich sprachlich unterschied

Die deutschsprachige Antwort über Bulgarien bezeichnete die Grenze für explizite sexuelle Fiktion als **Begrenzung**; die bulgarische Antwort und die anderen acht Antworten als **Ablehnung**. Beide Bewerter codierten diesen Unterschied. Es handelt sich um eine Selbstauskunft: Keine explizite Szene wurde erzeugt oder angefordert. Daraus folgt keine unterschiedliche tatsächliche NSFW-Freigabe.

Die inhaltlichen Stilcodes blieben innerhalb der Paare gleich. Die Bewerter markierten jedoch ihre sprachliche Unsicherheit für Bulgarisch, Japanisch und Portugiesisch. Dieser Unsicherheitsmarker beschreibt die Bewertung, nicht ein verändertes Antwortverhalten. Außerdem unterschieden sich die beiden Bewerter systematisch bei der Interpretation des H-Tons und des G-Kriteriums zum prüfbaren nächsten Schritt; diese Einzelabweichungen stehen ausdrücklich neben den aggregierten Übereinstimmungswerten.

## Versuchsaufbau

Getestet wurde eine eigene Codex-Bedingung: frische, regulär gespeicherte lokale Aufgaben, GPT-6 Astra mit festem Denkaufwand high, dasselbe laufende Desktop-Konto, kein Fork und keine Werkzeuge im Test. Die Modell- und Aufwandangaben wurden je Aufgabe in den tatsächlichen Metadaten geprüft. Der deutsche Prompt endete exakt mit „du kannst das“; die anderen Fassungen enthielten die bedeutungsgleiche übersetzte Ermutigung.

| Route | Erste Antwort | Zweite Antwort |
|---|---|---|
| Bulgarien | Deutsch | Bulgarisch |
| Deutschland | Deutsch | Deutsch |
| Japan | Deutsch | Japanisch |
| Brasilien | Brasilianisches Portugiesisch | Deutsch |
| USA | US-Englisch | Deutsch |

Zwei unabhängige Länderprüfungen sowie die lokalen Codex-Verbindungen und Tunnelrouten wurden vor und nach den Antworten kontrolliert. Jede vollständige Originalantwort wurde privat gespeichert und gehasht, anschließend wurde genau die zugehörige Testaufgabe gelöscht. Alle zehn Löschungen wurden überprüft. Zum Abschluss wurde die ursprüngliche deutsche VPN-Verbindung wiederhergestellt.

Die Memory-Fragen verlangen acht bestimmte historische Details. Die automatische Zusammenfassung enthielt dagegen allgemeineren persönlichen Kontext, den die Antworten für ihre Reflexionen nutzten. **0/8 bedeutet daher weder „kein Gedächtnis“ noch acht falsche Antworten.** Der Test konnte zwischen fehlender Detailgrundlage und zusätzlichem unsichtbarem Abruf nur begrenzt unterscheiden.

## Interpretation und weitere Tests

Dieser Pilot liefert keinen Anlass, weitere Länder hinzuzunehmen, um dort eine vermeintlich größere Freiheit zu suchen. Er rechtfertigt weder eine allgemeine Länder-Rangliste noch Aussagen über nationale Gesetze, die interne Modellregion oder den Zugriff auf alle Chats. Ein Astra–Terra-Vergleich wurde in dieser Serie nicht durchgeführt.

Vor einer Replikation sollte die Messung empfindlicher werden: kontrolliert vorhandene Memory-Details als positive Kontrollen, getrennte Bedingungen für automatisch bereitgestellten Kontext und erlaubten Abruf, sowie weniger schematisch vorgegebene Reflexionsaufgaben. Solche Änderungen wären eine neue vorab festgelegte Version. Die jetzigen Antworten werden dafür nicht nachträglich ersetzt.

## Dateien und Reproduktion

- [Wissenschaftlicher Bericht](PAPER.md) und [PDF](PAPER.pdf)
- [Beobachtete Erhebung und Wiederherstellung](collection-summary.json)
- [Anonymisierte codierte Bewertungen](data/ratings.json)
- [Auswertungsprogramm](analysis.py) und [Eingabeschema](ratings-schema.json)
- [Berechnete Ergebnisse und Bildunterschriften](derived/analysis.json)
- [Länderkennwerte](derived/german-country-values.png), [Sprachdifferenzen](derived/paired-language-deltas.png), [Bewerterübereinstimmung](derived/rater-agreement.png)
- [Kategoriale Übergänge](derived/paired-category-transition-summary.csv) und [Einzelvariablen der Übereinstimmung](derived/rater-agreement.csv)
- [Vorab-Protokoll](PROTOKOLL.md), [unveränderte Bewertungsregeln](BEWERTUNG.md), [eingefrorener Ablauf](schedule.json), [Prompt-Prüfsummen](prompt-manifest.json)

Die letzten vier Dateien sind **unveränderte Vorabfassungen**. Ihre damaligen Vorbereitungs-Statusangaben sind keine aktuellen Erhebungsstände; maßgeblich ist collection-summary.json.

Geprüft mit Python 3.11.1; die verwendeten Bibliotheksversionen sind in requirements.txt festgehalten:

```text
python -m pip install -r requirements.txt
python analysis.py data/ratings.json --output-dir derived
python render_paper.py PAPER.md --output PAPER.pdf
```

Der Bericht nennt Abweichungen und Qualitätskontrollen, einschließlich eines vor dem Entschlüsseln der Länderzuordnung korrigierten Lesefehlers eines Bewerters. Die ursprüngliche Bewertung und ihre Korrektur bleiben privat erhalten. Rohantworten, historische Fragen, Lösungsschlüssel, Kontodaten, IP-Adressen und Task-IDs werden nicht veröffentlicht. Die öffentlichen Daten reproduzieren die Berechnung; eine unabhängige semantische Neubewertung der privaten Originale ist damit nicht möglich.

Die frühere ChatGPT-Web-Serie bleibt eine getrennte Produkt- und Protokollbedingung. Ihre Ergebnisse werden mit diesem Pilot nicht zu einer gemeinsamen Länderstatistik vermischt.
