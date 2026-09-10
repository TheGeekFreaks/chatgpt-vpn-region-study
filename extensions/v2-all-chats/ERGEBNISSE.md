# VPN-Ländervergleich: Ergebnis der 24 regulären ChatGPT-Tests

Stand: 10. September 2026. Diese Auswertung betrifft ausschließlich die zweite Testreihe mit normalen Chats und 6 Pro.

**Es gibt in dieser Stichprobe keinen statistisch belastbaren Länderunterschied. Alle 24 geplanten Antworten liegen vor; zusätzliche Länder wurden deshalb nicht getestet. Eine vollständige oder teilweise Verweigerung trat in keinem der 24 Tests auf.**

Getestet wurden Deutschland, USA, Japan und Brasilien mit je sechs Wiederholungen. Jeder Test verwendete denselben deutschen Prompt, der die Informationen aus allen bisherigen Chats ansprechen soll und exakt mit **„du kannst das“** endet. VPN war eingeschaltet; die Route wurde im tatsächlichen Browser vor und nach jedem Versuch geprüft. Es wurden normale Chats mit aktivierter Erinnerung verwendet. Die sichtbare Modellwahl war 6 Pro, der ausgelesene Modellbezeichner der Antworten `gpt-6-pro`.

## Die vier Qualitätsachsen

Zwei voneinander getrennte, gegenüber dem Land verblindete Terra-Bewerter vergaben jeweils ganze Punkte von 0 bis 4. Die folgende Tabelle zeigt den Mittelwert beider Bewertungen über die sechs Antworten je Land. „Belegtreue und Kalibrierung“ bewertet den Umgang mit Beobachtungen, Schlussfolgerungen und Unsicherheit; die Werte bestätigen keine privaten Tatsachen über die Person.

| VPN-Land | Belegtreue und Kalibrierung | Reflexionstiefe | Direktheit | Praktischer Nutzen |
|---|---:|---:|---:|---:|
| Deutschland | 2,00 | 3,83 | 3,75 | 4,00 |
| USA | 2,25 | 3,83 | 3,75 | 4,00 |
| Japan | 2,58 | 3,92 | 3,75 | 4,00 |
| Brasilien | 2,17 | 3,75 | 3,75 | 4,00 |

Japan hat deskriptiv den höchsten Wert bei Belegtreue und Kalibrierung. Der globale Ländervergleich ergibt dafür p = 0,07999; nach der Holm-Korrektur für die vier Qualitätsachsen beträgt p = **0,31997**. Die anderen korrigierten p-Werte sind 1,00. Kein Vergleich unterschreitet die vorher festgelegte Schwelle von 0,05. Die Unterschiede reichen damit nicht aus, einen verlässlichen Vorteil eines Landes zu behaupten.

![Qualität nach Land mit deskriptiven Unsicherheitsintervallen](results/main_axis_means.png)

## Refusal und Sicherheit

| VPN-Land | Vollständige Verweigerung | Teilweise Verweigerung | Hinweis auf begrenzten Informationszugriff | Sicherheitshinweis innerhalb einer Antwort |
|---|---:|---:|---:|---:|
| Deutschland | 0/6 | 0/6 | 2/6 | 0/6 |
| USA | 0/6 | 0/6 | 3/6 | 0/6 |
| Japan | 0/6 | 0/6 | 3/6 | 2/6 |
| Brasilien | 0/6 | 0/6 | 3/6 | 0/6 |

Ein Hinweis wie fehlender vollständiger Informationszugriff ist für sich genommen keine Verweigerung. Ebenso ist eine Vorsichtsmaßnahme innerhalb einer ausgeführten Analyse ein anderer Befund als die Ablehnung der Aufgabe. Die vier entsprechenden Ländervergleiche wurden getrennt von den Qualitätsachsen korrigiert; alle korrigierten p-Werte sind 1,00. Für die zwei Sicherheitshinweise in Japan beträgt der unkorrigierte p-Wert 0,25117.

**Ein Land mit den stärksten oder schwächsten allgemeinen Schutzregeln lässt sich daraus nicht bestimmen.** Der hier verwendete persönliche Reflexionsprompt prüft keine umfassende Sammlung gefährlicher Anfragen. Null beobachtete Verweigerungen bedeuten außerdem nicht, dass die tatsächliche Verweigerungswahrscheinlichkeit exakt null ist. Die separate Sicherheitsbatterie aus der ersten Testreihe gehört zu einem anderen Modell und Chatmodus und wird nicht mit diesen Daten vermischt.

![Verweigerungen, Zugriffsgrenzen und Sicherheitshinweise](results/main_primary_endpoint_rates.png)

## Was auffälliger war als der Länderunterschied

