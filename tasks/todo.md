# Make old-name allele aliases reachable; NetMHC's short Mamu names (#216)

GitHub issue: #216

## Evidence

- [x] Find why `Mamu-B08` ignored the curated `B*08 -> B*008:01`. The parser
  zero-pads allele fields (Mamu-B to 3 digits) when it builds the `Allele`,
  and `transform_parse_candidate` looks the alias up afterwards, by `B*008`.
- [x] Measure it across the whole table rather than for one species. Parsing
  every gene-bearing alias key with `use_allele_aliases=True` and comparing
  with its target found 22 unreachable keys: the 7 Mamu-B two-digit names,
  Mamu `A1*1701`, `A1*5801`, `A1*030102`, and 11 old 5-digit MICA/MICB names
  (`MICA*00201` became `MICA*000:201`, not `MICA*002:01:01`). It also found a
  Mamu NetMHC row, `B*8701 -> B*087:01`, filed under Saha.
- [x] Settle "IPD's old names vs NetMHC's" from primary sources, not from our
  table. Our Mamu block matches the 2012 nomenclature report's ESM1 (PMID
  22526602) row for row. IPD-MHC's `previous` field names the allele numbered
  NN+1 for 33 of its 57 two-digit Mamu-A/B old names (A*26 -> A1*011:01,
  NHP01884). NetMHC 4.0's `MHC_allele_names.txt`, Wiseman 2011 Table 1 (PMID
  21270169) and the GenBank deposits' sequences agree with the report.
- [x] Check `Mamu-B17`: it is an IPD-MHC locus (`Mamu-B17*01:02:02`,
  NHP02096), not only NetMHC's short name for B*017:01.

## Implementation

- [x] `Parser._is_allele_alias_as_written`: when aliases are on and the fields
  as written are an alias key, build the allele without zero-padding so the
  alias step finds it. Default parsing is unchanged.
- [x] Add `A*07 -> A1*007:01` (NetMHC's `Mamu-A07`), move `B*8701` back to
  Mamu, and cite the sources in `curated_allele_aliases.yaml`. Regenerate
  `allele_aliases.yaml` with `combine_allele_aliases.sh`.
- [x] Leave bare `Mamu-B17` as the gene, and say why in the YAML and a test.
- [x] Tests: a sweep that every alias key resolves to its target (exceptions
  only for #231/#232), the issue's NetMHC table, narrow old names, default
  mode unchanged, current lineage names untouched, `Mamu-B17` stays the locus.
- [x] File what the sweep found that is not this bug: #231 (current names
  `A*02:172` / `B*15:112` collide with old colon-free keys) and #232 (alias
  resolution depends on `PYTHONHASHSEED`).
- [x] Bump to 3.64.12; run `./format.sh`, `./lint.sh`, `./test.sh`.

## Review

- Without aliases, `Mamu-B08` still parses to `Mamu-B*008`, which reads as
  the current B*008 lineage although the input names one allele. Resolving old
  names stays opt-in, as the issue suggested; #215 has to treat that output
  accordingly.
