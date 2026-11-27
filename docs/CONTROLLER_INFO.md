# Gilles Touch Controller — Technischer Hintergrund

> 🇩🇪 **Deutsch** · [🇬🇧 English](CONTROLLER_INFO.en.md)

Die Gilles-Touch-Steuerung in den HPK-RA-Kesseln basiert auf **industrieller Sigmatek-Hardware**, nicht auf maßgeschneiderter Gilles-Elektronik. Diese Seite sammelt Referenzinformationen zum Hardware- und Software-Stack.

## Hardware

- **Hersteller:** Sigmatek (Lamprechtshausen, Österreich)
- **Produktfamilie:** HZS-Serie Kessel-Steuerungspanels — typischerweise HZS 732 / 7321 (Multi-Touch) oder HZS 771 / 772 / 774 (Single-Touch)
- **Touchscreen:** 7" Farbdisplay
- **Anschlüsse:** Ethernet (100 Mbit), USB (für Parameter-Export und Firmware-Updates)

## Software

- **PLC-Runtime:** LASAL II (Sigmateks IEC 61131-3 konforme Runtime)
- **Visualisierung:** LSE (LASAL Screen Editor), läuft auf demselben Panel
- **Programmierumgebung:** LASAL Engineering Tool (Sigmatek proprietär)
- **Fernzugriff:**
  - VNC-Server auf Port 5900 (Touch-Spiegelung)
  - HTTP-Server auf Port 80 (LASAL Remote View Java-Applet — veraltet, läuft in modernen Browsern nicht mehr)
  - LASAL Service-Port auf 1954 (für Sigmateks Engineering-Tools)

## Modbus-Implementierungs-Eigenheiten

- **Stack:** Sigmateks integrierter Modbus-TCP-Server
- **Aktivierung:** Scheint by default aktiv zu sein, sobald der Kessel im Netzwerk ist. Wir haben keinen Menüpunkt gefunden, um das umzuschalten.
- **Beobachtete Einschränkungen:**
  - Function Code 03 (Read Holding Registers) ist der belegte Leseweg. Historische Versuche mit FC01, FC02 und FC04 ergaben Fehler oder keine Antwort; das ist keine vollständige Liste unterstützter Funktionen.
  - Der bekannte Bereich umfasst 40 logische Werte in 80 16-Bit-Registern ab Adresse 0. Historische Versuche oberhalb dieses Bereichs ergaben keine nutzbare Antwort.
  - Nach Modbus-Exceptions wurde ein Verbindungsende beobachtet. Clients müssen einen solchen Abbruch behandeln und bei Bedarf neu verbinden.
  - Mindest-Count für Reads scheint 2 Register zu sein (1-Register-Reads liefern „Illegal Data Value"-Exception).
  - Die Referenzanlage schließt TCP nach etwa drei Sekunden Leerlauf (Messung 2026-09-07). HA liest deshalb REG42 alle zwei Sekunden.
  - Der Python-Logger setzt `retries=1` direkt am Client und verbindet pro Abfrage neu. HA 2026.9.1 setzt Wiederholungen intern auf drei; der YAML-Schlüssel `retries: 1` überschreibt das nicht. [Messbeleg und Grenzen](HA_VALIDATION.md).

## Firmware-Versionen

Unser Testkessel läuft:
- LASAL II Version: v5.36.4 (10.01.2024)
- LSE Version: v5.36.4 (10.01.2024)

Beide Werte sind am Touch unter **Allgemeines → Version** sichtbar.

## Konfigurations-Export

Eine `Save to USB`-Funktion in **Allgemeines → Load/Save** schreibt drei Dateien auf einen angeschlossenen USB-Stick:

1. `parameter.txt` — Klartext-Export benannter LASAL-Parameter mit aktuellen Werten. Der Vergleich stützt mehrere Registerzuordnungen; Vollständigkeit und eine Entsprechung für jeden Modbus-Wert sind nicht belegt. Die Reihenfolge unterscheidet sich von der Modbus-Map.
2. `moduser.para` — Binär serialisierter Parametersatz. Nicht human-readable; scheint Sigmateks internes LASAL-Format zu sein.
3. `moduser.conf` — Winzige Konfigurationsdatei, die deklariert welche Subsysteme konfiguriert sind (z.B. `Heizkreis_1`, `Warmwasser_2`, `Puffer_3`).

Die `parameter.txt` von einer Beispielinstallation liegt in [`reference/parameter-export-sample.txt`](../reference/parameter-export-sample.txt).

## Umfang der bekannten Map

Die bisher zugeordneten Werte betreffen vor allem:

- Verbrennungs-Steuerungsparameter (Lambda-Luftverhältnisse, O2-Grenzen, Abgas-Grenzen)
- Kessel-Sollwerte (Tag/Nacht, Hysterese)
- Kessel-seitige Live-Messwerte (Kesseltemp, O2-Ist)
- Betriebsmodus und Statuscodes; der Türhinweis aus REG46=35 ist indirekt

Für weitere Heizkreis-, Warmwasser-, Puffer- und Zuführungsgrößen fehlen belastbare Modbus-Zuordnungen. REG68 bleibt ein Kandidat für eine aktuelle Einschubmenge mit offener Einheit und Skala. Aus diesen Lücken lässt sich keine Herstellerentscheidung oder grundsätzliche Unzugänglichkeit ableiten. Das [inoffizielle Leseprofil](spec/README.md) hält den bekannten Umfang und seine Grenzen fest.

## Hargassner-Beziehung

Hargassner hat Gilles im September 2020 übernommen. Trotz der Fusion:

- **Die Gilles-Touch-Hardware wird auf existierenden HPK-RA-Kesseln nicht ersetzt**
- **Die Hargassner-Modbus-Map ist komplett anders** — Adressen ≥40287, erfordert eine separat zu kaufende Modbus-ID-Karte, verwendet float32 statt int32
- Der Service wird weiterhin von Hargassner-Technikern erbracht, die das Gilles-System kennen

Während also Integrationen wie [TheRealKillaruna/nano_pk](https://github.com/TheRealKillaruna/nano_pk) für Hargassner Nano-PK / Touch-Tronic-Systeme funktionieren, sind sie **nicht kompatibel** mit Gilles HPK-RA. Deshalb existiert das vorliegende Repository.
