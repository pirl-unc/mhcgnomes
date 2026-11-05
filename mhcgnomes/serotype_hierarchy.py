"""Broad/split candidate expansion without changing reported serotype labels."""

import re
from collections.abc import Mapping, Sequence


def serotype_descendants(splits: Mapping[str, Sequence[str]]) -> dict[str, tuple[str, ...]]:
    """Return each broad antigen's sorted transitive split labels.

    Accept canonical HLA serological labels (e.g. B12, Cw3, DR2), with direct
    broad-to-split edges. Reject malformed labels, cross-locus edges, duplicate
    edges, multiple parents and cycles with ValueError. Leaf labels need not be
    keys. This validates relationships, not allele assignments or expression.
    """
    parents = {}
    for broad, children in splits.items():
        match = re.fullmatch(r"([A-Za-z]+)\d+", broad)
        if match is None or isinstance(children, str):
            raise ValueError(f"Invalid serotype relationship: {broad!r}: {children!r}")
        for child in children:
            child_match = re.fullmatch(r"([A-Za-z]+)\d+", child)
            if child_match is None or child_match[1] != match[1]:
                raise ValueError(f"Invalid cross-locus serotype edge: {broad} -> {child}")
            if child in parents:
                raise ValueError(f"Duplicate or conflicting parent for serotype {child}")
            parents[child] = broad

    descendants = {}
    visiting = set()

    def visit(name):
        if name in visiting:
            raise ValueError(f"Cyclic serotype relationship at {name}")
        if name in descendants:
            return descendants[name]
        visiting.add(name)
        children = set(splits.get(name, ()))
        for child in splits.get(name, ()):
            children.update(visit(child))
        visiting.remove(name)
        descendants[name] = tuple(sorted(children))
        return descendants[name]

    for broad in sorted(splits):
        visit(broad)
    return {broad: descendants[broad] for broad in sorted(splits)}


def expand_serotype_memberships(
    direct: Mapping[str, Sequence[str]], splits: Mapping[str, Sequence[str]]
) -> dict[str, list[str]]:
    """Expand direct allele-name assignments through a validated HLA split graph.

    Return fresh lists for the labels present in ``direct``. A broad's candidates
    include its direct members and every descendant's direct members, without
    duplicates. Only expanded lists are sorted; other lists retain source order.
    Neither input is modified. Missing assignments contribute no candidates and
    do not create new typing labels. These candidates are not a specific typing,
    exhaustive registry validation, or evidence of expression.
    """
    descendants = serotype_descendants(splits)
    expanded = {}
    for name, members in direct.items():
        if name in descendants:
            candidates = set(members)
            for child in descendants[name]:
                candidates.update(direct.get(child, ()))
            expanded[name] = sorted(candidates)
        else:
            expanded[name] = list(members)
    return expanded
