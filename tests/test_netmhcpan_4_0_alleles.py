from pathlib import Path

from mhcgnomes import Allele, AlleleWithoutGene, Gene, parse

TESTS_DIR = Path(__file__).parent
NETMHCPAN_3_0_PATH = TESTS_DIR / "netmhcpan_3_0_alleles.txt"
NETMHCPAN_4_0_PATH = TESTS_DIR / "netmhcpan_4_0_alleles.txt"


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


def test_netmhcpan_4_0_alleles():
    existing = set(_load_unique_alleles(NETMHCPAN_3_0_PATH))
    alleles = [a for a in _load_unique_alleles(NETMHCPAN_4_0_PATH) if a not in existing]
    assert len(alleles) == 1607
    failures = []
    for allele in alleles:
        result = parse(allele)
        if ":" in allele:
            if result.__class__ is not Allele:
                failures.append(f"{allele}: expected Allele, got {result!r}")
        elif result.__class__ not in (Gene, Allele, AlleleWithoutGene):
            failures.append(f"{allele}: unexpected type {result!r}")
    assert not failures, f"{len(failures)} NetMHCpan 4.0 alleles failed:\n" + "\n".join(
        failures[:20]
    )
