#!/usr/bin/env python3
"""Audit current registry identities and every generated alias against the runtime parser.

Run after combine_allele_aliases.sh. Inputs are the pinned allele-aliases download
group. Documented abandoned records are excluded and reported with provenance;
every remaining source name must parse successfully with aliases off and on.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mhcgnomes/data"))
from combine_allele_aliases import (  # noqa: E402
    partition_ipd_records,
    read_hla_history,
    read_ipd_xml,
)

from mhcgnomes import (  # noqa: E402
    AlleleWithoutGene,
    get_registry_identities,
    parse,
    registry_identities,
)
from mhcgnomes.data import allele_aliases  # noqa: E402
from mhcgnomes.errors import ParseError  # noqa: E402


def audit_alias_sources(records):
    """Return failure messages for eligible registry records and the installed alias index.

    Pass IPD records through partition_ipd_records first. All supplied names must
    parse identically with aliases off/on; no parsing failures are allowed.
    Every emitted allele alias must
    reach its declared target and reparse identically. Geneless curated targets
    are checked too. ParseError is reported; unexpected exceptions propagate.
    """
    failures, unparseable = [], set()
    for record in records:
        name = f"{record.species}-{record.current}"
        outcomes = []
        for enabled in (False, True):
            try:
                outcomes.append(parse(name, use_allele_aliases=enabled))
            except ParseError:
                outcomes.append(None)
        if outcomes == [None, None]:
            unparseable.add(name)
        elif outcomes[0] != outcomes[1]:
            failures.append(f"Current name changed: {name}: {outcomes}")
    if unparseable:
        failures.append(f"Unparseable registry names: {sorted(unparseable)}")
    print(f"Eligible records checked: {len(records)}; unparseable: {sorted(unparseable)}")
    checked = 0
    for prefix, table in allele_aliases.items():
        for old in table.keys():  # noqa: SIM118 -- keys() preserves original spellings
            new = table[old]
            checked += 1
            try:
                actual = parse(f"{prefix}-{old}", use_allele_aliases=True)
                if "*" not in new:
                    # Geneless curated targets have no standalone parse spelling;
                    # their source gene supplies class context (e.g. Saha-I*27).
                    expected = AlleleWithoutGene.get(prefix, new, mhc_class=actual.mhc_class)
                    if actual != expected:
                        failures.append(f"Geneless alias mismatch: {prefix}-{old} -> {new}")
                    continue
                expected = parse(f"{prefix}-{new}", use_allele_aliases=True)
                if actual != expected or actual != parse(
                    actual.to_string(), use_allele_aliases=True
                ):
                    failures.append(f"Alias mismatch: {prefix}-{old} -> {new}")
            except ParseError as exc:
                failures.append(f"Alias failed: {prefix}-{old} -> {new}: {exc}")
    print(f"Alias keys and reparses checked: {checked}")
    return failures


def main():
    """Read checkout-local pinned sources; print audit failures and return status 0/1."""
    ipd_records, excluded = partition_ipd_records(
        read_ipd_xml(ROOT / ".external-data/IPD-MHC-3.8.0.0.xml")
    )
    for record in excluded:
        print(
            f"Excluded {record['accession']} {record['name']}: {record['status']} "
            f"in {record['status_release']} ({record['status_source']})"
        )
    records = [
        *ipd_records,
        *read_hla_history(ROOT / ".external-data/IMGT-HLA-Allelelist-history-3.66.0.txt"),
    ]
    failures = audit_alias_sources(records)
    identities = registry_identities()
    if {r["accession"] for r in excluded} != {
        r.accession for r in identities.values() if r.status == "abandoned"
    }:
        failures.append("Annotated exclusions and runtime identity inventory differ")
    for identity in identities.values():
        for name in (identity.accession, identity.identifier, *identity.names):
            result = parse(name, use_allele_aliases=True, raise_on_error=False)
            expected = get_registry_identities(name)
            if result is None or result.registry_identities != expected:
                failures.append(f"Registry identity mismatch: {name} -> {expected}")
    print(f"Registry identities and recorded spellings checked: {len(identities)} records")
    for failure in failures:
        print(failure, file=sys.stderr)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
