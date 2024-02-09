from mhcgnomes import parse

def test_parse_FLA_E_18_01():
    s = "FLA-E*18:01"
    assert parse(s, verbose=True).to_string() == s
