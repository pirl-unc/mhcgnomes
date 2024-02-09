from mhcgnomes import parse, Allele, Species

def test_Bofr_species():
    species = Species.get("Bofr")
    assert species is not None
    assert len(species.gene_names) > 0

def test_Bofr_DQB1_010_11():
    result = parse("Bofr-DQB1*010:11")
    assert result is not None
    assert type(result) is Allele
    assert result.species.prefix == "Bofr"
    assert result.gene.name == "DQB1"
    assert result.allele_fields[0] == "010"
    assert result.allele_fields[1] == "11"
