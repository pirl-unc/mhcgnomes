# Give Gene the class II chain predicates it never had

Tracking issue: #137

## Specification

- [x] Reproduce: confirm `Gene.is_class2_alpha` / `is_class2_beta` are the
      inherited `Result` stubs, and that five chain-suffixed inputs fail.
- [x] Put one implementation where both `Gene` and `Allele` can reach it.
- [x] Check the mismatched-suffix case still fails.
- [x] Measure against a worktree of `main`.

## Review

- **`Gene` is a sibling of `ResultWithGene`, not a subclass.** Both descend
  from `ResultWithMhcClass`. `ResultWithGene` implemented the two predicates,
  so `Allele` and `Pair` were fine and `Gene` fell through to `Result`, where
  both are `return False`. Every class II gene therefore reported neither
  chain, with the answer sitting in `species.class2_gene_name_to_chain_type`.
- **It broke parsing, not just the API.** `parser.py` gates chain-suffixed
  candidates on these predicates and lists `Gene` among the candidate types, so
  a `Gene` candidate could never satisfy either branch:

  ```
  HLA-DRA alpha    ParseError     HLA-DR alpha         Gene HLA-DRA
  HLA-DRB1 beta    ParseError     HLA-DRA*01:01 alpha  Allele HLA-DRA*01:01
  ```

  The *less* specific input parsed and the more specific one did not, because
  `HLA-DR` is a `Class2Locus` and took a different branch.
- **The implementation moved up to `ResultWithMhcClass`** rather than being
  copied into `Gene`, and `ResultWithGene`'s copy is deleted. One expression
  now answers for `Gene`, `Allele` and `Pair`, and `Pair` -- which names no
  single gene -- correctly answers `None` through the same code path instead of
  through a stub that happened to agree.
- **A latent KeyError fixed on the way.** The old implementation indexed the
  chain table with `[]`, so a class II gene with no curated chain type would
  have crashed. Nothing in the ontology hits that today (a test asserts so),
  and `.get` now reports `None` rather than raising if one ever does.
- **Mismatched suffixes are still rejected**: `HLA-DRA beta`, `HLA-DRB1 alpha`
  and `HLA-DQA1 beta` all return `None`, so this answers the chain question
  rather than accepting any trailing word. `HLA-A alpha` parses because the
  class I heavy chain is an alpha chain, which is the existing rule.
- **Measured against a worktree of `main`:** 0 of 11,558 corpus names change.
  The change is purely additive -- names that failed now parse -- and no corpus
  name carries a chain suffix.
- 30 new tests, verified by mutation: stubbing the chain lookup back out fails
  14 of them.
- Bumped to 3.43.1, assuming #138 lands first as 3.43.0.
