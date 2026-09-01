"""
The serotype table against the script that generates it.

`serotypes_generated.yaml` is an intermediate artifact; `serotypes.yaml` is
what the runtime loads. They had drifted, and the drift was not the one it
looked like: the generator deliberately preserves rows the dictionary lacks,
so regenerating does not lose them. What it did lose was a curation fix.

https://github.com/pirl-unc/mhcgnomes/issues/156
"""

import sys
from pathlib import Path

import pytest
import yaml

pd = pytest.importorskip("pandas")
# pandas needs openpyxl to read .xlsx. In the dev extra so these run in CI; the
# skip is for a checkout that installed the package without it.
pytest.importorskip("openpyxl")
DATA = Path(__file__).parent.parent / "mhcgnomes" / "data"
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
generator = pytest.importorskip("generate_serotypes_from_hla_dictionary")

from .common import eq_, ok_  # noqa: E402

DICTIONARY = DATA / "hla_dictionary.xlsx"

# The dictionary was gitignored by a blanket `*.xlsx` rule until #156, so it
# existed only on whichever machine last regenerated the table. It is tracked
# now; the guard stays so a checkout without it degrades to a skip rather than
# an error.
needs_dictionary = pytest.mark.skipif(
    not DICTIONARY.exists(), reason="hla_dictionary.xlsx is not present in this checkout"
)


def _mappings():
    df = pd.read_excel(DICTIONARY)
    df.columns = [c.strip() for c in df.columns]
    return generator.build_serotype_mappings(df)


def test_regenerating_reproduces_the_runtime_table():
    """
    The property that keeps the two files from drifting. Runs the same
    transformation the script does and compares against what ships.
    """
    generated = yaml.safe_load((DATA / "serotypes_generated.yaml").read_text())["HLA"]
    runtime = yaml.safe_load((DATA / "serotypes.yaml").read_text())["HLA"]
    eq_(sorted(generated), sorted(runtime))
    differing = sorted(k for k in generated if generated[k] != runtime[k])
    eq_(differing, [], f"generated and runtime disagree on: {differing}")


@needs_dictionary
def test_the_curated_exclusion_survives_regeneration():
    """
    A*24:18 carries the dual WHO type "A24(9)/A3", so parse_serotype puts it in
    both. The dictionary's own Comments column says "short A24 with most A3 and
    A9 reactive; NN: A24", so A24 is the assignment. Curation removed it from
    A3, and regenerating used to put it back.
    """
    mappings = _mappings()
    ok_("A*2418" not in mappings.get("A3", []), "A*2418 is back in A3")
    ok_("A*2418" in mappings.get("A24", []), "A*2418 should still be an A24 allele")


@needs_dictionary
def test_every_exclusion_is_one_the_dictionary_actually_asserts():
    """
    An exclusion for a pair the dictionary never produces is dead weight that
    will outlive whatever it was for.
    """
    df = pd.read_excel(DICTIONARY)
    df.columns = [c.strip() for c in df.columns]
    asserted = set()
    for _, row in df.iterrows():
        value = row.get("WHO Assigned Type", "")
        if pd.isna(value):
            continue
        allele = generator.normalize_allele_name(row["HLA Allele"])
        for serotype in generator.parse_serotype(str(value)):
            asserted.add((serotype, allele))
    stale = sorted(p for p in generator.CURATED_EXCLUSIONS if p not in asserted)
    eq_(stale, [], f"exclusions for pairs the dictionary never assigns: {stale}")


@needs_dictionary
def test_rows_the_dictionary_does_not_support_are_still_carried():
    """
    The generator preserves serotypes the dictionary has no row for -- the C
    locus above Cw10, the DP workshop specificities, the B17 splits. That is
    deliberate, and #153 turns on it: Cw15 and Cw17 are among them, so they are
    not evidence about what the dictionary says.
    """
    mappings = _mappings()
    runtime = yaml.safe_load((DATA / "serotypes.yaml").read_text())["HLA"]
    unsupported = sorted(set(runtime) - set(mappings))
    for expected in ["Cw15", "Cw17", "DPw1", "B17.1", "DR5"]:
        ok_(expected in unsupported, f"{expected} is no longer in the carried-forward set")
