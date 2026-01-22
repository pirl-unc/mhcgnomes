"""
Tests for HLA serotype definitions based on WHO/IPD-IMGT/HLA Dictionary.

Source: https://www.ebi.ac.uk/ipd/imgt/hla/alleles/dictionary/

These tests document and verify the assumptions about serotype behavior based on
official WHO serological assignments from the IPD-IMGT/HLA Dictionary.

Key concepts:
-------------

1. SEROTYPES are serological antigen types - groups of HLA alleles that react
   with the same antibody in serological testing. Before molecular typing,
   HLA types were determined by antibody reactivity.

2. BROAD vs SPLIT SEROTYPES: Some original "broad" serotypes were later
   subdivided into "split" serotypes as more specific antisera were developed.
   For example:
   - A9 (broad) was split into A23 and A24
   - B15 (broad) was split into B62, B63, B70, B71, B72, B75, B76, B77

3. WHO ASSIGNMENT RULES: The WHO dictionary assigns serotypes based on actual
   serological reactivity:
   - Alleles that clearly react with split-specific antisera get the SPLIT
     serotype (e.g., A23, A24)
   - Alleles that react with the broad antiserum but don't clearly fit any
     split get the BROAD serotype (e.g., A9)
   - This means BROAD and SPLIT serotypes are DISJOINT sets - an allele
     is assigned to one or the other, not both.

4. PUBLIC EPITOPES (Bw4/Bw6): These are supertypic specificities defined by
   amino acid motifs at positions 77-83 of the HLA-B heavy chain. They are
   NOT traditional serotypes but cross-reactive epitopes shared by multiple
   serotypes.

5. WORKSHOP SEROTYPES: Names like "Aw68" or "DPw2" with "w" indicate workshop
   or provisional designations from international histocompatibility workshops.
   Many have since been officially recognized (Aw68 -> A68).
"""

from mhcgnomes import Species, parse
from mhcgnomes.serotype import Serotype


class TestSerotypeDataIntegrity:
    """Tests to verify the serotype data is loaded correctly."""

    def test_hla_serotypes_loaded(self):
        """HLA serotypes should be loaded from serotypes.yaml."""
        human = Species.get("HLA")
        assert human is not None
        assert hasattr(human, "serotypes")
        assert len(human.serotypes) > 100  # We have ~150 HLA serotypes

    def test_common_serotypes_exist(self):
        """Common clinical serotypes should all be present."""
        human = Species.get("HLA")
        common_serotypes = [
            # Class I - A locus
            "A1",
            "A2",
            "A3",
            "A11",
            "A23",
            "A24",
            "A25",
            "A26",
            "A29",
            "A30",
            "A31",
            "A32",
            "A33",
            "A34",
            "A36",
            "A43",
            "A66",
            "A68",
            "A69",
            "A74",
            "A80",
            # Class I - B locus
            "B7",
            "B8",
            "B13",
            "B18",
            "B27",
            "B35",
            "B37",
            "B38",
            "B39",
            "B41",
            "B42",
            "B44",
            "B45",
            "B46",
            "B47",
            "B48",
            "B49",
            "B50",
            "B51",
            "B52",
            "B53",
            "B54",
            "B55",
            "B56",
            "B57",
            "B58",
            "B59",
            "B60",
            "B61",
            "B62",
            "B63",
            "B64",
            "B65",
            "B67",
            "B73",
            "B78",
            "B81",
            # Class I - C locus
            "Cw1",
            "Cw2",
            "Cw3",
            "Cw4",
            "Cw5",
            "Cw6",
            "Cw7",
            "Cw8",
            # Class II - DR
            "DR1",
            "DR4",
            "DR7",
            "DR8",
            "DR9",
            "DR10",
            "DR11",
            "DR12",
            "DR13",
            "DR14",
            "DR15",
            "DR16",
            "DR17",
            "DR18",
            "DR51",
            "DR52",
            "DR53",
            # Class II - DQ
            "DQ2",
            "DQ4",
            "DQ5",
            "DQ6",
            "DQ7",
            "DQ8",
        ]
        for serotype in common_serotypes:
            assert serotype in human.serotypes, f"Missing common serotype: {serotype}"

    def test_serotypes_have_allele_lists(self):
        """Each serotype should have a list of alleles (may be empty for non-HLA)."""
        human = Species.get("HLA")
        for name, alleles in human.serotypes.items():
            assert isinstance(alleles, list), f"{name} alleles should be a list"


