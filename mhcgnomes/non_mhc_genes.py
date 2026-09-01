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

"""
Gene names that turn up in MHC-region downloads but do not name an MHC
molecule.

Two consumers, which is why this is its own module rather than living beside
either of them:

  * `parse_gene_class` reports them as `non_mhc=True` instead of guessing.
  * The parser refuses to split them into a locus plus an allele suffix.

The second matters more than it looks. "Kdm5d" under a mouse species used to
parse as `H2-K*dm5d` -- the valid mouse locus K, plus everything after it read
as an allele -- and `Daxx` as `H2-D*axx`. Both look syntactically valid and get
dispatched onward, so the failure is silent. See issue #133.
"""

# Maps a normalized name to the canonical gene it stands for. Several entries
# are historic aliases: RING4/PSF1/HAM1/ABCB2 all named TAP1 before the
# transporter genes were renamed.
NON_MHC_REGION_GENE_NAMES = {
    "ABCB2": "TAP1",
    "ABCB3": "TAP2",
    "B2M": "B2M",
    "CIITA": "CIITA",
    "HAM1": "TAP1",
    "HAM2": "TAP2",
    "HM13": "HM13",
    "PRR3": "PRR3",
    "PSF1": "TAP1",
    "PSF2": "TAP2",
    "RING11": "TAP2",
    "RING4": "TAP1",
    "TAP-L": "TAP-L",
    "TAPL": "TAP-L",
    "TAP1": "TAP1",
    "TAP2": "TAP2",
    "TAPBP": "TAPBP",
    # Reported in #133 from a UniProt MHC-region download. All five are
    # HGNC-approved symbols for proteins that are not MHC molecules; three of
    # them lie inside the MHC region, which is why they arrive in these files
    # at all. Checked against https://rest.genenames.org/search/symbol/...
    "ARHGAP45": "ARHGAP45",  # HGNC:17102, Rho GTPase activating protein 45
    "ATP6V1G2": "ATP6V1G2",  # HGNC:862, V-ATPase subunit G2, MHC class III
    "COL11A2": "COL11A2",  # HGNC:2187, collagen XI alpha 2, MHC class II region
    "DAXX": "DAXX",  # HGNC:2681, death domain associated protein
    "KDM5D": "KDM5D",  # HGNC:11115, lysine demethylase 5D
}


def normalize_non_mhc_gene_name(gene_name):
    """
    The spelling used as a key above.

    Deliberately the same rule `parse_gene_class` already applied to its gene
    token, so moving the table here changes no behaviour: strip whitespace and
    trailing punctuation, then upper-case.
    """
    if not gene_name:
        return ""
    return str(gene_name).strip().strip(",;").upper()


def is_non_mhc_gene_name(gene_name):
    return normalize_non_mhc_gene_name(gene_name) in NON_MHC_REGION_GENE_NAMES
