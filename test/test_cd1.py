from mhcgnomes import parse, Gene

def test_mamu_cd1b():
    seq = "rhesus macaque CD1b"
    result = parse(seq)
    assert result == Gene.get("Mamu", "CD1b")

def test_mamu_cd1b_dash():
    seq = "rhesus monkey-CD1b"
    result = parse(seq)
    assert result == Gene.get("Mamu", "CD1b")
