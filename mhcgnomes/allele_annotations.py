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

valid_functional_annotations = {
    "N",
    "L",
    "S",
    "C",
    "A",
    "Q",
    "G",
    "P",
    "Ps",
    "Sp,"
}



def parse_functional_annotations_from_seq(seq):
    functional_annotations = []

    for annot in valid_functional_annotations:
        n_annot_chars = len(annot)
        if seq[-n_annot_chars:].lower() == annot.lower():
            functional_annotations = [annot] + functional_annotations
            seq = seq[:-n_annot_chars]
    return seq, functional_annotations

def parse_functional_annotations_from_allele_fields(allele_fields):
    if isinstance(allele_fields, str):
        allele_fields = [
            field.strip()
            for field in
            allele_fields.split(":")
        ]
    allele_fields = tuple(allele_fields)

    last_field = allele_fields[-1]

    functional_annotations = []

    for annot in valid_functional_annotations:
        n_annot_chars = len(annot)
        if last_field[-n_annot_chars:].lower() == annot.lower():
            functional_annotations = [annot] + functional_annotations
            last_field = last_field[:-n_annot_chars]

    allele_fields = allele_fields[:-1] + (last_field.strip(),)
    return allele_fields, functional_annotations