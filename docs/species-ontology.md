# Species and gene ontology

This page documents the curated data behind the parser: the YAML files, the
species tree and what its edges mean, the prefix conventions and tiers, and how
genes are classified. Read it before adding a species, changing a `parent`
link, or interpreting why a prefix resolves the way it does. The
[curation guide](curation.md) has the procedures; this page has the model.

MHCgnomes maintains a curated ontology of species prefixes and MHC gene names
in YAML data files under `mhcgnomes/data/`. The key files are:

| File | Purpose |
| --- | --- |
| `species.yaml` | Canonical species entries with MHC prefixes, genes, classes, properties, and families |
| `gene_aliases.yaml` | Alternative gene spellings that normalize to canonical genes |
| `allele_aliases.yaml` | Retired or shorthand allele names that normalize to canonical alleles |
| `known_alleles.yaml` | Curated known allele labels per species/gene |

## The species tree

Species entries form a tree through their `parent` links. A `parent` is a
containment claim — "this species is inside that group" — and it is taxonomic
wherever it can be: exactly one parent link in the whole ontology points at
another genus's node. Genes, and the rest of a species' curated data, are
inherited along these links.

Every MHC prefix owns a node, and an umbrella prefix covers everything beneath
its node:

```
Bos sp. [BoLA]     ->  Bota, Boin, Bofr, Bogr, Bubu
Macaca sp. [RhLA]  ->  Mafa, Mamu, Mane, Masi, Math
Canis sp. [DLA]    ->  Calu, Cala, Caru, Casi, Caba
```

