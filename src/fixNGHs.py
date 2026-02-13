#!/usr/bin/env python3

# Jake Gordon
# 13 Feb 2026
#
# (Written mostly by ChatGPT, at my direction)
#
# Given an input_path and optional output_path, search the file at input_path
# for NGH rows that don't end with "N[012]", and add the missing suffix.  The
# resulting text is written to the file at output_path, or if not provided
# then back to the input_path. Syntax:
#
# ./fixNGHs.py input.txt
# OR
# ./fixNGHs.py input.txt -o output.txt

from pathlib import Path
from constants import outOfSightValue
import argparse


def fix_neighbor_suffixes(input_path: str, output_path: str | None = None) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path) if output_path else input_path

    with input_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        if line.startswith("PNT\t"):
            fixed_lines.append(line)

            fields = line.split("\t")

            # Defensive check: ensure at least 7 columns
            if len(fields) <= 6:
                raise ValueError(f"Malformed PNT row (not enough columns): {line}")

            is_oos = fields[6] == outOfSightValue

            i += 1

            if is_oos:
                # OOS points must NOT have NGH rows
                if i < len(lines) and lines[i].startswith("NGH\t"):
                    raise ValueError(
                        f"PNT marked OOS should not have NGH rows, but found: {lines[i].rstrip()}"
                    )
                continue

            # Otherwise, expect exactly three NGH rows
            for neighbor_index in range(3):
                if i >= len(lines):
                    raise ValueError("Unexpected end of file after PNT row")

                ngh_line = lines[i].rstrip("\n")

                if not ngh_line.startswith("NGH\t"):
                    raise ValueError(
                        f"Expected NGH row after PNT, got: {ngh_line}"
                    )

                fields = ngh_line.split("\t")
                expected_suffix = f"N{neighbor_index}"

                if fields and fields[-1] in {"N0", "N1", "N2"}:
                    fields[-1] = expected_suffix
                else:
                    fields.append(expected_suffix)

                fixed_lines.append("\t".join(fields))
                i += 1

        else:
            fixed_lines.append(line)
            i += 1

    with output_path.open("w", encoding="utf-8") as f:
        for line in fixed_lines:
            f.write(line + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix missing or incorrect N0/N1/N2 suffixes on NGH rows."
    )

    parser.add_argument(
        "input_file",
        help="Path to input file"
    )

    parser.add_argument(
        "-o", "--output",
        help="Path to output file (default: overwrite input file)",
        default=None
    )

    args = parser.parse_args()

    fix_neighbor_suffixes(args.input_file, args.output)


if __name__ == "__main__":
    main()
