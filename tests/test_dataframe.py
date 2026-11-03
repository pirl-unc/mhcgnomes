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


def test_tolerant_rows_preserve_input_order_and_errors():
    import pandas as pd

    from mhcgnomes import ParseError

    names = ["HLA-A*02:01", None, "zzz-not-mhc", pd.NA, "H2-b"]
    df = dataframe_from_string_list(names, raise_on_error=False)
    assert len(df) == len(names)
    assert df["input"].iloc[1] is None
    assert df["input"].iloc[3] is pd.NA
    assert df["type"].tolist() == ["Allele", "ParseError", "ParseError", "ParseError", "Haplotype"]
    assert df["error"].iloc[1] == "Missing MHC name"
    assert df["normalized"].iloc[4] == "H2-b"
    assert df["gene"].iloc[0] == "HLA-A"
    assert df["gene_name"].iloc[0] == "A"
    assert dataframe_from_parsed_objects(
        [parse("H2-b"), None, ParseError("bad")], raise_on_error=False
    )["type"].tolist() == ["Haplotype", "ParseError", "ParseError"]


def test_dataframe_forwards_constraints_and_aliases():
    from mhcgnomes import Allele

    df = dataframe_from_string_list(
        ["Mamu-A01", "Mamu-B17"],
        use_allele_aliases=True,
        required_result_types=[Allele],
        raise_on_error=False,
    )
    assert df["normalized"].iloc[0] == "Mamu-A1*001:01"
    assert df["type"].iloc[1] == "ParseError"
    df = dataframe_from_string_list(
        ["HLA-A*02:01", "A*02:01"], require_explicit_species=True, raise_on_error=False
    )
    assert df["type"].tolist() == ["Allele", "ParseError"]
    assert (
        dataframe_from_string_list(["BoLA-DRB3*01:01"], species="Bos taurus")[
            "species_latin_name"
        ].iloc[0]
        == "Bos taurus"
    )


def test_dataframe_errors_are_not_silently_swallowed():
    import pytest

    from mhcgnomes import ParseError

    with pytest.raises(ParseError):
        dataframe_from_string_list(["HLA-A*02:01", None])
    with pytest.raises(ParseError):
        dataframe_from_parsed_objects([None])
    with pytest.raises(TypeError, match="expected str"):
        dataframe_from_string_list([123], raise_on_error=False)
    with pytest.raises(TypeError):
        dataframe_from_string_list(["HLA-A*02:01"], imaginary_option=True, raise_on_error=False)


def test_empty_frames_have_predictable_outcome_columns():
    from mhcgnomes.parse_outcome import OUTCOME_COLUMNS

    for frame in [dataframe_from_string_list([]), dataframe_from_parsed_objects([])]:
        assert list(frame.columns) == list(OUTCOME_COLUMNS)
        assert len(frame) == 0


def test_public_outcome_api_shared_with_cli():
    import pytest

    from mhcgnomes import ParseError, parse_outcome_to_row
    from mhcgnomes.cli import outcome_to_cli_row

    result = parse("HLA-A*02:01")
    row = parse_outcome_to_row("original input", result)
    assert row["input"] == "original input"
    assert row["gene"] == "HLA-A"
    assert row["gene_name"] == "A"
    assert row["error"] == ""
    cli = outcome_to_cli_row("original input", result)
    assert cli["normalized"] == row["normalized"]
    assert cli["gene"] == row["gene_name"]
    assert (
        parse_outcome_to_row("bad", ParseError("specific failure"))["error"] == "specific failure"
    )
    assert parse_outcome_to_row("bad", None)["type"] == "ParseError"
    with pytest.raises(TypeError, match="expected Result"):
        parse_outcome_to_row("bad", object())
