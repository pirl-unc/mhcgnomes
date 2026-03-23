#!/usr/bin/env python3
"""
Shared analysis helpers for the paper validation corpus.
"""

import csv
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mhcgnomes import Species, parse


VALIDATION_DIR = ROOT / "paper" / "validation"
RESULTS_DIR = ROOT / "paper" / "results"

CORPORA = OrderedDict(
    [
        (
            "publisher_pmid",
            {
                "label": "Publisher / PMID",
                "files": ["all_papers.tsv"],
                "color": "#1f6aa5",
            },
        ),
        (
            "pmc_open_access",
            {
                "label": "PMC open access",
                "files": ["all_papers_v2.tsv"],
                "color": "#e07a1f",
            },
        ),
        (
            "combined",
            {
                "label": "Combined",
                "files": ["all_papers.tsv", "all_papers_v2.tsv"],
                "color": "#4f6d4f",
            },
        ),
    ]
)

TSV_FILENAMES = {
    "corpus_summary": "paper_corpus_summary.tsv",
    "taxon_summary": "paper_taxon_summary.tsv",
    "species_summary": "paper_species_summary.tsv",
    "source_summary": "paper_source_summary.tsv",
    "failure_mode_summary": "paper_failure_mode_summary.tsv",
    "failure_rows": "paper_failure_rows.tsv",
    "round_trip_summary": "paper_round_trip_summary.tsv",
}

HUMAN_FALLBACK_PATTERN = re.compile(
    r"^(?:"
    r"HLA-.*|"
    r"[ABC]\*[\d:]+[A-Za-z]?$|"
    r"(?:DR|DQ|DP)[A-Z0-9]*\*[\d:]+[A-Za-z]?$|"
    r"(?:A|B|C)\d{1,3}$|"
    r"Cw\d+$|"
    r"Bw[46]$|"
    r"DR\d+$|"
    r"DQ\d+$|"
    r"DPw\d+$"
    r")"
)
SPECIES_PREFIX_PATTERN = re.compile(r"^([A-Z][A-Za-z0-9]{2,15})-")
UPPERCASE_MHC_PREFIXES = {
    "HLA",
    "Mafa",
    "Mamu",
    "Patr",
    "Papa",
    "Gogo",
    "BoLA",
    "DLA",
    "SLA",
    "ELA",
    "FLA",
}
OTHER_MAMMAL_KEYWORDS = {
    "bat",
    "bovine",
    "canine",
    "cat",
    "deer",
    "dog",
    "elephant",
    "goat",
    "horse",
    "koala",
    "macaque",
    "monkey",
    "mule",
    "pig",
    "porcine",
    "primate",
    "rodent",
    "seal",
    "sheep",
    "vole",
    "mouse",
    "devil",
    "cattle",
}


def corpus_output_path(key):
    return RESULTS_DIR / TSV_FILENAMES[key]


def iter_validation_rows(corpus_key):
    for filename in CORPORA[corpus_key]["files"]:
        path = VALIDATION_DIR / filename
        with path.open() as fd:
            reader = csv.DictReader(fd, delimiter="\t")
            for row in reader:
                yield row


def lineage_names(species):
    names = []
    current = species
    while current is not None:
        names.append(current.name)
        current = current.parent
    return names


def infer_species_from_raw(raw):
    raw = raw.strip()
    if not raw:
        return None

    match = SPECIES_PREFIX_PATTERN.match(raw)
    if match:
        species = Species.get(match.group(1))
        if species is not None:
            return species.name

    if raw.startswith(("H2", "H-2")):
        species = Species.get("Mus musculus")
        return species.name if species is not None else None

    if raw.startswith("RT1"):
        species = Species.get("RT1") or Species.get("Rattus norvegicus")
        return species.name if species is not None else None

    if HUMAN_FALLBACK_PATTERN.match(raw):
        species = Species.get("Homo sapiens")
        return species.name if species is not None else None

    return None


