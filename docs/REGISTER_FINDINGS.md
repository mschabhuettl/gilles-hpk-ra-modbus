# Anonymisierte Registerbefunde

> 🇩🇪 **Deutsch** · [🇬🇧 English](REGISTER_FINDINGS.en.md)

Eine erweiterte passive Auswertung korrigiert mehrere frühere Registerdeutungen. Diese öffentliche Zusammenfassung enthält ausschließlich verallgemeinerte technische Befunde. Rohbeobachtungen bleiben privat; Messreihen, Screenshots, konkrete Betriebszeitpunkte, Laufzeiten und anlagenspezifische Messwerte werden nicht veröffentlicht. Die Zusammenfassung allein erlaubt daher keine unabhängige Nachrechnung der beobachteten Zusammenhänge.

## REG56: berechneter O₂-Sollwert als starke Hypothese

REG56 ist im Regelbetrieb anhaltend aktiv und folgt einer abgastemperaturabhängigen Beziehung. Die frühere Beschreibung als bloßer kurzer Impuls ist überholt. Die Übereinstimmung mit einer linearen Interpolation zwischen den konfigurierten Temperatur- und O₂-Endpunkten zeigt sich auch in einem weiteren natürlichen Brennlauf. Damit ist die Beziehung qualitativ wiederholt beobachtet, aber noch nicht am Touch bestätigt:

```text
T       = REG50 × 0,1              # Abgastemperatur Ist
T_low   = REG36 × 0,1              # sAbgasTempSollMin
T_high  = REG38 × 0,1              # sAbgasTempMax
O_low   = REG16 × 0,1              # sO2Min: O₂ am unteren Temperatur-Endpunkt
O_high  = REG14 × 0,1              # sO2Max: O₂ am oberen Temperatur-Endpunkt

O2_target_candidate = O_low + (T − T_low) × (O_high − O_low) / (T_high − T_low)
REG56 × 0,1 ≈ O2_target_candidate
```

Voraussetzung ist `T_high ≠ T_low`. Die Namen `sO2Min` und `sO2Max` beschreiben hier die Parameterzuordnung; sie garantieren keine numerische Reihenfolge der O₂-Werte. Begrenzungen außerhalb des beobachteten Regelbereichs, andere Parameterkombinationen und das Verhalten in anderen Phasen sind ungeklärt. Die Formel ist ein Prüfmodell, keine verifizierte Steuerungslogik.

Vertrauen: **starke Hypothese (✓)**. Eine weitere Touch-Seite zeigt „Restsauerstoff“ mit getrennten Spalten „Ist“ und „Soll“. Im verglichenen ruhenden Zustand sind der dortige Sollwert und REG56 null. Damit ist eine passende Vergleichsanzeige gefunden; die Gleichheit bei null bestätigt weder die Registerfunktion noch die Skalierung. Zur Bestätigung fehlt der gleichzeitige Abgleich bei einem Nichtnull-Sollwert im Regelbetrieb. Die Übersichtsseite mit „O2 Wert“ zeigt dagegen den Istwert. Es wird daraus weder eine Regelung noch ein bestätigter Sollwertsensor abgeleitet.

## Weitere Register

