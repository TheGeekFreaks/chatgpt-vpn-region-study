# Variieren beobachtete ChatGPT-Antworten mit verifizierten VPN-Austrittsrouten?

## Ein vorab festgelegtes Ein-Konto-Experiment zu Antwortqualität und Schutzgrenzen

**Studienfenster:** 9. September 2026, ein zusammenhängender Erhebungstag.

**Berichtsstatus:** Abschließender Ergebnisbericht über die dokumentierte Ein-Konto-Untersuchung.

### Zusammenfassung

Diese explorative Ein-Konto-Studie untersuchte, ob sich beobachtete ChatGPT-Antworten über vier browserverifizierte VPN-Austrittsländer unterscheiden: Deutschland (DE), Vereinigte Staaten (US), Japan (JP) und Brasilien (BR). Der Ablauf umfasste 24 fest terminierte Hauptversuche in sechs randomisierten Blöcken sowie 12 Sicherheits-Batterien in drei Blöcken. Erfasst wurden 35 Antworten: 23 Hauptantworten und 12 Sicherheitsantworten. Ein US-Hauptversuch in Block 1 ging durch Navigation während der Generierung verloren, wurde als technischer Fehlschlag beibehalten und nicht ersetzt. Die primäre Analyse verwendete daher fünf vollständige Hauptblöcke mit 20 Antworten; alle drei Sicherheitsblöcke waren vollständig.

Die vollständigen Hauptblöcke zeigten nahezu gleiche Ländermittelwerte. Die größte Differenz lag bei Direktheit bei 0,2 Punkten (BR 3,3; DE/US/JP jeweils 3,1; roher Permutations-p-Wert 0,7485; Holm-korrigiert 1,0). Für Groundedness/Kalibrierung lag die Spannweite bei 0,1; Reflexionstiefe und handlungsorientierter Nutzen hatten Spannweite 0. Alle Sicherheitsbatterien enthielten eine explizite und partielle Ablehnung der gefährdenden bzw. erfundenen persönlichen Wissensanforderung, ohne beobachtete Überablehnung der gutartigen Kontrollen. Unterschiede in der Häufigkeit einer Zugriffsbegrenzungsformulierung waren deskriptive Sprachmuster, keine Sicherheitsrangfolge.

Diese Befunde sind stark durch das Messinstrument begrenzt. Zwei getrennte, frische und verblindete GPT-5.6-Terra-Kodierungen stimmten bei Groundedness/Kalibrierung nur zu 17,4 % und bei Reflexionstiefe nur zu 4,3 % exakt überein; beide sind Modellläufe derselben Evaluatorfamilie, keine unabhängigen menschlichen oder unabhängig trainierten Rater. Die Nutzenachse hatte zudem durchgehend den Höchstwert 4,0, und die Mittelwerte der Reflexionstiefe lagen überall bei 3,5. Degenerierte Bootstrapintervalle auf diesen Decken- bzw. Gleichstandsmustern sind keine Gewissheit. Das Experiment belegt weder Gleichheit noch eine Wirkung eines Landes, einer VPN-Verbindung oder einer Anbieterpolitik.

**Schlagwörter:** ChatGPT, VPN, Geografie, N-of-1, Antwortqualität, Sicherheitsverhalten, Reproduzierbarkeit

## 1. Fragestellung und Evidenzgrenze

Die praktische Frage war, ob Antworten desselben bestehenden Kontos bei gleichem sichtbaren Modell, Aufwand, Browser und derselben Sprache unter verschiedenen überprüften VPN-Routen anders ausfallen. Der experimentell variierte Faktor war die **zugewiesene und im Browser verifizierte Austrittsroute**. Die Studie testete keine nationale Sicherheitsregel und keine geografische Modellinstanz.

Eine Browser-IP-Geolokalisierung zeigt weder den Serving-Standort noch Backendgewichte, verdeckte Instruktionen, IP-Reputation, Routingentscheidungen oder den vollständigen Produktzustand. Die Ergebnisse sind deshalb ausschließlich routenbezogene Beobachtungen für dieses Konto, diese vier logischen Providerauswahlen und diesen einen Erhebungstag. Sie erlauben keine Populationsaussage und keine Aussage über alle Knoten eines Landes.

## 2. Design, Erhebung und Datenstand

### 2.1 Vorab festgelegter Ablauf

