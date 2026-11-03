# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# What each allele-name suffix means, for callers that report why an allele was
# flagged (#217). Each description paraphrases the authority quoted beside it.
annotation_descriptions = {
    # https://hla.alleles.org/pages/nomenclature/naming_alleles/ -- "Alleles
    # that have been shown not to be expressed - `Null` alleles - have been
    # given the suffix `N`." IPD-MHC's NHP and BoLA pages use N for an allele
    # "characterised by a premature stop codon".
    "N": "null allele: not expressed",
    # https://hla.alleles.org/pages/nomenclature/assigning_suffixes/ for L, S, C,
    # A and Q. L: "shown to have `Low` cell surface expression when compared to
    # normal levels".
    "L": "low cell-surface expression",
    # S: "a protein which is expressed as a soluble, `Secreted` molecule but is
    # not present on the cell surface".
    "S": "secreted soluble protein, not on the cell surface",
    # C: "proteins that are present in the `Cytoplasm` and not on the cell
    # surface".
    "C": "cytoplasmic protein, not on the cell surface",
    # A: "`Aberrant` expression where there is some doubt as to whether a
    # protein is actually expressed".
    "A": "aberrant expression: whether the protein is expressed is in doubt",
    # Q: "alleles that are considered to have questionable expression".
    "Q": "questionable expression",
    # https://hla.alleles.org/pages/p&g_groups/g_groups/ -- "identical
    # nucleotide sequences across the exons encoding the peptide binding
    # domains (exon 2 and 3 for HLA class I and exon 2 only for HLA class II".
    "G": "G group: identical nucleotide sequence across the peptide-binding-domain exons",
    # https://hla.alleles.org/pages/p&g_groups/p_groups/ -- "nucleotide
    # sequences that encode the same protein sequence for the peptide binding
    # domains". Coarser than G: same protein, not same nucleotides.
    "P": "P group: identical protein sequence in the peptide-binding domain",
    # https://www.ebi.ac.uk/ipd/mhc/group/NHP/nomenclature/ -- "Ps is used as
    # prefix and suffix, and indicates when the described gene is a
    # pseudogene."
    "Ps": "pseudogene",
    # Same page: "Sp is used to indicate that the described allele is a splice
    # variant."
    "Sp": "splice variant",
    # https://www.ebi.ac.uk/ipd/mhc/group/BoLA/nomenclature/ explicitly
    # assigns SV to splice variants (e.g. BoLA-NC1*004:01SV).
    "SV": "splice variant",
}

valid_functional_annotations = set(annotation_descriptions)
_sorted_functional_annotations = sorted(valid_functional_annotations, key=len, reverse=True)

# Annotations that bear on whether the protein reaches the cell surface, by
# what they say about it. Read by Allele.cell_surface_expression.
_NOT_ON_CELL_SURFACE = frozenset({"N", "S", "C", "Ps"})
_CELL_SURFACE_EXPRESSION_UNCERTAIN = frozenset({"A", "Q"})
_LOW_CELL_SURFACE_EXPRESSION = frozenset({"L"})


def _has_two_digit_prefix(seq, annot_len):
    if len(seq) < annot_len + 2:
        return False
    return seq[-annot_len - 1].isdigit() and seq[-annot_len - 2].isdigit()


def check_for_workshop_prefix(seq):
    """
    Returns either original sequence and empty list or trims "W"
    from the front of the sequence.

    Despite the name, the W on allele fields that mhcgnomes meets is not the
    HLA "workshop" w, which marked provisional serological specificities
    (HLA-Cw, Bw4) and never an allele field. It is IPD-MHC's: "W or w is used
    to indicate when an allele cannot be defined to a locus/gene yet"
    (https://www.ebi.ac.uk/ipd/mhc/group/NHP/nomenclature/), as in
    Mamu-DRB*W003:07.
    """
    if len(seq) <= 2:
        return seq, []

    # an allele not yet assigned to a locus starts with W
    if seq[0].lower() == "w" and seq[1].isdigit() and seq[2].isdigit():
        return seq[1:], ["W"]
    else:
        return seq, []


def peel_suffix_annotations(seq):
    """
    Remove suffix functional annotations from end of sequence,
    return string without annotations and list of parsed annotations.
    """
    if len(seq) < 3:
        return seq, []

    functional_annotations = []
    while True:
        found = False
        for annot in _sorted_functional_annotations:
            n_annot_chars = len(annot)
            if not _has_two_digit_prefix(seq, n_annot_chars):
                continue
            if seq[-n_annot_chars:].lower() == annot.lower():
                functional_annotations = [annot, *functional_annotations]
                seq = seq[:-n_annot_chars]
                found = True
                break
        if not found:
            break
    return seq, functional_annotations


def parse_annotations_from_seq(seq):
    """
    Returns pair of:
        - str of remaining sequence to parse
        - list of annotations
    """
    seq, prefix_annotations = check_for_workshop_prefix(seq)
    seq, suffix_annotations = peel_suffix_annotations(seq)
    return seq, tuple(prefix_annotations), tuple(suffix_annotations)


def parse_annotations_from_allele_fields(allele_fields):
    """
    Returns tuple:
        - tuple of allele fields without any annotations
        - prefix annotations (currently only "W")
        - suffix annotations
    """
    if isinstance(allele_fields, str):
        allele_fields = [field.strip() for field in allele_fields.split(":")]
    allele_fields = list(allele_fields)

    allele_fields[0], prefix_annotations = check_for_workshop_prefix(allele_fields[0])

    allele_fields[-1], suffix_annotations = peel_suffix_annotations(allele_fields[-1])
    return (tuple(allele_fields), tuple(prefix_annotations), tuple(suffix_annotations))
