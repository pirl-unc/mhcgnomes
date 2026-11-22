import csv
from pathlib import Path

from mhcgnomes import parse

IEDB_CSV_PATH = Path(__file__).parent / "iedb_allele_counts.csv"


def _load_iedb_alleles(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return sorted({row["allele"] for row in reader})


def test_iedb_allele_names():
    alleles = _load_iedb_alleles(IEDB_CSV_PATH)
    assert len(alleles) == 573
    failures = [allele for allele in alleles if parse(allele) is None]
    assert not failures, f"{len(failures)} IEDB allele names failed to parse:\n" + "\n".join(
        failures[:20]
    )