Die Hinweise auf begrenzten Informationszugriff änderten sich im Verlauf: In den ersten zwölf Antworten wurden sie 0-mal, in den letzten zwölf Antworten 11-mal codiert. Auch die gemessene Zeit vom Absenden bis zur Erfassung stieg deutlich. Diese Zeit enthält manuelle Warte- und Erfassungsanteile und ist keine Messung der reinen Serverlatenz. Die Beobachtung lässt sich keinem bestimmten Land zuordnen und beweist weder einen Modellwechsel noch eine regionale Anbieterregel.

Die Testreihe wurde nach dem ersten Versuch über Nacht unterbrochen. Bei der Fortsetzung gab es Unsicherheit über Profilanzeige und wirksamen Kontext. Der erste Testchat blieb entgegen dem vorgesehenen Ablauf bis nach Test 14 im Verlauf und wurde erst dann nach erneuter Archivprüfung gelöscht. Das kann spätere Erinnerungs- oder Kontextabrufe beeinflusst haben. Die übrigen Testchats wurden nach privater Sicherung jeweils gezielt gelöscht. Die Löschung eines Chats garantiert nicht, dass bereits daraus gebildete Erinnerungen verschwinden. Siehe die [OpenAI Memory FAQ](https://help.openai.com/en/articles/8590148-memory-faq).

Die [zusätzliche Auswertung ohne den unterbrochenen ersten Block](derived/README.md) umfasst 20 Antworten und ergibt ebenfalls keinen belastbaren Länderunterschied: Alle korrigierten Qualitäts-p-Werte sind 1,00, der kleinste korrigierte Endpunkt-p-Wert ist 0,98150. Auch dieser Ausschluss beseitigt den möglichen Einfluss des länger erhaltenen ersten Chats nicht. Die ersten 14 Bewertungen aus der Zwischenanalyse wurden unverändert übernommen; nur die letzten zehn Antworten wurden neu bewertet. Meinungsverschiedenheiten bei den binären Merkmalen wurden verblindet entschieden.

Bei vier Versuchen erschien vorübergehend eine technische Meldung über zu viele Anfragen. Alle vier ursprünglichen Antworten wurden anschließend vollständig erfasst, ohne den Prompt erneut abzusenden. Diese Meldungen wurden als technische Ereignisse dokumentiert und nicht als Modellverweigerung gezählt.

Sechs Antworten je Land, die geringe Streuung einiger Punktwerte und zwei Bewerter aus derselben Modellfamilie begrenzen die Aussagekraft. Insbesondere der durchgängige Höchstwert beim praktischen Nutzen zeigt die geringe Trennschärfe dieser Skala in der vorliegenden Stichprobe. Nichtsignifikanz ist kein Nachweis, dass alle Regionen gleich reagieren.

## Modellvergleich und Abschluss

Nach der Auswahl „6 Pro nehmen“ wurde die reguläre ChatGPT-Testreihe mit 6 Pro durchgeführt. OpenAI beschreibt dieses Angebot als von Astra betrieben; Terra steht laut der überprüften Dokumentation nicht als auswählbares Modell in normalen ChatGPT-Chats bereit. Deshalb liegt hier **kein experimenteller Astra-gegen-Terra-Vergleich** vor. Terra diente ausschließlich zur Bewertung der gespeicherten Antworten. Die Modellbezeichnung in der Oberfläche legt die verborgene Infrastruktur oder den tatsächlich abgerufenen Kontext nicht offen. Quelle: [OpenAI zu GPT-5.6 und GPT-6 Pro in ChatGPT](https://help.openai.com/en/articles/20001354-gpt-5-6-in-chatgpt).

Alle 24 Testantworten sind privat gesichert, alle genau zugeordneten Testchats inzwischen gelöscht und die VPN- sowie profilspezifischen Einstellungen auf den Zustand vor der Fortsetzung zurückgestellt. Der wiederverwendbare [Skill](../../skill/chatgpt-vpn-region-audit/SKILL.md) ist aktualisiert und lokal installiert. Persönliche Antworttexte, Kontodaten und IP-Adressen sind nicht Bestandteil des öffentlichen Repositories.

- [Wissenschaftliches Paper als PDF](paper/PAPER.pdf)
- [Manuskript mit Methodik und Grenzen](paper/PAPER.md)
- [Vollständige statistische Auswertung](results/results.md)
- [Numerische Daten zum Nachrechnen](data/trials.csv)
- [Erhaltene Zwischenanalyse](interim/INTERIM.md)
- [Dokumentierte Abweichungen vom Ablauf](protocol/DEVIATIONS.md)
- [GitHub-Repository](https://github.com/TheGeekFreaks/chatgpt-vpn-region-study)
