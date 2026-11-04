"""Generate audited legacy-name aliases from pinned registry and curated sources.

The public helpers in this maintainer script operate on source records and plain
mappings; they do not import or depend on the runtime parser's existing tables.
See EXTERNAL_DATA.md for precedence, provenance and regeneration commands.
"""

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class RegistryRecord:
    """One accession's source name and distinct historical names, without species prefixes.

    ``current`` is the source's latest name, not proof that the accession is active.
    IPD XML can retain abandoned entries; use partition_ipd_records before curation.
    """

    species: str
    accession: str
    current: str
    previous: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class AliasCandidate:
    """A proposed old -> new name, with source/accession provenance and curated priority."""

    species: str
    old: str
    new: str
    source: str
    accession: str = ""
    curated: bool = False


def alias_key(name):
    """Return a case-insensitive lookup key, retaining stars and colon field boundaries."""
    return name.strip().upper().replace("-", "").replace("_", "").replace("'", "")


def strip_species(name, species):
    """Remove only the matching species prefix from a source allele name."""
    name = str(name).strip()
    prefix = species + "-"
    return name[len(prefix) :] if name.lower().startswith(prefix.lower()) else name


def read_ipd_xml(path):
    """Read current-schema IPD-MHC entries into RegistryRecords.

    Accepts the pinned release's additional_fields/field[@name='nomenclature']
    history. Raises ValueError for missing entries, malformed names, or no
    history fields: a changed schema must not produce a successful empty import.
    """
    path = Path(path)
    entries = ET.parse(path).getroot().find("entries")
    if entries is None or not len(entries):
        raise ValueError(f"{path.name}: no IPD-MHC entries")
    records = []
    history_fields = 0
    for entry in entries:
        name = entry.findtext("name", "")
        species, sep, current = name.partition("-")
        if not sep or not current or not entry.get("id"):
            raise ValueError(f"{path.name}: malformed IPD-MHC entry {name!r}")
        fields = entry.findall("./additional_fields/field[@name='nomenclature']")
        history_fields += len(fields)
        previous = tuple(
            dict.fromkeys(
                strip_species(old, species)
                for field in fields
                for old in (field.text or "").split(",")
                if old.strip()
            )
        )
        records.append(RegistryRecord(species, entry.get("id"), current, previous, path.name))
    if not history_fields:
        raise ValueError(f"{path.name}: no nomenclature history fields; check the XML schema")
    return records


def partition_ipd_records(records):
    """Return (eligible records, annotated exclusions) for an iterable of IPD records.

    Maintainer API: applies ipd_record_annotations.json only to matching source
    filenames and accessions. An exact-name mismatch or unsupported annotation
    status raises ValueError. Unannotated records remain eligible, even without
    sequences; this inventory is not a complete registry-status classifier.
    Exclusions retain source/accession/name, status evidence and historical names
    for the generated audit. No replacement or alias is inferred.
    """
    annotations = json.loads(
        Path(__file__).with_name("ipd_record_annotations.json").read_text(encoding="utf-8")
    )
    by_identity = {(row["source"], row["accession"]): row for row in annotations}
    eligible, excluded = [], []
    for record in records:
        annotation = by_identity.get((record.source, record.accession))
        if annotation is None:
            eligible.append(record)
            continue
        name = f"{record.species}-{record.current}"
        if annotation["name"] != name:
            raise ValueError(f"IPD annotation name mismatch for {record.accession}: {name}")
        if annotation["status"] != "abandoned":
            raise ValueError(f"Unsupported IPD annotation status: {annotation['status']}")
        excluded.append({**annotation, "historical_names": list(record.previous)})
    return eligible, excluded


