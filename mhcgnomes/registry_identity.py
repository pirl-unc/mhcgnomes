"""Accession identities for the explicitly curated IPD-MHC record inventory.

This is a names-and-status index, not a sequence catalog or validity check.
Unknown names return no identity; they can still be parsed by the general parser.
"""

import json
from dataclasses import dataclass
from functools import cache
from types import MappingProxyType

from .data import get_path


@dataclass(frozen=True, eq=False)
class RegistryIdentity:
    """One registry accession with its latest recorded name, aliases and status.

    Equality and hashing use the namespaced identifier. ``canonical_name`` means
    latest recorded designation, including for abandoned records; it does not
    assert an active allele, a valid molecule, or a known replacement.
    ``locus`` is the registry's designation, not a new ontology gene.
    """

    registry: str
    accession: str
    canonical_name: str
    aliases: tuple[str, ...]
    status: str
    species_name: str
    mhc_class: str
    locus: str
    source_release: str
    status_source: str
    record_source: str

    def __post_init__(self):
        object.__setattr__(self, "aliases", tuple(self.aliases))

    @property
    def identifier(self):
        """Stable namespaced accession, e.g. IPD-MHC:NHP00355."""
        return f"{self.registry}:{self.accession}"

    @property
    def names(self):
        """Latest recorded name followed by distinct historical names."""
        return (self.canonical_name, *self.aliases)

    def __eq__(self, other):
        return isinstance(other, RegistryIdentity) and self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def to_record(self):
        """Return fresh flat metadata for table/CLI serialization."""
        return {
            "registry_id": self.identifier,
            "registry_accession": self.accession,
            "registry_name": self.canonical_name,
            "registry_status": self.status,
            "registry_aliases": self.aliases,
            "registry_source": self.record_source,
        }


def build_registry_index(identities, include_aliases=True):
    """Return a read-only mapping of lookup keys to sorted identity tuples.

    Keys ignore case and surrounding whitespace, preserving field boundaries.
    Accessions outrank names and latest names outrank history. Equal-priority
    collisions retain every candidate, ordered by identifier. Duplicate accessions
    raise ValueError. Historical names are included only when include_aliases is true.
    """
    identities = tuple(identities)
    if len({r.identifier for r in identities}) != len(identities):
        raise ValueError("Duplicate registry identifiers")
    index, priorities = {}, {}
    for identity in identities:
        values = [(identity.identifier, 2), (identity.accession, 2), (identity.canonical_name, 1)]
        if include_aliases:
            values.extend((name, 0) for name in identity.aliases)
        for value, priority in values:
            key = value.strip().casefold()
            if priority > priorities.get(key, -1):
                index[key] = {identity}
                priorities[key] = priority
            elif priority == priorities[key]:
                index[key].add(identity)
    return MappingProxyType(
        {key: tuple(sorted(rows, key=lambda r: r.identifier)) for key, rows in index.items()}
    )


@cache
def registry_identities():
    """Return the cached read-only mapping of namespaced IDs to curated identities.

    Coverage is the 76 IPD-MHC accessions abandoned in release 3.7.0.0 plus two
    related public accessions needed to represent name collisions. This is not
    the complete IPD registry. Invalid bundled data raises ValueError;
    file/JSON errors propagate.
    """
    with open(get_path("registry_allele_identities.json"), encoding="utf-8") as stream:
        rows = json.load(stream)
    identities = [RegistryIdentity(**{**row, "aliases": tuple(row["aliases"])}) for row in rows]
    build_registry_index(identities)
    return MappingProxyType({identity.identifier: identity for identity in identities})


@cache
def _registry_index(include_aliases):
    return build_registry_index(registry_identities().values(), include_aliases=include_aliases)


def get_registry_identities(value, include_aliases=True):
    """Resolve a name or accession to a sorted tuple of RegistryIdentity candidates.

    Accepts full species-prefixed names, raw MHC accession IDs and namespaced
    IDs. Matching ignores case and surrounding whitespace only. Historical
    names resolve by default in this explicit registry-lookup API; use
    include_aliases=False to match only accessions and latest recorded names.
    Latest names outrank history; duplicate latest names retain both accessions.
    Unknown strings return an empty tuple. Non-string inputs raise TypeError.
    No network access or biological inference.
    """
    if not isinstance(value, str):
        raise TypeError(f"expected str, got {type(value).__name__}")
    return _registry_index(bool(include_aliases)).get(value.strip().casefold(), ())


def get_registry_identity(value, include_aliases=True):
    """Return the unique identity, or None for unknown or ambiguous recorded names.

    Uses get_registry_identities' matching/precedence and input contract. Use that
    plural API to inspect ambiguity; accession IDs are always definitive.
    """
    identities = get_registry_identities(value, include_aliases=include_aliases)
    return identities[0] if len(identities) == 1 else None
