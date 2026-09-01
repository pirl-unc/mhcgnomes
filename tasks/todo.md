# Make every printed form parse back (#177)

## Review

- **The invariant was never tested, which is why 148 names violated it.**
  Requiring that `parse(x.to_string())` succeed is now a test in its own right,
  over every CD1 form in the ontology. Whatever is decided later about the CD1
  branch, printing something unparseable fails here first.

- **Two causes, found by chasing rather than assuming.** #178 fixed the first:
  the species matcher tried three leading tokens, so 41 long common names were
  unreachable. That took the failures 148 -> 130 and no further, which is what
  pointed at the second.

- **`normalize_string` deletes hyphens; the parser joins tokens with a space.**
  So "long-haired rat" is stored as `LONGHAIRED RAT`, while a token sequence
  produces `LONG HAIRED RAT`. A hyphenated multi-word name could never be
  reconstructed, however wide the window. Registering the space-substituted
  spelling as an additional alias makes both reachable, and only ever adds
  keys.

- **Guarded so it cannot invent gene names.** The extra alias is added only for
  identifiers that already contain a space, so `DMB-1` cannot become the
  two-token `DMB 1`. There is a test for exactly that.

- **Measured:** round-trip failures **130 -> 0**; every printed form in the
  36,752-name corpus now parses back. 359 corpus names change, **every one
  `None` -> a result**, none lost. 16,982 tests pass; removing the alias
  registration fails 127 of them.
- Bumped to 3.62.0.