def major_taxon_for_species(species_name):
    if not species_name:
        return "Unassigned"

    species = Species.get(species_name)
    if species is None:
        return "Unassigned"

    if species.name == "Homo sapiens":
        return "Human"

    lineage = set(lineage_names(species))
    if "Primata sp." in lineage:
        return "Non-human primate"
    if "Cetacea sp." in lineage:
        return "Cetacean"
    if "Aves sp." in lineage:
        return "Bird"
    if "Actinopterygii sp." in lineage or "Chondrichthyes sp." in lineage:
        return "Fish"
    if "Reptilia sp." in lineage:
        return "Reptile"
    if "Amphibia sp." in lineage:
        return "Amphibian"
    if (
        "Marsupialia sp." in lineage
        or "Chiroptera sp." in lineage
        or "Rodentia sp." in lineage
    ):
        return "Other mammal"

    common_name = species.common_name.lower() if species.common_name else ""
    if any(keyword in common_name for keyword in OTHER_MAMMAL_KEYWORDS):
        return "Other mammal"

    return "Other vertebrate"


def classify_failure_mode(raw, inferred_species):
    raw = raw.strip()
    prefix_match = SPECIES_PREFIX_PATTERN.match(raw)
    prefix = prefix_match.group(1) if prefix_match else ""

    if prefix in UPPERCASE_MHC_PREFIXES:
        return "Unsupported locus / gene family"

    # Mouse/rat shorthand typically indicates a normalization gap rather than
    # missing species curation.
    if raw.startswith(("H2", "H-2", "RT1")):
        return "Formatting / normalization edge case"

    if inferred_species and prefix and Species.get(prefix) is not None:
        return "Uncurated species-specific nomenclature"

    if "*" in raw or ":" in raw:
        return "Formatting / normalization edge case"

    if "-" in raw:
        return "Residual non-MHC extraction"

    return "Other / ambiguous"


def analyze_row(corpus_key, row):
    raw = row["raw_string"].strip()
    source = row.get("source", "").strip()
    expected_species = row.get("expected_species", "").strip()

    parsed = False
    result_type = ""
    parsed_species = ""
    normalized = ""
    round_trip_ok = ""
    round_trip_reparsed = ""
    error_type = ""
    error_message = ""

    try:
        result = parse(raw, raise_on_error=True)
        normalized = result.to_string() if hasattr(result, "to_string") else str(result)
        result_type = type(result).__name__
        species = getattr(result, "species", None)
        parsed_species = species.name if species is not None else ""
        parsed = True

        try:
            reparsed = parse(normalized, raise_on_error=True)
            round_trip_reparsed = (
                reparsed.to_string() if hasattr(reparsed, "to_string") else str(reparsed)
            )
            round_trip_ok = round_trip_reparsed == normalized
        except Exception:
            round_trip_reparsed = "PARSE_ERROR"
            round_trip_ok = False
    except Exception as exc:
        error_type = type(exc).__name__
        error_message = str(exc)

    inferred_species = parsed_species or infer_species_from_raw(raw) or ""
    major_taxon = major_taxon_for_species(inferred_species)
    failure_mode = "" if parsed else classify_failure_mode(raw, inferred_species)

    return {
        "corpus": corpus_key,
        "corpus_label": CORPORA[corpus_key]["label"],
        "source": source,
        "raw_string": raw,
        "expected_species": expected_species,
        "parsed": parsed,
        "result_type": result_type,
        "parsed_species": parsed_species,
        "inferred_species": inferred_species or "Unassigned",
        "major_taxon": major_taxon,
        "normalized": normalized,
        "round_trip_ok": round_trip_ok,
        "round_trip_reparsed": round_trip_reparsed,
        "error_type": error_type,
        "error_message": error_message,
        "failure_mode": failure_mode,
    }


def build_analysis_records():
    records_by_corpus = {}
    for corpus_key in CORPORA:
        records_by_corpus[corpus_key] = [
            analyze_row(corpus_key, row) for row in iter_validation_rows(corpus_key)
        ]
    return records_by_corpus


