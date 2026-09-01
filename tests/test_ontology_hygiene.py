import re
from pathlib import Path

import yaml

from mhcgnomes import Species

SPECIES_PATH = Path(__file__).parent.parent / "mhcgnomes" / "data" / "species.yaml"
GENE_ALIASES_PATH = Path(__file__).parent.parent / "mhcgnomes" / "data" / "gene_aliases.yaml"

# These are unusual but source-backed canonical names already exercised by tests
# and external nomenclature datasets.
ALLOWLISTED_MULTI_LOWERCASE_GENES = {
    "B-F-minor",
    "DQA2like",
    "DQB2like",
    "Mill1",
    "Mill2",
}

ALLOWLISTED_LIKE_GENES = {
    "DQA2like",
    "DQB2like",
}

FORBIDDEN_GENE_PATTERNS = (
    re.compile(r"^LOC\d+$", re.IGNORECASE),
    re.compile(r"^ENS[A-Z0-9]*\d+$", re.IGNORECASE),
)

FORBIDDEN_GENE_SUBSTRINGS = (
    "scaffold",
    "unplaced",
    "protein",
    "chain",
)


def load_yaml(path: Path):
    with path.open() as fd:
        return yaml.safe_load(fd)


def iter_raw_canonical_genes():
    species_data = load_yaml(SPECIES_PATH)
    for latin_name, species_info in species_data.items():
        genes = species_info.get("genes", {}) or {}
        for mhc_class, members in genes.items():
            if isinstance(members, list):
                for gene in members:
                    yield latin_name, mhc_class, None, str(gene)
            else:
                for locus, locus_genes in members.items():
                    for gene in locus_genes:
                        yield latin_name, mhc_class, str(locus), str(gene)


def test_canonical_genes_do_not_look_like_model_records_or_free_text():
    bad = []
    for latin_name, mhc_class, locus, gene in iter_raw_canonical_genes():
        lower = gene.lower()
        if any(ch.isspace() for ch in gene):
            bad.append((latin_name, mhc_class, locus, gene, "whitespace"))
            continue
        if lower.startswith("mhc"):
            bad.append((latin_name, mhc_class, locus, gene, "mhc-prefix"))
            continue
        if any(pattern.match(gene) for pattern in FORBIDDEN_GENE_PATTERNS):
            bad.append((latin_name, mhc_class, locus, gene, "model-record"))
            continue
        for substring in FORBIDDEN_GENE_SUBSTRINGS:
            if substring in lower:
                bad.append((latin_name, mhc_class, locus, gene, substring))
                break
    assert not bad, bad


def test_only_allowlisted_canonical_genes_have_long_lowercase_runs():
    nonstandard = sorted(
        {
            gene
            for _latin_name, _mhc_class, _locus, gene in iter_raw_canonical_genes()
            if re.search(r"[a-z]{3,}", gene)
        }
    )
    assert nonstandard == sorted(ALLOWLISTED_MULTI_LOWERCASE_GENES)


def test_only_allowlisted_canonical_genes_use_like_suffix_style_names():
    like_genes = sorted(
        {
            gene
            for _latin_name, _mhc_class, _locus, gene in iter_raw_canonical_genes()
            if "like" in gene.lower()
        }
    )
    assert like_genes == sorted(ALLOWLISTED_LIKE_GENES)


def test_gene_alias_targets_resolve_to_runtime_gene_or_locus():
    alias_data = load_yaml(GENE_ALIASES_PATH)
    bad = []
    for species_key, aliases in alias_data.items():
        species = Species.get(species_key)
        if species is None:
            bad.append((species_key, None, None, "unknown species key"))
            continue
        for alias, target in aliases.items():
            gene_target = species.find_matching_gene_name(target)
            locus_target = species.find_matching_class2_locus_name(target)
            if gene_target is None and locus_target is None:
                bad.append((species_key, alias, target, "unresolved target"))
    assert not bad, bad


def test_gene_alias_entries_do_not_use_model_record_style_strings():
    alias_data = load_yaml(GENE_ALIASES_PATH)
    bad = []
    for species_key, aliases in alias_data.items():
        for alias, target in aliases.items():
            for role, value in (("alias", alias), ("target", target)):
                lower = value.lower()
                if any(ch.isspace() for ch in value):
                    bad.append((species_key, role, value, "whitespace"))
                    continue
                if any(pattern.match(value) for pattern in FORBIDDEN_GENE_PATTERNS):
                    bad.append((species_key, role, value, "model-record"))
                    continue
                for substring in FORBIDDEN_GENE_SUBSTRINGS:
                    if substring in lower:
                        bad.append((species_key, role, value, substring))
                        break
    assert not bad, bad


def test_every_whitelisted_species_key_has_a_consumer():
    """
    `SPECIES_ENTRY_KEYS` exists so a misspelled key cannot load silently while
    the YAML asserts something the runtime never read. Whitelisting a key that
    nothing reads has the same effect with extra confidence: `alias` and
    `haplotype prefix` sat there unread until #139.

    So every accepted key must be fetched somewhere in species.py.
    """
    from mhcgnomes.species import SPECIES_ENTRY_KEYS

    source = (Path(__file__).parent.parent / "mhcgnomes" / "species.py").read_text()
    # Match the call without its closing paren, since several are fetched with
    # a default: species_info.get("genes", {}).
    unread = sorted(key for key in SPECIES_ENTRY_KEYS if f'species_info.get("{key}"' not in source)
    assert unread == [], (
        f"species.yaml keys accepted but never read: {unread}. Either read them or "
        f"drop them from SPECIES_ENTRY_KEYS -- see issue #139."
    )


def test_dropped_keys_are_gone_from_the_data_too():
    """A key removed from the whitelist must not linger in species.yaml, or
    the file stops loading."""
    from mhcgnomes.species import SPECIES_ENTRY_KEYS

    entries = load_yaml(SPECIES_PATH)
    used = {key for entry in entries.values() for key in entry}
    unexpected = sorted(used - set(SPECIES_ENTRY_KEYS))
    assert unexpected == [], f"species.yaml uses keys the loader rejects: {unexpected}"