def read_hla_history(path):
    """Read HLA history CSV: accession, newest-release name, then historical names.

    Deleted accessions (empty/NA newest name) are excluded. Raises ValueError
    when the expected header or current names are absent.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as stream:
        rows = csv.reader(line for line in stream if not line.startswith("#"))
        header = next(rows, [])
        if len(header) < 3 or header[0] != "HLA_ID":
            raise ValueError(f"{path.name}: expected HLA_ID and release columns")
        records = []
        for row in rows:
            if len(row) < 2 or row[1] in {"", "NA"}:
                continue
            previous = tuple(dict.fromkeys(name for name in row[2:] if name and name != "NA"))
            records.append(RegistryRecord("HLA", row[0], row[1], previous, path.name))
    if not records:
        raise ValueError(f"{path.name}: no current HLA names")
    return records


def read_hla_deletions(path, current_by_accession):
    """Return documented deletion/suffix redirects and rows with no asserted identity.

    current_by_accession maps HLA accessions to current names. It takes priority
    for suffix changes (including reversed changes). For deleted accessions,
    only explicit rename/equality clauses are accepted; later resubmissions are
    not assumed to have the old sequence's identity. Unresolved rows are returned
    for the audit, rather than guessed from other names in descriptive prose.
    """
    path = Path(path)
    candidates, unresolved = [], []
    target_pattern = re.compile(
        r"(?:renamed|identical to|changed to|becoming|=)\s+(?:corrected\s+)?(?:HLA-)?([A-Z0-9]+\*[\w:]+)",
        re.IGNORECASE,
    )
    with path.open(encoding="utf-8") as stream:
        for row in csv.reader(line for line in stream if not line.startswith("#")):
            if not row or row[0] == "AlleleID":
                continue
            if len(row) < 3:
                raise ValueError(f"{path.name}: malformed deletion row {row!r}")
            accession, old = row[:2]
            description = ",".join(row[2:])
            target = current_by_accession.get(accession)
            if target is None:
                match = target_pattern.search(description)
                target = match.group(1) if match else None
            if target:
                candidates.append(AliasCandidate("HLA", old, target, path.name, accession))
            else:
                unresolved.append({"accession": accession, "name": old, "description": description})
    return candidates, unresolved


def read_curated_aliases(path):
    """Read explicitly curated aliases; source comments remain their scientific provenance."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        AliasCandidate(species, str(old), str(new), path.name, curated=True)
        for species, table in data.items()
        for old, new in table.items()
    ]


def meaningful_alias(old, new, allow_numeric_target=False):
    """Whether names assert a rename beyond case/colon insertion, with no parenthetical text."""
    if not allow_numeric_target and "*" not in old:
        # Bare historical names can also denote loci or haplotypes.
        return False
    if any(c in old + new for c in "()"):
        return False
    if old.replace(":", "").isdigit():
        return False
    if not allow_numeric_target and new.replace(":", "").isdigit():
        return False
    # Adding fields only increases resolution; history does not authorize
    # choosing one descendant of a present-day partial name (e.g. Mamu-B*008:01).
    if alias_key(new).startswith(alias_key(old) + ":"):
        return False
    return alias_key(old).replace(":", "") != alias_key(new).replace(":", "")


def resolve_aliases(records, candidates):
    """Resolve candidate mappings under current-name and explicit-curation precedence.

    Returns (species -> old -> terminal name, provenance, audit). Current names
    cannot be alias keys. Curated edges outrank registry history, but never a
    current name. Incompatible automatic targets are excluded and audited.
    Compatible field extensions choose the most specific target. Rename cycles
    raise ValueError before output is written. All decisions use sorted keys.
    """
    current = {(r.species, alias_key(r.current)) for r in records}
    groups = defaultdict(list)
    counts = defaultdict(Counter)
    rejected = []
    for candidate in candidates:
        c = AliasCandidate(
            candidate.species,
            strip_species(candidate.old, candidate.species),
            strip_species(candidate.new, candidate.species),
            candidate.source,
            candidate.accession,
            candidate.curated,
        )
        counts[c.source]["candidates"] += 1
        if not meaningful_alias(c.old, c.new, c.curated):
            counts[c.source]["unchanged_or_unsupported"] += 1
            continue
        if (c.species, alias_key(c.old)) in current:
            counts[c.source]["current_name_preserved"] += 1
            rejected.append({"reason": "current_name", **c.__dict__})
            continue
        groups[c.species, alias_key(c.old)].append(c)

    chosen = {}
    for key, options in sorted(groups.items()):
        curated = [c for c in options if c.curated]
        eligible = curated or options
        targets = sorted({c.new for c in eligible}, key=lambda name: (-len(name), name))
        longest = targets[0]
        if not all(
            alias_key(longest) == alias_key(t) or alias_key(longest).startswith(alias_key(t) + ":")
            for t in targets
        ):
            for c in options:
                counts[c.source]["ambiguous"] += 1
                rejected.append({"reason": "ambiguous", **c.__dict__})
            continue
        winners = [c for c in eligible if c.new == longest]
        old = sorted(c.old for c in winners)[0]
        chosen[key] = (old, longest, winners)
        for c in options:
            if c in winners:
                counts[c.source]["accepted"] += 1
            else:
                counts[c.source]["superseded"] += 1
                rejected.append(
                    {"reason": "curated_precedence" if curated else "field_extension", **c.__dict__}
                )

    aliases, provenance = defaultdict(dict), defaultdict(dict)
    for (species, key), (old, new, origins) in sorted(chosen.items()):
        visited = {key}
        origins = list(origins)
        while (species, alias_key(new)) in chosen:
            next_key = alias_key(new)
            if next_key in visited:
                raise ValueError(f"Cyclic allele alias for {species}: {old} -> {new}")
            visited.add(next_key)
            _, new, next_origins = chosen[species, next_key]
            origins.extend(next_origins)
        aliases[species][old] = new
        provenance[species][old] = sorted({f"{c.source} {c.accession}".strip() for c in origins})
    audit = {
        "sources": {
            source: dict(sorted(stats.items())) for source, stats in sorted(counts.items())
        },
        "decisions": sorted(
            rejected, key=lambda d: (d["species"], d["old"], d["source"], d["accession"], d["new"])
        ),
        "emitted_aliases": sum(map(len, aliases.values())),
    }
    return dict(aliases), dict(provenance), audit


