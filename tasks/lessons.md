# Lessons

Patterns worth not repeating, written after a correction landed.

## Do not generalize one exception into a model

**What happened.** `Bubalus bubalis` sits under `Bos sp.` despite being another
genus. Working out why (#109, #115) produced a correct answer -- the edge
exists because IPD-MHC files water buffalo in the BoLA group -- and then an
incorrect generalization: that the whole species tree is "prefix scope, not a
phylogeny". That went into the README, `docs/curation.md` and `AGENTS.md`, with
`Homo sapiens` sitting outside `Primata sp.` offered as the clinching second
example. #122 pointed out that human's placement was not evidence for a model,
it was a bug.

**Why it was wrong.** One counterexample bounds a rule; it does not replace it.
A sweep of every parent link found exactly one that crosses a genus boundary. The tree is containment, taxonomic wherever it can be, with the
umbrella prefix as a separate opt-out-able property -- which the loader had
always implemented and which nobody had looked at.

**How to apply.** Before writing a model into the docs, count how many entries
actually support it. If the answer is one, write down the exception, not the
model. Reading the code that implements the structure is part of establishing
what the structure means.

## Verify which copy of the package you just measured

**What happened.** An A/B measurement of a data change reported "0 changes" and
also, impossibly, no change to the field being edited. The measurement scripts
lived in a scratchpad directory, so `sys.path[0]` was that directory and
`import mhcgnomes` resolved to the installed copy in the shared virtualenv, not
the working tree. Both halves of the A/B measured the released version.

**Why it matters.** The failure is silent and the output looks like a clean
result. It would have supported the wrong conclusion just as convincingly as
the right one.

**How to apply.** Any script that measures the working tree asserts it first:

```python
import mhcgnomes, os
assert os.path.abspath(mhcgnomes.__file__).startswith(os.path.abspath(os.getcwd()))
```

More generally: when a measurement returns exactly the null result, check that
the instrument was pointed at the thing being measured. A diff that shows no
change to the line you just edited is an instrument fault, not a finding.
