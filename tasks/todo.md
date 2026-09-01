# Fix what the #138 review found, after it shipped

Follow-up to #138 (3.43.0), which merged before its review reported.

## Review

- **The error message asserted something untrue.** A contested prefix reached
  the `context only prefixes` bucket, whose message says the string is
  "source-attested for multiple species". Nothing has ever published a
  `ChryPict-*` allele -- the form exists only because the 4+4 rule derives it
  from two binomials. The message now branches:

  ```
  ChryPict -> "derivable by the same naming rule from Chrysemys picta,
               Chrysolophus pictus, so it names neither"
  Moal     -> "source-attested for multiple species (Monopterus albus,
               Motacilla alba)"
  ```

  `Moal` genuinely is attested for both, so it keeps the old wording.
- **The remedy it offered had the same bug it was diagnosing.** The message
  suggested `sp.prefix` as "a collision-free canonical prefix", which for
  *Chrysolophus pictus* is `Chpi` -- and Klein's 2+2 rule derives `Chpi` from
  *Chrysemys picta* too. It now offers the concatenated binomial, the only form
  with no collisions anywhere in the ontology.
- **An explicit non-claimant species lost the diagnostic.** The contested-prefix
  message was only built when `species is None`, so
  `parse("ChryPict-UA*01", species="Gallus gallus")` fell back to
  "Could not parse" -- failing quietly in exactly the case where the caller had
  been most explicit. It now explains, and adds which species was asked for.
- **My README example demonstrated nothing.** It used `ChryPict-B`, but
  *Chrysemys picta* declares no `B` gene, so that string returned `None` on
  3.42.0 as well. The input that actually changed is `ChryPict-UA*01`. Both the
  README and `docs/curation.md` used the vacuous one.
- **The prefix table mixed two releases** under one "was -> now" heading, so a
  reader on 3.42.0 would conclude *Chrysemys picta* was about to change (it had
  already) and *Lanius collurio* had already (it was about to). Split by
  release, and 3.43.0 now carries the breaking-change callout that 3.42.0's
  section established.
- **`group` accepted any truthy value.** Its neighbour `prefix source` is
  validated against a value set, but `group` was read with a bare `.get`, so
  `group: "false"` would have silently turned a species into a group entry --
  stopping it handing its prefix down to every descendant. Only `true` is
  accepted now.
- **`Species.is_group` is public.** #135 moved group-ness into the data but
  left it behind a module-private function reading `raw_species_dict`, so a
  downstream consumer still had to re-derive it from `name.endswith(" sp.")` --
  the heuristic that gets NHP wrong, which was the point of #135.
- Also: `"group"` had been inserted directly under the comment declaring the
  keys below it dead, so a future cleanup of #139 would have deleted it;
  `_is_group_entry`'s docstring claimed group-ness alone decides provenance,
  when it is one half of a conjunction; six identical four-line rationales in
  `species.yaml` collapsed to one line each pointing at `docs/curation.md`; the
  `context only prefixes` definition 290 lines earlier still said the bucket is
  only for attested strings; five over-long prose lines re-wrapped; and a
  function-local import moved to module scope.
- **Measured:** 0 of 11,558 corpus names change against a worktree of `main`.
  6 new tests, covering both wordings, the suggested prefix, the explicit-species
  path, the `group` validation and `is_group`.
- 3.43.2, since 3.43.1 is #140.
