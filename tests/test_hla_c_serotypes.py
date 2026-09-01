"""
The HLA-C serological specificities, and why the table stopped at Cw10.

`HLA-Cw16` did not parse, though `Cw15` and `Cw17` did and 1,624 rows of the
hitlist corpus use it. The obstacle was that the shipped `hla_dictionary.xlsx`
does not support any of them: every `C*16` row in it reads

    WHO Assigned Type    = "-"
    Expert Assigned Type = "Undefined"

and its WHO column stops at Cw10. That is not the dictionary disagreeing --
it is a snapshot taken before the specificities existed.

The WHO Nomenclature Committee's own file settles it. `wmda/hla_nom.txt`
(IPD-IMGT/HLA 3.65.0, 2026-07-14, "author: WHO, Steven G. E. Marsh") assigns
Cw12, Cw14, Cw15, Cw16, Cw17 and Cw18 on 2026-01-28, the date of the 2026 HLA
Nomenclature Report.

https://github.com/pirl-unc/mhcgnomes/issues/153
https://raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/wmda/hla_nom.txt
"""

from pathlib import Path

import pytest
import yaml

from mhcgnomes import Serotype, parse

from .common import eq_, ok_

DATA = Path(__file__).parent.parent / "mhcgnomes" / "data"
RUNTIME_SEROTYPES = yaml.safe_load((DATA / "serotypes.yaml").read_text())["HLA"]

# hla_nom.txt, the Cw block, minus the four-digit associated antigens. The
# first ten were assigned between 1975 and 1987; the six added in 2026 are the
# ones the shipped dictionary cannot know about.
WHO_RECOGNISED = [
    "Cw1",
    "Cw2",
    "Cw3",
    "Cw4",
    "Cw5",
    "Cw6",
    "Cw7",
    "Cw8",
    "Cw9",
    "Cw10",
    "Cw12",
    "Cw14",
    "Cw15",
    "Cw16",
    "Cw17",
    "Cw18",
]

# Cw11 was assigned on 1987-11-21 and deleted on 1991-11-14 for "Sequence
# error"; Cw13 has no line in hla_nom.txt at all. Both absences are correct,
# and neither should quietly acquire a row.
WITHDRAWN_OR_NEVER_ASSIGNED = ["Cw11", "Cw13"]


@pytest.mark.parametrize("serotype", WHO_RECOGNISED)
def test_every_who_recognised_c_specificity_parses(serotype):
    result = parse(f"HLA-{serotype}", required_result_types=[Serotype])
    eq_(result.name, serotype)


@pytest.mark.parametrize("serotype", WITHDRAWN_OR_NEVER_ASSIGNED)
def test_a_withdrawn_or_unassigned_specificity_does_not_parse(serotype):
    eq_(parse(f"HLA-{serotype}", raise_on_error=False), None)


def test_cw16_names_the_associated_antigens_who_assigns_it():
    """
    wmda/rel_ser_ser.txt reads `Cw;16;;1601/1602`, and rel_dna_ser.txt maps
    C*16:01 to 1601 and C*16:02 to 1602.
    """
    result = parse("HLA-Cw16", required_result_types=[Serotype])
    eq_(sorted(allele.to_string() for allele in result.alleles), ["HLA-C*16:01", "HLA-C*16:02"])


def test_the_c_serotype_table_is_exactly_the_who_list_plus_cw4c():
    """
    Pinned so that a row added without a source has to come here and say what
    assigns it. Cw4c is the one entry with no line in hla_nom.txt: it comes
    from the dictionary's own WHO column, which spells it that way.
    """
    ours = sorted(name for name in RUNTIME_SEROTYPES if name.startswith("C"))
    eq_(ours, sorted([*WHO_RECOGNISED, "Cw4c"]))


def test_the_shipped_dictionary_still_cannot_support_the_2026_specificities():
    """
    The reason this row is hand-curated rather than generated. If this starts
    failing, the dictionary has been refreshed past the 2026 report and #156's
    fifteen carried-forward rows can be regenerated instead.
    """
    pd = pytest.importorskip("pandas")
    pytest.importorskip("openpyxl")
    frame = pd.read_excel(DATA / "hla_dictionary.xlsx")
    c16 = frame[frame["HLA Allele"].astype(str).str.startswith("C*16")]
    ok_(len(c16) > 0, "the dictionary no longer carries C*16 rows at all")
    eq_(sorted(set(c16["WHO Assigned Type"].astype(str))), ["-"])
    assigned = {str(v) for v in frame["WHO Assigned Type"].dropna()}
    for serotype in ["Cw12", "Cw14", "Cw15", "Cw16", "Cw17", "Cw18"]:
        ok_(serotype not in assigned, f"the dictionary now assigns {serotype}; regenerate")
