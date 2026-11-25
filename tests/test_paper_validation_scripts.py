"""Regression tests for paper-validation extraction and source bookkeeping (#189)."""

import csv
import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "paper" / "scripts"


def _load_script(name: str):
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"paper_script_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scrape_paper = _load_script("scrape_paper")
collect_all = _load_script("collect_all")
collect_all_v2 = _load_script("collect_all_v2")


@pytest.mark.parametrize(
    "text",
    [
        "UDP-N",
        "Hi-C",
        "SLIT-ROBO",
        "CCR4-NOT",
        "North-European",
        "Holstein-Friesian",
        "MHC-I",
        "MHC-II",
        "Acyl-CoA",
        "RIG-I",
        "IPD-MHC",
        "Acyl-CoA dehydrogenase family member 10",
    ],
)
def test_generic_hyphenated_phrases_are_rejected(text):
    assert not scrape_paper.looks_like_mhc(text)
    assert scrape_paper.extract_from_text(text) == set()


@pytest.mark.parametrize(
    "token",
    [
        "HLA-C*12:02",
        "HLA-A*02:01",
        "HLA-A",
        "HLA-U",
        "HLA-A2",
        "HLA-DQ2.5",
        "Mamu-B*017:01",
        "BoLA-DRB3*01:01",
        "SLA-1*04:01",
        "Gaga-BF1",
        "Dare-UBA",
        "Modo-UA1",
        "H2-Kk",
        "H2-IAb",
        "RT1-Aa",
        "MhcPama-DAB1*01",
        "UAA*01",
        "DAB*02:01",
        "MHC-DRB1",
        "Clgl-DQA*08:02/Clgl-DQA*08:01",
        "Newx-DAB1",
    ],
)
def test_attested_mhc_allele_and_gene_forms_accepted(token):
    assert scrape_paper.looks_like_mhc(token)
    assert scrape_paper.extract_from_text(token) == {token}


def test_extract_from_text_does_not_emit_partial_substrings():
    assert scrape_paper.extract_from_text("Patient carried HLA-C*12:02 allele.") == {"HLA-C*12:02"}
    assert scrape_paper.extract_from_text("Locus HLA-C and allele HLA-C*12:02 were typed.") == {
        "HLA-C",
        "HLA-C*12:02",
    }


def test_docx_supported_consistently_in_scraping_and_collection(tmp_path):
    docx_path = tmp_path / "supp_table.docx"
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        "<w:p><w:r><w:t>Found HLA-C*12:02 and BoLA-DRB3*01:01 alongside Hi-C and UDP-N.</w:t></w:r></w:p>"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(docx_path, "w") as zf:
        zf.writestr("word/document.xml", document_xml)

    # Directory collection includes .docx files.
    collected = scrape_paper.collect_input_files(input_dir=tmp_path)
    assert docx_path in collected

    # Direct file processing extracts real alleles without partial duplicates or FPs.
    assert scrape_paper.process_file(docx_path) == ["BoLA-DRB3*01:01", "HLA-C*12:02"]

    # collect_all.py does not skip .docx in its non-scrapeable suffix list.
    source_text = (SCRIPTS_DIR / "collect_all.py").read_text()
    assert '".docx"' not in source_text.split("Skip non-scrapeable files")[1].split("continue")[0]


def test_source_formatting_never_double_prefixes_pmc(tmp_path):
    assert collect_all_v2.normalize_pmc_source("10691135") == "PMC:10691135"
    assert collect_all_v2.normalize_pmc_source("PMC10691135") == "PMC:10691135"
    assert collect_all_v2.normalize_pmc_source("PMC:10691135") == "PMC:10691135"
    assert collect_all_v2.normalize_pmc_source("PMC:PMC10691135") == "PMC:10691135"
    assert collect_all_v2.normalize_pmc_source("PMID:12345678") == "PMID:12345678"
    assert collect_all_v2.normalize_pmc_source("doi:10.1000/xyz") == "doi:10.1000/xyz"

    merged_tsv = tmp_path / "PMC_10691135_merged.tsv"
    review_tsv = tmp_path / "PMC_10691135_review.tsv"
    with open(merged_tsv, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["raw_string", "expected_species", "source"], delimiter="\t"
        )
        writer.writeheader()
        writer.writerow(
            {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:10691135"}
        )

    collect_all_v2.generate_review_file(merged_tsv, review_tsv, "PMC10691135", "Example paper")
    with open(review_tsv) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 1
    assert rows[0]["source"] == "PMC:10691135"


def test_deduplication_removes_within_paper_dups_and_keeps_cross_paper(tmp_path):
    tsv1 = tmp_path / "file1.tsv"
    tsv2 = tmp_path / "file2.tsv"
    merged = tmp_path / "merged.tsv"
    for path, rows in [
        (
            tsv1,
            [
                {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:111"},
                {"raw_string": "HLA-B*07:02", "expected_species": "", "source": "PMC:111"},
            ],
        ),
        (
            tsv2,
            [
                {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:111"},
                {"raw_string": "HLA-C*12:02", "expected_species": "", "source": "PMC:111"},
            ],
        ),
    ]:
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["raw_string", "expected_species", "source"], delimiter="\t"
            )
            writer.writeheader()
            writer.writerows(rows)

    merged_rows = collect_all_v2.merge_paper_tsvs([tsv1, tsv2], merged)
    assert [r["raw_string"] for r in merged_rows] == ["HLA-A*02:01", "HLA-B*07:02", "HLA-C*12:02"]

    # Same string in a second paper is retained.
    consolidated = collect_all_v2.deduplicate_rows(
        [
            *merged_rows,
            {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:222"},
            {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:222"},
        ]
    )
    assert [(r["raw_string"], r["source"]) for r in consolidated] == [
        ("HLA-A*02:01", "PMC:111"),
        ("HLA-B*07:02", "PMC:111"),
        ("HLA-C*12:02", "PMC:111"),
        ("HLA-A*02:01", "PMC:222"),
    ]