def summarize_corpus(records):
    parsed_records = [r for r in records if r["parsed"]]
    return {
        "corpus": records[0]["corpus"] if records else "",
        "corpus_label": records[0]["corpus_label"] if records else "",
        "total_strings": len(records),
        "parsed_strings": len(parsed_records),
        "parse_rate_pct": round(100.0 * len(parsed_records) / len(records), 1) if records else 0.0,
        "unique_sources": len({r["source"] for r in records}),
        "unique_inferred_species": len(
            {r["inferred_species"] for r in records if r["inferred_species"] != "Unassigned"}
        ),
        "unique_normalized": len({r["normalized"] for r in parsed_records if r["normalized"]}),
        "round_trip_failures": sum(1 for r in parsed_records if r["round_trip_ok"] is False),
    }


def summarize_taxa(records):
    stats = defaultdict(
        lambda: {"total_strings": 0, "parsed_strings": 0, "sources": set(), "species": set()}
    )
    for record in records:
        key = record["major_taxon"]
        stats[key]["total_strings"] += 1
        stats[key]["sources"].add(record["source"])
        if record["inferred_species"] != "Unassigned":
            stats[key]["species"].add(record["inferred_species"])
        if record["parsed"]:
            stats[key]["parsed_strings"] += 1

    rows = []
    for major_taxon, values in stats.items():
        rows.append(
            {
                "corpus": records[0]["corpus"] if records else "",
                "corpus_label": records[0]["corpus_label"] if records else "",
                "major_taxon": major_taxon,
                "total_strings": values["total_strings"],
                "parsed_strings": values["parsed_strings"],
                "parse_rate_pct": round(
                    100.0 * values["parsed_strings"] / values["total_strings"], 1
                ),
                "unique_sources": len(values["sources"]),
                "unique_species": len(values["species"]),
            }
        )
    return sorted(rows, key=lambda row: (-row["total_strings"], row["major_taxon"]))


def summarize_species(records):
    stats = defaultdict(
        lambda: {
            "total_strings": 0,
            "parsed_strings": 0,
            "sources": set(),
            "major_taxon": "Unassigned",
        }
    )
    for record in records:
        species = record["inferred_species"]
        stats[species]["total_strings"] += 1
        stats[species]["sources"].add(record["source"])
        stats[species]["major_taxon"] = record["major_taxon"]
        if record["parsed"]:
            stats[species]["parsed_strings"] += 1

    rows = []
    for species, values in stats.items():
        rows.append(
            {
                "corpus": records[0]["corpus"] if records else "",
                "corpus_label": records[0]["corpus_label"] if records else "",
                "species": species,
                "major_taxon": values["major_taxon"],
                "total_strings": values["total_strings"],
                "parsed_strings": values["parsed_strings"],
                "parse_rate_pct": round(
                    100.0 * values["parsed_strings"] / values["total_strings"], 1
                ),
                "unique_sources": len(values["sources"]),
            }
        )
    return sorted(rows, key=lambda row: (-row["total_strings"], row["species"]))


def summarize_sources(records):
    stats = defaultdict(
        lambda: {
            "total_strings": 0,
            "parsed_strings": 0,
            "parsed_species": set(),
            "major_taxa": defaultdict(int),
        }
    )
    for record in records:
        source = record["source"]
        stats[source]["total_strings"] += 1
        stats[source]["major_taxa"][record["major_taxon"]] += 1
        if record["parsed"]:
            stats[source]["parsed_strings"] += 1
            if record["parsed_species"]:
                stats[source]["parsed_species"].add(record["parsed_species"])

    rows = []
    for source, values in stats.items():
        dominant_taxon = max(values["major_taxa"].items(), key=lambda item: item[1])[0]
        rows.append(
            {
                "corpus": records[0]["corpus"] if records else "",
                "corpus_label": records[0]["corpus_label"] if records else "",
                "source": source,
                "major_taxon": dominant_taxon,
                "total_strings": values["total_strings"],
                "parsed_strings": values["parsed_strings"],
                "parse_rate_pct": round(
                    100.0 * values["parsed_strings"] / values["total_strings"], 1
                ),
                "unique_parsed_species": len(values["parsed_species"]),
            }
        )
    return sorted(rows, key=lambda row: (-row["total_strings"], row["source"]))


