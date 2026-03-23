#!/usr/bin/env python3
"""
Evaluate mhcgnomes parse rate and correctness on validation data.

Usage:
    python paper/scripts/evaluate.py paper/validation/*.tsv

Input format (TSV):
    raw_string\texpected_species\tsource

Output: summary statistics + per-source breakdown + error analysis.
"""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import mhcgnomes
from mhcgnomes import parse


def load_validation_data(paths):
    """Load validation TSV files. Columns: raw_string, expected_species, source."""
    records = []
    for path in paths:
        with open(path) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                records.append(row)
    return records


def evaluate(records):
    """Parse each record and classify the result."""
    results = []
    for rec in records:
        raw = rec["raw_string"].strip()
        expected_species = rec.get("expected_species", "").strip()
        source = rec.get("source", "unknown").strip()

        try:
            result = parse(raw, raise_on_error=True)
            parsed = True
            result_type = type(result).__name__
            parsed_species = getattr(result, "species", None)
            species_name = parsed_species.name if parsed_species else None
            normalized = result.to_string() if hasattr(result, "to_string") else str(result)

            # Check species correctness if expected_species provided
            if expected_species and species_name:
                species_correct = species_name == expected_species
            else:
                species_correct = None
        except Exception:
            parsed = False
            result_type = None
            species_name = None
            normalized = None
            species_correct = None

        results.append({
            "raw": raw,
            "source": source,
            "expected_species": expected_species,
            "parsed": parsed,
            "result_type": result_type,
            "species_name": species_name,
            "normalized": normalized,
            "species_correct": species_correct,
        })

    return results


def round_trip_check(results):
    """Check that parse(x).to_string() round-trips correctly."""
    rt_pass = 0
    rt_fail = 0
    rt_failures = []

    for r in results:
        if not r["parsed"] or r["normalized"] is None:
            continue
        try:
            reparsed = parse(r["normalized"], raise_on_error=True)
            if reparsed.to_string() == r["normalized"]:
                rt_pass += 1
            else:
                rt_fail += 1
                rt_failures.append((r["normalized"], reparsed.to_string()))
        except Exception:
            rt_fail += 1
            rt_failures.append((r["normalized"], "PARSE_ERROR"))

    return rt_pass, rt_fail, rt_failures


def summarize(results):
    """Print summary statistics."""
    total = len(results)
    parsed = sum(1 for r in results if r["parsed"])
    failed = total - parsed

    print(f"{'Total strings':.<40} {total}")
    print(f"{'Parsed successfully':.<40} {parsed} ({100*parsed/total:.1f}%)")
    print(f"{'Failed to parse':.<40} {failed} ({100*failed/total:.1f}%)")
    print()

    # Species correctness (where expected_species was provided)
    with_expected = [r for r in results if r["expected_species"] and r["parsed"]]
    if with_expected:
        correct = sum(1 for r in with_expected if r["species_correct"])
        wrong = len(with_expected) - correct
        print(f"{'Species correctness (of parsed with expected)':.<40}")
        print(f"  {'Correct':.<38} {correct} ({100*correct/len(with_expected):.1f}%)")
        print(f"  {'Wrong species':.<38} {wrong}")
        print()

    # Normalization yield
    raw_unique = len(set(r["raw"] for r in results if r["parsed"]))
    norm_unique = len(set(r["normalized"] for r in results if r["parsed"]))
    if raw_unique > 0:
        print(f"{'Unique raw strings (parsed)':.<40} {raw_unique}")
        print(f"{'Unique normalized forms':.<40} {norm_unique}")
        print(f"{'Compression ratio':.<40} {raw_unique/norm_unique:.2f}x")
        print()

    # Round-trip fidelity
    rt_pass, rt_fail, rt_failures = round_trip_check(results)
    if rt_pass + rt_fail > 0:
        print(f"{'Round-trip fidelity':.<40}")
        print(f"  {'Pass':.<38} {rt_pass}")
        print(f"  {'Fail':.<38} {rt_fail}")
        if rt_failures:
            print(f"  First 5 failures:")
            for orig, reparsed in rt_failures[:5]:
                print(f"    {orig} → {reparsed}")
        print()

    # Per-source breakdown
    by_source = defaultdict(lambda: {"total": 0, "parsed": 0})
    for r in results:
        by_source[r["source"]]["total"] += 1
        if r["parsed"]:
            by_source[r["source"]]["parsed"] += 1

    print("Per-source parse rates:")
    print(f"  {'Source':<30} {'Parsed':>8} {'Total':>8} {'Rate':>8}")
    for source in sorted(by_source):
        s = by_source[source]
        rate = 100 * s["parsed"] / s["total"] if s["total"] else 0
        print(f"  {source:<30} {s['parsed']:>8} {s['total']:>8} {rate:>7.1f}%")
    print()

    # Result type distribution
    type_counts = Counter(r["result_type"] for r in results if r["parsed"])
    print("Result type distribution:")
    for rtype, count in type_counts.most_common():
        print(f"  {rtype:<30} {count}")
    print()

    # Failure analysis: sample of unparsed strings
    failures = [r["raw"] for r in results if not r["parsed"]]
    if failures:
        print(f"Sample of failed strings ({min(20, len(failures))} of {len(failures)}):")
        for s in failures[:20]:
            print(f"  {s}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Validation TSV files")
    args = parser.parse_args()

    records = load_validation_data(args.files)
    if not records:
        print("No records loaded.", file=sys.stderr)
        return 1

    results = evaluate(records)
    summarize(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
