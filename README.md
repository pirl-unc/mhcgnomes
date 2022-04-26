<a href="https://travis-ci.com/pirl-unc/mhcgnomes">
    <img src="https://travis-ci.com/pirl-unc/mhcgnomes.svg?branch=main" alt="Build Status" />
</a>
<a href="https://coveralls.io/github/pirl-unc/mhcgnomes?branch=main">
    <img src="https://coveralls.io/repos/pirl-unc/mhcgnomes/badge.svg?branch=main&service=github" alt="Coverage Status" />
</a>
<a href="https://pypi.python.org/pypi/mhcgnomes/">
    <img src="https://img.shields.io/pypi/v/mhcgnomes.svg?maxAge=1000" alt="PyPI" />
</a>


![](https://raw.githubusercontent.com/til-unc/mhcgnomes/main/gnome-red-text.png) 

# mhcgnomes: Parsing MHC nomenclature in the wild

MHCgnomes is a parsing library for multi-species MHC nomenclature which
aims to correctly parse every name in [IEDB](http://www.iedb.org/), [IMGT/HLA](https://www.ebi.ac.uk/ipd/imgt/hla/), [IPD/MHC](https://www.ebi.ac.uk/ipd/mhc/), and the allele lists for both [NetMHCpan](https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1) and [NetMHCIIpan](https://services.healthtech.dtu.dk/service.php?NetMHCIIpan-4.0) predictors. This allows for standardization between immune databases and tools, which often use different naming conventions.

## Usage example

```python

In [1]: mhcgnomes.parse("HLA-A0201")
Out[1]: Allele(
    gene=Gene(
        species=Species(name="Homo sapiens', prefix="HLA"), 
        name="A"), 
    allele_fields=("02", "01"), 
    annotations=(), 
    mutations=())

In [2]: mhcgnomes.parse("HLA-A0201").to_string()
Out[2]: 'HLA-A*02:01'

In [3]: mhcgnomes.parse("HLA-A0201").compact_string()
Out[3]: 'A0201'

```

## The problem: MHC nomenclature is nuts

Despite the valiant efforts of groups such as the [Comparative MHC Nomenclature Committee](https://www.ebi.ac.uk/ipd/mhc/committee/), the names of MHC alleles you might encounter in different datasets (or accepted by immunoinformatics tools) are frustratingly ill specified. It's not uncommon to see dozens of different forms for the same allele.

For example, these all refer to the same MHC protein sequence:

* "HLA-A\*02:01"
* "HLA-A02:01"
* "HLA-A:02:01"
* "HLA-A0201"


Additionally, for human alleles, the species prefix is often omitted:

* "A\*02:01"
* "A\*0201"
* "A02:01"
* "A:02:01"
* "A0201"


### Annotations

Sometimes, alleles are bundled with modifier suffixes which specify 
the functionality or abundance of the MHC. Here's an example with an allele
which is secreted instead of membrane-bound:

* "HLA-A\*02:01:01S"

These are collected in the `annotations` field of an 
[`Allele`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
result.

### Mutations

MHC proteins are sometimes described in terms of mutations to a known allele. 

* "HLA-B\*08:01 N80I mutant"

These mutations are collected in the `mutations` field of an 
[`Allele`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) result.

### Beyond humans

To make things worse, several model organisms (like mice and rats) use archaic
naming systems, where there is no notion of allele groups or four/six/eight
digit alleles but every allele is simply given a name, such as:

* "H2-Kk"
* "RT1-9.5f"


In the above example "H2"/"RT1" correspond to species, "K"/"9.5" are
the gene names and "k"/"f" are the allele names.

To make these even worse, the name of a species is subject to variation (e.g. "H2" vs. "H-2") as well as drift over time (e.g. ChLA -> MhcPatr -> Patr).  

### Serotypes, haplotypes, and other named entitites

Besides alleles are also other named MHC related entities you'll encounter in immunological data. Closely related to alleles are serotypes, which effectively denote a grouping of alleles that are all recognized by the same antibody:

* "HLA-A2"
* "A2"

In many datasets the exact allele is not known but an experiment might note the genetic background of a model animal, resulting in loose haplotype restrictions such as: 

* "H2-k class I"

Yes, good luck disambiguating "H2-k" the haplotype from "H2-K" the gene, especially since capitalization is not stable enough to be relied on for parsing. 

In some cases immunological data comes only with a denoted species (e.g. "mouse"), a gene (e.g. "HLA-A"), or an MHC class ("human class I"). MHCgnomes has a structured representation for all of these cases and more. 

## Parsing strategy

It is a fool's errand to curate *all* possible MHC allele names since that list grows daily as the MHC loci of more people (and non-human animals) are sequenced. Instead, MHCgnomes contains an ontology of curated species and genes and then attempts to parse any given string into a multiple candidates of the following types:

* [`Species`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/species.py)
* [`Gene`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/gene.py)
* [`Allele`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
* [`AlleleWithoutGene`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/allele_without_gene.py)
* [`Class2Pair`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/class2_pair.py)
* [`Class2Locus`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/class2_locus.py)
* [`MhcClass`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/mhc_class.py)
* [`Haplotype`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py)
* [`Serotype`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)


The set of candidate interpretations for each string are then 
ranked according to heuristic rules. For example, a string will be 
preferentially interpreted as an [`Allele`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) rather 
than a [`Serotype`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)
or [`Haplotype`](https://github.com/til-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py). 


## How many digits per field?

Originally alleles for many genes were numbered with two digits:

* "HLA-MICB\*01"

But as the number of identified alleles increased, the number of
fields specifying a distinct protein increase to two. This became 
conventionally called a "four digit" format, since each field has two
digits. Yet, as the number of identified alleles continued to increase, then 
the number of digits per field has often increased from two to three: 

* "MICB\*002:01"
* "HLA-A00201"
* "A:002:01"
* "A\*00201"

These are not always currently treated as equivalent to allele strings with two digits in their first field, but that feature is in the works.

However, if databases such as [IPD-MHC](https://www.ebi.ac.uk/ipd/mhc/) or [IMGT-HLA](https://www.ebi.ac.uk/ipd/imgt/hla/) recorded an older form of an allele, then MHCgnomes can optionally map it onto the modern version (including capturing differences in numbers of digits per field). 

## References

* [IPD-MHC: nomenclature requirements for the non-human major histocompatibility complex in the next-generation sequencing era](https://link.springer.com/article/10.1007%2Fs00251-018-1072-4)
* [Comparative MHC nomenclature: report from the ISAG/IUIS-VIC committee 2018]()
* [ISAG/IUIS-VIC Comparative MHC Nomenclature
Committee report, 2005](https://link.springer.com/content/pdf/10.1007%2Fs00251-005-0071-4.pdf)
* [Marsupial MHC Class II β Genes Are Not Orthologous to the Eutherian β Gene Families]()
* [Nomenclature for factors of the SLA system, update 2008](https://www.ncbi.nlm.nih.gov/pubmed/19317739)
