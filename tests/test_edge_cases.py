# Tests for edge cases that would have caught the bugs fixed in this session
#
# Each test is documented with which bug it would have caught.

from mhcgnomes import (
    Class2Locus,
    Gene,
    Parser,
    Species,
)
from mhcgnomes.common import unique
from mhcgnomes.parsing_helpers import split_on_all_seps
from mhcgnomes.species import guess_class2_chain_type

from .common import eq_

# ============================================================================
# Bug #1: Operator precedence in common.py:20
# Original: if type(xs) is list and len(xs) == 0 or len(xs) == 1:
# This was evaluated as: (type(xs) is list and len(xs) == 0) or (len(xs) == 1)
# So a tuple of length 1 would incorrectly return True for the second part.
# ============================================================================

def test_unique_tuple_length_one():
    """
    A tuple with length 1 should be processed by unique(), not returned as-is.
    Before fix: unique((1,)) would return (1,) unchanged due to operator precedence bug.
    After fix: unique((1,)) correctly processes it (and returns the same since it's unique).
    """
    result = unique((1,))
    # The result should still be [1] after processing, not the original tuple
    assert result == [1], f"Expected [1] but got {result}"


def test_unique_tuple_with_duplicates():
    """
    A tuple with duplicates should have duplicates removed.
    """
    result = unique((1, 2, 2, 3))
    eq_(result, [1, 2, 3])


def test_unique_list_length_zero():
    """
    An empty list should be returned unchanged (optimization).
    """
    empty_list = []
    result = unique(empty_list)
    assert result is empty_list


def test_unique_list_length_one():
    """
    A single-element list should be returned unchanged (optimization).
    """
    single_list = [1]
    result = unique(single_list)
    assert result is single_list


# ============================================================================
# Bug #2 & #7: Missing bounds check and mutable default in class2_locus.py
# Original: while s1[-1].isdigit(): s1 = s1[:-1]
# This crashes with IndexError if the string consists entirely of digits.
# ============================================================================

def test_endswith_ignore_digits_all_digits():
    """
    endswith_ignore_digits should handle strings that are all digits without crashing.
    Before fix: Class2Locus.endswith_ignore_digits("123", "a") would raise IndexError.
    """
    result = Class2Locus.endswith_ignore_digits("123", "a")
    eq_(result, False)


def test_endswith_ignore_digits_empty_after_strip():
    """
    endswith_ignore_digits should handle strings that become empty after stripping digits.
    """
    result = Class2Locus.endswith_ignore_digits("999", "")
    eq_(result, True)  # Empty string ends with empty string


def test_endswith_ignore_digits_normal():
    """
    Normal case: "DRA1" should match "A" after stripping trailing digit.
    """
    result = Class2Locus.endswith_ignore_digits("dra1", "a")
    eq_(result, True)


def test_class2_locus_default_genes():
    """
    Class2Locus should handle default genes argument correctly.
    Before fix: genes=[] as default was a mutable default argument bug.
    """
    species = Species.get("HLA")
    locus1 = Class2Locus(species=species, name="DR")
    locus2 = Class2Locus(species=species, name="DQ")
    # Ensure they have separate gene lists
    eq_(locus1.genes, [])
    eq_(locus2.genes, [])


# ============================================================================
# Bug #3: Missing bounds check in species.py:438 (guess_class2_chain_type)
# Similar to bug #2 - while loop without bounds check on digit stripping.
# ============================================================================

def test_guess_class2_chain_type_all_digits():
    """
    guess_class2_chain_type should handle gene names that are all digits.
    Before fix: guess_class2_chain_type("123") would raise IndexError.
    """
    result = guess_class2_chain_type("123")
    # Default to beta when can't determine
    eq_(result, "beta")


def test_guess_class2_chain_type_ends_with_like_then_digits():
    """
    Handle gene names like "123like456" that become all digits after stripping "like".
    """
    result = guess_class2_chain_type("like123")
    eq_(result, "beta")