def summarize_failure_modes(records):
    failed = [r for r in records if not r["parsed"]]
    stats = defaultdict(lambda: {"count": 0, "examples": []})
    for record in failed:
        mode = record["failure_mode"]
        stats[mode]["count"] += 1
        if record["raw_string"] not in stats[mode]["examples"] and len(stats[mode]["examples"]) < 3:
            stats[mode]["examples"].append(record["raw_string"])

    rows = []
    for mode, values in stats.items():
        rows.append(
            {
                "corpus": records[0]["corpus"] if records else "",
                "corpus_label": records[0]["corpus_label"] if records else "",
                "failure_mode": mode,
                "count": values["count"],
                "pct_of_failures": round(100.0 * values["count"] / len(failed), 1) if failed else 0.0,
                "example_1": values["examples"][0] if len(values["examples"]) > 0 else "",
                "example_2": values["examples"][1] if len(values["examples"]) > 1 else "",
                "example_3": values["examples"][2] if len(values["examples"]) > 2 else "",
            }
        )
    return sorted(rows, key=lambda row: (-row["count"], row["failure_mode"]))


def failure_rows(records):
    rows = []
    for record in records:
        if record["parsed"]:
            continue
        rows.append(
            {
                "corpus": record["corpus"],
                "corpus_label": record["corpus_label"],
                "source": record["source"],
                "raw_string": record["raw_string"],
                "inferred_species": record["inferred_species"],
                "major_taxon": record["major_taxon"],
                "failure_mode": record["failure_mode"],
                "error_type": record["error_type"],
                "error_message": record["error_message"],
            }
        )
    return rows


def round_trip_rows(records):
    rows = []
    for record in records:
        if not record["parsed"] or record["round_trip_ok"] is not False:
            continue
        rows.append(
            {
                "corpus": record["corpus"],
                "corpus_label": record["corpus_label"],
                "source": record["source"],
                "raw_string": record["raw_string"],
                "normalized": record["normalized"],
                "round_trip_reparsed": record["round_trip_reparsed"],
            }
        )
    return rows


