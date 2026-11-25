# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Which prefix normalized output uses.

Issue #129 and #188: print a short prefix only where an external database or
the literature attests it, and otherwise the concatenated full binomial, so
that ``CyanistesCaeruleus-DAB1`` cannot be mistaken for established
nomenclature the way ``CyanCaer-DAB1`` can.

``ATTESTED`` is the default policy. Callers that explicitly want the compact
curated/4+4 display prefix (e.g. ``HypoMoli-DAB``) can opt into ``CURATED``
via ``prefix_display_policy(CURATED)`` or ``set_prefix_display_policy(CURATED)``.

The question the policy asks is ``Species.prefix_provenance``, which #131 spent
its length populating: "designated" means a source is cited beside the entry in
species.yaml, and every other value means the prefix is one this package
minted or could not establish externally.

    >>> parse("CyanCaer-DAB1").to_string()
    'CyanistesCaeruleus-DAB1'
    >>> with prefix_display_policy(CURATED):
    ...     parse("CyanCaer-DAB1").to_string()
    'CyanCaer-DAB1'
    >>> parse("HLA-A*02:01").to_string()   # designated, so unchanged
    'HLA-A*02:01'

Both spellings keep parsing under either policy. The compatibility change #129
and #188 describe is display only.
"""

from contextlib import contextmanager
from threading import local

# Print the prefix curated in species.yaml, whatever its provenance (explicit
# compact 4+4 / curated display mode, #188).
CURATED = "curated"

# Print a short prefix only where prefix_provenance says a source attests it,
# and the concatenated binomial otherwise. Default policy (#129, #188).
ATTESTED = "attested"

POLICIES = (ATTESTED, CURATED)

# Thread-local rather than a plain module global: a policy set in one thread
# must not change what another thread is midway through formatting.
_state = local()


def get_prefix_display_policy() -> str:
    """The policy in force on this thread (defaults to ``ATTESTED``)."""
    return getattr(_state, "policy", ATTESTED)


def set_prefix_display_policy(policy: str) -> None:
    """
    Set the policy for this thread until it is set again.

    Prefer `prefix_display_policy`, the context manager; this exists for
    callers configuring a process once at startup.
    """
    if policy not in POLICIES:
        raise ValueError(f"Unknown prefix display policy {policy!r}; expected one of {POLICIES}")
    _state.policy = policy


@contextmanager
def prefix_display_policy(policy: str):
    """Use `policy` for the duration of the block, then restore the previous one."""
    previous = get_prefix_display_policy()
    set_prefix_display_policy(policy)
    try:
        yield
    finally:
        set_prefix_display_policy(previous)


def display_prefix_for(species) -> str:
    """
    The prefix to print for this species under the current policy.

    Falls back to the curated prefix wherever a binomial cannot produce one --
    group nodes such as `Bos sp.`, and trinomials, which the emitter declines.
    Those keep their labels under either policy, which is #129's own point 6.
    """
    # `canonical_mhc_prefix`, not `.prefix`: on a Species those are the same
    # value, but `.prefix` now routes back through this function, so reading it
    # here recurses until the stack gives out.
    curated = species.canonical_mhc_prefix
    if get_prefix_display_policy() == CURATED:
        return curated
    if species.prefix_provenance == "designated":
        return curated

    from .species import unambiguous_prefix_for

    return unambiguous_prefix_for(species)
