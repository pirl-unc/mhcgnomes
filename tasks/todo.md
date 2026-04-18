# Ontology Precision Fix Plan

- [x] Review the amphibian hierarchy and confirm where `UEA` should live
- [x] Check the removed fish/turtle parser labels against literature and database naming
- [x] Move `UEA` from `Amphibia sp.` to a frog-level node that matches the evidence
- [x] Add a salamander parent node and reparent salamander/newt species under it
- [x] Remove redundant inherited bird chain additions that do not change runtime behavior
- [x] Add targeted tests for amphibian inheritance and redundant bird cleanup
- [x] Run `./format.sh`
- [x] Run `./lint.sh`
- [x] Run `./test.sh`

# Notes

- `UEA` is supported in Xenopus-backed sources, not as a pan-amphibian gene.
- Recent salamander work supports a distinct salamander architecture from Xenopus,
  but not a single shared salamander-specific locus set that is safe to canonize
  across Ambystoma, Triturus, Lissotriton, and Andrias.
- `Ctid-UHA103`, `Dila-a1..a30`, and `Pesi-B01` look like paper-local or
  sequence-level labels rather than stable comparative MHC nomenclature.

# Review

- Added `Xenopus sp.` as the narrow inheritance point for `UEA` and `Caudata sp.`
  as the salamander parent node, then reparented Xenopus and salamander entries.
- Removed redundant `genes:` blocks from `Falco sp.`, `Accipitriformes sp.`,
  `Gruiformes sp.`, and `Ardeidae sp.` because those genes were already inherited
  from `Aves sp.`.
- Added regression coverage to confirm:
  - Xenopus keeps `UEA`
  - salamanders do not inherit `UEA`
  - sequence-like labels `Ctid-UHA103`, `Dila-a1`, and `Dila-a30` stay rejected
  - `Pesi-B01` parses as allele `B*01`, not as a separate gene
- Validation:
  - `./format.sh` passed
  - `./lint.sh` passed
  - `./test.sh` passed (`52649` tests)
