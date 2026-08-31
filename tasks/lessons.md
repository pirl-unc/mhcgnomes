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
