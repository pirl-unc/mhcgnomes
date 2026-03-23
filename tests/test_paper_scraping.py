import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name, relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


collect_all = load_script_module("paper_collect_all", "paper/scripts/collect_all.py")
collect_all_v2 = load_script_module("paper_collect_all_v2", "paper/scripts/collect_all_v2.py")
scrape_paper = load_script_module("paper_scrape_paper", "paper/scripts/scrape_paper.py")


def test_scrape_paper_rejects_generic_hyphenated_tokens():
    for token in [
        "UDP-N",
        "Hi-C",
        "SLIT-ROBO",
        "CCR4-NOT",
        "North-European",
        "Holstein-Friesian",
        "H2A",
        "MHC-I",
    ]:
        assert not scrape_paper.looks_like_mhc(token), token

    assert scrape_paper.extract_from_text("UDP-N Hi-C SLIT-ROBO CCR4-NOT") == set()


def test_scrape_paper_extracts_specific_tokens_from_longer_text():
    text = """
    (b) Regional associations conditioned on HLA-C*12:02
    # MHC-I Alleles Expected
    Diagnostic MHC-I Alleles
    """
    assert scrape_paper.extract_from_text(text) == {"HLA-C*12:02"}


def test_scrape_paper_accepts_gene_and_allele_examples():
    text = "Acar-UA*01:01 Gaga-BF1 BoLA-DRB3 H-2Kb RT1-Aa MhcTyal-DAB1*01:01 UAA*01 HLA-A2"
    assert scrape_paper.extract_from_text(text) == {
        "Acar-UA*01:01",
        "Gaga-BF1",
        "BoLA-DRB3",
        "H-2Kb",
        "RT1-Aa",
        "MhcTyal-DAB1*01:01",
        "UAA*01",
        "HLA-A2",
    }


def test_scrape_paper_collect_input_files_includes_docx(tmp_path):
    for name in ["table.xlsx", "notes.txt", "supp.docx", "image.pdf"]:
        (tmp_path / name).write_text("placeholder")

    files = scrape_paper.collect_input_files(input_dir=tmp_path)
    assert [path.name for path in files] == ["notes.txt", "supp.docx", "table.xlsx"]


def test_collect_all_marks_docx_as_scrapeable():
    assert ".docx" in collect_all.SCRAPEABLE_SUFFIXES


def test_collect_all_v2_title_filter_rejects_off_target_titles():
    assert collect_all_v2.title_looks_mhc_related(
        "Crystal Structure of a Classical MHC Class I Molecule in Dogs; Comparison of DLA-88*0 and DLA-88*5 Category Molecules."
    )
    assert collect_all_v2.title_looks_mhc_related(
        "Evidence of Pathogen-Induced Immunogenetic Selection across the Large Geographic Range of a Wild Seabird."
    )
    assert not collect_all_v2.title_looks_mhc_related(
        "Seasonal variation in gut microbiota of migratory wild raptors: a case study in white-tailed eagles."
    )
    assert not collect_all_v2.title_looks_mhc_related(
        "Sequencing the orthologs of human autosomal forensic short tandem repeats provides individual- and species-level identification in African great apes."
    )


def test_collect_all_v2_deduplicates_rows_within_a_paper():
    rows = [
        {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:123"},
        {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:123"},
        {"raw_string": "HLA-B*07:02", "expected_species": "", "source": "PMC:123"},
    ]

    assert collect_all_v2.deduplicate_validation_rows(rows) == [
        {"raw_string": "HLA-A*02:01", "expected_species": "", "source": "PMC:123"},
        {"raw_string": "HLA-B*07:02", "expected_species": "", "source": "PMC:123"},
    ]


def test_collect_all_v2_review_generation_preserves_source(tmp_path):
    scrape_tsv = tmp_path / "scrape.tsv"
    with scrape_tsv.open("w", newline="") as fd:
        writer = csv.DictWriter(
            fd,
            fieldnames=["raw_string", "expected_species", "source"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerow(
            {
                "raw_string": "HLA-A*02:01",
                "expected_species": "",
                "source": "PMC:6155461",
            }
        )

    review_path = tmp_path / "review.tsv"
    collect_all_v2.generate_review_file(scrape_tsv, review_path)

    with review_path.open() as fd:
        rows = list(csv.DictReader(fd, delimiter="\t"))

    assert rows[0]["parsed"] == "yes"
    assert rows[0]["source"] == "PMC:6155461"
