# Carry the caller's spelling to the gene lookup (#160)

## Review

- **The ranking key had never fired.** `parse_gene_without_species` ranks
  candidate species by `declares_gene_with_same_case(gene_name)` first, and the
  comment above it explains that "Ia1" is *Paralichthys olivaceus* and "IA1" is
  *Chrysolophus pictus*. But the tokenizer lower-cases every token, so the
  function only ever saw `ia1`, which nobody spells that way. The key was dead
  code the comment described as working.

- **`Token.raw_string` had the spelling the whole time.** Threaded it to the
  gene and allele lookups; `parse_haplotype` has no use for it, so the call
  loop pairs each function with its own kwargs rather than growing a
  parameter nobody wants.

- **19 gene forms that returned None now resolve**, and nothing stops
  resolving: `Ia1`/`IA1`, `Ia2`/`IA2`, `AB1` (mouse) vs `Ab1` (Roborovski
  hamster), `DAA-1`, `DAA-2`, `DAA2`, `DMB-1`. Each has exactly one same-case
  declarer, so each is precise rather than a guess.

- **A second bug fell out of the first.** The preference for a species the
  caller named compared `default_species` -- often a latin-name *string* --
  against a list of `Species` objects, so it fired only for callers passing an
  object. Nothing noticed while the case-aware key was dead. Once spellings
  worked, a UniProt line reading `OS=Mus musculus ... GN=Mr1` lost its own
  species to *Rattus sp.*, the only entry spelling MR1 that way. Fixed by
  resolving `default_species` before the membership test; a named species now
  outranks a spelling, which is the right order.

- **Measured:** 0 of 36,752 corpus names change; 19 of 1,066 gene forms change,
  all None -> a resolution. 16,129 tests pass. Reverting the spelling
  pass-through fails 18 tests, reverting the default-species fix fails 2.
- Bumped to 3.52.0.