| Register | Qualitative Beobachtung | Folgerung und offene Frage |
|---|---|---|
| REG42 | Code 10 wurde im Abschaltpfad zwischen Code 9 und Standby 0 beobachtet. Im zugehörigen aufgezeichneten Pfad erschien Code 8 nicht. | Code 10 ist ein beobachteter Zykluszustand mit unbekannter Bedeutung; kein Flammennachweis. Ein sehr kurzer Schritt kann zwischen Abfragen fehlen, daher ist das Ausbleiben von Code 8 in der Aufzeichnung kein Nachweis seines physischen Ausbleibens. |
| REG46 | Code 61 ist vorläufig mit „Puffertemperatur erreicht“ am Touch verbunden. Der zusätzlich beobachtete Code 43 beginnt im Abschaltverlauf und reicht bis in den Standby; der Kessel-Sollwert fällt erst später. | Die zugehörige Touch-Meldung für Code 43 fehlt. Weder Fehler, Übertemperatur, Pufferzustand noch „Kessel-Soll null“ sind belegt. Code 43 wird neutral als Rohcode gezeigt; die Türstellung bleibt dabei unbekannt. Für Code 61 fehlt weiterhin der exakt synchronisierte Vergleich über einen Meldungswechsel; Enum oder Bitfeld bleibt offen. |
| REG58 / REG62 | Die bisherige HA-Skalierung passt nicht eindeutig zu historischen Touch-Zuordnungen und Parametergrenzen. | Ein Faktor-10-Unterschied ist möglich. Nichtnull-Rohwerte, HA-Anzeige und Touch-Prozent gleichzeitig vergleichen, bevor die Skalierung geändert wird. |
| REG64 | Der aktive Kessel-Sollwert kann null sein, während REG44 weiterhin den Modus Puffer/Boiler anzeigt. | Null bedeutet hier keinen aktiven Kessel-Sollwert, nicht zwingend einen deaktivierten Betriebsmodus. Modus, Brennphase und aktuelle Anforderung getrennt betrachten. |
| REG66 | Der aktive Abgas-Sollwert ändert sich innerhalb der Regelphase. | Kein fester Zweizustandswert; REG42=7 bedeutet Regelbetrieb und belegt keine Volllast. |
| REG68 | Steigt und fällt, einschließlich wiederkehrender Nullintervalle. Der Touch zeigt eine „aktuelle Einschubmenge“ in Prozent, im verglichenen ruhenden Zustand ebenfalls null. | „Aktuelle Einschubmenge“ ist ein konkreter Kandidat für den nächsten Vergleich. Der Null-Match bestätigt weder die Funktion noch eine Prozent-Skalierung. Kein monotoner Verbrauchs- oder Laufzeitzähler; keine Umrechnung in Brennstoffmenge oder Energie. |
| REG72 | Aktivität im Zusammenhang mit Zündung und Anbrennen erneut beobachtet. | Der Zusammenhang mit der Zündung wird gestützt; konkreter Aktor weiterhin unbekannt. |
| REG76 | Wiederkehrende High-Intervalle auch bei REG42=0. | Aktivität ist nicht auf den Brennbetrieb beschränkt. Funktion, Periodizität und physische Impulsdauer bleiben offen. |
| REG78 | Lange High-Intervalle und Pulse im Standby erneut beobachtet; dabei steigt der Rücklauf bei fallender Kesseltemperatur. Dieses Muster widerspricht der bisherigen unmittelbaren Zuordnung zum Aschemotor. | Die Wärmeverschiebung stützt Pumpe oder Freigabe als Hypothese, identifiziert aber keinen Aktor. Aschemotor-Zuordnung bleibt zurückgenommen. Historische HA-IDs bleiben erhalten, gezählte Flanken sind keine bestätigten Aschezyklen. |
| REG70 / REG74 | Bisher nur null beobachtet. | Keine Aussage über dauerhafte Inaktivität oder eine Reservierung für ungenutzte Erweiterungen. |

## Aussagekraft der zusätzlichen Touch-Seiten

Die Parameterseiten erlauben einen erneuten Abgleich mehrerer bereits zugeordneter Konfigurationsregister mit ihren beschrifteten Touch-Feldern. Die übereinstimmenden Nichtnull-Parameter stützen die bestehenden Parameterzuordnungen und deren Skalierung. Das überträgt sich nicht auf die offenen Skalen der aktuellen Betriebswerte: Ein Primärluft-Grenzwert und der aktuelle Primärluftwert sind verschiedene Register.

