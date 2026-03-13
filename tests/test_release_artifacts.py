import csv

from mhcgnomes.release_artifacts import gene_rows, species_rows, write_release_artifacts


def _find_row(rows, **expected):
    for row in rows:
        if all(row.get(key) == value for key, value in expected.items()):
            return row
    raise AssertionError(f"Missing row with {expected}")


def test_species_rows_include_curated_runtime_species():
    rows = species_rows()

    hla_row = _find_row(rows, species_prefix="HLA")
    assert hla_row["species_name"] == "Homo sapiens"
    assert int(hla_row["num_genes"]) > 0

    paol_row = _find_row(rows, species_prefix="Paol")
    assert paol_row["species_name"] == "Paralichthys olivaceus"
    assert int(paol_row["num_genes"]) >= 4


def test_gene_rows_include_gene_metadata_and_aliases():
    rows = gene_rows()

    hla_a = _find_row(rows, species_prefix="HLA", gene_name="A")
    assert hla_a["mhc_class"] == "Ia"
    assert hla_a["class2_locus"] == ""

    sasa_daa = _find_row(rows, species_prefix="Sasa", gene_name="DAA")
    assert sasa_daa["mhc_class"] == "IIa"
    assert sasa_daa["class2_locus"] == "DA"
    assert "DAA1" in sasa_daa["aliases"].split(";")


def test_write_release_artifacts(tmp_path):
    paths = write_release_artifacts(tmp_path)

    assert paths["species"].exists()
    assert paths["genes"].exists()

    with paths["species"].open(encoding="utf-8") as handle:
        species_file_rows = list(csv.DictReader(handle))
    with paths["genes"].open(encoding="utf-8") as handle:
        gene_file_rows = list(csv.DictReader(handle))

    assert _find_row(species_file_rows, species_prefix="Acsc")["species_name"] == (
        "Acrocephalus schoenobaenus"
    )
    assert _find_row(gene_file_rows, species_prefix="Cyse", gene_name="DBB")["mhc_class"] == "IIa"
