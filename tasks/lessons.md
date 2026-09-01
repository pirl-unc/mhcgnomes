# Lessons

Patterns worth not repeating, written after a correction landed.

## Do not generalize one exception into a model

**What happened.** `Bubalus bubalis` sits under `Bos sp.` despite being another
genus. Working out why (#109, #115) produced a correct answer -- the edge
exists because IPD-MHC files water buffalo in the BoLA group -- and then an
incorrect generalization: that the whole species tree is "prefix scope, not a
phylogeny". That went into the README, `docs/curation.md` and `AGENTS.md`, with
`Homo sapiens` sitting outside `Primata sp.` offered as the clinching second
example. #122 pointed out that human's placement was not evidence for a model,
it was a bug.

**Why it was wrong.** One counterexample bounds a rule; it does not replace it.
A sweep of every parent link found exactly one that crosses a genus boundary. The tree is containment, taxonomic wherever it can be, with the
umbrella prefix as a separate opt-out-able property -- which the loader had
always implemented and which nobody had looked at.

**How to apply.** Before writing a model into the docs, count how many entries
actually support it. If the answer is one, write down the exception, not the
model. Reading the code that implements the structure is part of establishing
what the structure means.

## Prefer fixing the structure to encoding an exception

**What happened.** #122 said `Primata sp.` excludes `Homo sapiens` because its
prefix is `NHP`. Two fixes were shipped before the right one. The first made
human a child of the node and blocked prefix inheritance, which leaked (below).
The second added a `prefix excludes` YAML key, a `prefix_excluded_species`
field, a `Species.can_name` predicate and a docs section explaining when to
prefer it over `compatible_with`. A downstream reader filed #126 within hours
asking which of the two predicates answered which question.

**Why it was wrong.** `NHP` is the primate order *minus humans* -- paraphyletic,
not a taxon -- and it was sitting on the node for the primate order. One node
was standing for two different sets. Every line of that machinery existed to
paper over that. Giving `NHP` its own entry, sibling to `Homo sapiens`, made
both questions plain ancestry and deleted all of it.

**How to apply.** When a fix needs a new concept to describe a special case,
check first whether the data can be shaped so the special case does not exist.
A predicate that has to be explained in docs is a sign the structure is wrong;
"which of these two similar methods do I want" is a question the data model
should be answering, not the reader.

## An invariant asserted in prose has to be tested on every path

**What happened.** The first fix for #122 gave `Homo sapiens` a parent of
`Primata sp.` and blocked the `NHP` prefix from being inherited, then said in
the README, in `docs/curation.md` and in the PR body that "`NHP-*` still cannot
name it". Code review found that it could:

```
parse("NHP-E*01:01", species="Homo sapiens")  ->  HLA-E*01:01
Species.get("Homo sapiens").compatible_with("NHP")  ->  True
```

**Why it was wrong.** Prefix inheritance is only one of four things that read a
parent link. `is_ancestor_of`, `compatible_with` and the ancestor-to-descendant
conversion behind `parse(..., species=...)` all saw a plain parent edge and had
no way to know about the opt-out, because the opt-out lived in the loader. The
measurement that "proved" the change inert -- 11,558 corpus names, every field
of 671 species objects -- did not cover the `species=` argument at all, so a
clean result was mistaken for a complete one.

**How to apply.** Before writing a guarantee into docs, grep for every consumer
of the thing being changed and write a test per consumer. And when a
measurement comes back clean, ask what it does not cover: a corpus of names
exercises one entry point, not the API surface around it.

## Verify which copy of the package you just measured

**What happened.** An A/B measurement of a data change reported "0 changes" and
also, impossibly, no change to the field being edited. The measurement scripts
lived in a scratchpad directory, so `sys.path[0]` was that directory and
`import mhcgnomes` resolved to the installed copy in the shared virtualenv, not
the working tree. Both halves of the A/B measured the released version.

**Why it matters.** The failure is silent and the output looks like a clean
result. It would have supported the wrong conclusion just as convincingly as
the right one.

**How to apply.** Any script that measures the working tree asserts it first:

```python
import mhcgnomes, os
assert os.path.abspath(mhcgnomes.__file__).startswith(os.path.abspath(os.getcwd()))
```

The same trap has a second form: `git stash` only puts back *uncommitted*
changes, so once a branch has commits on it, stash-and-remeasure compares the
branch against itself. Compare against a `git worktree` of `main` instead.

More generally: when a measurement returns exactly the null result, check that
the instrument was pointed at the thing being measured. A diff that shows no
change to the line you just edited is an instrument fault, not a finding.

## A corpus is only as good as what is in it

**What happened.** Every measurement for several PRs was quoted as "0 of 25,200
corpus names change". Measuring #130's lineage rule against that corpus also
reported 0 differences -- while 17 tests failed, nearly all of them on IEDB's
bare `BF2*2101` forms. The scratchpad corpus had been built from some of the
bundled name lists and not others: `tests/iedb_allele_counts.csv` and the
netMHCpan/netMHCIIpan lists were missing. Rebuilt, it is 36,752 names, and the
BF2 forms showed up immediately.

**Why it was wrong.** A zero from an incomplete corpus reads exactly like a
zero from a complete one, and it is the more reassuring of the two. The
earlier PRs' zeros happened to survive re-measurement against the larger set,
but that was luck, not method.

**How to apply.** Build the corpus from the repo's own name lists, by globbing
them, not by hand. Before quoting a difference count, say which corpus and how
many names -- a number that never changes between PRs is a sign it is stale.
And when tests disagree with the corpus, the corpus is the thing to doubt.

## "Attested" in our own curation is a claim, not evidence

**What happened.** Two prefixes carried notes saying someone else had attested
them. `Iibi` for the greater prairie chicken: *"mhcseqs uses Iibi -- unusual
but attested"*. The six primate `_LA` codes: the mhcseqs registry cites the de
Groot nomenclature report. Following both citations: `IIBI` occurs once in the
entire nucleotide database, as `/gene="IIBI"` `/product="MHC class II antigen
beta chain 2"` -- a gene symbol, harvested as a species code -- while `Tycu`
names 80 GenBank records at allele level. And the de Groot report contains
`Patr` 77 times and none of the six `_LA` codes at all.

**Why it was wrong.** Both notes read as if the checking had been done. Neither
recorded *what* was attested or *where*, so the claim propagated unexamined --
in one case into the runtime prefix, so `Tycu-BLB*28` was displayed under a
gene symbol.

**How to apply.** A note that says "attested" without a PMID, accession or URL
is a to-do, not a source. Both of these were also derivable-rule failures:
neither `Iibi` nor any `_LA` code can be produced from its binomial by the
Klein rule, which is a free check that would have flagged both.

## When the canonical URL is dead, look for the mirror

**What happened.** #153 turned on whether `Cw16` is a recognised serological
specificity. `hla.alleles.org/pages/antigens/recognised_serology/` is a 404,
the 2010 nomenclature paper's table did not extract, and the conclusion drawn
from the shipped dictionary -- that HLA-C serology stops at Cw10 -- was wrong.

**Why it was wrong.** The WHO Nomenclature Committee's own files were one fetch
away the whole time. ANHIG/IMGTHLA mirrors `wmda/hla_nom.txt`,
`rel_ser_ser.txt` and `rel_dna_ser.txt`, and `hla_nom.txt` records
`Cw;16;20260128;;;` -- assigned by the 2026 nomenclature report, after the
bundled dictionary was made. The same repository holds `Allelelist.txt`, which
settled #113 in one fetch after I had asserted the opposite from the gene list.

**How to apply.** For IPD-IMGT/HLA, go to
`raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/` first: it is versioned,
machine-readable, and current. "The source is unreachable" is a claim about
one URL, not about the source.

## A comment and its code disagreeing means the code has never done it

**What happened.** Three separate bugs in one session, all the same shape.

- `parse_gene_without_species` ranked candidates by
  `declares_gene_with_same_case`, above a comment explaining that "Ia1" is
  *Paralichthys olivaceus* and "IA1" is *Chrysolophus pictus*. The tokenizer
  lower-cases every token, so the key had never once fired (#160).
- `Gene.to_string` renders CD1 genes with "the common species name **if
  possible**", and never checked whether it was possible. 148 printed forms did
  not parse back (#177).
- `Species.get`'s ladder said "prefer the species that isn't a subspecies (**no
  parent with same identifier**)" and tested `sp.parent_species is None` -- no
  parent at all -- so it only fired for root entries, and a common name shared
  by a genus node and its own descendant resolved to nothing (#180).

**Why it happens.** A comment records what someone meant. The code records what
they wrote. Nothing keeps them together, and the mismatch is invisible because
the comment reads as documentation of working behaviour -- in each case the
surrounding tests passed, because they tested the outcome the broken path
happened to produce by another route.

**How to apply.** When reading a comment that explains *why* a line is subtle,
check that the line does the subtle thing. Cheapest version: construct the
input the comment is about and watch it flow through. "Ia1" versus "IA1",
`Aole-CD1a`, `Species.get("swordtail")` -- one example each, and all three fell
over immediately. A comment that names a specific case is offering you a test;
write it.

## Ask what else an invariant would catch

**What happened.** #176 needed a measurement, so it got one: every string the
package prints must parse back. That had never been tested. It failed 148 times
and produced #178 and #179. Asking the same question about a *different*
property -- does every identifier a species advertises resolve back to it --
produced #180 within minutes.

**Why it matters.** None of the three was reported by anyone. They were found by
stating a property the package obviously ought to have and then checking it,
which is much cheaper than reading code looking for bugs.

**How to apply.** After adding a measurement for one change, ask what its
siblings are and run them once. Six were checked here; two found bugs and four
came back clean, and the clean ones are worth knowing too -- they are why the
sweep could stop. Stop when the technique stops producing, not when the list of
possible probes runs out.

## Published nomenclature is not registry membership

**What happened.** Comments called `SahaI*49/82` and `SahaI*74/88` "IPD-style"
and said their four candidate names were "IPD entries". The `SahaI*NN`
convention is real and well attested in Tasmanian-devil papers and GenBank, but
the current IPD-MHC release contains no `Saha` or *Sarcophilus* entry at all.

**Why it was wrong.** A name can be used consistently in primary literature
without being curated by the registry that governs related nomenclature. The
paper and registry answer different questions, and borrowing the registry's
authority made the source-specific slash semantics sound standardized.

**How to apply.** Cite the paper for how an author writes a name, the sequence
accession for what biological record it denotes, and the registry release for
whether the registry contains it. Never substitute one of those checks for
another.