def write_aliases(path, aliases, provenance):
    """Write deterministic YAML with source/accession comments next to each alias."""
    lines = [
        "# GENERATED by combine_allele_aliases.py; do not edit by hand.",
        "# Registry URLs, releases and checksums: external_sources.json.",
        "# Curated mapping evidence: curated_allele_aliases.yaml.",
        "# Current registry spellings take precedence over historical redirects.",
    ]
    for species, table in sorted(aliases.items()):
        lines.append(f"{species}:")
        for old, new in sorted(table.items()):
            lines.append("  # " + "; ".join(provenance[species][old]))
            lines.append(f"  {json.dumps(old)}: {json.dumps(new)}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def protected_current_names(records, aliases):
    """Return current spellings that could collide with allele alias lookup.

    Lookup can try alternate gene names and inherited species tables, but
    preserves the allele-field string. Keep all current names sharing that
    string with any alias key. This conservative index protects exact current
    identities without bundling a complete registry or depending on the parser.
    It is a precedence guard, not a registry-membership API.
    """
    fields = {alias_key(old).split("*")[-1] for table in aliases.values() for old in table}
    result = defaultdict(set)
    for record in records:
        if alias_key(record.current).split("*")[-1] in fields:
            result[record.species].add(record.current)
    return {species: sorted(names) for species, names in sorted(result.items())}


def write_current_name_guards(path, names):
    """Write deterministic current-name precedence guards from pinned registries."""
    lines = [
        "# GENERATED by combine_allele_aliases.py; do not edit by hand.",
        "# Exact current names that may collide with historical alias lookup.",
        "# Not a complete registry. Sources/releases/hashes: external_sources.json.",
    ]
    for species, values in names.items():
        lines.append(f"{species}:")
        lines.extend("  - " + json.dumps(name) for name in values)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(args_list=None):
    """Generate aliases and optional JSON audit; malformed sources/cycles fail the command."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--yaml-input-file", "-y", nargs="+", default=[])
    parser.add_argument("--xml-input-file", "-x", nargs="+", default=[])
    parser.add_argument("--allele-history-input-file", "-a", nargs="+", default=[])
    parser.add_argument("--csv-input-file", "-s", nargs="+", default=[])
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--audit-output")
    parser.add_argument("--current-names-output")
    args = parser.parse_args(args_list)
    records, candidates, coverage, unresolved, excluded_records = [], [], {}, {}, []
    for paths, reader in [
        (args.xml_input_file, read_ipd_xml),
        (args.allele_history_input_file, read_hla_history),
    ]:
        for path in paths:
            rows = reader(path)
            source_records = len(rows)
            if reader is read_ipd_xml:
                rows, excluded = partition_ipd_records(rows)
                excluded_records.extend(excluded)
            records.extend(rows)
            coverage[Path(path).name] = {
                "source_records": source_records,
                "excluded_records": source_records - len(rows),
                "current_records": len(rows),
                "records_with_history": sum(bool(r.previous) for r in rows),
                "historical_names": sum(len(r.previous) for r in rows),
            }
            candidates.extend(
                AliasCandidate(r.species, old, r.current, r.source, r.accession)
                for r in rows
                for old in r.previous
            )
    hla_current = {r.accession: r.current for r in records if r.species == "HLA"}
    for path in args.csv_input_file:
        rows, unassigned = read_hla_deletions(path, hla_current)
        candidates.extend(rows)
        unresolved[Path(path).name] = unassigned
    for path in args.yaml_input_file:
        candidates.extend(read_curated_aliases(path))
    aliases, provenance, audit = resolve_aliases(records, candidates)
    audit["coverage"] = coverage
    audit["excluded_records"] = excluded_records
    audit["unresolved_deletions"] = unresolved
    write_aliases(args.output, aliases, provenance)
    if args.current_names_output:
        guards = protected_current_names(records, aliases)
        write_current_name_guards(args.current_names_output, guards)
        audit["protected_current_names"] = sum(map(len, guards.values()))
    if args.audit_output:
        Path(args.audit_output).write_text(
            json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "coverage": coverage,
                "sources": audit["sources"],
                "emitted_aliases": audit["emitted_aliases"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