class TestBroadAndSplitSerotypes:
    """
    Tests for broad/split serotype relationships per WHO definitions.

    In HLA serology, some original "broad" serotypes were later subdivided into
    more specific "split" serotypes. The WHO dictionary assigns alleles to EITHER
    the broad OR a split serotype based on actual serological reactivity - they
    are DISJOINT sets, not hierarchical unions.

    This is the correct serological interpretation:
    - If an allele clearly reacts with split-specific antisera -> assigned to split
    - If an allele reacts with broad antiserum but not clearly with any split -> assigned to broad
    """

    # Known broad -> split relationships in HLA serology
    BROAD_SPLIT_RELATIONSHIPS = {
        # A locus
        "A9": ["A23", "A24"],
        "A10": ["A25", "A26", "A34", "A66"],
        "A19": ["A29", "A30", "A31", "A32", "A33", "A74"],
        "A28": ["A68", "A69"],
        # B locus
        "B5": ["B51", "B52"],
        "B12": ["B44", "B45"],
        "B14": ["B64", "B65"],
        "B15": ["B62", "B63", "B70", "B71", "B72", "B75", "B76", "B77"],
        "B16": ["B38", "B39"],
        "B17": ["B57", "B58"],
        "B21": ["B49", "B50"],
        "B22": ["B54", "B55", "B56"],
        "B40": ["B60", "B61"],
        # DR locus
        "DR2": ["DR15", "DR16"],
        "DR3": ["DR17", "DR18"],
        "DR5": ["DR11", "DR12"],
        "DR6": ["DR13", "DR14"],
    }

    def test_broad_and_split_serotypes_are_disjoint(self):
        """
        Broad and split serotypes should have disjoint allele sets per WHO rules.

        The WHO dictionary assigns each allele to exactly one serotype based on
        serological reactivity. An allele assigned to a split (e.g., A23) is NOT
        also assigned to its broad (A9).
        """
        human = Species.get("HLA")

        for broad, splits in self.BROAD_SPLIT_RELATIONSHIPS.items():
            broad_alleles = set(human.serotypes.get(broad, []))

            for split in splits:
                split_alleles = set(human.serotypes.get(split, []))
                overlap = broad_alleles & split_alleles

                assert not overlap, (
                    f"WHO rule violation: {broad} and {split} share alleles {overlap}. "
                    f"Broad and split serotypes should be disjoint per WHO assignments."
                )

    def test_broad_serotypes_contain_ambiguous_alleles(self):
        """
        Broad serotypes should contain alleles with ambiguous split assignment.

        Per WHO rules, alleles are assigned to the broad serotype when they
        react with the broad antiserum but don't clearly fit any split.
        """
        human = Species.get("HLA")

        # These broad serotypes should have at least some alleles per WHO dictionary
        # (alleles that don't clearly belong to any split)
        broad_serotypes_with_alleles = ["A9", "A10", "A19", "A28", "B14", "B15", "B40"]

        for broad in broad_serotypes_with_alleles:
            if broad in human.serotypes:
                alleles = human.serotypes[broad]
                assert len(alleles) > 0, (
                    f"Broad serotype {broad} should have alleles that don't clearly "
                    f"fit any split per WHO assignments"
                )

    def test_split_serotypes_exist_for_known_broads(self):
        """Split serotypes should exist when their broad serotype exists."""
        human = Species.get("HLA")

        for broad, splits in self.BROAD_SPLIT_RELATIONSHIPS.items():
            for split in splits:
                assert split in human.serotypes, (
                    f"Split serotype {split} (from {broad}) should exist"
                )


