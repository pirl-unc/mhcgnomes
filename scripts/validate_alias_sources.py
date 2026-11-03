#!/usr/bin/env python3
"""Audit current registry identities and every generated alias against the runtime parser.

Run after combine_allele_aliases.sh. Inputs are the pinned allele-aliases download
group. The single known unparseable source accession is reported explicitly;
new failures or repaired exceptions fail the audit for review.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mhcgnomes/data"))
from combine_allele_aliases import read_hla_history, read_ipd_xml  # noqa: E402

from mhcgnomes import AlleleWithoutGene, parse  # noqa: E402
from mhcgnomes.data import allele_aliases  # noqa: E402
from mhcgnomes.errors import ParseError  # noqa: E402

# NHP10764, organism Papio hamadryas. The source has no cross-reference.
# Do not guess whether DP1 is a locus or typo: https://github.com/pirl-unc/mhcgnomes/issues/243
EXPECTED_UNPARSEABLE = {"Paha-DP1*06:01"}


def audit_alias_sources(records):
    """Return failure messages for registry records and the installed alias index.

    Current names must parse identically with aliases off/on; both failures are
    permitted only for EXPECTED_UNPARSEABLE. Every emitted allele alias must
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
    if unparseable != EXPECTED_UNPARSEABLE:
        failures.append(f"Unparseable registry names changed: {sorted(unparseable)}")
    print(f"Current records checked: {len(records)}; known unparseable: {sorted(unparseable)}")
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
    records = [
        *read_ipd_xml(ROOT / ".external-data/IPD-MHC-3.8.0.0.xml"),
        *read_hla_history(ROOT / ".external-data/IMGT-HLA-Allelelist-history-3.66.0.txt"),
    ]
    failures = audit_alias_sources(records)
    for failure in failures:
        print(failure, file=sys.stderr)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