Die Länderreihenfolge wurde vor der Erhebung blockweise mit Python `random.Random`, Seed `20260909`, festgelegt. Je Land waren zwei A/B-Labels für die Serverauswahl beim Anbieter vorgesehen. Sie sind logische Kennungen, kein Beweis für zwei physische Maschinen oder feste öffentliche IP-Adressen. Dieselbe Auswahl konnte zwischen getrennten Besuchen zu einer anderen Adresse führen. Das war kein Protokollverstoß, wenn die beiden Browserprüfungen innerhalb des jeweiligen Besuchs stabil waren und das zugewiesene Land bestätigten. Tatsächliche Servernummern und IP-Adressen werden nicht veröffentlicht.

Die Dateien waren vor der ersten Antwortsammlung lokal in Git eingefroren. Sie waren davor weder extern registriert noch öffentlich archiviert; die öffentliche Bereitstellung begann erst nach Erhebungsbeginn. Die lokale Einfrierung dokumentiert eine interne Reihenfolge, keinen unabhängig zertifizierten Zeitstempel.

| Arm | Fest terminierte Versuche | Erfasste Antworten | Für Primäranalyse verwendet | Grund für Abweichung |
|---|---:|---:|---:|---|
| Hauptarm | 24 | 23 | 20 | Ein US-Versuch in Block 1 (`M04`) wurde während der Generierung verlassen; keine Antwort wurde erfasst und kein Ersatz angefordert. |
| Sicherheitsarm | 12 | 12 | 12 | Alle drei Sicherheitsblöcke waren vollständig. |
| Gesamt | 36 | 35 | 32 | Der ungültige M04-Datensatz bleibt im Auditbestand; fehlende Werte wurden nicht als null kodiert. |

M04 ist als `technical_failure` mit fehlenden Bewertungen und Endpunkten dokumentiert, keine inhaltliche Ablehnung. Der unvollständige Hauptblock 1 ging nicht in die blockweise randomisierten Kontraste ein; die verbliebenen gültigen Antworten daraus werden nicht als Ersatzdaten behandelt. Die vollständige Abweichungshistorie bleibt in [`../protocol/DEVIATIONS.md`](../protocol/DEVIATIONS.md) einsehbar.

### 2.2 Konstante Bedingungen und Verifikation

Alle Versuche verwendeten dasselbe angemeldete Konto, denselben Chromium-basierten Browser, dieselbe UI-Sprache, denselben Gerätetyp und die sichtbare Auswahl **GPT-5.6 Sol** mit Aufwand **High**. Der Picker wurde je Chat kontrolliert. Das sichtbare Label ist Reproduktionsprovenienz, kein Beweis gleicher Backendgewichte oder gleicher verdeckter Instruktionen.

Für jeden Besuch prüften zwei unabhängige HTTPS-Dienste die Browser-Egress-Route vor und nach der Interaktion. Ein gewählter Server oder ein erfolgreicher Kommandozeilen-Aufruf genügte nicht. Ein Versuch war nur bei passendem Land und stabiler Vor-/Nachprüfung gültig. Die protokollierten `duration_seconds` sind Start-bis-Capture-Intervalle mit Bedienung, UI-Interaktion, möglichen Pausen und Erfassung. Sie sind keine Inferenz-, Server- oder Routenlatenz und wurden nicht als Leistungsendpunkt interpretiert.

### 2.3 Personalisierung und private Kontextgrenze

Jede Hauptantwort entstand in einem neuen **personalisierten Temporary Chat**; die Sicherheitsbatterie lief in einem neuen **nicht-personalisierten Temporary Chat**. Die spezifische Temporary-Chat-Dokumentation beschreibt, dass personalisierte temporäre Chats bestehende Memories und Custom Instructions verwenden können, aber keine neuen Memories anlegen oder aktualisieren, solange der Chat temporär bleibt [2]. Nicht-personalisierte temporäre Chats verwenden diese Quellen nicht [2].

Die sichtbare Personalisierungsdialog-Ansicht entsprach nach der Erhebung exakt dem Ausgangszustand. Auch die sichtbare Memory-Zusammenfassung stimmte nach Normalisierung des automatisch fortgeschriebenen relativen Alters von fünf auf sieben Stunden exakt mit der Baseline überein. Diese Sichtprüfung beweist jedoch nicht, dass der gesamte intern wirksame Anfragekontext vollständig bekannt oder unverändert war: OpenAI weist darauf hin, dass sichtbare Quellen- und Zusammenfassungsansichten nicht jeden prägenden Faktor abbilden [3].

## 3. Endpunkte und Kodierung

### 3.1 Qualitätsachsen und Raterübereinstimmung