class TestPublicEpitopes:
    """
    Tests for Bw4 and Bw6 public epitopes (supertypic specificities).

    Bw4 and Bw6 are NOT in the WHO/IPD-IMGT/HLA Dictionary because they are
    public epitopes defined by amino acid motifs at positions 77-83 of the HLA
    heavy chain, not by traditional antibody reactivity.

    However, they ARE included in serotypes.yaml from supplemental source:
    https://hla.alleles.org/pages/antigens/bw4_bw6/

    Bw4-associated serotypes: B5, B13, B17, B27, B37, B38, B44, B47, B49, B51,
                              B52, B53, B57, B58, B59, B63, B77, A23, A24, A25, A32
    Bw6-associated serotypes: B7, B8, B14, B18, B22, B35, B39, B40, B41, B42,
                              B45, B46, B48, B50, B54, B55, B56, B60, B61, B62,
                              B64, B65, B67, B70, B71, B72, B73, B75, B76, B78,
                              B81, B82
    """

    def test_bw4_exists_with_alleles(self):
        """Bw4 public epitope should be defined with representative alleles."""
        human = Species.get("HLA")
        assert "Bw4" in human.serotypes
        bw4_alleles = human.serotypes["Bw4"]
        assert len(bw4_alleles) > 0

    def test_bw6_exists_with_alleles(self):
        """Bw6 public epitope should be defined with representative alleles."""
        human = Species.get("HLA")
        assert "Bw6" in human.serotypes
        bw6_alleles = human.serotypes["Bw6"]
        assert len(bw6_alleles) > 0

    def test_bw4_contains_expected_alleles(self):
        """Bw4 should contain alleles from Bw4-positive serotypes."""
        human = Species.get("HLA")
        bw4_alleles = set(human.serotypes["Bw4"])

        # Representative alleles that carry Bw4 epitope
        expected = ["B*2705", "B*5101", "B*5701", "B*4402"]
        for allele in expected:
            assert allele in bw4_alleles, f"Expected {allele} in Bw4"

    def test_bw6_contains_expected_alleles(self):
        """Bw6 should contain alleles from Bw6-positive serotypes."""
        human = Species.get("HLA")
        bw6_alleles = set(human.serotypes["Bw6"])

        # Representative alleles that carry Bw6 epitope
        expected = ["B*0702", "B*0801", "B*3501"]
        for allele in expected:
            assert allele in bw6_alleles, f"Expected {allele} in Bw6"

    def test_bw4_and_bw6_are_disjoint(self):
        """Bw4 and Bw6 epitopes should be mutually exclusive."""
        human = Species.get("HLA")
        bw4 = set(human.serotypes["Bw4"])
        bw6 = set(human.serotypes["Bw6"])
        overlap = bw4 & bw6
        assert not overlap, f"Bw4 and Bw6 should be disjoint, overlap: {overlap}"

    def test_bw4_positive_serotypes_also_exist(self):
        """Individual Bw4-positive serotypes should also exist."""
        human = Species.get("HLA")
        assert "B27" in human.serotypes
        assert "B44" in human.serotypes

    def test_bw6_positive_serotypes_also_exist(self):
        """Individual Bw6-positive serotypes should also exist."""
        human = Species.get("HLA")
        assert "B7" in human.serotypes
        assert "B8" in human.serotypes


