from pathlib import Path

from mhcgnomes import Allele, AlleleWithoutGene, Gene, parse

ALLELES_PATH = Path(__file__).parent / "netmhcpan_3_0_alleles.txt"


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


def test_netmhcpan_3_0_alleles():
    alleles = _load_unique_alleles(ALLELES_PATH)
    assert len(alleles) == 3708
    failures = []
    for allele in alleles:
        result = parse(allele)
        if ":" in allele:
            if result.__class__ is not Allele:
                failures.append(f"{allele}: expected Allele, got {result!r}")
        elif result.__class__ not in (Gene, Allele, AlleleWithoutGene):
            failures.append(f"{allele}: unexpected type {result!r}")
    assert not failures, f"{len(failures)} NetMHCpan 3.0 alleles failed:\n" + "\n".join(
        failures[:20]
    )
