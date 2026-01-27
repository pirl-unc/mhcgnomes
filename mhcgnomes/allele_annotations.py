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

# N = null
# L = low surface expression
# S = soluble / secreted
# C = cytoplasm / not on the surface
# A = aberrant expression
# Q = questionable
# G = group of alleles with identical peptide binding region
# P = same as G?
# Ps = pseudogene
# Sp = splice variant
# For more information see:
# - http://hla.alleles.org/nomenclature/naming.html
# - http://hla.alleles.org/alleles/g_groups.html
# - https://www.ebi.ac.uk/ipd/mhc/group/NHP/page/nomenclature/

valid_functional_annotations = {"N", "L", "S", "C", "A", "Q", "G", "P", "Ps", "Sp"}
_sorted_functional_annotations = sorted(valid_functional_annotations, key=len, reverse=True)


def _has_two_digit_prefix(seq, annot_len):
    if len(seq) < annot_len + 2:
        return False
    return seq[-annot_len - 1].isdigit() and seq[-annot_len - 2].isdigit()


def check_for_workshop_prefix(seq):
    """
    Returns either original sequence and empty list or trims "W"
    from the front of the sequence.
    """
    if len(seq) <= 2:
        return seq, []

    # workshop alleles start with W
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
