# Unofficial Gilles Modbus specification

[Deutsch](README.md)

Document version **0.1.0**, published on **27 November 2026**. The evidence baseline is project version **0.9.1**, commit `03696e929aa14fee1007d7c630489978c27533fc`. This edition consolidates existing findings; it confirms no new register function and includes no private telemetry.

| Edition | Download |
|---|---|
| German specification | [PDF](gilles-modbus-spec-v0.1.0-de.pdf) |
| English specification | [PDF](gilles-modbus-spec-v0.1.0-en.pdf) |
| Complete LaTeX sources | [ZIP](gilles-modbus-spec-v0.1.0-sources.zip) |

The document describes the observed FC03 read profile, the 40 known int32 values across 80 Modbus words, MBAP and word order, phases and status codes, error handling and synthetic telegrams. Verified identifications, strong hypotheses and unknown functions remain explicitly distinct. REG58/60/62 scaling is still unresolved. This specification is not manufacturer approval and defines no write operations.

## Build and check

Requirements: Python 3, XeLaTeX with the usual LaTeX extra packages, Babel for German/English and the freely available URW Base35 fonts **P052**, **Nimbus Sans** and **Nimbus Mono PS**. On Debian/Ubuntu these are typically provided by `texlive-xetex`, `texlive-latex-extra`, `texlive-lang-german` and `fonts-urw-base35`.

Run in this directory, or use the appropriate script path:

```sh
python3 build_spec.py --check
python3 build_spec.py
```

The first command checks complete register coverage, evidence grades, six int32 test values and five telegram examples. It never connects to a device. The second regenerates tables from `registers.json`, compiles both PDFs with three XeLaTeX passes each and packages the sources. Intermediate files go to `build/`. `--tables` generates only the tables; `--package` generates tables and the source archive without compiling.

These are document consistency checks, not certification of a client implementation. Visually inspect the PDF pages after changes as well. The build treats overfull boxes, missing glyphs and unresolved references as errors.

## Maintaining the sources

`gilles-modbus-spec.de.tex` and `gilles-modbus-spec.en.tex` contain the text; `gilles-spec.sty` supplies their shared layout. `registers.json` supplies both register tables. Generated `registers.*.tex` files are included for direct LaTeX use. The ZIP contains all sources and the project license at its top level and builds without a repository checkout.

Document and integration versions are independent. Corrections must identify their evidence and uncertainty and be applied in both languages. Publish only synthetic telegrams; private installation identifiers and raw operating histories do not belong in the sources.

Text and sources use the project's MIT license. Linked Modbus and manufacturer documents retain their own terms.
