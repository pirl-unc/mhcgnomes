# Make serotype regeneration idempotent, and fix the release flow AGENTS.md documents

Tracking issues: #156, #152

## Review

### #156 -- and I filed it with the hazard backwards

I reported that regenerating `serotypes_generated.yaml` would silently drop 15
rows. That is wrong. I had compared `build_serotype_mappings` output -- the
pure dictionary transform, 135 rows -- against the file, and never ran the
script. `generate_yaml` explicitly carries forward serotypes the dictionary has
no row for, with a comment saying so, and running it produces **170** rows, not
135. The C locus above Cw10, the DP workshop specificities and the B17 splits
are preserved by design.

**The real hazard is narrower and points the other way.** Regenerating
*re-adds* `A*2418` to `A3`, undoing a curation fix:

```
A*24:18   WHO Assigned Type = "A24(9)/A3"
          Comments = "A2403x3; short A24 with most A3 and A9 reactive; NN: A24"
```

`parse_serotype` splits the dual type into both serotypes, so the allele lands
in `A3` as well as `A24`. Curation had removed it from `A3` -- correctly, on
the dictionary's own comment -- and a regeneration would put it back with
nothing to notice.

So the fix is a `CURATED_EXCLUSIONS` set in the generator, carrying the pair
and the reason. With it, regenerating reproduces the runtime table exactly:

```
regenerated == serotypes.yaml : True
differing rows                : []
```

Four tests pin it, including one asserting every exclusion is a pair the
dictionary actually asserts, so a stale entry cannot outlive its reason.
Verified by mutation: removing the exclusion fails the suite.

This also settles part of #153. `Cw15` and `Cw17` are in the carried-forward
set -- not derived from the dictionary -- so they are not evidence about what
the dictionary says, and a test now names them so that stays visible.

### #152 -- AGENTS.md documented a command that does not exist

Golden Rule 2 said `deploy.sh <version>` handles the bump. `deploy.py` has no
positional version argument, and `deploy.sh` runs `./lint.sh` and `./test.sh`
before passing arguments through, so following the instruction burns the full
suite and then fails on argparse.

Corrected to the flow that exists and that every release in this repo actually
uses: bump `version.py` in the PR, then `./deploy.sh` with no arguments from a
clean `main`. Implementing the argument instead would have made `deploy.sh`
mutate the working tree, which its own `ensure_clean_tree` check exists to
prevent.

- **Measured:** 0 of 11,558 corpus names change. The runtime serotype table is
  byte-identical; only the intermediate artifact and the generator changed.
- Bumped to 3.48.2.
