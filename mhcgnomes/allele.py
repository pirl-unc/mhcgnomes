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

from typing import List, Tuple, Union


from .gene import Gene
from .mutation import Mutation
from .result_with_species import ResultWithSpecies

class Allele(ResultWithSpecies):
    """
    Allele name which specifies a unique protein amino acid sequence
    using this kind of notation: "HLA-A*02:01" or more generally:
            Species-Gene*Group:ProteinID
    """
    def __init__(
            self,
            gene : Gene,
            allele_fields : Union[List[str], Tuple[str]],
            annotations : Union[List[str], Tuple[str]] = [],
            mutations : Union[List[Mutation], Tuple[Mutation]] = [],
            raw_string=None):
        ResultWithSpecies.__init__(
            self,
            gene.species,
            raw_string=raw_string)
        self.gene = gene
        self.allele_fields = tuple(allele_fields)
        self.annotations = tuple(annotations)
        self.mutations = tuple(mutations)

    @classmethod
    def tuple_field_names(cls):
        return (
            "gene",
            "allele_fields",
            "annotations",
            "mutations",
            "raw_string"
        )


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
    def gene_name(self):
        return self.gene.gene_name

    @property
    def num_allele_fields(self):
        return len(self.allele_fields)

    @property
    def name(self):
        return ":".join(self.allele_fields)

    def restrict_num_allele_fields(
            self,
            num_fields,
            drop_annotations=False,
            drop_mutations=False):
        if num_fields >= self.num_allele_fields:
            return self
        else:
            self.copy(
                allele_fields=self.allele_fields[:num_fields],
                annotations=[] if drop_annotations else self.annotations,
                mutations=[] if drop_mutations else self.mutations)

    @property
    def group_id(self):
        if self.num_allele_fields > 0:
            return self.allele_fields[0]
        else:
            return None

    @property
    def protein_id(self):
        n = self.num_allele_fields
        if n == 0:
            return None
        return ":".join(self.allele_fields[:2])

    @property
    def coding_sequence_id(self):
        n = self.num_allele_fields
        if n == 0:
            return None
        return ":".join(self.allele_fields[:3])


    @property
    def genomic_sequence_id(self):
        n = self.num_allele_fields
        if n == 0:
            return None
        return ":".join(self.allele_fields[:4])

    @property
    def mhc_class(self):
        return self.gene.mhc_class

    @property
    def is_class1(self):
        return self.gene.is_class1

    @property
    def is_class2(self):
        return self.gene.is_class2

    @property
    def is_class2_alpha(self):
        return self.gene.is_class2_alpha

    @property
    def is_class2_beta(self):
        return self.gene.is_class2_beta

    @property
    def provisional_workshop_name(self):
        return self.fields[0].startswith("W")

    @property
    def annotation_null(self):
        return "N" in self.annotations

    @property
    def annotation_cystosolic(self):
        return "C" in self.annotations

    @property
    def annotation_secreted(self):
        return "S" in self.annotations

    @property
    def annotation_questionable(self):
        return "Q" in self.annotations

    @property
    def annotation_low_expression(self):
        return "L" in self.annotations

    @property
    def annotation_aberrant_expression(self):
        return "A" in self.annotations

    @property
    def annotation_group(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return "G" in self.annotations

    @property
    def annotation_pseudogene(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return "Ps" in self.annotations

    @property
    def annotation_splice_variant(self):
        # designates a group of genomic sequence alleles
        # with identical peptide binding region
        return "Sp" in self.annotations

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
            gene,
            allele_fields,
            annotations=[],
            mutations=[],
            raw_string=None):
        if gene is None:
            return None

        allele_fields = cls.split_allele_fields(allele_fields)
        if len(allele_fields) == 0:
            return None

        if annotations is None:
            annotations = []

        if mutations is None:
            mutations = []

        return Allele(
            gene=gene,
            allele_fields=allele_fields,
            annotations=annotations,
            mutations=mutations,
            raw_string=raw_string)

    @classmethod
    def parse_canonical_format(cls, allele_string, default_species=None):
        """
        Parse allele in the canonical format:
            Species-Gene*Allele
        Any alleles which don't conform to this format must be parsed using
        the Parser object.

        Returns Allele or None
        """
        if (allele_string.count("-") == 0):
            if default_species is None:
                return None
            species = default_species
            gene_and_allele = allele_string
        elif allele_string.count("-") == 1:
            species, gene_and_allele = allele_string.split("-")

        if gene_and_allele.count("*") != 1:
            return None

        gene, allele = gene_and_allele.split("*")
        return cls.get(species, gene, allele)

    @classmethod
    def get(
            cls,
            species_prefix,
            gene_name,
            *allele_fields,
            annotation=None,
            mutations=None,
            raw_string=None):
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
            mutations=mutations,
            raw_string=raw_string)

    def to_string(
            self,
            include_species=True,
            use_old_species_prefix=False,
            include_annotations=True):
        """
        Return allele strings like "HLA-A*02:01"
        """
        gene_str = self.gene.to_string(
            include_species=include_species,
            use_old_species_prefix=use_old_species_prefix)
        result = "%s*%s" % (gene_str, ":".join(self.allele_fields))
        if include_annotations:
            for annot in self.annotations:
                result += annot
        if self.is_mutant:
            result += " %s mutant" % self.mutation_string()
        return result

    def compact_string(
            self,
            include_species=False,
            use_old_species_prefix=False,
            include_annotations=False):
        """
        Compact representation of a Allele, omits the "*" and ":"
        in allele names
            Normalized: HLA-A*02:01
            Compact: HLA-A0201
        """
        result = "%s%s%s" % (
            self.gene.compact_string(
                include_species=include_species,
                use_old_species_prefix=use_old_species_prefix),
            "*" if self.gene_name[-1].isdigit() else "",
            "".join(self.allele_fields))
        if self.is_mutant:
            result += " %s mutant" % self.mutation_string()
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

