# MHC nomenclature in the wild

This page explains the naming problems mhcgnomes exists to solve: the many
spellings of one allele, the suffixes and mutations attached to allele names,
the archaic systems used outside humans, and the named entities that are not
alleles at all. Read it if you are deciding what your data actually contains.
For how the parser resolves these strings, see the
[parsing guide](parsing.md).

## The problem: MHC nomenclature is nuts

Despite the valiant efforts of groups such as the [Comparative MHC Nomenclature Committee](https://www.ebi.ac.uk/ipd/mhc/committee/), the names of MHC alleles you might encounter in different datasets (or accepted by immunoinformatics tools) are frustratingly ill-specified. It's not uncommon to see dozens of different forms for the same allele.

For example, these all refer to the same MHC protein sequence:

- "HLA-A\*02:01"
- "HLA-A02:01"
- "HLA-A:02:01"
- "HLA-A0201"

Additionally, for human alleles, the species prefix is often omitted:

- "A\*02:01"
- "A\*0201"
- "A02:01"
- "A:02:01"
- "A0201"

## Annotations

Sometimes, alleles are bundled with modifier suffixes which specify
the functionality or abundance of the MHC. Here's an example with an allele
which is secreted instead of membrane-bound:

- "HLA-A\*02:01:01S"

These are collected in the `annotations` field of an
[`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
result. `annotation_descriptions` says what each one means; the full table is
`mhcgnomes.allele_annotations.annotation_descriptions`, with the IMGT/HLA or
IPD-MHC definition behind each entry cited in its source. A caller that only
needs to know whether the protein reaches the cell surface can ask
`cell_surface_expression`. It returns `"absent"` for N, S, C or a pseudogene,
`"uncertain"` for A or Q, `"low"` for L, and `None` when the name says
nothing about expression:

```python
>>> import mhcgnomes
>>> allele = mhcgnomes.parse("HLA-A*24:02:01:02L")
>>> allele.annotation_descriptions
{'L': 'low cell-surface expression'}
>>> allele.cell_surface_expression
'low'
>>> mhcgnomes.parse("HLA-B*44:02:01:02S").cell_surface_expression
'absent'
>>> mhcgnomes.parse("HLA-A*02:01").cell_surface_expression is None
True
```

Multi-letter annotations are also used in some non-human systems. In particular,
`Ps` (pseudogene) and `Sp` (splice variant) appear as suffixes on allele fields,
e.g. `Mamu-B*074:03Sp` or `Caja-B5*01:01Ps`, and are parsed into the
`annotations` field as `Sp` or `Ps` respectively.

Note that `Ps` can also appear as part of a gene name (prefix or suffix) in
non-human primates, such as `Caja-G2Ps*01`. In those cases `Ps` is treated as
part of the gene name, not an allele annotation.

The suffix-specific `annotation_pseudogene` property remains separate from
species/gene ontology status. `Gene.pseudogene_status` is `True`, `False`, or
`None` when no status has been curated; `Gene.is_pseudogene` is true only for a
curated pseudogene. `Allele.is_pseudogene` combines gene-level status with an
explicit `Ps` suffix:

```python
>>> import mhcgnomes
>>> mhcgnomes.parse("HLA-H*02:01").is_pseudogene
True
>>> mhcgnomes.parse("Mamu-G*01:01").is_pseudogene
True
>>> mhcgnomes.parse("HLA-G*01:01").is_pseudogene
False
>>> mhcgnomes.parse("Caja-B5*01:01Ps").annotation_pseudogene
True
```

## Loci that name no alleles

A few loci are named by a nomenclature authority which then deposits no
sequence under them. IMGT/HLA names the class I gene fragments `X` and `Z`, the
class II pseudogenes `DQB3` and `DPA3`, and `MICC`/`MICD`/`MICE`/`PSMB8`/
`PSMB9`, and IPD-IMGT/HLA gives every one of them zero alleles. The gene
resolves; an allele built on top of it does not.

```python
>>> mhcgnomes.parse("HLA-Z")
Gene(species=Species(name='Homo sapiens', mhc_prefix='HLA'), name='Z', mutations=())
>>> mhcgnomes.parse("HLA-Z*01:01", raise_on_error=False) is None
True
>>> mhcgnomes.parse("HLA-W*01:01:01:01").gene.name  # W has 13 deposited alleles
'W'
```

## Genes which need the species named

Every HLA class I gene fragment is a single letter, and a bare `N`, `R`, `S`,
`U` or `Z` is mouse or rat haplotype shorthand long before it is a human gene.
These genes are marked `context only` in the ontology: they resolve when the
species is named -- by prefix or by `species=` -- and stay out of species-less
lookup, so the shorthand keeps its meaning.

```python
>>> mhcgnomes.parse("N").to_string()      # rat haplotype, as it always was
'RT1-n'
>>> mhcgnomes.parse("HLA-N").to_string()
'HLA-N'
>>> mhcgnomes.parse("N", species="Homo sapiens").to_string()
'HLA-N'
```

## A locus a haplotype does not have

Some haplotypes are defined partly by what is *missing*. The swine haplotype
`Hp-2.0` has no SLA-3 at all, which its source states as `null`, and
low-resolution swine types are written `SLA-1*15XX or Blank`. That is a
different claim from a locus nobody typed, so it is recorded rather than left
out:

```python
>>> hap = mhcgnomes.parse("Hp-2.0")
>>> [allele.to_string() for allele in hap.alleles]
['SLA-1*02:01', 'SLA-1*07:01', 'SLA-2*02:01']
>>> [gene.to_string() for gene in hap.absent_genes]
['SLA-3']
```

`absent_genes` is empty for every haplotype that does not say otherwise, and it
narrows with the alleles beside it: `parse("Hp-2.0 class II").absent_genes` is
empty, because an absent class I locus says nothing about a class II reading.

## Mutations

MHC proteins are sometimes described in terms of mutations to a known allele.

- "HLA-B\*08:01 N80I mutant"

These mutations are collected in the `mutations` field of an
[`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) result.

## Beyond humans

To make things worse, several model organisms (like mice and rats) use archaic
naming systems, where there is no notion of allele groups or four/six/eight
digit alleles but every allele is simply given a name, such as:

- "H2-Kk"
- "RT1-9.5f"

In the above example "H2"/"RT1" correspond to species, "K"/"9.5" are
the gene names and "k"/"f" are the allele names.

To make these even worse, the name of a species is subject to variation (e.g. "H2" vs. "H-2") as well as drift over time (e.g. ChLA -> MhcPatr -> Patr).

## Serotypes, supertypes, haplotypes, and other named entities

Besides alleles there are also other named MHC related entities you'll encounter in immunological data. Closely related to alleles are serotypes, which effectively denote a grouping of alleles that are all recognized by the same antibody:

- "HLA-A2"
- "A2"

Supertypes are functional groupings based on shared peptide-binding specificity rather than serological reactivity (Sidney et al. 2008). These are parsed when the "supertype" keyword is present:

- "A2 supertype"
- "HLA-B44 supertype"

Class II heterodimers can be specified using dot notation, which is common in celiac disease literature:

- "DQ2.5" (equivalent to DQA1\*05:01/DQB1\*02:01)
- "DQ8.5"

In many datasets the exact allele is not known but an experiment might note the genetic background of a model animal, resulting in loose haplotype restrictions such as:

- "H2-k class I"

Yes, good luck disambiguating "H2-k" the haplotype from "H2-K" the gene, especially since capitalization is not stable enough to be relied on for parsing.

In some cases immunological data comes only with a denoted species (e.g. "mouse"), a gene (e.g. "HLA-A"), or an MHC class ("human class I"). MHCgnomes has a structured representation for all of these cases and more.

## How many digits per field?

Originally alleles for many genes were numbered with two digits:

- "HLA-MICB\*01"

But as the number of identified alleles increased, the number of
fields specifying a distinct protein increased to two. This became
conventionally called a "four digit" format, since each field has two
digits. Yet, as the number of identified alleles continued to increase,
the number of digits per field has often increased from two to three:

- "MICB\*002:01"
- "HLA-A00201"
- "A:002:01"
- "A\*00201"

MHCgnomes normalizes allele field widths by zero-padding to each gene's canonical minimum (e.g. 3 digits for MICA/MICB). Coverage of per-gene field widths is still incomplete for some non-human species.

However, if databases such as [IPD-MHC](https://www.ebi.ac.uk/ipd/mhc/) or [IMGT-HLA](https://www.ebi.ac.uk/ipd/imgt/hla/) recorded an older form of an allele, then MHCgnomes can optionally map it onto the modern version (including capturing differences in numbers of digits per field).

## References

- [IPD-MHC: nomenclature requirements for the non-human major histocompatibility complex in the next-generation sequencing era](https://link.springer.com/article/10.1007%2Fs00251-018-1072-4)
- [Comparative MHC nomenclature: report from the ISAG/IUIS-VIC committee 2018](https://link.springer.com/article/10.1007/s00251-018-1074-2)
- [ISAG/IUIS-VIC Comparative MHC Nomenclature
  Committee report, 2005](https://link.springer.com/content/pdf/10.1007%2Fs00251-005-0071-4.pdf)
- [Nomenclature for factors of the SLA system, update 2008](https://www.ncbi.nlm.nih.gov/pubmed/19317739)
