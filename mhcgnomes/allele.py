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

from collections.abc import Iterable
from typing import Union

from .gene import Gene
from .mutation import Mutation
from .result_with_gene import ResultWithGene


class Allele(ResultWithGene):
    """
    Represents an MHC allele with gene and allele field information.

    An Allele specifies a unique protein amino acid sequence using notation
    like "HLA-A*02:01" or more generally: Species-Gene*Group:ProteinID

    Alleles can have annotations (e.g., "N" for null, "S" for secreted)
    and mutations (e.g., "N80I").

    Parameters
    ----------
    gene : Gene
        The gene this allele belongs to.
    allele_fields : Iterable[str]
        The allele field identifiers (e.g., ("02", "01") for A*02:01).
    annotations : Iterable[str], optional
        Functional annotations like "N" (null), "S" (secreted), etc.
    mutations : Iterable[Mutation], optional
        Any mutations from the reference sequence.
    raw_string : str, optional
        The original unparsed string.

    Attributes
    ----------
    gene : Gene
        The gene this allele belongs to.
    allele_fields : tuple of str
        The allele field identifiers.
    annotations : tuple of str
        Functional annotations.
    mutations : tuple of Mutation
        Any mutations from the reference sequence.

    Examples
    --------
    >>> from mhcgnomes import parse
    >>> allele = parse("HLA-A*02:01")
    >>> allele.gene_name
    'A'
    >>> allele.allele_fields
    ('02', '01')
    >>> allele.to_string()
    'HLA-A*02:01'
    """

    def __init__(
        self,
        gene: Gene,
        allele_fields: Iterable[str],
        annotations: Iterable[str] = (),
        mutations: Iterable[Mutation] = (),
        raw_string=None,
    ):
        if gene.is_mutant:
            gene_mutations = tuple(gene.mutations)
            gene = gene.copy_without_mutations()
        else:
            gene_mutations = ()
        ResultWithGene.__init__(self, gene=gene, raw_string=raw_string)
        self.allele_fields = tuple(allele_fields)
        self.annotations = tuple(annotations)
        self.mutations = gene_mutations + tuple(mutations)

    def __hash__(self):
        return hash((self.gene, self.allele_fields, self.annotations, self.mutations))

    def __eq__(self, other):
        if type(other) is not Allele:
            return False
        return (
            self.gene == other.gene
            and self.allele_fields == other.allele_fields
            and self.annotations == other.annotations
            and self.mutations == other.mutations
        )

    @classmethod
    def tuple_field_names(cls):
        return ("gene", "allele_fields", "annotations", "mutations", "raw_string")

    @classmethod
    def str_field_names(cls):
        return (
            "gene",
            "allele_fields",
            "annotations",
            "mutations",
        )

    @classmethod
    def eq_field_names(cls):
        return (
            "gene",
            "allele_fields",
            "annotations",
            "mutations",
        )

    @property
    def num_allele_fields(self):
        return len(self.allele_fields)

    @property
    def name(self):
        return ":".join(self.allele_fields) + "".join(self.annotations)

    def restrict_allele_fields(self, num_fields, drop_annotations=False, drop_mutations=False):
        if num_fields >= self.num_allele_fields:
            return self
        else:
            return self.copy(
                allele_fields=self.allele_fields[:num_fields],
                annotations=[] if drop_annotations else self.annotations,
                mutations=[] if drop_mutations else self.mutations,
            )

    @classmethod
    def split_allele_fields(cls, allele_fields):
        if isinstance(allele_fields, str):
            allele_fields = allele_fields.split(":")
        allele_fields = [str(s).strip() for s in allele_fields]
        allele_fields = [s for s in allele_fields if len(s) > 0]
        return tuple(allele_fields)

    @classmethod
    def get_with_gene(
        cls,
        gene: Gene,
        allele_fields: Iterable[str],
        annotations: Union[Iterable[str], None] = None,
        mutations: Union[Iterable[Mutation], None] = None,
        raw_string: Union[str, None] = None,
    ):
        """
        Create an Allele from a Gene object and allele fields.

        Parameters
        ----------
        gene : Gene
            The gene this allele belongs to.
        allele_fields : Iterable[str]
            The allele field identifiers.
        annotations : Iterable[str], optional
            Functional annotations.
        mutations : Iterable[Mutation], optional
            Mutations from reference sequence.
        raw_string : str, optional
            Original unparsed string.

        Returns
        -------
        Allele or None
            The constructed Allele, or None if gene is None or no allele
            fields provided.
        """
        if gene is None:
            return None

        allele_fields = cls.split_allele_fields(allele_fields)

        if len(allele_fields) == 0:
            return None

        if annotations is None:
            annotations = ()

        if mutations is None:
            mutations = ()

        return Allele(
            gene=gene,
            allele_fields=allele_fields,
            annotations=annotations,
            mutations=mutations,
            raw_string=raw_string,
        )

    @classmethod
    def get(
        cls,
        species_prefix,
        gene_name,
        *allele_fields,
        annotation=None,
        mutations=None,
        raw_string=None,
    ):
        """
        Create an Allele from species prefix, gene name, and allele fields.

        This is the primary factory method for creating Allele objects
        programmatically.

        Parameters
        ----------
        species_prefix : str
            Species prefix (e.g., "HLA" for human).
        gene_name : str
            Gene name (e.g., "A", "B", "DRB1").
        *allele_fields : str
            Variable number of allele field arguments, or a single
            colon-separated string.
        annotation : str, optional
            Single functional annotation.
        mutations : str or list, optional
            Mutations as string or list of Mutation objects.
        raw_string : str, optional
            Original unparsed string.

        Returns
        -------
        Allele or None
            The constructed Allele, or None if species/gene not found.

        Examples
        --------
        >>> Allele.get("HLA", "A", "02", "01")
        Allele(gene=..., allele_fields=('02', '01'), ...)
        >>> Allele.get("HLA", "A", "02:01")  # Also valid
        Allele(gene=..., allele_fields=('02', '01'), ...)
        """
        gene = Gene.get(species_prefix, gene_name)
        if not gene:
            return None

        if len(allele_fields) == 1:
            allele_fields = cls.split_allele_fields(allele_fields[0])

        if len(allele_fields) == 0:
            return None

        if annotation:
            annotations = [annotation]
        else:
            annotations = []

        if mutations is None:
            mutations = []

        elif type(mutations) is str:
            mutations = mutations.split()

        parsed_mutations = []
        for mut in mutations:
            if type(mut) is str:
                mut = Mutation.parse(mut, raise_on_error=False)
            if mut is None:
                return None
            if type(mut) is not Mutation:
                return None
            parsed_mutations.append(mut)
        return Allele.get_with_gene(
            gene=gene,
            allele_fields=allele_fields,
            annotations=annotations,
            mutations=parsed_mutations,
            raw_string=raw_string,
        )

    def to_string(
        self, include_species=True, use_old_species_prefix=False, include_annotations=True
    ):
        """
        Return allele strings like "HLA-A*02:01"
        """
        gene_str = self.gene.to_string(
            include_species=include_species, use_old_species_prefix=use_old_species_prefix
        )
        result = "{}*{}".format(gene_str, ":".join(self.allele_fields))
        if include_annotations:
            for annot in self.annotations:
                result += annot
        if self.is_mutant:
            result += f" {self.mutation_string()} mutant"
        return result

    def compact_string(
        self, include_species=False, use_old_species_prefix=False, include_annotations=False
    ):
        """
        Compact representation of a Allele, omits the "*" and ":"
        in allele names
            Normalized: HLA-A*02:01
            Compact: HLA-A0201
        """
        result = "{}{}{}".format(
            self.gene.compact_string(
                include_species=include_species, use_old_species_prefix=use_old_species_prefix
            ),
            "*" if self.gene_name[-1].isdigit() else "",
            "".join(self.allele_fields),
        )
        if self.is_mutant:
            result += f" {self.mutation_string()} mutant"
        return result

    def copy_with_extra_mutations(self, mutations):
        new_mutations = tuple(self.mutations) + tuple(mutations)
        return self.copy(mutations=new_mutations)

    @property
    def is_mutant(self):
        return len(self.mutations) > 0

    def mutation_string(self):
        return " ".join([mut.to_string() for mut in self.mutations])

    def to_record(self):
        """
        Returns dictionary with all fields of this allele,
        as well as its representations as a gene, allele group,
        and four digit allele.
        """
        d = self.gene.to_record()
        d["allele"] = self.to_string()
        d["annotations"] = self.annotations
        d["mutations"] = self.mutation_string()
        d["is_mutant"] = self.is_mutant
        return d

    def _check_annotation(self, annotation):
        """
        Check if given annotation is in the annotation list.
        """
        return annotation in self.annotations

    @property
    def annotation_null(self):
        return self._check_annotation("N")

    @property
    def annotation_cystosolic(self):
        return self._check_annotation("C")

    @property
    def annotation_secreted(self):
        return self._check_annotation("S")

    @property
    def annotation_questionable(self):
        return self._check_annotation("Q")

    @property
    def annotation_low_expression(self):
        return self._check_annotation("L")

    @property
    def annotation_aberrant_expression(self):
        return self._check_annotation("A")

    @property
    def annotation_group(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return self._check_annotation("G")

    @property
    def annotation_pseudogene(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return self._check_annotation("Ps")

    @property
    def annotation_splice_variant(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return self._check_annotation("Sp")
