# Give NHP its own node instead of a naming predicate

Tracking issues: #126 (raised against 3.40.0), follow-up to #122

3.40.0 put `Homo sapiens` under `Primata sp.` and, because that node owns the
`NHP` prefix, had to add a `prefix excludes` declaration and a
`Species.can_name` predicate to stop `NHP-*` naming a human. #126 pointed out
the cost: `compatible_with` was quietly switched from ancestry to naming, so
there was no longer a way to ask the ancestry question, and two near-identical
predicates now had to be chosen between.

## Specification

- [x] Check whether the two questions can be made one by shaping the data
      instead of adding a predicate.
- [x] Give `NHP` its own entry, sibling to `Homo sapiens` under `Primata sp.`,
      and move the 55 non-human primates under it.
- [x] Delete `prefix excludes`, `prefix_excluded_species` and
      `Species.can_name`; restore `compatible_with` to plain ancestry.
- [x] Measure against a worktree of `main`: corpus, compatibility over every
      species pair, and every structural field.
- [x] Record the paraphyly constraint the split imposes on future taxa.
- [x] Update README, `docs/curation.md`, `AGENTS.md` and the tests.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, `./test.sh`.

## Review

- **The structure answers both questions, so the predicate is unnecessary.**
  `Primata sp.` is now the primate order with prefix `Primata`; `NHP` is a node
  of its own holding the 55 non-human primates. `Homo sapiens` is a sibling of
  `NHP`, not a descendant, so:

  ```
  compatible_with("Homo sapiens", "Primata sp.")  ->  True   (was False)
  compatible_with("Homo sapiens", "NHP")          ->  False
  parse("NHP-E*01:01", species="Homo sapiens")    ->  None
  ```

  All three are plain `is_ancestor_of`. `can_name`, `prefix excludes` and the
  docs section explaining which predicate to use are gone.
- **The general rule this yields:** every MHC prefix owns a node, so "is X
  inside taxon Y" and "can Y's prefix name X" are the same question. A prefix
  whose group is not a taxon needs its own node. `NHP` is the first such case
  because it is paraphyletic -- the primate order minus humans.
- **Constraint recorded on the node.** Any taxon added under `Primata sp.` must
  sit wholly inside or wholly outside `NHP`. `Homo sp.` works as a sibling;
  `Hominidae sp.` would not, since it would have to pull `Gorilla sp.`,
  `Pan sp.` and `Pongo sp.` out of the umbrella.
- **Measured against a worktree of `main`** (3.40.0's `Primata sp.` placement
  is the baseline): 0 of 11,558 corpus names change. Over the 671 species that
  exist in both, exactly one compatibility pair changes -- `Homo sapiens` vs
  `Primata sp.`, now True, which is what #126 asked for. One node is added.
- **A simplification falls out.** On main `find_matching_species_objects("NHP")`
  returned 54 objects, because 53 species carried `NHP` as an inherited
  `old prefix` and were collapsed to the owner by the #103 tie-break. `NHP` is
  its own taxon name now, so nothing inherits it and the lookup returns 1.
- **Visible output change.** `NHP` and `NHP class I` resolve to the new node
  rather than to `Primata sp.`, and `primate` now resolves to `Primata sp.`
  with prefix `Primata`. Those two strings used to give the same answer; they
  are different questions and now give different answers. No corpus name is
  affected.
- Bumped 3.40.0 to 3.41.0. `Species.can_name`, added in 3.40.0, is removed
  again in the same day; it was public for one release and is called out in the
  PR so anything that picked it up knows to use `compatible_with`.