**`NHP` is a node, not the primate order.** IPD-MHC's `NHP` group is [Non-Human
Primates](https://www.ebi.ac.uk/ipd/mhc/group/NHP/), so it is the primate order
*minus humans* — paraphyletic, and not a taxon. It gets its own entry, sibling
to `Homo sapiens`:

```
Primata sp. [Primata]        the primate order, and the genes all primates share
├── Homo sapiens [HLA]
└── NHP [NHP]                the IPD-MHC group
    └── 55 non-human primates
```

That keeps both questions as plain ancestry, with no second predicate:

```python
>>> import mhcgnomes
>>> from mhcgnomes import Species, parse
>>> Species.get("Homo sapiens").compatible_with("Primata sp.")
True                              # humans are primates
>>> Species.get("Homo sapiens").compatible_with("NHP")
False                             # NHP-* cannot denote one
>>> parse("NHP-E*01:01", species="Homo sapiens", raise_on_error=False) is None
True                              # so this is refused, not converted
```

Because `NHP` is paraphyletic, any taxon added under `Primata sp.` has to sit
wholly inside or wholly outside it. A `Homo sp.` node holding *H. sapiens* and
*H. neanderthalensis* is fine as a sibling of `NHP`; a `Hominidae sp.` spanning
humans and the great apes is not, since it would have to pull `Gorilla sp.`,
`Pan sp.` and `Pongo sp.` out of the `NHP` umbrella.

**`Bubalus bubalis` is under `Bos sp.` despite being a different genus.** This
is the one edge that is deliberately not taxonomy. Water buffalo belongs to
*Bubalus*, a sister genus of *Bos* within Bovini, but IPD-MHC files water
buffalo in the BoLA group and the literature assigns buffalo class II sequences
to cattle loci by trans-species polymorphism — `Bubu-DRB` is the orthologue of
`BoLA-DRB3`. The edge is load-bearing: the entry declares only `DQA`, `DQA1`
and `DQB` itself, so `Bubu-DRA`, `Bubu-DRB3`, `Bubu-DQA2` and `Bubu-DQB1` all
parse by inheritance, and `Bubu-DRB` normalizes to `Bubu-DRB3` because of it.

So before "correcting" a parent link that looks taxonomically wrong, check what
parses through it.

Two further consequences are easy to get wrong:

**`Gnathostomata sp.` is a universal root.** Every species descends from it, so
"do these two share a common ancestor?" is true for any pair and useless as a
compatibility test — worse, it fails open. Only a direct ancestor or descendant
relation is meaningful. `Species.compatible_with` implements that rule:

```python
>>> Species.get("Bos taurus").compatible_with("Bos sp.")
True                     # less specific, not contradictory
>>> Species.get("Macaca mulatta").compatible_with("Macaca fascicularis")
False                    # siblings
```

This is what you want when checking a declared species against the species
mhcgnomes derives from an allele, since the two legitimately differ in
specificity: `BoLA` belongs to the genus-level `Bos sp.`, so a `BoLA-N*013:01`
allele on a sample curated as *Bos taurus* is compatible.

**Compatibility can follow an edge that exists for naming.** A `Bubu-*` allele
is compatible with a curated `Bos sp.`, since `Bos sp.` denotes the BoLA group
and water buffalo is in it. That is the intended answer, not a wart.

An `X sp.` node is a group entry: it holds the prefix and the genes shared by
everything beneath it. `Bos sp.` owns `BoLA` and the cattle gene list; `Bos
taurus` inherits both.

## Species prefix conventions

Each species is identified by a short prefix (usually 2-4 characters) such as
`HLA` (human), `H2` (mouse), `Gaga` (chicken), or `Dare` (zebrafish). The
parser uses these prefixes to identify species before parsing gene names and
allele fields.

Prefixes are matched case-insensitively after stripping punctuation. A leading
`Mhc` prefix (common in bird MHC literature, e.g. `MhcTyal-DAB1*01:01`) is
automatically stripped as a fallback when normal prefix matching fails.

Some historically important prefixes are not single-species codes. Prefixes
such as `DLA`, `SLA`, `OLA`, `BoLA`, and `CELA` are curated as umbrella taxon
nodes in the ontology because the external nomenclature itself is genus- or
clade-level rather than species-specific. For example:

- `DLA` maps to `Canis sp.`, while `Calu` maps specifically to `Canis lupus`
- `SLA` maps to `Sus sp.`, while `Susc` maps specifically to `Sus scrofa`
- `BoLA` maps to `Bos sp.`, while `Bota` maps specifically to `Bos taurus`
- `OLA` maps to `Ovis sp.`, while `Ovar` maps specifically to `Ovis aries`
- `CELA` maps to `Cetacea sp.`, while `Tutr` maps specifically to `Tursiops truncatus`

This distinction matters when interpreting parsed objects: an allele parsed
from `BoLA-...` is attached to the generic cattle node unless the parse is
explicitly constrained or rewritten to a descendant species.

## MHC gene class assignments

Genes in `species.yaml` are organized by MHC class:

- **Ia**: Classical class I (associates with B2M, presents peptides)
- **Ib**: Non-classical class I (in MHC locus, associates with B2M)
- **Ic**: Related MHC locus genes, no B2M association (e.g. MICA)
- **Id**: Class I-related genes on other chromosomes
- **IIa**: Classical class II alpha/beta chains presenting peptides
- **IIb**: Accessory or non-classical class II proteins
- **other**: Antigen processing genes (TAP1, TAP2, TAPBP, B2M)

## Species-specific gene properties and families

`species.yaml` can attach source-backed properties to canonical genes. These
properties inherit through the species tree and descendants can override them,
so the same gene name may have different biology in different lineages. For
example, human HLA-G is explicitly functional while MHC-G is a pseudogene in
the macaque lineage. Missing metadata remains unknown rather than being inferred
from the spelling of a gene.

The ontology can also define exact gene families. The jawed-vertebrate root
defines `TAP` as the family containing `TAP1` and `TAP2`. The strict parser does
not promote `TAP` to a gene, but the species-aware `parse_gene_class` API can
classify legacy family-level inputs without choosing a family member:

```python
>>> info = mhcgnomes.parse_gene_class("SLA-TAP*1*01:01")
>>> (info.gene_name, info.mhc_class, info.non_mhc, info.source)
('TAP', 'other', True, 'ontology_family')
```

This classification uses the selected species' inherited ontology family; it
does not infer TAP membership from a regex or a shared gene-name pattern.

## Species prefix tiers

As mhcgnomes supports more species, short prefix codes increasingly collide.
Codes like `HLA`/`SLA`/`DLA`, `OrLA`, and four-letter codes like `Calu` all hit
collisions as coverage grows. Three forms are supported so that every species
is always reachable:

| Tier | Form | Example | When used |
| --- | --- | --- | --- |
| Established short prefix | 1–4 letters | `HLA`, `Gaga`, `Crpo` | Published in MHC literature or IPD-MHC. Preferred for display. |
| Full latin name | Concatenated genus + species | `HomoSapiens`, `ChrysemysPicta` | The default generated form. Collision-free across every binomial in the ontology. |
| 4+4 shorthand | First 4 of genus + first 4 of species | `TachAcul`, `AbraBram` | Compact shorthand, and the curated prefix of most species without a literature code. Emitted as an alias only where globally unique. |

All are parsed case-insensitively. These all resolve to the same allele:

```
HLA-A*02:01          # established prefix
HomoSapiens-A*02:01  # full latin name
HomoSapi-A*02:01     # 4+4 shorthand (auto-generated alias)
Homo sapiens-A*02:01 # latin name with space
```

Two limits are worth knowing:

**4+4 is not collision-free, and a contested form names nobody.** Three forms
are derivable from two species each — `ChryPict` from both *Chrysemys picta*
and *Chrysolophus pictus*, `LaniColl` from two shrikes, `LeucLeuc` from a dace
and a crane. Since 3.43.0 none of them resolves on its own:

```python
>>> parse("ChryPict-UA*01", raise_on_error=False) is None
True                       # 3.42.0 gave a painted turtle, even if you meant the pheasant
>>> parse("ChryPict-UA*01", species="Chrysolophus pictus").species.name
'Chrysolophus pictus'      # explicit species still resolves it
```

Raising instead of returning `None` explains the ambiguity rather than the
symptom:

```
Prefix 'ChryPict' is derivable by the same naming rule from Chrysemys picta,
Chrysolophus pictus, so it names neither. Use species='<latin name>' or an
unambiguous prefix such as ChrysemysPicta (Chrysemys picta),
ChrysolophusPictus (Chrysolophus pictus).
```

Both claimants list the form under `context only prefixes`, so it resolves
only when the caller has already said which species they mean. **This is a breaking parse change.** `ChryPict`, `LaniColl` and `LeucLeuc` all
resolved on 3.42.0 and now need an explicit `species=`. The species that had
held a contested form as their canonical prefix use their concatenated binomial
instead, so their normalized output changes too.

Canonical prefix changed **in 3.42.0**:

| species | was | now | old spelling |
|---|---|---|---|
| *Chrysemys picta* | `ChryPict` | `ChrysemysPicta` | alias, then context only in 3.43.0 |
| *Lanius collaris* | `LaniCola` | `LaniusCollaris` | plain alias, uncontested |
| *Leuciscus leuciscus* | `LeucisLeucis` | `LeuciscusLeuciscus` | plain alias, uncontested |

Canonical prefix changed **in 3.43.0**, because each still held a form its
sibling derives too:

| species | was | now | old spelling |
|---|---|---|---|
| *Lanius collurio* | `LaniColl` | `LaniusCollurio` | context only |
| *Leucogeranus leucogeranus* | `LeucLeuc` | `LeucogeranusLeucogeranus` | context only |

*Chrysolophus pictus* keeps `Chpi` throughout and gains `ChryPict` as a
context-only prefix, since it derives that form as well.

**Subspecies mint no generated alias.** A trinomial entry such as *Canis lupus
baileyi* deliberately does not claim `CanisLupus`, which belongs to its parent
binomial, and no third-token variant is generated. Subspecies are reached by
their curated prefix (`Caba`) or by latin name.

A 5+5 form (`HomoSapie`) existed up to 3.41.0 as a leftover of the pre-v3.12
scheme, and was removed in 3.42.0: no bundled corpus name, and no species token
in the sibling `mhcseqs` dataset, ever used one. See issue #128.

**This is a breaking parse change.** 596 auto-generated 5+5 aliases stop
resolving, and so do ten that had been curated by hand as `other prefixes`
when the scheme was introduced:

```
MonopAlbus  GaviaGange  CaimaCroco  CaimaLatir  CaretCaret
ChrysPicta  CasuaCasua  CyaniCaeru  PhasiColch  CycluCarin
```

Anything written with a 5+5 form should move to the concatenated binomial —
`HomoSapie-A*02:01` becomes `HomoSapiens-A*02:01`.

## Where a prefix came from

`Species.prefix_provenance` says how an entry came by its prefix:

| value | meaning |
| --- | --- |
| `"designated"` | Published nomenclature — IPD-MHC or IMGT/HLA writes alleles with it. Curated with a source in `species.yaml`; never inferred. |
| `"generated"` | mhcgnomes derived it from the latin name. Provable by re-deriving it. |
| `"group label"` | Names a grouping rather than a species, and is never written on an allele: `Aves`, `Galliformes`, `NHP`. |
| `None` | Not established. |

```python
>>> Species.get("HLA").prefix_provenance
'designated'
>>> Species.get("TachAcul").prefix_provenance
'generated'
>>> Species.get("NHP").prefix_provenance
'group label'
```

`None` is deliberately distinct from `"designated"`: a prefix mhcgnomes did not
generate is not thereby proven to be in published use. Most short prefixes are
still unchecked — see issue #131.

**Which prefixes are established vs generated:** Comments in `species.yaml`
document which prefixes are attested in MHC literature and which were generated
by mhcgnomes. Established prefixes are never changed; generated prefixes are
subject to replacement if a community convention emerges.

See the [curation guide](curation.md) for the full prefix conflict resolution
policy.