def write_tsv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fd:
        writer = csv.DictWriter(fd, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def export_summary_tables(records_by_corpus=None):
    if records_by_corpus is None:
        records_by_corpus = build_analysis_records()

    corpus_rows = []
    taxon_rows = []
    species_rows = []
    source_rows = []
    failure_summary_rows = []
    failure_detail_rows = []
    round_trip_detail_rows = []

    for corpus_key, records in records_by_corpus.items():
        corpus_rows.append(summarize_corpus(records))
        taxon_rows.extend(summarize_taxa(records))
        species_rows.extend(summarize_species(records))
        source_rows.extend(summarize_sources(records))
        failure_summary_rows.extend(summarize_failure_modes(records))
        failure_detail_rows.extend(failure_rows(records))
        round_trip_detail_rows.extend(round_trip_rows(records))

    write_tsv(
        corpus_output_path("corpus_summary"),
        corpus_rows,
        [
            "corpus",
            "corpus_label",
            "total_strings",
            "parsed_strings",
            "parse_rate_pct",
            "unique_sources",
            "unique_inferred_species",
            "unique_normalized",
            "round_trip_failures",
        ],
    )
    write_tsv(
        corpus_output_path("taxon_summary"),
        taxon_rows,
        [
            "corpus",
            "corpus_label",
            "major_taxon",
            "total_strings",
            "parsed_strings",
            "parse_rate_pct",
            "unique_sources",
            "unique_species",
        ],
    )
    write_tsv(
        corpus_output_path("species_summary"),
        species_rows,
        [
            "corpus",
            "corpus_label",
            "species",
            "major_taxon",
            "total_strings",
            "parsed_strings",
            "parse_rate_pct",
            "unique_sources",
        ],
    )
    write_tsv(
        corpus_output_path("source_summary"),
        source_rows,
        [
            "corpus",
            "corpus_label",
            "source",
            "major_taxon",
            "total_strings",
            "parsed_strings",
            "parse_rate_pct",
            "unique_parsed_species",
        ],
    )
    write_tsv(
        corpus_output_path("failure_mode_summary"),
        failure_summary_rows,
        [
            "corpus",
            "corpus_label",
            "failure_mode",
            "count",
            "pct_of_failures",
            "example_1",
            "example_2",
            "example_3",
        ],
    )
    write_tsv(
        corpus_output_path("failure_rows"),
        failure_detail_rows,
        [
            "corpus",
            "corpus_label",
            "source",
            "raw_string",
            "inferred_species",
            "major_taxon",
            "failure_mode",
            "error_type",
            "error_message",
        ],
    )
    write_tsv(
        corpus_output_path("round_trip_summary"),
        round_trip_detail_rows,
        [
            "corpus",
            "corpus_label",
            "source",
            "raw_string",
            "normalized",
            "round_trip_reparsed",
        ],
    )

    return {
        "corpus_summary": corpus_rows,
        "taxon_summary": taxon_rows,
        "species_summary": species_rows,
        "source_summary": source_rows,
        "failure_mode_summary": failure_summary_rows,
        "failure_rows": failure_detail_rows,
        "round_trip_summary": round_trip_detail_rows,
    }


def write_markdown_summary(summary_tables):
    corpus_rows = {row["corpus"]: row for row in summary_tables["corpus_summary"]}
    combined_species = [
        row for row in summary_tables["species_summary"] if row["corpus"] == "combined"
    ]
    combined_sources = [
        row for row in summary_tables["source_summary"] if row["corpus"] == "combined"
    ]
    combined_failures = [
        row for row in summary_tables["failure_mode_summary"] if row["corpus"] == "combined"
    ]

    path = RESULTS_DIR / "paper_summary.md"
    lines = [
        "# Paper validation corpus summary",
        "",
        "## Corpus totals",
        "",
        "| Corpus | Strings | Parsed | Parse rate | Sources | Inferred species |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for corpus_key in ("publisher_pmid", "pmc_open_access", "combined"):
        row = corpus_rows[corpus_key]
        lines.append(
            "| {label} | {total} | {parsed} | {rate:.1f}% | {sources} | {species} |".format(
                label=row["corpus_label"],
                total=row["total_strings"],
                parsed=row["parsed_strings"],
                rate=row["parse_rate_pct"],
                sources=row["unique_sources"],
                species=row["unique_inferred_species"],
            )
        )

    lines.extend(
        [
            "",
            "## Top inferred species",
            "",
            "| Species | Taxon | Strings | Parsed | Parse rate | Sources |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in combined_species[:15]:
        if row["species"] == "Unassigned":
            continue
        lines.append(
            "| {species} | {taxon} | {total} | {parsed} | {rate:.1f}% | {sources} |".format(
                species=row["species"],
                taxon=row["major_taxon"],
                total=row["total_strings"],
                parsed=row["parsed_strings"],
                rate=row["parse_rate_pct"],
                sources=row["unique_sources"],
            )
        )

    lines.extend(
        [
            "",
            "## Top sources",
            "",
            "| Source | Strings | Parsed | Parse rate | Taxon |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in combined_sources[:15]:
        lines.append(
            "| {source} | {total} | {parsed} | {rate:.1f}% | {taxon} |".format(
                source=row["source"],
                total=row["total_strings"],
                parsed=row["parsed_strings"],
                rate=row["parse_rate_pct"],
                taxon=row["major_taxon"],
            )
        )

    lines.extend(
        [
            "",
            "## Failure modes",
            "",
            "| Failure mode | Count | % of failures | Example 1 | Example 2 |",
            "| --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in combined_failures:
        lines.append(
            "| {mode} | {count} | {pct:.1f}% | `{ex1}` | `{ex2}` |".format(
                mode=row["failure_mode"],
                count=row["count"],
                pct=row["pct_of_failures"],
                ex1=row["example_1"],
                ex2=row["example_2"],
            )
        )

    path.write_text("\n".join(lines) + "\n")
    return path
