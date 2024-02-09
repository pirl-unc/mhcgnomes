from mhcgnomes import parse, Species, Allele, Haplotype, Gene

def test_parse_BF2_gene():
    result = parse("BF2")
    expected = Gene.get("chicken", "BF2")
    assert expected is not None
    assert result == expected

def test_parse_BF2_15_01():
    result = parse("BF2*15:01")
    chicken = Species.get("chicken")
    expected = Allele.get(chicken, "BF2", "15", "01")
    assert result == expected

def test_parse_BF2_1501():
    result = parse("BF2*1501")
    expected = Allele.get(Species.get("chicken"), "BF2", "15", "01")
    assert result == expected

def test_chicken_haplotype_B12():
    result = parse("B12", default_species="Gaga")
    print(result)
    assert type(result) == Haplotype
    assert result.name == "B12"
    assert result.is_chicken


def test_chicken_haplotype_B19_class_II():
    result = parse("B19 Class II")
    assert type(result) == Haplotype
    assert result.name == "B19"
    assert result.is_chicken
    assert result.is_class2

def test_chicken_haplotype_BF19_class_I():
    result = parse("BF19 Class I")
    assert type(result) == Haplotype
    assert result.name == "BF19"
    assert result.is_chicken
    assert result.is_class1

def test_chicken_YF1w_7_1():
    result = parse("YF1w*7.1")
    assert type(result) == Allele
    assert result.name == "7.1"
    assert result.gene_name == "YF1"
    assert result.is_chicken
    assert result.is_class1

def test_YF1w_in_gene_aliases():
    species = Species.get("chicken")
    gene_names_and_aliases = species.gene_names_and_aliases
    assert "YF1w" in gene_names_and_aliases, gene_names_and_aliases
