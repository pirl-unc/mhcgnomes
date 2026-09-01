# Correct what the Lr- tables say about "+" (#162)

## Review

- **I wrote an interpretation into a curated file that the source does not
  state.** #183's comment said the five excluded rows use `+` to mean "an
  additional allele beyond the group". That was my reading, not the paper's.

- **What the paper actually says.** Table 1 never explains `+` at all. Table 2's
  footnote 3 addresses one instance and says only "Positive with both DQA*04XX
  primer sets in lanes D12 and C12" -- an assay result, not a definition of the
  notation. Whether `12XX + 11:04` means a second allele at the locus, a
  duplicated locus, or an unresolved call is not something these tables say.

- **And "+" was never the representation problem I implied.** Two members at
  one locus is already how Lr-02.0 records `02XX,07XX`. Those five rows are out
  because the meaning is unestablished, not because the format cannot hold
  them -- a materially different reason, and the one a future curator needs.

- **"/" is unaffected.** A slash between two specificities at one locus reads
  as alternatives, and a disjunction really is a member this format cannot
  express. That remains the open half of #162.

- No data changed; 17,130 tests pass.
- Bumped to 3.64.1.
