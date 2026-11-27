#!/usr/bin/env python3
"""Validate the offline specification fixtures, generate tables and build PDFs."""

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = "0.1.0"
LANGUAGES = ("de", "en")
GRADES = {"verified": "V", "strong_hypothesis": "H", "unknown": "U"}
REQUEST = "00 01 00 00 00 06 01 03 00 30 00 02"
RESPONSE = "00 01 00 00 00 07 01 03 04 00 00 04 D2"
BLOCK_REQUEST = "00 02 00 00 00 06 01 03 00 00 00 50"
BLOCK_HEADER = "00 02 00 00 00 A3 01 03 A0"
EXCEPTION = "00 01 00 00 00 03 01 83 03"


def validate(rows):
    """Check published examples without connecting to a device."""
    if [r["address"] for r in rows] != list(range(0, 80, 2)):
        raise ValueError("Expected exactly the 40 ordered pair addresses 0..78")
    if Counter(r["confidence"] for r in rows) != {
        "verified": 25, "strong_hypothesis": 9, "unknown": 6
    }:
        raise ValueError("Evidence-grade counts differ from this edition")
    for row in rows:
        for field in ("name", "scale", "unit", "description_de", "description_en"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"Missing {field} for REG{row['address']}")

    for wire, expected in (
        ("00000000", 0), ("000004D2", 1234), ("00010002", 65538),
        ("7FFFFFFF", 2147483647), ("FFFFFFFF", -1),
        ("80000000", -2147483648),
    ):
        data = bytes.fromhex(wire)
        high, low = struct.unpack(">HH", data)
        unsigned = high * 65536 + low
        signed = unsigned if unsigned < 2**31 else unsigned - 2**32
        if signed != expected or struct.unpack(">i", data)[0] != expected:
            raise ValueError(f"Invalid int32 vector: {wire}")

    frames = (
        (REQUEST, 1, bytes.fromhex("03 00 30 00 02")),
        (RESPONSE, 1, bytes.fromhex("03 04 00 00 04 D2")),
        (BLOCK_REQUEST, 2, bytes.fromhex("03 00 00 00 50")),
        (EXCEPTION, 1, bytes.fromhex("83 03")),
    )
    for hex_frame, transaction, expected_pdu in frames:
        frame = bytes.fromhex(hex_frame)
        tid, protocol, length, unit = struct.unpack(">HHHB", frame[:7])
        if (tid, protocol, length, unit) != (transaction, 0, len(frame) - 6, 1):
            raise ValueError(f"Invalid MBAP vector: {hex_frame}")
        if frame[7:] != expected_pdu:
            raise ValueError("Invalid PDU vector")
    block = bytes.fromhex(BLOCK_HEADER) + bytes(160)
    if len(block) != 6 + 163 or block[8] != 80 * 2:
        raise ValueError("Invalid full-block length")
    for lang in LANGUAGES:
        source = (ROOT / f"gilles-modbus-spec.{lang}.tex").read_text()
        for vector in (REQUEST, RESPONSE, BLOCK_REQUEST, BLOCK_HEADER, EXCEPTION):
            if vector not in source:
                raise ValueError(f"{lang}: source and tested telegrams differ")
    print("Validated: 40 register pairs, 25/9/6 grades, 6 int32 and 5 telegram vectors")


def tex(text):
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
        "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in text)


def scale_label(row, lang):
    scale = row["scale"]
    if scale == "unknown":
        scale = "offen" if lang == "de" else "unknown"
    elif scale.startswith("HA "):
        scale = "HA × 0.1; " + ("offen" if lang == "de" else "unresolved")
    elif "raw 0/1 observed" in scale:
        scale = "× 1; " + ("0/1 beobachtet" if lang == "de" else "0/1 observed")
    elif "hypothesis" in scale:
        scale = "× 0.1 (H)"
    elif "structure unresolved" in scale:
        scale = "× 1; " + ("Struktur offen" if lang == "de" else "structure unknown")
    else:
        scale = scale.replace("x ", "× ")
    return tex(scale) + r"\newline " + tex(row["unit"])


def generate_tables(rows):
    for lang in LANGUAGES:
        labels = ("Adr.", "Projektname", "Skala / Einheit", "Grad", "Bedeutung und Grenze") if lang == "de" else (
            "Addr.", "Project name", "Scale / unit", "Grade", "Meaning and limits")
        header = " & ".join(r"\textbf{" + label + "}" for label in labels)
        for section, subset in (("parameters", rows[:21]), ("live", rows[21:])):
            lines = [
                "% Generated from registers.json by build_spec.py; do not edit.",
                r"\begingroup\small",
                r"\begin{longtable}{@{}L{10mm}L{42mm}L{25mm}L{9mm}L{77mm}@{}}",
                r"\toprule " + header + r"\\\midrule\endhead",
                r"\bottomrule\endfoot",
            ]
            for row in subset:
                cells = [
                    str(row["address"]), r"\code{" + tex(row["name"]) + "}",
                    scale_label(row, lang), r"\grade{" + GRADES[row["confidence"]] + "}",
                    tex(row[f"description_{lang}"]),
                ]
                lines.append(" & ".join(cells) + r"\\[4pt]")
            lines.extend((r"\end{longtable}", r"\endgroup", ""))
            (ROOT / f"registers.{lang}.{section}.tex").write_text("\n".join(lines))


def build():
    if not shutil.which("xelatex"):
        raise SystemExit("Install XeLaTeX, LaTeX extra packages and the URW Base35 fonts.")
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    for lang in LANGUAGES:
        name = f"gilles-modbus-spec.{lang}"
        # Three passes settle the table widths, contents and cross-references.
        for _ in range(3):
            result = subprocess.run(
                ["xelatex", "-no-shell-escape", "-interaction=nonstopmode",
                 "-halt-on-error", f"-output-directory={output}", f"{name}.tex"],
                cwd=ROOT, capture_output=True, text=True,
            )
            if result.returncode:
                raise SystemExit(result.stdout[-8000:] + result.stderr[-2000:])
        log = (output / f"{name}.log").read_text(errors="replace")
        for marker in ("Overfull ", "Missing character:", "undefined references"):
            if marker in log:
                raise SystemExit(f"Review {name}.log: {marker}")
        destination = ROOT / f"gilles-modbus-spec-v{VERSION}-{lang}.pdf"
        shutil.copyfile(output / f"{name}.pdf", destination)
        print(f"Built {destination.name}")


def package():
    sources = [ROOT / "build_spec.py", ROOT / "registers.json", ROOT / "gilles-spec.sty"]
    sources += sorted(ROOT.glob("*.tex"))
    sources += [ROOT / "README.md", ROOT / "README.en.md"]
    license_path = ROOT / "LICENSE"
    if not license_path.exists():
        license_path = ROOT.parent.parent / "LICENSE"
    sources.append(license_path)
    archive = ROOT / f"gilles-modbus-spec-v{VERSION}-sources.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for source in sources:
            info = zipfile.ZipInfo(source.name, date_time=(2026, 11, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, source.read_bytes())
    print(f"Packaged {archive.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="offline fixture checks only")
    parser.add_argument("--tables", action="store_true", help="also regenerate LaTeX tables")
    parser.add_argument("--package", action="store_true", help="package sources without compiling")
    args = parser.parse_args()
    rows = json.loads((ROOT / "registers.json").read_text())
    validate(rows)
    if args.check and not args.tables and not args.package:
        return
    generate_tables(rows)
    if not (args.check or args.tables or args.package):
        build()
        package()
    elif args.package:
        package()


if __name__ == "__main__":
    main()
