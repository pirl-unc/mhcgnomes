import pytest

from mhcgnomes import Allele, parse

# One accession-backed representative for every species prefix in the official IPD-MHC 3.8.0.0
# protein release. These explicit cases preserve broad cross-species coverage without deriving
# biological behavior from name regexes. Source commit and checksum are pinned in
# mhcgnomes/data/external_sources.json.
IPD_PREFIX_EXAMPLES = (
    ("Alpi", "IPD-MHC:NHP09575", "Alpi-DRB*W105:01"),
    ("Aoaz", "IPD-MHC:NHP01450", "Aoaz-DRB3*06:01"),
    ("Aole", "IPD-MHC:NHP10004", "Aole-F*05:01"),
    ("Aona", "IPD-MHC:NHP00001", "Aona-DQA1*27:01"),
    ("Aoni", "IPD-MHC:NHP00056", "Aoni-DRB1*03:01"),
    ("Aotr", "IPD-MHC:NHP00058", "Aotr-DQB2*01:02"),
    ("Aovo", "IPD-MHC:NHP01546", "Aovo-DRB1*03:01"),
    ("Atbe", "IPD-MHC:NHP00075", "Atbe-B*01"),
    ("Atfu", "IPD-MHC:NHP00083", "Atfu-E*03:01"),
    ("BoLA", "IPD-MHC:BoLA02982", "BoLA-2*012:01"),
    ("Bofr", "IPD-MHC:BoLA09755", "Bofr-DQB*043:01"),
    ("Bogr", "IPD-MHC:BoLA09194", "Bogr-DQA1*001:01"),
    ("Bubu", "IPD-MHC:BoLA03223", "Bubu-DQA*001:01"),
    ("Cahi", "IPD-MHC:CLA00002", "Cahi-DRB1*02:01:01"),
    ("Caja", "IPD-MHC:NHP00086", "Caja-DQA1*27:01"),
    ("Camo", "IPD-MHC:NHP00122", "Camo-DRB11*01:01"),
    ("Capy", "IPD-MHC:NHP00153", "Capy-DRB1*03:01"),
    ("Ceap", "IPD-MHC:NHP00137", "Ceap-DRB*W013:01"),
    ("Ceat", "IPD-MHC:NHP06535", "Ceat-A1*01:01"),
    ("Cemi", "IPD-MHC:NHP00143", "Cemi-DQA1*01:01"),
    ("Cene", "IPD-MHC:NHP00151", "Cene-DQA1*26:01"),
    ("Chae", "IPD-MHC:NHP00155", "Chae-DQA1*01:01"),
    ("Chpy", "IPD-MHC:NHP09290", "Chpy-A*01:01"),
    ("Chsa", "IPD-MHC:NHP04182", "Chsa-A*04:01"),
    ("Cogu", "IPD-MHC:NHP00178", "Cogu-DQA1*25:01"),
    ("DLA", "IPD-MHC:DLA04814", "DLA-DQA1*012:01:2"),
    ("Eqca", "IPD-MHC:ELA04917", "Eqca-DQA1*001:01"),
    ("Gaga", "IPD-MHC:CHICKEN08554", "Gaga-BF1*002:01:01"),
    ("Gobe", "IPD-MHC:NHP09050", "Gobe-OKO*01:01"),
    ("Gogo", "IPD-MHC:NHP00179", "Gogo-A*01:01:01"),
    ("Hyla", "IPD-MHC:NHP00241", "Hyla-A*01"),
    ("Hymo", "IPD-MHC:NHP05528", "Hymo-DRB*W094:01"),
    ("Lero", "IPD-MHC:NHP00254", "Lero-G*03:01"),
    ("Loat", "IPD-MHC:NHP00256", "Loat-DQA1*01:01"),
    ("Maar", "IPD-MHC:NHP00257", "Maar-DPA1*02:01"),
    ("Maas", "IPD-MHC:NHP05090", "Maas-B*039:01"),
    ("Mafa", "IPD-MHC:NHP00272", "Mafa-DPA1*02:01"),
    ("Mafu", "IPD-MHC:NHP01068", "Mafu-DRB1*10:01"),
    ("Male", "IPD-MHC:NHP04403", "Male-DRB1*03:01"),
    ("Malo", "IPD-MHC:NHP07111", "Malo-A1*003:01"),
    ("Mamu", "IPD-MHC:NHP00361", "Mamu-DPA1*02:01"),
    ("Mane", "IPD-MHC:NHP00610", "Mane-A1*003:01"),
    ("Masi", "IPD-MHC:NHP00634", "Masi-DRB1*03:01"),
    ("Masp", "IPD-MHC:NHP01348", "Masp-DRB1*03:01"),
    ("Math", "IPD-MHC:NHP04436", "Math-DPB1*15:01"),
    ("Onmy", "IPD-MHC:FISH08119", "Onmy-DAA*01:01"),
    ("Ovar", "IPD-MHC:OLA02424", "Ovar-DRB1*03:02"),
    ("Ovca", "IPD-MHC:OLA08844", "Ovca-DRA*01:01:01"),
    ("Paan", "IPD-MHC:NHP00643", "Paan-AG*01:01:01"),
    ("Pacy", "IPD-MHC:NHP00651", "Pacy-A*03:01"),
    ("Paha", "IPD-MHC:NHP00669", "Paha-DPA1*02:01"),
    ("Papa", "IPD-MHC:NHP00678", "Papa-A*01:01"),
    ("Papp", "IPD-MHC:NHP00701", "Papp-DQA1*01:01"),
    ("Patr", "IPD-MHC:NHP00705", "Patr-A*01:01"),
    ("Paur", "IPD-MHC:NHP01381", "Paur-DRB*W048:01"),
    ("Pipi", "IPD-MHC:NHP00913", "Pipi-B*01"),
    ("Poab", "IPD-MHC:NHP04649", "Poab-B*04:01:01:01"),
    ("Popy", "IPD-MHC:NHP00922", "Popy-A*01:01"),
    ("Rano", "IPD-MHC:RT108344", "Rano-A*av1"),
    ("SLA", "IPD-MHC:SLA05920", "SLA-DMA*01:01:01"),
    ("Safu", "IPD-MHC:NHP00966", "Safu-G*03:01"),
    ("Sage", "IPD-MHC:NHP00972", "Sage-PS1*01"),
    ("Sala", "IPD-MHC:NHP04229", "Sala-DRB*W076:01"),
    ("Samy", "IPD-MHC:NHP00974", "Samy-PS1*01"),
    ("Saoe", "IPD-MHC:NHP00976", "Saoe-DPB1*01:01"),
    ("Sasa", "IPD-MHC:FISH08192", "Sasa-DAA*01:01"),
    ("Sasc", "IPD-MHC:NHP01052", "Sasc-DPA1*05:01"),
    ("Seen", "IPD-MHC:NHP02068", "Seen-DPB1*01"),
    ("Thge", "IPD-MHC:NHP02069", "Thge-DQA1*01:01"),
)


def test_ipd_prefix_inventory_is_explicit_and_cross_species():
    prefixes = [prefix for prefix, _accession, _raw_string in IPD_PREFIX_EXAMPLES]
    assert len(prefixes) == 69
    assert len(set(prefixes)) == len(prefixes)
    assert {"DLA", "Gaga", "Onmy", "SLA", "Mamu"}.issubset(prefixes)


@pytest.mark.parametrize("prefix, accession, raw_string", IPD_PREFIX_EXAMPLES)
def test_ipd_mhc_short_prefix_example_parses_without_species(prefix, accession, raw_string):
    result = parse(raw_string, raise_on_error=False)
    assert isinstance(result, Allele), (
        f"Failed to parse IPD-MHC {accession} ({prefix}) as an allele: {raw_string}; got {result!r}"
    )
