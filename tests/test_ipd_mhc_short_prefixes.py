from pathlib import Path

import pytest

from mhcgnomes import parse


def _load_ipd_prefix_examples():
    """
    Build one representative raw allele string per short species prefix from
    the local IPD-MHC protein dump.
    """
    path = Path(__file__).with_name("MHC_prot.fasta")
    examples = {}
    for line in path.read_text().splitlines():
        if not line.startswith(">"):
            continue
        parts = line[1:].split()
        if len(parts) < 2:
            continue
        raw = parts[1]
        if "-" not in raw:
            continue
        prefix = raw.split("-", 1)[0]
        examples.setdefault(prefix, raw)
    return sorted(examples.items())


IPD_PREFIX_EXAMPLES = _load_ipd_prefix_examples()


def test_local_ipd_prefix_fixture_is_nonempty():
    assert IPD_PREFIX_EXAMPLES


@pytest.mark.parametrize("prefix, raw_string", IPD_PREFIX_EXAMPLES)
def test_ipd_mhc_short_prefix_example_parses_without_species(prefix, raw_string):
    result = parse(raw_string, raise_on_error=False)
    assert result is not None, f"Failed to parse IPD-MHC example for {prefix}: {raw_string}"
