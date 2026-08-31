## Golden Rules

1. **Never commit to `main`.** Always `git checkout -b <feature-branch>` before editing. Land via PR.
2. **Every PR bumps the version.** Even doc-only PRs — at minimum a patch bump. `deploy.sh <version>` handles the bump + commit + push.
3. **"Done" means merged AND deployed to PyPI** — never stop at merge. After a PR merges, run `./deploy.sh` from a clean main. Skipping deploy = task not done.
4. **File problems as issues, don't silently work around them.** If you hit a bug here or in a sibling openvax/pirl-unc repo, open a GitHub issue on the correct repo and link it from the PR.
5. **After a PR ships, look for the next block of work.** Read open issues across the relevant openvax repos, group by dependency + urgency. Prefer *foundational* changes that unblock multiple downstream improvements; otherwise chain the smallest independent improvements.

---

## Before Completing Any Task

Before considering any code change complete, you MUST:

1. **Run `./format.sh`** - Auto-format all code
2. **Run `./lint.sh`** - Verify linting passes (this runs both `ruff check` and `ruff format --check`)
3. **Run `./test.sh`** - Verify all tests pass

Do not tell the user you are "done" or that changes are "complete" until all three of these pass.

## Scripts

- `./format.sh` - Formats code with ruff (run this first)
- `./lint.sh` - Checks linting and formatting (must pass). **Always use this for linting if it exists.**
- `./test.sh` - Runs pytest with coverage (must pass)
- `./deploy.sh` - Deploys to PyPI (gates on lint.sh and test.sh). **Always use this for deploying if it exists.**
- `./develop.sh` - Installs package in development mode

## Code Style

- Use ruff for formatting and linting
- Configuration is in `pyproject.toml` under `[tool.ruff]`
- Line length: 100 characters
- Target Python version: 3.9+

---

## Workflow Orchestration

### 1. Upfront Planning
- For ANY non-trivial task (3+ steps or architectural decisions): write a detailed spec before touching code
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use planning/verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 3. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between the latest code and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 4. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 5. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Fix failing unit tests without being told how

---

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Scientific Domain Knowledge

- **Read the literature. Always.** Before changing anything that expresses a
  scientific claim — a gene's class, a species' prefix, a parent-child
  relationship, a pseudogene flag — go and read the source. Do not reason from
  the name, from what is already in the file, or from what sounds right.
- **Do not guess.** If you cannot find a source, say so plainly and leave the
  data alone. "I could not establish this" is a valid, useful answer. A
  confident guess written into a curated ontology is worse than a gap, because
  the next reader cannot tell it from a checked fact.
- **Do not assume our existing curation is right.** It is a secondary source
  and it has been wrong: Patr-AL was class Ia when the paper describing it is
  titled "nonclassical" (#107); `Pren` was claimed by two different genera
  (#110); `Homo sapiens` hung off the root rather than under the primate node,
  so the library denied that humans are primates (#122). Existing tests can
  encode the same errors — check the authority before assuming a failing test
  means your change is wrong.
- **Do not assume our curation is wrong either.** The inverse of the rule
  above, and just as costly. Structure that looks incorrect is often load-
  bearing: `Bubalus bubalis` sits under `Bos sp.` despite being another genus,
  which two readers filed as a bug, but IPD-MHC files water buffalo in the BoLA
  group and detaching it would have broken every published `Bubu-*` class II
  parse. Before changing a structure, check what depends on it -- what stops
  parsing, what test covers it, what the papers actually write.
- **Do not generalize one exception into a model.** The buffalo edge is a real
  departure from taxonomy, but reading it as proof that the whole tree is
  "prefix scope, not phylogeny" was an over-correction: exactly one parent link
  in the ontology points at another genus's node. One counterexample bounds a
  rule; it does not replace it.
- **An invariant you assert in prose has to be tested on every path.** The
  first fix for #122 blocked `NHP` from reaching humans through prefix
  inheritance, and the PR said "`NHP-*` still cannot name it" -- but three
  other things read the parent link, and `parse("NHP-E*01:01",
  species="Homo sapiens")` duly returned `HLA-E*01:01`. Before claiming a
  guarantee, enumerate the consumers of the thing you changed and test each
  one.
- **Prefer fixing the structure to encoding an exception.** The next attempt at
  #122 kept `NHP` on the primate node and added a `prefix excludes` key, a
  `Species.can_name` predicate and a docs section to explain when to use which
  of two near-identical predicates. Giving `NHP` its own node deleted all three
  and made both questions plain ancestry (#126). If a fix needs a new concept
  to describe a special case, check whether the data can be shaped so the
  special case does not exist.
- **An official designation is not the same as attested usage.** The naming
  rule is mechanical, so several species can derive the same code, and only
  one of them is usually the one that appears in print — the rest are
  synthetic. Before handing a prefix to a species because a committee assigned
  it, check whether anyone has actually published alleles under it. `Caau` is
  designated to *Canis aureus*, which has no deposited sequences, while
  `Caau-DAB` and `Caau-UFA` are in active use for *Carassius auratus*; giving
  the designation the runtime prefix silently broke every goldfish parse.
  Where they conflict, the attested side gets the prefix and the designation
  is recorded as `context only prefixes`.
- **Flag inconsistencies**: if code expresses a scientific model at odds with
  the literature, say so and file it rather than working around it.

### Authorities to check

Check the primary source, not a summary of it. When a tool summarizes a page
for you, re-read the specific claim verbatim before acting on it — summaries
invent plausible entries (a summary of the IPD-MHC group list reported "CLA =
cat" and "CeLA = deer"; both are wrong — CLA is goat, CeLA is cetacean).

| resource | authoritative for | where |
|---|---|---|
| IPD-MHC | non-human species designations, prefixes, loci | `ebi.ac.uk/ipd/mhc/group/<CODE>/species` |
| IMGT/HLA | human gene names and pseudogene status | `hla.alleles.org/genes/index.html` |
| Comparative MHC Nomenclature Committee | official prefix assignments (via IPD-MHC) | `ebi.ac.uk/ipd/mhc/committee/` |
| Klein et al. 1990 | the naming rule itself | Immunogenetics 31:217-219, PMID 2329006 |
| de Groot et al. 2019/2020 | primate MHC nomenclature report | Immunogenetics 72:25-36 |
| NCBI Taxonomy / GBIF | species synonymy and rank | for parent-child questions |

The species prefix rule (Klein 1990, restated on every IPD-MHC nomenclature
page) is **first two letters of the genus, last two of the species** — `Patr`
for *Pan troglodytes*. It is mechanical, so a prefix can be checked by
derivation, and a prefix that cannot be derived from a species' binomial does
not belong to it.

### Record the source

**When you establish something from a source, cite it where the data lives** —
a comment in `species.yaml` next to the entry, or in the code next to the rule.
Include the PMID or URL and one line on what it establishes, so the next person
does not have to redo the search. Follow the style already in `species.yaml`:

```yaml
    Ib:
      # PMID 11564803 (Adams, Cooper & Parham, J Immunol 2001;167:3858) named
      # AL a nonclassical class I molecule in its title: only three allotypes,
      # present on ~50% of chimpanzee MHC haplotypes, low expression.
      - AL
```

A finding that is not written down next to the data will be re-litigated.