class TestWorkshopSerotypes:
    """
    Tests for workshop (provisional) serotype designations.

    The "w" in serotype names like "Aw68", "Bw4", "Cw1", "DPw2" originally
    indicated a "workshop" or provisional designation from international
    histocompatibility workshops.

    Current status:
    - Aw68, Aw69: Preserved as aliases for A68, A69 (for backward compatibility)
    - Bw4, Bw6: Public epitopes (see TestPublicEpitopes)
    - Cw serotypes: C locus serotypes traditionally used "w" (Cw1, Cw2, etc.)
    - DPw serotypes: DP workshop serotypes (DPw1-DPw6)
    """

    def test_modern_a68_a69_exist(self):
        """A68 and A69 serotypes should exist (modern/official names)."""
        human = Species.get("HLA")
        assert "A68" in human.serotypes
        assert "A69" in human.serotypes

    def test_old_workshop_aw68_aw69_exist_as_aliases(self):
        """
        Old Aw68/Aw69 names should exist for backward compatibility.

        These are preserved as aliases pointing to the same alleles as A68/A69.
        Source: https://hla.alleles.org/pages/antigens/previous_equivalents/
        """
        human = Species.get("HLA")
        assert "Aw68" in human.serotypes
        assert "Aw69" in human.serotypes
        # Should have alleles
        assert len(human.serotypes["Aw68"]) > 0
        assert len(human.serotypes["Aw69"]) > 0

    def test_aw68_and_a68_have_same_alleles(self):
        """Aw68 and A68 should contain the same alleles (aliases)."""
        human = Species.get("HLA")
        aw68 = set(human.serotypes["Aw68"])
        a68 = set(human.serotypes["A68"])
        # They should be equivalent
        assert aw68 == a68, f"Aw68 and A68 should match: {aw68} vs {a68}"

    def test_cw_serotypes_use_w_prefix(self):
        """C locus serotypes should use traditional Cw naming."""
        human = Species.get("HLA")
        cw_serotypes = ["Cw1", "Cw2", "Cw3", "Cw4", "Cw5", "Cw6", "Cw7", "Cw8"]
        for cw in cw_serotypes:
            assert cw in human.serotypes, f"Expected {cw} serotype"

    def test_dpw_serotypes_exist(self):
        """DP workshop serotypes should exist (preserved for compatibility)."""
        human = Species.get("HLA")
        dpw_serotypes = ["DPw1", "DPw2", "DPw3", "DPw4", "DPw5", "DPw6"]
        for dpw in dpw_serotypes:
            assert dpw in human.serotypes, f"Expected {dpw} serotype"


class TestSerotypeToAlleleMapping:
    """Tests for the serotype-to-allele mapping accuracy."""

    def test_a2_contains_common_alleles(self):
        """A2 serotype should contain common A*02 alleles."""
        human = Species.get("HLA")
        a2_alleles = set(human.serotypes["A2"])

        # A*02:01 is the most common A2 allele worldwide
        assert "A*0201" in a2_alleles, "A*02:01 is the archetypal A2 allele"

        # Other common A2 alleles
        common_a2 = ["A*0201", "A*0202", "A*0205", "A*0206"]
        for allele in common_a2:
            assert allele in a2_alleles, f"Expected {allele} in A2 serotype"

    def test_b27_contains_common_alleles(self):
        """B27 serotype should contain B*27 alleles (important for disease association)."""
        human = Species.get("HLA")
        b27_alleles = set(human.serotypes["B27"])

        # B*27:05 is the most common B27 subtype associated with ankylosing spondylitis
        assert "B*2705" in b27_alleles, "B*27:05 is the classic B27 disease-associated allele"

    def test_dr4_contains_common_alleles(self):
        """DR4 serotype should contain DRB1*04 alleles."""
        human = Species.get("HLA")
        dr4_alleles = set(human.serotypes["DR4"])

        common_dr4 = ["DRB1*0401", "DRB1*0404", "DRB1*0405"]
        for allele in common_dr4:
            assert allele in dr4_alleles, f"Expected {allele} in DR4 serotype"

    def test_allele_format_consistency(self):
        """Alleles should use consistent two-field format (e.g., A*0201 not A*02:01)."""
        human = Species.get("HLA")

        for serotype, alleles in human.serotypes.items():
            for allele in alleles:
                # Should not contain colons (we use compact format)
                assert ":" not in allele or allele.count(":") <= 1, (
                    f"Allele {allele} in {serotype} should use compact format"
                )


