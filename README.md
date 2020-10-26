<a href="https://travis-ci.org/openvax/mhcgnomes">
    <img src="https://travis-ci.com/til-unc/mhcgnomes.svg?branch=main" alt="Build Status" />
</a>
<a href="https://coveralls.io/github/openvax/mhcgnomes?branch=master">
    <img src="https://coveralls.io/repos/til-unc/mhcgnomes/badge.svg?branch=main&service=github" alt="Coverage Status" />
</a>
<a href="https://pypi.python.org/pypi/mhcgnomes/">
    <img src="https://img.shields.io/pypi/v/mhcgnomes.svg?maxAge=1000" alt="PyPI" />
</a>


![](gnome-red-text.png)

# mhcgnomes: Parsing MHC nomenclature in the wild

MHCgnomes is a parsing library for multi-species MHC nomenclature which
aims to correctly parse every name in IEDB, IMGT, and the allele lists
for both NetMHCpan and NetMHCIIpan predictors. This allows for standardization
between immune databases and tools, which all seems to use different naming
conventions.

## Example

```python
In [1]: mhcgnomes.parse("HLA-A0201")
Out[1]: FourDigitAllele(species='HLA', gene_name='A', group_id='02', protein_id='01')

In [2]: mhcgnomes.compact_string("HLA-A*02:01")
Out[2]: 'A0201'
```

## MHC Nomenclature

MHC alleles are named with a frustratingly loose system. It's not uncommon
to see dozens of different forms for the same allele.

Note: this function works with both class I and class II allele names (including
alpha/beta pairs).

For example, these all refer to the same MHC protein sequence:
    * HLA-A\*02:01
    * HLA-A02:01
    * HLA-A:02:01
    * HLA-A0201
    * HLA-A00201

Additionally, for human alleles, the species prefix is often omitted:
* A\*02:01
* A\*00201
* A\*0201
* A02:01
* A:02:01
* A:002:01
* A0201
* A00201

We might also encounter "6 digit" and "8 digit" MHC types (which specify
variants that don't affect amino acid sequence):

* A\*02:01:01
* A\*02:01:01:01

There are also modifier suffixes which specify whether an allele
is e.g. secreted instead of membrane-bound:

* HLA-A\*02:01:01S

There are serotypes, which correspond to groups of four digit alleles.
* HLA-A2
* A2

To make things worse, several model organisms (like mice and rats) use archaic
naming systems, where there is no notion of allele groups or four/six/eight
digit alleles but every allele is simply given a name, such as:
* H2-Kk
* RT1-9.5f

In the above example "H2"/"RT1" correspond to species, "K"/"9.5" are
the gene names and "k"/"f" are the allele names.

## References

* [IPD-MHC: nomenclature requirements for the non-human major histocompatibility complex in the next-generation sequencing era](https://link.springer.com/article/10.1007%2Fs00251-018-1072-4)
* [Comparative MHC nomenclature: report from the ISAG/IUIS-VIC committee 2018]()
* [ISAG/IUIS-VIC Comparative MHC Nomenclature
Committee report, 2005](https://link.springer.com/content/pdf/10.1007%2Fs00251-005-0071-4.pdf)
* [Marsupial MHC Class II β Genes Are Not Orthologous to the Eutherian β Gene Families]()
* [Nomenclature for factors of the SLA system, update 2008](https://www.ncbi.nlm.nih.gov/pubmed/19317739)