Die I/O-Seiten zeigen unter anderem Türkontakte, Motorschutz-/Thermokontakte und die Lambdaheizung. Die Farbe eines solchen Signals belegt ohne Kenntnis der Kontaktpolarität und Anzeigelogik weder die physische Türstellung noch einen laufenden Motor. Insbesondere ist „X28-Brennraumtür offen“ zusammen mit einer grünen Anzeige kein ausreichender Türpositionsnachweis. Ein Thermokontakt der Registerreinigung ist außerdem kein Ausgangssignal ihres Motors. Anlagenoption, Eingangszustand, Zeitparameter und tatsächlicher Aktorbetrieb müssen getrennt betrachtet werden; allein ein eingetragener Reinigungszeitplan beweist keine freigegebene Reinigungsfunktion.

Ein O₂-Istwert am Touch im Zustand „Brenner Aus“ bestätigt zunächst nur, dass der angezeigte Wert auch von der Steuerung stammt. Die Anzeige der Lambdaheizung liefert zusätzlichen Betriebskontext, aber weder einen Nachweis ihrer elektrischen Leistung noch eine Bestätigung der Messgültigkeit. Aus dem ruhenden Zustand werden deshalb keine Aussagen zur Verbrennungsqualität oder zu einem Sondendefekt abgeleitet.

Die Laufzeitseite führt Steuerung, Brenner, Zellenrad und Dosierung getrennt auf und besitzt eine Anzeige „Anzahl Zündungen“. Rücksetzbedingungen und Bezugszeitraum dieses Zählers sind nicht bekannt. Er darf daher weder als Lebensdauer- oder Tageszähler bezeichnet noch allein aufgrund eines gleichen Anzeigewerts mit einem HA-Brennstartzähler gleichgesetzt werden. Eine Modbus-Adresse ist dadurch ebenfalls nicht identifiziert.

## Grenzen und nächste Vergleichsbeobachtungen

HA-Verläufe enthalten Erkennungszeitpunkte asynchron abgefragter Sensoren. Unveränderte Werte werden in einer Zustandsänderungshistorie nicht als neue Messung dargestellt. Gehaltene Werte auf einem gemeinsamen Raster sind daher keine unabhängigen synchronen Messpaare. Gespeicherte High-Dauern beweisen weder die physische Laufzeit eines Motors noch eine genaue Periodizität; kurze Pulse können zwischen Abfragen fehlen.

Eine Touch-Aufnahme mit ausgeschalteten Aktoren unterstützt lediglich die Zuordnung eines ruhenden Betriebszustands. Sie identifiziert die unbekannten binären Register nicht und klärt keine Skalierung, weil null bei beiden Kandidatenskalen null bleibt. Angezeigte Puffertemperaturen belegen zudem nicht, dass diese Messwerte in der getesteten Modbus-Map exportiert werden.

Die nächste besonders hilfreiche Aufnahme ist die Ist/Soll-Seite während eines natürlichen Regelbetriebs mit Nichtnullwerten: Sie vereint O₂-Soll, aktuelle Einschubmenge und die Gebläseanzeigen und ermöglicht damit einen gemeinsamen Vergleich von REG56, REG58/60/62 und REG68. Für die unbekannten binären Register werden zusätzlich die tatsächlichen Aktoranzeigen der Hauptübersicht für Zündung, Dosierung, Zellenrad, Registerreinigung, Ascheaustragung und Rücklaufpumpe benötigt. Schutzkontaktseiten ersetzen diese Ausgangsanzeigen nicht. Für REG42=10 wird die zugehörige Brennerstatusanzeige benötigt. Für REG46=43 fehlt die Meldung der Hauptübersicht; ein natürlicher Wechsel zwischen den Statuscodes hilft, die Meldungszuordnung zu prüfen. Dafür müssen weder Heizparameter geändert noch ein zusätzlicher Brennzyklus ausgelöst werden.

Die aktuellen Vertrauensgrade und offenen Zuordnungen stehen in der [Registermap](REGISTER_MAP.md), das Vorgehen in der [Methodik](METHODOLOGY.md).
