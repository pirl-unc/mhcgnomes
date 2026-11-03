# Parsing guide

This page covers what `parse` returns and how to control it: the candidate
types it ranks, how to restrict results when the input is untrusted, how to
tell an explicit species from an inferred one, and how `species=` and
`default_species=` differ. Read it before running mhcgnomes over data you did
not curate yourself.

## Parsing strategy

It is a fool's errand to curate _all_ possible MHC allele names since that list grows daily as the MHC loci of more people (and non-human animals) are sequenced. Instead, MHCgnomes contains an ontology of curated species and genes and then attempts to parse any given string into multiple candidates of the following types:

- [`Species`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/species.py)
- [`Gene`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/gene.py)
- [`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py)
- [`AlleleWithoutGene`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele_without_gene.py)
- [`Pair`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/pair.py)
- [`Class2Locus`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/class2_locus.py)
- [`MhcClass`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/mhc_class.py)
- [`Haplotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py)
- [`Serotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)
- [`Supertype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/supertype.py)

The set of candidate interpretations for each string are then
ranked according to heuristic rules. For example, a string will be
preferentially interpreted as an [`Allele`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/allele.py) rather
than a [`Serotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/serotype.py)
or [`Haplotype`](https://github.com/pirl-unc/mhcgnomes/blob/main/mhcgnomes/haplotype.py).

## Which result type means what

Several result types are legitimate MHC designations without being molecules,
which is why `HLA-DR15` and `BoLA-DR` parse cleanly but yield no allele:

| Type | Means | Example |
| --- | --- | --- |
| `Allele` | A specific allele | `HLA-A*02:01` |
| `Gene` | A locus, no allele given | `Patr-AL` |
| `Pair` | Class II alpha/beta pairing | `HLA-DPA1*01:03/DPB1*06:01` |
| `AlleleWithoutGene` | Allele name whose gene is unknown | `BoLA-D18.4` |
| `Class2Locus` | A class II locus family | `BoLA-DR` |
| `Serotype` | Serological group, may cover many alleles | `HLA-DR15` |
| `Haplotype` | Named haplotype | `H2-b` |
| `Supertype` | Functional grouping of alleles | `HLA-A02` |
| `MhcClass` | Just a class, with or without species | `HLA class I` |
| `Species` | Only a species was named | `HLA` |

### One allele or an allele group?

An `Allele` can also be an allele group. In IMGT/HLA and IPD-MHC names the
first field is the group and the second names a protein, so `HLA-A*02` is a
group and `HLA-A*02:01` is one allele. `is_allele_group` classifies the written name; it does not validate a molecule.
False does not establish registry membership, a complete sequence, normal
expression, or suitability for a binding predictor.
Field counts alone go wrong both ways: `HLA-MICA*001` is one complete allele,
and `SLA-1*15XX` is a group.

```python
>>> from mhcgnomes import parse
>>> [parse(name).is_allele_group for name in ["HLA-A*02", "HLA-A*02:01", "H2-Kb"]]
[True, False, False]
>>> [parse(name).is_allele_group for name in ["HLA-MICA*001", "SLA-1*15XX"]]
[False, True]
```

Old names are recognized only after alias resolution. NetMHC's `Mamu-A01` is
an allele in the `Mamu-A1*001:01` lineage once `use_allele_aliases=True` resolves it.
Without alias resolution it stays the one-field `Mamu-A*01` and reads as a
group. Unknown names can still parse: validate the sequence and any downstream
requirements separately. G/P groups also require separate handling.

```python
>>> parse("Mamu-A01", use_allele_aliases=True).is_allele_group
False
>>> parse("Mamu-A01").is_allele_group
True
```

## Parsing untrusted input

`parse` accepts anything that looks like MHC nomenclature, which is the right
default for a known-good allele list and the wrong one for free text. Scanning
curator notes or a spreadsheet column, "it parsed" is not the same as "this is
an MHC molecule": a stray `HLA class I` is a valid `MhcClass`, and a bare `d`
is a valid mouse `Haplotype`.

Say what you will accept, and let anything else come back as `None`:

```python
from mhcgnomes import parse, Allele, Gene, Pair

result = parse(token, required_result_types=(Allele, Gene, Pair), raise_on_error=False)
if result is None:
    continue  # not an MHC molecule
```

```
HLA-A*02:01                -> Allele        n/a                 -> None
H2-K*b                     -> Allele        -                   -> None
Patr-AL                    -> Gene          HLA class I         -> None
HLA-DPB1*06:01/DPA1*01:03  -> Pair          d                   -> None
```

This is more robust than filtering on the returned type yourself, since it also
prevents a lower-ranked interpretation from being chosen in the first place.

## Was the species explicit, or guessed?

Species inference is right most of the time and load-bearing when it is wrong.
A bare gene symbol can carry a species you never supplied, and the default
species means a deliberately generic string still comes back with one:

```python
>>> import mhcgnomes
>>> from mhcgnomes import parse
>>> parse("Gaga-BLB2*02").species_source
'explicit'
>>> parse("BLB2*02").species_source     # inferred from the gene name
'inferred'
>>> parse("MHC class II").species_source  # fell back to default_species
'default'
```

`result.species_from_input` is the boolean form, true only for `explicit` — it
answers the question a caller actually has: did I supply this species, or did
the parser? To reject anything you did not name outright — the right rule when
validating curated data — ask for it at parse time:

```python
>>> parse("BLB2*02", require_explicit_species=True, raise_on_error=False) is None
True
```

Provenance is not part of a result's identity: two alleles that differ only in
how their species was determined still compare equal and hash the same. It is
also computed only when asked, so it costs nothing if you never look.

## Printing only the prefixes a source attests

`HLA-A*02:01` and `CyanCaer-DAB1` look alike, but only the first is published
nomenclature — the second was minted here so the blue tit would have a unique
prefix. `prefix_provenance` tells them apart, and an opt-in display policy acts
on it:

```python
>>> from mhcgnomes.prefix_display_policy import prefix_display_policy, ATTESTED
>>> parse("CyanCaer-DAB1").to_string()
'CyanCaer-DAB1'
>>> with prefix_display_policy(ATTESTED):
...     parse("CyanCaer-DAB1").to_string()
'CyanistesCaeruleus-DAB1'
>>> with prefix_display_policy(ATTESTED):
...     parse("HLA-A*02:01").to_string()   # designated, so untouched
'HLA-A*02:01'
```

The default is unchanged, both spellings parse under either policy, and group
labels such as `SLA` and `BoLA` keep their labels. `set_prefix_display_policy`
is the process-wide form; the policy is thread-local.

## Gene symbols shared by several species

A gene symbol only carries a species when it belongs to one lineage. `DRB1` is
declared by 45 species across humans, cattle, dogs and horses, so on its own it
names none of them:

```python
>>> parse("DRB1*01:01", default_species=None, raise_on_error=False) is None
True
>>> parse("DRB1*01:01").to_string()  # with the default species, as before
'HLA-DRB1*01:01'
>>> parse("BLB2*02").to_string()  # chicken and the Galliformes node: one lineage
'Gaga-BLB2*02'
```

A species that uses a shared symbol but does not own its bare form says so in
the ontology with `context only`, which is why `BF2*02:01` still resolves to
the chicken although the guineafowl also has a BF2.

Gene lookup is case- and separator-normalizing, so some symbols differ only in
spelling. Where they do, your spelling decides:

```python
>>> parse("Ia1").species.name   # Paralichthys olivaceus spells it this way
'Paralichthys olivaceus'
>>> parse("IA1").species.name   # Chrysolophus pictus spells it this way
'Chrysolophus pictus'
>>> parse("ia1", raise_on_error=False) is None  # neither, so neither is named
True
```

A species you name outright still wins over a spelling that points elsewhere —
`OS=Mus musculus GN=Mr1` is a mouse gene even though *Rattus sp.* is the entry
that spells `MR1` as `Mr1`.

## Species-directed parsing

`species=` constrains parsing to a single species. The final parsed object
must match that species exactly, or parsing fails. This is useful when you
know the organism and want to reject cross-species mismatches:

```python
>>> mhcgnomes.parse("BoLA-DRB3*01:01", species="Bos taurus").to_string()
'Bota-DRB3*01:01'
>>> mhcgnomes.parse("HLA-A*02:01", species="Bos taurus", raise_on_error=False) is None
True
>>> mhcgnomes.parse("A*02:01", species="Homo sapiens").species.name
'Homo sapiens'
```

When the input uses an ancestor prefix (like `BoLA` for genus-level *Bos sp.*),
`species=` rewrites the result to the requested descendant species if valid.

`default_species=` is a less strict alternative — it provides a fallback
species hint for inputs that don't contain a species prefix, but does not
reject inputs that resolve to a different species:

```python
>>> mhcgnomes.parse("A*02:01", default_species="Homo sapiens").species.name
'Homo sapiens'
>>> mhcgnomes.parse("DMA", default_species="Chelonia mydas").species.name
'Chelonia mydas'
```

## Resolving legacy allele names

Alias resolution is opt-in: `parse(name, use_allele_aliases=True)`. It follows
curated renames to their terminal target. Lookup tries the supplied gene first,
then its canonical name and sorted alternate names, so the answer does not
depend on Python's hash seed.

Colons are meaningful in alias keys. A legacy digit string is looked up before
it is split into modern fields:

```pycon
>>> parse("HLA-A*02172", use_allele_aliases=True).to_string()
'HLA-A*02:17:02:01'
>>> parse("HLA-A*02:172", use_allele_aliases=True).to_string()
'HLA-A*02:172'
```

A modern two-field name is not expanded merely because its colon-free spelling
is a legacy key. For example, `HLA-B*08:01` retains two fields, while the old
`HLA-B*0801` resolves to `HLA-B*08:01:01:01`. Explicit modern-name renames still
apply. Alias tables are curated historical data, not a live registry validator;
see [#238](https://github.com/pirl-unc/mhcgnomes/issues/238) for the remaining
current-name conflicts found in the registry audit.