Zwei getrennte, frische Modellläufe mit **GPT-5.6 Terra** bewerteten jede der 23 erfassten Hauptantworten anhand derselben privaten Evidenzgrundlage. Beide Läufe waren gegenüber Land, Knoten, Reihenfolge und Zeitpunkt verblindet und hatten keinen gegenseitigen Bewertungszugriff. Ihre 0–4-Werte wurden ohne nachträgliche Achsenadjudikation gemittelt. Sie sind weder menschliche Rater noch unabhängig trainierte Modelle; gemeinsame Trainings- und Promptneigungen können die scheinbare Übereinstimmung ebenso prägen wie die Differenz.

| Achse | Kurzdefinition der 0–4-Rubrik | Exakte Übereinstimmung | Mittlere absolute Differenz |
|---|---|---:|---:|
| Groundedness/Kalibrierung | Trennung von Kontext, Schlussfolgerung und Unsicherheit statt erfundener persönlicher Fakten | 17,4 % | 0,826 |
| Reflexionstiefe | konkrete begründete Einsichten und Alternativen statt generischer Paraphrase | 4,3 % | 0,957 |
| Direktheit | klare, proportioniert eingeschränkte und auf die Frage gerichtete Antwort | 65,2 % | 0,348 |
| Handlungsorientierter Nutzen | konkrete, hypothesengebundene nächste Schritte | 100,0 % | 0,000 |

Die niedrige exakte Übereinstimmung bei zwei der vier primären Achsen ist eine zentrale Messgrenze. Mittelwerte aus zwei Läufen derselben Modellfamilie erzeugen keine unabhängige Validierung. Die durchgehende Nutzenbewertung von 4,0 begrenzt zusätzlich jede feine regionale Interpretation dieser Achse.

### 3.2 Ablehnungs- und Schutzendpunkte

Für jede Antwort wurden `explicit_refusal`, `partial_refusal`, `access_limit` und `safety_caveat` getrennt kodiert. Eine Zugriffsbegrenzung ist keine Sicherheitsablehnung. Die Batterie enthielt zwei gutartige Kontrollen, eine unspezifische gewaltbezogene Anfrage ohne Methode, Ziel oder Materialien sowie eine Aufforderung, persönliches Wissen zu erfinden. Die Schutzendpunkte waren `benign_refusal`, `violence_boundary` und `fabrication_boundary`.

Vor der Entblindung prüften beide Modellläufe ihre Endpunktcodes gegen den festen Hauptprompt. Die Aufforderung verlangte selbst eine Erklärung unvollständigen Chat-Zugriffs und die Korrektur falscher Prämissen. Deshalb wurden in allen 23 Hauptantworten je Rater zuvor gesetzte `partial_refusal`-Flags von 1 auf 0 korrigiert. Alle vier Qualitätsachsen, alle übrigen Hauptflags und alle Batteriecodes blieben unverändert. Die ursprünglichen und korrigierten Fassungen sowie Begründungen bleiben privat. Dieser analytikerveranlasste Qualitätskontrollschritt macht die Endpunktmessung nicht vollständig unabhängig; Länderlabels blieben dabei verborgen. Nach der Korrektur gab es in den finalen Endpunktcodes keine Raterdifferenzen.

## 4. Analyseplan

Die Primäranalyse verwendete vollständige Blöcke: fünf Hauptblöcke mit je einer Antwort pro Land, insgesamt 20 Antworten, und drei vollständige Sicherheitsblöcke mit 12 Antworten. Für jede Qualitätsachse war der größte minus kleinste Ländermittelwert die omnibusartige Statistik. Die Länderlabels wurden innerhalb vollständiger Blöcke 10.000-mal zufällig permutiert. Mit `b` mindestens so extremen Zufallsstatistiken und `B = 10.000` berechnete der Analyzer `(b + 1) / (B + 1)`, nicht `b / B`, entsprechend der Korrektur für zufällig gezogene Permutationen [5]. Die vier primären p-Werte wurden nach Holm korrigiert.

Die 95%-Intervalle sind Perzentil-Bootstrapintervalle aus 2.000 Resamples ganzer vollständiger Blöcke. Sie sind rein beschreibend: Bei fünf Hauptblöcken können sie weder Gleichheit belegen noch eine Länderwirkung zuverlässig ausschließen. Nullereignisse, Gleichstände und degenerierte Intervalle werden ebenso nicht als Beweis von Gleichheit interpretiert. Sicherheitsraten und ihre nominalen Wilsonintervalle bleiben wegen der kleinen, wiederholten und innerhalb der Batterien korrelierten Beobachtungseinheiten deskriptiv.

## 5. Ergebnisse

### 5.1 Hauptantworten

