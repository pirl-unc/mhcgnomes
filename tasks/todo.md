# Add the rabbit class I locus series Orcu-U1..U9 (#170)

## Review

- **Filed this issue and then answered it.** I found `Orcu-U2*05:02:01:01`
  failing to parse while establishing the `Orcu` prefix from GenBank (#169),
  filed #170, and handed it back on the grounds that `U` is the teleost class I
  convention and so deserved the literature rather than an accession title.
  Reading further settles it in the other direction.

- **It is a system, not a submitter's label.** GenBank has 104
  *Oryctolagus cuniculus* MHC class I records spread over nine loci:

      Orcu-U1  29    Orcu-U4  10    Orcu-U7   9
      Orcu-U2  17    Orcu-U5   5    Orcu-U8   9
      Orcu-U3  13    Orcu-U6   5    Orcu-U9   7

  The submissions accompany Zhang et al., "MHC-I diversity enables rapid
  adaptation during a viral pandemic in wild rabbit populations", PNAS
  2026;123:e2532064123 (PMID 42113988), whose authors include Jim Kaufman. The
  `U` prefix being a non-mammalian convention is what made it worth checking,
  and is not evidence against it.

- **Filed as class I with no subclass.** The records say "MHC class I antigen"
  and nothing establishes which of the nine are classical.

- **On the species, not the genus node**, because that is what the records
  name. The A/A1/A2/A3/D series stays where it is on `Oryctolagus sp.` under
  the RLA prefix (PMID 32522857); how the two nomenclatures relate is still
  open and is the remaining half of #170.

- **The bare `Orcu*19` form is deliberately not added.** Twenty-one older
  records label the gene with the species code itself. Making a prefix its own
  gene name is the shape that put a class II beta chain symbol in the prefix
  column for the greater prairie chicken (#165).

- **Bare `U1` and `U2` stop resolving, and that is the honest answer.** Rattus
  sp. declares both, so they are now genuinely ambiguous between rat and
  rabbit; nothing attests the bare form for either, and the rat won them only
  by being the sole declarer. `RT1-U1` and `Orcu-U1` both work. U3-U9 have one
  declarer and resolve bare.

- **Measured:** 0 of 36,752 corpus names change. Of 1,080 gene forms, 4 stop
  resolving (`U1`, `U2` and their allele forms) and 14 start. 16,409 tests
  pass.
- Bumped to 3.57.0.