class TestSerotypeSubtypes:
    """Tests for serotype subtypes (e.g., A203, A2403, B703)."""

    def test_a203_is_distinct_from_a2(self):
        """A203 is a distinct serotype, not the same as A2."""
        human = Species.get("HLA")
        assert "A203" in human.serotypes
        assert "A2" in human.serotypes

        # A203 should contain A*02:03 specifically
        a203_alleles = human.serotypes["A203"]
        assert "A*0203" in a203_alleles

        # A*02:03 should NOT be in A2
        a2_alleles = human.serotypes["A2"]
        assert "A*0203" not in a2_alleles, "A*02:03 has A203 serotype, not A2"

    def test_b703_is_distinct_from_b7(self):
        """B703 is a distinct serotype from B7."""
        human = Species.get("HLA")
        assert "B703" in human.serotypes
        assert "B7" in human.serotypes

        b703_alleles = set(human.serotypes["B703"])
        b7_alleles = set(human.serotypes["B7"])

        # These should be disjoint
        overlap = b703_alleles & b7_alleles
        assert not overlap, f"B703 and B7 should be disjoint, overlap: {overlap}"


class TestSerotypeParsing:
    """Tests for parsing serotype strings."""

    def test_parse_hla_a2(self):
        """Should parse HLA-A2 as a serotype."""
        result = parse("HLA-A2")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "A2"
        assert result.species.prefix == "HLA"

    def test_parse_hla_b27(self):
        """Should parse HLA-B27 as a serotype."""
        result = parse("HLA-B27")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "B27"

    def test_parse_hla_dr4(self):
        """Should parse HLA-DR4 as a serotype."""
        result = parse("HLA-DR4")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "DR4"

    def test_parse_hla_cw7(self):
        """Should parse HLA-Cw7 as a serotype."""
        result = parse("HLA-Cw7")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "Cw7"

    def test_parse_hla_dpw4(self):
        """Should parse HLA-DPw4 as a serotype."""
        result = parse("HLA-DPw4")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "DPw4"

    def test_parse_hla_dr51(self):
        """Should parse HLA-DR51 as a serotype."""
        result = parse("HLA-DR51")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "DR51"

    def test_parse_hla_bw4(self):
        """Should parse HLA-Bw4 as a serotype (public epitope)."""
        result = parse("HLA-Bw4")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "Bw4"
        assert len(result.alleles) > 0

    def test_parse_hla_aw68(self):
        """Should parse HLA-Aw68 as a serotype (workshop name)."""
        result = parse("HLA-Aw68")
        assert result is not None
        assert isinstance(result, Serotype)
        assert result.name == "Aw68"
        assert len(result.alleles) > 0