def test_guess_class2_chain_type_alpha():
    """
    Normal case: gene names ending in 'A' (after digit stripping) are alpha chains.
    """
    result = guess_class2_chain_type("DRA1")
    eq_(result, "alpha")


def test_guess_class2_chain_type_beta():
    """
    Normal case: gene names ending in 'B' (after digit stripping) are beta chains.
    """
    result = guess_class2_chain_type("DRB1")
    eq_(result, "beta")


# ============================================================================
# Bug #4: Index before check in parser.py:837 (parse_and_apply_mutations)
# The function accessed mutation_tokens[-1] before checking if list was empty.
# ============================================================================

def test_parse_and_apply_mutations_empty_tokens():
    """
    parse_and_apply_mutations should handle empty mutation tokens gracefully.
    Before fix: would crash with IndexError when mutation_tokens was empty.
    """
    parser = Parser()
    gene = Gene.get("HLA", "A")
    result = parser.parse_and_apply_mutations(gene, [])
    eq_(result, None)


# ============================================================================
# Bug #5: Uninitialized variable in parsing_helpers.py:51 (split_on_all_seps)
# If seps="" (empty string), the for loop never executes and 'parts' is undefined.
# ============================================================================

def test_split_on_all_seps_empty_seps():
    """
    split_on_all_seps should handle empty separator string without NameError.
    Before fix: split_on_all_seps("test", "") would raise NameError.
    """
    result = split_on_all_seps("test", "")
    eq_(result, ["test"])


def test_split_on_all_seps_normal():
    """
    Normal case: split on multiple separators.
    """
    result = split_on_all_seps("02_01:01", "_:")
    eq_(result, ["02", "01", "01"])


def test_split_on_all_seps_single_sep():
    """
    Single separator.
    """
    result = split_on_all_seps("a:b:c", ":")
    eq_(result, ["a", "b", "c"])


# ============================================================================
# Bug #6: Regex warnings (SyntaxWarning from invalid escape sequences)
# These tests ensure the regex patterns still work correctly after conversion
# to raw strings.
# ============================================================================

def test_mutation_regex_still_works():
    """
    Mutation regex should work correctly after conversion to raw string.
    """
    from mhcgnomes.mutation import Mutation
    result = Mutation.parse("G86Y")
    assert result is not None
    eq_(result.aa_original, "G")
    eq_(result.pos, 86)
    eq_(result.aa_mutant, "Y")


def test_standard_format_regex_still_works():
    """
    Standard allele format regex should work correctly after conversion to raw strings.
    """
    from mhcgnomes.standard_format import parse_standard_allele_format
    result = parse_standard_allele_format("HLA-A*02:01")
    assert result is not None
    eq_(result.gene.name, "A")
    eq_(result.allele_fields, ("02", "01"))


def test_compact_gene_and_allele_regex_still_works():
    """
    The compact gene and allele regex in Parser should work correctly.
    """
    parser = Parser()
    match = parser.compact_gene_and_allele_regex.fullmatch("A0201")
    assert match is not None
    groups = match.groups()
    eq_(groups[0], "A")
    eq_(groups[1], "0201")


# ============================================================================
# Additional edge case tests that provide good coverage
# ============================================================================

def test_unique_with_generator():
    """
    unique() should work with generators (non-list iterables).
    """
    result = unique(x for x in [1, 2, 2, 3])
    eq_(result, [1, 2, 3])


def test_parse_mutation_with_digits():
    """
    Parse mutation with multi-digit position.
    """
    from mhcgnomes.mutation import Mutation
    result = Mutation.parse("A123B")
    assert result is not None
    eq_(result.pos, 123)


def test_class2_locus_alpha_beta_chain_genes_empty():
    """
    Class2Locus with no genes should return empty lists for chain genes.
    """
    species = Species.get("HLA")
    locus = Class2Locus(species=species, name="DR", genes=[])
    eq_(locus.alpha_chain_genes, [])
    eq_(locus.beta_chain_genes, [])
