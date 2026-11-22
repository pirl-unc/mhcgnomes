from pathlib import Path

from mhcgnomes import Pair, parse

ALLELES_PATH = Path(__file__).parent / "netmhciipan_3_1_alleles.txt"


def _load_unique_alleles(path: Path) -> list[str]:
    alleles: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        allele = line.split()[0]
        if allele not in seen:
            seen.add(allele)
            alleles.append(allele)
    return alleles


def test_netmhciipan_3_1_alleles():
    alleles = _load_unique_alleles(ALLELES_PATH)
    assert len(alleles) == 5631
    failures = []
    for allele in alleles:
        result = parse(allele, infer_class2_pairing=True)
        if result.__class__ is not Pair:
            failures.append(f"{allele}: expected Pair, got {result!r}")
    assert not failures, f"{len(failures)} NetMHCIIpan 3.1 alleles failed:\n" + "\n".join(
        failures[:20]
    )