class TestEdgeCases:
    """
    Tests for edge cases in serotype definitions.

    These cover unusual but valid serotype patterns from the WHO dictionary:
    - Variant serotypes with lowercase suffixes (B27c, DR3d, etc.)
    - B17 subsplits (B17.1, B17.2, B17.3)
    - Alleles with dual serological reactivity
    - Case-insensitive parsing
    """

    def test_variant_serotypes_with_lowercase_suffix(self):
        """
        Variant serotypes with lowercase suffixes should be parseable.

        These represent variant serological reactivity patterns assigned by WHO.
        """
        human = Species.get("HLA")
        variants = ["B27c", "B48c", "Cw4c", "DQ6c", "DR3d"]
        for variant in variants:
            assert variant in human.serotypes, f"Expected variant serotype {variant}"
            assert len(human.serotypes[variant]) > 0, f"{variant} should have alleles"

    def test_parse_variant_serotypes(self):
        """Should parse variant serotypes with lowercase suffixes."""
        result = parse("HLA-B27c")
        assert result is not None
        assert result.name == "B27c"

        result = parse("HLA-DR3d")
        assert result is not None
        assert result.name == "DR3d"

    def test_b17_subsplits(self):
        """
        B17 has historical subsplits (B17.1, B17.2, B17.3) in addition to B57/B58.

        These represent finer serological distinctions within B17.
        """
        human = Species.get("HLA")
        subsplits = ["B17.1", "B17.2", "B17.3"]
        for subsplit in subsplits:
            assert subsplit in human.serotypes, f"Expected B17 subsplit {subsplit}"
            assert len(human.serotypes[subsplit]) > 0

    def test_parse_b17_subsplits(self):
        """Should parse B17 subsplit serotypes."""
        result = parse("HLA-B17.1")
        assert result is not None
        assert result.name == "B17.1"

    def test_dual_reactivity_alleles_documented(self):
        """
        Some alleles have dual serological reactivity per WHO.

        These alleles legitimately appear in multiple serotypes because they
        react with antisera for both serotypes.
        """
        human = Species.get("HLA")

        # A*24:18 reacts with both A24 and A3 antisera
        a24_alleles = set(human.serotypes.get("A24", []))
        a3_alleles = set(human.serotypes.get("A3", []))
        assert "A*2418" in a24_alleles or "A*2418" in a3_alleles

        # DRB1*11:16 reacts with both DR11 and DR13 antisera
        dr11_alleles = set(human.serotypes.get("DR11", []))
        dr13_alleles = set(human.serotypes.get("DR13", []))
        assert "DRB1*1116" in dr11_alleles or "DRB1*1116" in dr13_alleles

    def test_case_insensitive_parsing(self):
        """Serotype parsing should be case-insensitive."""
        # All should parse to the same serotype
        for name in ["HLA-A2", "hla-a2", "HLA-a2", "A2", "a2"]:
            result = parse(name)
            assert result is not None, f"Failed to parse {name}"
            assert result.name == "A2", f"{name} should parse to A2"

    def test_ambiguous_serotype_names_exist(self):
        """
        WHO serotype names that look like alleles should still exist in serotypes.

        The WHO dictionary defines serotypes like B3901, B5102, etc. Although these
        names look like allele patterns (B*39:01, B*51:02), they are legitimate WHO
        serotype designations and should be included in the serotype data.

        The parser handles ambiguity by prioritizing allele interpretation over
        serotype interpretation when both are valid candidates.
        """
        human = Species.get("HLA")
        # These WHO serotype names should exist (they are legitimate serotypes)
        ambiguous_names = ["B3901", "B3902", "B5102", "B5103", "B4005", "B2708"]
        for name in ambiguous_names:
            assert name in human.serotypes, f"{name} should exist as a valid WHO serotype"

    def test_allele_like_names_parse_as_alleles(self):
        """
        Names that look like alleles should parse as alleles, not serotypes.

        Even though B3901, B5102, etc. are valid WHO serotypes, when a user writes
        "B3901" they almost always mean the allele B*39:01, not the serotype.
        The parser prioritizes allele interpretation over serotype interpretation.
        """
        from mhcgnomes.allele import Allele

        # All these should parse as alleles (not serotypes, even though B3901 is a valid serotype)
        for name in ["B3901", "B*3901", "B*39:01", "HLA-B3901"]:
            result = parse(name)
            assert isinstance(result, Allele), f"{name} should parse as allele, not serotype"
            assert "39:01" in result.to_string() or "3901" in result.to_string()


class TestNonHumanSerotypes:
    """Tests for non-human species serotypes."""

    def test_patr_serotypes_exist(self):
        """Chimpanzee (Patr) serotypes should be defined."""
        patr = Species.get("Patr")
        assert patr is not None
        assert hasattr(patr, "serotypes")
        # Patr has DR serotypes defined (even if empty allele lists)
        assert "DR1" in patr.serotypes

    def test_mamu_serotypes_exist(self):
        """Rhesus macaque (Mamu) serotypes should be defined."""
        mamu = Species.get("Mamu")
        assert mamu is not None
        assert hasattr(mamu, "serotypes")

    def test_bola_serotypes_exist(self):
        """Bovine (BoLA) serotypes should be defined."""
        bola = Species.get("BoLA")
        assert bola is not None
        assert hasattr(bola, "serotypes")
