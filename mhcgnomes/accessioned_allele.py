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

import re
from dataclasses import dataclass

from .gene import Gene
from .mhc_class_helpers import is_class1, is_class2, valid_class_restrictions
from .result_with_mhc_class import ResultWithMhcClass
from .species import Species

# Supported external sequence/structure database namespaces for explicit
# accession-backed MHC identifiers (#309, #326, #332), e.g.:
#   AnasPlatyrhynchos-UAA*uniprot:Q6I7L2
#   Saha-classI*uniprot:G3V1L5
#   Saha-uniprot:G3V1L5
VALID_ACCESSION_SOURCES = frozenset(
    {
        "uniprot",
        "genbank",
        "refseq",
        "ena",
        "embl",
        "ddbj",
        "pdb",
    }
)

# Official UniProt primary accession format (optionally with -N isoform suffix;
# https://www.uniprot.org/help/accession_numbers).
UNIPROT_ACCESSION_RE = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-\d+)?$"
)

# NCBI RefSeq accession format (e.g. NP_001234.1, XP_012345678.2, NM_002116.8).
_REFSEQ_ACCESSION_RE = re.compile(r"^[A-Z]{2}_\d+(?:\.\d+)?$")

# INSDC (GenBank / ENA / EMBL / DDBJ) nucleotide or protein accession format
# (e.g. U12345, GQ411457.1, AAA12345.1, KAA1234567.1).
_INSDC_ACCESSION_RE = re.compile(r"^[A-Z]{1,6}\d{4,}(?:\.\d+)?$")

# RCSB PDB 4-character entry ID with optional chain suffix (e.g. 1HSA, 1HSA_A).
_PDB_ACCESSION_RE = re.compile(r"^([0-9][A-Za-z0-9]{3})(?:([_:])([A-Za-z0-9]+))?$")


def normalize_accession(source: str, accession: str) -> tuple[str, str] | None:
    """Validate and canonicalize an ``(accession_source, accession)`` pair.

    Returns ``(canonical_source, canonical_accession)`` or ``None`` if the
    database namespace is unsupported or the accession does not conform to
    that database's syntax.
    """
    if not isinstance(source, str) or not isinstance(accession, str):
        return None
    source_norm = source.strip().lower()
    if source_norm not in VALID_ACCESSION_SOURCES:
        return None
    acc = accession.strip()
    if not acc:
        return None

    if source_norm == "uniprot":
        acc_upper = acc.upper()
        if UNIPROT_ACCESSION_RE.fullmatch(acc_upper):
            return (source_norm, acc_upper)
        return None

    if source_norm == "refseq":
        acc_upper = acc.upper()
        if _REFSEQ_ACCESSION_RE.fullmatch(acc_upper):
            return (source_norm, acc_upper)
        return None

    if source_norm in {"genbank", "ena", "embl", "ddbj"}:
        acc_upper = acc.upper()
        if _INSDC_ACCESSION_RE.fullmatch(acc_upper):
            return (source_norm, acc_upper)
        return None

    if source_norm == "pdb":
        match = _PDB_ACCESSION_RE.fullmatch(acc)
        if not match:
            return None
        pdb_id = match.group(1).upper()
        if match.group(2) is not None:
            return (source_norm, f"{pdb_id}{match.group(2)}{match.group(3)}")
        return (source_norm, pdb_id)

    return None


