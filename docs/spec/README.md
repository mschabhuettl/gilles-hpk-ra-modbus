# Inoffizielle Gilles-Modbus-Spezifikation

[English](README.en.md)

Dokumentversion **0.1.0**, veröffentlicht am **27. November 2026**. Befundbasis ist der Projektstand **0.9.1**, Commit `03696e929aa14fee1007d7c630489978c27533fc`. Diese Ausgabe fasst vorhandene Erkenntnisse zusammen; sie bestätigt keine neue Registerfunktion und enthält keine private Telemetrie.

| Ausgabe | Download |
|---|---|
| Deutsche Spezifikation | [PDF](gilles-modbus-spec-v0.1.0-de.pdf) |
| English specification | [PDF](gilles-modbus-spec-v0.1.0-en.pdf) |
| Vollständige LaTeX-Quellen | [ZIP](gilles-modbus-spec-v0.1.0-sources.zip) |

Das Dokument beschreibt das beobachtete FC03-Leseprofil, die 40 bekannten int32-Werte in 80 Modbus-Wörtern, MBAP und Wortreihenfolge, Phasen und Statuscodes, Fehlerbehandlung sowie synthetische Telegramme. Verifizierte Zuordnungen, starke Hypothesen und offene Funktionen bleiben ausdrücklich unterscheidbar. Die Skalen von REG58/60/62 sind weiterhin ungeklärt. Die Spezifikation ist keine Herstellerfreigabe und definiert keine Schreibzugriffe.

## Bauen und prüfen

Benötigt werden Python 3, XeLaTeX mit den üblichen LaTeX-Extra-Paketen, Babel für Deutsch/Englisch und die frei verfügbaren URW-Base35-Schriften **P052**, **Nimbus Sans** und **Nimbus Mono PS**. Unter Debian/Ubuntu werden diese typischerweise durch `texlive-xetex`, `texlive-latex-extra`, `texlive-lang-german` und `fonts-urw-base35` bereitgestellt.

Aus diesem Verzeichnis oder mit entsprechendem Skriptpfad ausführen:

```sh
python3 build_spec.py --check
python3 build_spec.py
```

Der erste Aufruf prüft die vollständige Registerabdeckung, Vertrauensgrade, sechs int32-Testwerte und fünf Telegrammbeispiele. Er stellt keine Verbindung zu einem Gerät her. Der zweite Aufruf erzeugt die Tabellen aus `registers.json`, baut beide PDFs in jeweils drei XeLaTeX-Durchläufen und erstellt das Quellen-ZIP. Zwischenprodukte liegen unter `build/`. `--tables` erzeugt nur die Tabellen; `--package` nur Tabellen und Quellenarchiv.

Die Prüfungen sind Konsistenzprüfungen des Dokuments, keine Zertifizierung einer Clientimplementierung. Nach Änderungen sind außerdem die PDF-Seiten visuell zu prüfen. Der Build meldet überlaufende Boxen, fehlende Schriftzeichen und unaufgelöste Verweise als Fehler.

## Quellenpflege

`gilles-modbus-spec.de.tex` und `gilles-modbus-spec.en.tex` enthalten die Texte, `gilles-spec.sty` das gemeinsame Layout. `registers.json` ist die gemeinsame Datengrundlage beider Registertabellen. Die generierten `registers.*.tex` werden für die direkte LaTeX-Nutzung mitgeliefert. Im ZIP liegen alle Quellen und die Projektlizenz auf einer Ebene; das Archiv lässt sich ohne Repository-Checkout bauen.

Dokumentversion und Integrationsversion werden unabhängig geführt. Korrekturen müssen Beleg und Unsicherheit benennen und in beiden Sprachen nachgezogen werden. Nur synthetische Telegramme veröffentlichen; private Anlagenkennungen und Rohverläufe gehören nicht in die Quellen.

Texte und Quellen stehen unter der MIT-Lizenz des Projekts. Die verlinkten Modbus- und Herstellerdokumente behalten ihre eigenen Bedingungen.
