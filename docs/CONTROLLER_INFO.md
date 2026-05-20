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
  - Nur Function Code 03 (Read Holding Registers) wird unterstützt. Coils (FC01), Discrete Inputs (FC02) und Input Registers (FC04) liefern Fehler oder keine Antwort.
  - Map exportiert genau 40 logische Werte (80 16-bit-Register) ab Adresse 0. Höhere Adressen liefern keine Antwort.
  - Die TCP-Verbindung wird nach jeder Modbus-Exception geschlossen. Clients müssen neu verbinden.
  - Mindest-Count für Reads scheint 2 Register zu sein (1-Register-Reads liefern „Illegal Data Value"-Exception).
  - Default pymodbus-Retry-Count von 3 kann den Controller in einen „hängenden" Zustand bringen — `retries=1` setzen.

## Firmware-Versionen

Unser Testkessel läuft:
- LASAL II Version: v5.36.4 (10.01.2024)
- LSE Version: v5.36.4 (10.01.2024)

Beide Werte sind am Touch unter **Allgemeines → Version** sichtbar.

## Konfigurations-Export

Eine `Save to USB`-Funktion in **Allgemeines → Load/Save** schreibt drei Dateien auf einen angeschlossenen USB-Stick:

1. `parameter.txt` — Klartext-Export aller benannten LASAL-Parameter mit aktuellen Werten. Extrem nützlich für Reverse Engineering: jeder Modbus-Wert entspricht einem dieser Parameter (allerdings unterscheidet sich die Reihenfolge in Modbus von der in parameter.txt).
2. `moduser.para` — Binär serialisierter Parametersatz. Nicht human-readable; scheint Sigmateks internes LASAL-Format zu sein.
3. `moduser.conf` — Winzige Konfigurationsdatei, die deklariert welche Subsysteme konfiguriert sind (z.B. `Heizkreis_1`, `Warmwasser_2`, `Puffer_3`).

Die `parameter.txt` von einer Beispielinstallation liegt in [`reference/parameter-export-sample.txt`](../reference/parameter-export-sample.txt).

## Warum ist die Map so klein?

Gilles hat offenbar gewählt, nur eine kuratierte Teilmenge von Parametern via Modbus zu exportieren — fokussiert auf:

- Verbrennungs-Steuerungsparameter (Lambda-Luftverhältnisse, O2-Grenzen, Abgas-Grenzen)
- Kessel-Sollwerte (Tag/Nacht, Hysterese)
- Kessel-seitige Live-Messwerte (Kesseltemp, O2-Ist)
- Status-Flags (Betriebsmodus, Türstatus)

Heizkreis-, Warmwasser-, Puffer- und Pellet-Zuführungs-Daten werden intern von der LASAL-Anwendung verwaltet, aber nicht über die Modbus-Schnittstelle herausgegeben. Das ist eine bewusste Design-Entscheidung, nicht eine Einschränkung der zugrundeliegenden Plattform — Sigmatek HZS könnte problemlos tausende Register exportieren.

## Hargassner-Beziehung

Hargassner hat Gilles im September 2020 übernommen. Trotz der Fusion:

- **Die Gilles-Touch-Hardware wird auf existierenden HPK-RA-Kesseln nicht ersetzt**
- **Die Hargassner-Modbus-Map ist komplett anders** — Adressen ≥40287, erfordert eine separat zu kaufende Modbus-ID-Karte, verwendet float32 statt int32
- Der Service wird weiterhin von Hargassner-Technikern erbracht, die das Gilles-System kennen

Während also Integrationen wie [TheRealKillaruna/nano_pk](https://github.com/TheRealKillaruna/nano_pk) für Hargassner Nano-PK / Touch-Tronic-Systeme funktionieren, sind sie **nicht kompatibel** mit Gilles HPK-RA. Deshalb existiert das vorliegende Repository.