@dataclass(eq=False, repr=False, frozen=True, init=False)
class AccessionedAllele(ResultWithMhcClass):
    """
    Sequence-accessioned MHC allele without an assigned IPD/IMGT allele name.

    Represents explicit database-backed identifiers such as:
      - ``AnasPlatyrhynchos-UAA*uniprot:Q6I7L2`` (with a curated ontology gene)
      - ``Saha-classI*uniprot:G3V1L5`` (gene-less with known MHC class)
      - ``Saha-uniprot:G3V1L5`` (gene-less without known MHC class)

    Unlike :class:`Allele`, the identifier is backed by an external sequence or
    structure accession rather than numeric nomenclature fields, so
    :meth:`restrict_allele_fields` leaves it unchanged.
    """

    accession_source: str = ""
    accession: str = ""
    gene: Gene | None = None

    def __init__(
        self,
        species: Species,
        accession_source: str,
        accession: str,
        gene: Gene | None = None,
        mhc_class: str | None = None,
        raw_string: str | None = None,
    ):
        if gene is not None and mhc_class is None:
            mhc_class = gene.mhc_class
        ResultWithMhcClass.__init__(
            self,
            species=species,
            mhc_class=mhc_class,
            raw_string=raw_string,
        )
        self._set_field(self, "accession_source", accession_source)
        self._set_field(self, "accession", accession)
        self._set_field(self, "gene", gene)

    @property
    def gene_name(self) -> str | None:
        """Canonical short gene name, or ``None`` when no gene is assigned."""
        return self.gene.name if self.gene is not None else None

    @property
    def name(self) -> str:
        """Namespaced accession string (e.g. ``'uniprot:Q6I7L2'``)."""
        return f"{self.accession_source}:{self.accession}"

    @property
    def pseudogene_status(self):
        """Ontology pseudogene status from the associated gene, or ``None``."""
        if self.gene is None:
            return None
        return self.gene.pseudogene_status

    @property
    def is_pseudogene(self) -> bool:
        """Whether the associated ontology gene is curated as a pseudogene."""
        return self.pseudogene_status is True

    @property
    def is_mutant(self) -> bool:
        """Accessioned sequence records do not carry synthetic mutation annotations."""
        return False

    @property
    def mutations(self):
        """Empty tuple for interface parity with :class:`Allele`."""
        return ()

    @property
    def annotations(self):
        """Empty tuple for interface parity with :class:`Allele`."""
        return ()

    @property
    def is_allele_group(self) -> bool:
        """False: an accession identifies a specific sequence record, not a lineage group."""
        return False

    def to_string(self, include_species=True, use_old_species_prefix=False) -> str:
        """Render canonical whitespace-free, lossless accession-backed identifier (#309, #326, #332).

        - With a curated gene: ``<Species>-<Gene>*<source>:<accession>``
          (analogous to ``HLA-A*02:01``).
        - Without a gene, with known MHC class (``I``, ``Ia``..``Id``, ``II``,
          ``IIa``, ``IIb``): ``<Species>-class<mhc_class>*<source>:<accession>``
          (e.g. ``Saha-classI*uniprot:G3V1L5``, ``Saha-classII*uniprot:G3V1L5``).
        - Without a gene and without a known MHC class:
          ``<Species>-<source>:<accession>`` (e.g. ``Saha-uniprot:G3V1L5``).
        """
        if self.gene is not None:
            gene_str = self.gene.to_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix,
            )
            return f"{gene_str}*{self.accession_source}:{self.accession}"

        species_str = self.species.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix,
        )
        if self.mhc_class in valid_class_restrictions:
            class_slot = f"class{self.mhc_class}*{self.accession_source}:{self.accession}"
            return f"{species_str}-{class_slot}" if species_str else class_slot
        if species_str:
            return f"{species_str}-{self.accession_source}:{self.accession}"
        return f"{self.accession_source}:{self.accession}"

    def compact_string(self, include_species=False, use_old_species_prefix=False) -> str:
        """Compact representation omitting the species prefix by default."""
        return self.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix,
        )

    def restrict_allele_fields(self, num_fields, drop_annotations=False, drop_mutations=False):
        """Leave accession-backed identifiers unchanged (atomic sequence reference)."""
        return self

    def to_record(self):
        """Serialize species, optional gene, MHC class, and accession metadata."""
        if self.gene is not None:
            record = self.gene.to_record()
        else:
            record = self.species.to_record()
            record["mhc_class"] = self.mhc_class
            record["pseudogene_status"] = self.pseudogene_status
            record["is_pseudogene"] = self.is_pseudogene
        record["allele"] = self.to_string()
        record["accession_source"] = self.accession_source
        record["accession"] = self.accession
        return record

    @classmethod
    def get(
        cls,
        species,
        accession_source: str,
        accession: str,
        gene: Gene | str | None = None,
        mhc_class: str | None = None,
        raw_string: str | None = None,
    ):
        """Construct a validated :class:`AccessionedAllele`, or return ``None``."""
        resolved_species = Species.get(species) if not isinstance(species, Species) else species
        if resolved_species is None:
            return None

        normalized = normalize_accession(accession_source, accession)
        if normalized is None:
            return None
        source_norm, acc_norm = normalized

        resolved_gene = None
        if gene is not None:
            if isinstance(gene, Gene):
                if gene.species != resolved_species:
                    return None
                resolved_gene = gene
            else:
                resolved_gene = Gene.get(resolved_species, gene)
                if resolved_gene is None:
                    return None

        resolved_class = mhc_class
        if resolved_gene is not None:
            if resolved_class is not None and (
                (is_class1(resolved_class) and not resolved_gene.is_class1)
                or (is_class2(resolved_class) and not resolved_gene.is_class2)
            ):
                return None
            resolved_class = resolved_gene.mhc_class

        return cls(
            species=resolved_species,
            accession_source=source_norm,
            accession=acc_norm,
            gene=resolved_gene,
            mhc_class=resolved_class,
            raw_string=raw_string,
        )