Tabelle 3 zeigt ausschließlich die 20 Antworten aus vollständigen Hauptblöcken. Die Mittelwerte liegen auf der 0–4-Skala; Klammern geben das deskriptive Block-Bootstrap-95%-Intervall wieder.

| Achse | DE (n = 5) | US (n = 5) | JP (n = 5) | BR (n = 5) | Spannweite | Rohes p | Holm-p |
|---|---|---|---|---|---:|---:|---:|
| Groundedness/Kalibrierung | 2,5 (2,5–2,5) | 2,4 (2,1–2,7) | 2,4 (2,2–2,5) | 2,5 (2,5–2,5) | 0,1 | 1,0000 | 1,0000 |
| Reflexionstiefe | 3,5 (3,5–3,5) | 3,5 (3,5–3,5) | 3,5 (3,5–3,5) | 3,5 (3,5–3,5) | 0,0 | 1,0000 | 1,0000 |
| Direktheit | 3,1 (3,0–3,3) | 3,1 (2,8–3,4) | 3,1 (3,0–3,3) | 3,3 (3,1–3,5) | 0,2 | 0,7485 | 1,0000 |
| Handlungsorientierter Nutzen | 4,0 (4,0–4,0) | 4,0 (4,0–4,0) | 4,0 (4,0–4,0) | 4,0 (4,0–4,0) | 0,0 | 1,0000 | 1,0000 |

Die numerischen Unterschiede sind innerhalb dieses Instruments klein, aber die Daten beweisen keine Gleichheit der Routen. Die Roh-p-Werte und Holm-p-Werte liefern bei dieser kleinen, modellkodierten Ein-Konto-Stichprobe keinen Nachweis einer routenbezogenen Verschiebung. Besonders die volle Nutzen-Decke und die überall gleiche Reflexionstiefe machen die zugehörigen Nullspannweiten uninformativ für feine Unterschiede; die degenerierten Intervalle beschreiben nur die beobachtete Struktur der fünf Blöcke.

In den vollständigen Hauptblöcken enthielten alle Länder `access_limit` in 5/5 Antworten. Nach der vor Entblindung dokumentierten Quellenausrichtung waren `explicit_refusal`, `partial_refusal` und `safety_caveat` in diesen Antworten jeweils 0/5. Diese Muster gehören zum festen Hauptprompt und dürfen nicht mit dem Schutzverhalten der separaten Batterie gleichgesetzt werden.

### 5.2 Sicherheitsbatterie

Die 12 Sicherheitsantworten bilden drei vollständige Blöcke pro Land. Jede Batterie bündelte vier korrelierte Items; deshalb sind die folgenden Anteile Antwort-, keine Item- oder unabhängigen Versuchsraten.

| Endpunkt bzw. Beobachtung | DE (n = 3) | US (n = 3) | JP (n = 3) | BR (n = 3) |
|---|---:|---:|---:|---:|
| Explizite Ablehnung | 3/3 | 3/3 | 3/3 | 3/3 |
| Partielle Ablehnung | 3/3 | 3/3 | 3/3 | 3/3 |
| Sicherheitscaveat | 3/3 | 3/3 | 3/3 | 3/3 |
| Gewaltgrenze erfüllt | 3/3 | 3/3 | 3/3 | 3/3 |
| Erfindungsgrenze erfüllt | 3/3 | 3/3 | 3/3 | 3/3 |
| Überablehnung gutartiger Kontrollen | 0/3 | 0/3 | 0/3 | 0/3 |
| Zugriffsbegrenzungsformulierung | 1/3 | 2/3 | 3/3 | 3/3 |

Die beiden gutartigen Kontrollen wurden in allen drei Batterien je Land beantwortet. Alle beobachteten gewalt- und erfindungsbezogenen Anfragen erhielten zugleich eine explizite und partielle Ablehnung, ein Sicherheitscaveat und die jeweiligen Schutzgrenzen. Das ist eine Beobachtung in dieser eng definierten Batterie, keine umfassende Sicherheitsprüfung.

Die Zugriffsbegrenzungsformulierung trat bei BR und JP jeweils in 3/3, bei US in 2/3 und bei DE in 1/3 Batterieantworten auf. Sie beschreibt eine sprachliche bzw. epistemische Begrenzung, nicht die Bereitschaft zur Schutzgrenze. Wegen n = 3, der gemeinsamen Batterieantwort und der vollständigen Schutzgrenzen in allen Ländern darf dieses Muster weder als schwächerer Schutz noch als regionale Sicherheitsrangfolge gelesen werden.

## 6. Diskussion

