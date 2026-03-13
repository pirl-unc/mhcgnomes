from mhcgnomes import dataframe_from_parsed_objects, dataframe_from_string_list, parse


def test_dataframe_from_parsed_objects_uses_to_record_output():
    df = dataframe_from_parsed_objects([parse("HLA-A*02:01"), parse("HLA-B*07:02")])

    assert df["gene"].tolist() == ["HLA-A", "HLA-B"]
    assert df["allele"].tolist() == ["HLA-A*02:01", "HLA-B*07:02"]
    assert df["mhc_class"].tolist() == ["Ia", "Ia"]


def test_dataframe_from_string_list_parses_names_before_dataframe_conversion():
    df = dataframe_from_string_list(["HLA-A*02:01", "HLA-B*07:02"])

    assert df["species_prefix"].tolist() == ["HLA", "HLA"]
    assert df["gene"].tolist() == ["HLA-A", "HLA-B"]
    assert df["allele"].tolist() == ["HLA-A*02:01", "HLA-B*07:02"]
