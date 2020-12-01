from mhcgnomes import parse
from nose.tools import eq_

def test_parse_FLA_E_18_01():
    s = "FLA-E*18:01"
    eq_(parse(s, verbose=True).to_string(), s)