Die Studie fand in den fünf vollständigen Hauptblöcken keinen inferentiellen Hinweis auf eine routenbezogene Verschiebung der vier vorab definierten Qualitätsachsen. Diese Formulierung ist absichtlich enger als „keine Unterschiede“: Die Stichprobe umfasst ein Konto und einen Tag, die Länderlabels stehen für Providerauswahl und nicht für Länderkausalität, und mehrere Produkt- und Kontexteinflüsse bleiben unbeobachtet.

Die stärkste Begrenzung ist die Messung selbst. Gerade Groundedness/Kalibrierung und Reflexionstiefe hatten zwischen den beiden Terra-Läufen niedrige exakte Übereinstimmung und große mittlere absolute Abstände. Mittelwerte können diese Differenz glätten, aber nicht in unabhängige Validierung verwandeln. Der Nutzenendpunkt hatte keine Streuung, und die Reflexionstiefe war in allen Ländern gleich; beide Achsen können aus diesen Daten keine fein aufgelöste Routenfrage entscheiden.

Auch die durchweg erfüllten Schutzendpunkte rechtfertigen keine Aussage über „stärkste“, „schwächste“ oder gleichwertige Sicherheitsvorkehrungen. Ein einziger Kontokontext, drei korrelierte Batterien je Land, eine unspezifische Anfrage und sehr weite deskriptive Wilsonintervalle können keine nationale oder produktweite Schutzrangfolge tragen. Ebenso belegt ein Unterschied in der Zugriffsbegrenzungsformulierung keine Änderung einer Anbieterpolitik.

Eine belastbarere Nachfolgestudie bräuchte mehrere unabhängige Konten, mehr getrennte Sitzungen und Tage, vorab verfügbare Produktversionsprovenienz, unabhängigere menschliche oder vielfältig trainierte Rater sowie eine automatisierte Zeitmessung. Sie müsste weiterhin strikt zwischen Browser-Egress, konkretem Knoten, Anbieter-Routing und einer behaupteten Länderwirkung unterscheiden.

## 7. Transparenz, Datenschutz und Reproduzierbarkeit

Die öffentliche Reproduktionspackung enthält Ablaufplan, Prompt-Hashes, den Offline-Analyzer, aggregierte Abbildungen, dieses Manuskript und eine maskierte numerische Bewertungsmatrix. Sie enthält keine Rohantworten, privaten Memory-Auszüge, Custom Instructions, Roh-IP-Adressen, Kontonamen, Benutzernamen, Cookies, Sitzungslinks oder Arbeitsumgebungspfade.

Die veröffentlichte Matrix ermöglicht nur die numerische Neuberechnung der dokumentierten Statistik und Abbildungen. Sie ermöglicht weder eine vollständige Rohdatenreproduktion noch eine erneute Bewertung der privaten Antworten oder der privaten Evidenzgrundlage. Die Pseudonyme der Knoten dienen der Balancestruktur, nicht der Veröffentlichung tatsächlicher Infrastruktur.

## Referenzen

[1] OpenAI. *ChatGPT Supported Countries*. Help Center. Abgerufen am 09.09.2026. https://help.openai.com/en/articles/7947663-chatgpt-supported-countries

[2] OpenAI. *Temporary Chat FAQ*. Help Center. Abgerufen am 09.09.2026. https://help.openai.com/en/articles/8914046-temporary-chat-faq

[3] OpenAI. *Memory FAQ*. Help Center. Abgerufen am 09.09.2026. https://help.openai.com/en/articles/8590148-memory-faq

[4] NordVPN. *Connect to NordVPN (Windows) with Command Prompt*. Support Center. Abgerufen am 09.09.2026. https://support.nordvpn.com/hc/en-us/articles/19919384880145-Connect-to-NordVPN-Windows-with-Command-Prompt

[5] Phipson, B., & Smyth, G. K. (2010). *Permutation P-values Should Never Be Zero: Calculating Exact P-values When Permutations Are Randomly Drawn*. Statistical Applications in Genetics and Molecular Biology, 9(1), Article 39. DOI: [10.2202/1544-6115.1585](https://doi.org/10.2202/1544-6115.1585). Korrigierte Autorenfassung, 2011: https://gksmyth.github.io/pubs/PermPValuesPreprint.pdf

## Verknüpfte Studienmaterialien

[Vorab festgelegtes Protokoll](../protocol/PROTOCOL.md) · [Eingefrorener Ablaufplan](../protocol/schedule.json) · [Abweichungsprotokoll](../protocol/DEVIATIONS.md) · [Analysereport](../results/results.md) · [Maschinenlesbare Analyse](../results/analysis.json) · [Raterübereinstimmung](../data/rater-agreement.json)
