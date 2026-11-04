"""Offline source fixtures exercise the public maintainer API and source precedence."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from mhcgnomes import Species, parse

SPEC = importlib.util.spec_from_file_location(
    "alias_generator", Path(__file__).parents[1] / "mhcgnomes/data/combine_allele_aliases.py"
)
generator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = generator
SPEC.loader.exec_module(generator)
RegistryRecord = generator.RegistryRecord
AliasCandidate = generator.AliasCandidate


def test_actual_ipd_history_schema_and_comma_separated_names(tmp_path):
    path = tmp_path / "MHC.xml"
    path.write_text("""<database><entries><entry id="NHP01884">
      <name>Mamu-A1*011:01:01:01</name><additional_fields>
        <field name="nomenclature">Mamu-A1*01104, A1*011:01</field>
        <field name="nomenclature">Mamu-A1*011:01</field>
      </additional_fields></entry></entries></database>""")
    (record,) = generator.read_ipd_xml(path)
    assert record == RegistryRecord(
        "Mamu", "NHP01884", "A1*011:01:01:01", ("A1*01104", "A1*011:01"), "MHC.xml"
    )
    path.write_text(
        '<database><entries><entry id="NHP1"><name>Mamu-A*01</name>'
        "<nomenclature>A*02</nomenclature></entry></entries></database>"
    )
    with pytest.raises(ValueError, match="check the XML schema"):
        generator.read_ipd_xml(path)


def test_current_hla_column_and_deletion_identity(tmp_path):
    history = tmp_path / "history.txt"
    history.write_text(
        "# version: 3.66.0\nHLA_ID,3660,3650,3420\n"
        "HLA02908,A*02:01:14,A*02:01:14Q,A*02:01:14Q\n"
        "HLA33848,NA,A*02:01:08,A*02:01:08\n"
    )
    (record,) = generator.read_hla_history(history)
    assert record.previous == ("A*02:01:14Q",)
    deletions = tmp_path / "deleted.txt"
    deletions.write_text(
        "AlleleID,Allele,Reason\n"
        "HLA02908,A*02:01:14Q,Suffix added becoming A*02:01:14Q. Then removed becoming A*02:01:14\n"
        "HLA33848,A*02:01:08,Sequence extended and renamed A*02:1040:01 (January 2022)\n"
        "HLA03493,DRB1*1171,Sequence shown to be identical to corrected DRB1*11:02:01:01\n"
        "HLA99999,A*99:99,Sequence incorrect. Later resubmitted now named A*99:100\n"
    )
    candidates, unresolved = generator.read_hla_deletions(
        deletions, {record.accession: record.current}
    )
    assert [c.new for c in candidates] == ["A*02:01:14", "A*02:1040:01", "DRB1*11:02:01:01"]
    assert [r["accession"] for r in unresolved] == ["HLA99999"]


def test_precedence_boundaries_conflicts_and_order_independence():
    records = [RegistryRecord("HLA", "CURRENT", "A*30:100", (), "history")]
    candidates = [
        AliasCandidate("HLA", "A*30:100", "A*30:02:12", "history", "OLD"),
        AliasCandidate("HLA", "A*30:100", "A*30:02:12", "curated", curated=True),
        AliasCandidate("HLA", "A*02172", "A*02:17:02", "history"),
        AliasCandidate("HLA", "A*02172", "A*02:17:02:01", "history"),
        AliasCandidate("HLA", "A*90", "A*91:01", "history"),
        AliasCandidate("HLA", "A*90", "A*91:010", "history"),
        AliasCandidate("Mamu", "A*01", "A1*002:01", "history"),
        AliasCandidate("Mamu", "A*01", "A1*001:01", "curated", curated=True),
    ]
    result = generator.resolve_aliases(records, candidates)
    assert result == generator.resolve_aliases(records[::-1], candidates[::-1])
    aliases, provenance, audit = result
    assert aliases == {"HLA": {"A*02172": "A*02:17:02:01"}, "Mamu": {"A*01": "A1*001:01"}}
    assert provenance["Mamu"]["A*01"] == ["curated"]
    assert audit["sources"]["history"]["current_name_preserved"] == 1
    assert audit["sources"]["history"]["ambiguous"] == 2
    assert generator.alias_key("HLA-A*02:172") != generator.alias_key("HLA-A*02172")


def test_chains_resolve_and_cycles_fail():
    candidates = [
        AliasCandidate("HLA", "A*01", "A*02", "history"),
        AliasCandidate("HLA", "A*02", "A*03", "curated", curated=True),
    ]
    aliases, provenance, _ = generator.resolve_aliases([], candidates)
    assert aliases["HLA"]["A*01"] == "A*03"
    assert provenance["HLA"]["A*01"] == ["curated", "history"]
    with pytest.raises(ValueError, match="Cyclic allele alias"):
        generator.resolve_aliases(
            [], [*candidates, AliasCandidate("HLA", "A*03", "A*01", "history")]
        )


def test_source_coverage_is_recorded():
    audit = json.loads(
        (Path(__file__).parents[1] / "data-sources/allele-alias-audit.json").read_text()
    )
    assert audit["coverage"]["IPD-MHC-3.8.0.0.xml"] == {
        "source_records": 11756,
        "excluded_records": 1,
        "current_records": 11755,
        "records_with_history": 5261,
        "historical_names": 7288,
    }
    assert audit["sources"]["IPD-MHC-3.8.0.0.xml"]["accepted"] > 2900
    (excluded,) = audit["excluded_records"]
    assert excluded["accession"] == "NHP10764"
    assert excluded["name"] == "Paha-DP1*06:01"
    assert excluded["status"] == "abandoned"
    assert excluded["status_release"] == "3.7.0.0"
    assert excluded["status_source"] == "https://www.ebi.ac.uk/ipd/mhc/version/v3700/"
    assert excluded["replacement"] is None


def test_abandoned_ipd_record_is_retained_in_audit_only(tmp_path):
    source = tmp_path / "IPD-MHC-3.8.0.0.xml"
    source.write_text("""<database><entries>
      <entry id="NHP01884"><name>Mamu-A1*011:01:01:01</name><additional_fields>
        <field name="nomenclature">A*06:01</field>
      </additional_fields></entry>
      <entry id="NHP10764"><name>Paha-DP1*06:01</name><cross_references/>
        <additional_fields><field name="organism">Papio hamadryas</field></additional_fields>
      </entry>
      <entry id="NHP99999"><name>Paha-DP1*99:99</name><cross_references/></entry>
    </entries></database>""")
    records = generator.read_ipd_xml(source)
    eligible, excluded = generator.partition_ipd_records(records)
    # Absence of a sequence is not grounds for exclusion: only sourced status is.
    assert [r.accession for r in eligible] == ["NHP01884", "NHP99999"]
    assert [r["accession"] for r in excluded] == ["NHP10764"]

    output, audit_path, guards = (tmp_path / name for name in ("aliases", "audit", "guards"))
    generator.main(
        [
            "--xml-input-file",
            str(source),
            "--output",
            str(output),
            "--audit-output",
            str(audit_path),
            "--current-names-output",
            str(guards),
        ]
    )
    audit = json.loads(audit_path.read_text())
    assert audit["excluded_records"] == excluded
    assert audit["coverage"][source.name]["source_records"] == 3
    assert audit["coverage"][source.name]["current_records"] == 2
    assert "DP1*06:01" not in guards.read_text()
    assert "DP1*06:01" not in output.read_text()
    assert "DPB1*06:01" not in output.read_text()


def test_ipd_annotation_requires_matching_source_accession_and_name():
    name = "DP1*06:01"
    other_source = RegistryRecord("Paha", "NHP10764", name, (), "another-release.xml")
    other_accession = RegistryRecord("Paha", "NHP99999", name, (), "IPD-MHC-3.8.0.0.xml")
    assert generator.partition_ipd_records([other_source, other_accession]) == (
        [other_source, other_accession],
        [],
    )
    for species, changed_name in [("Paha", "DPB1*06:01"), ("Mamu", name)]:
        with pytest.raises(ValueError, match="annotation name mismatch for NHP10764"):
            generator.partition_ipd_records(
                [RegistryRecord(species, "NHP10764", changed_name, (), "IPD-MHC-3.8.0.0.xml")]
            )


def test_abandoned_designation_has_no_inferred_replacement():
    for enabled in (False, True):
        assert parse("Paha-DP1*06:01", use_allele_aliases=enabled, raise_on_error=False) is None
    assert Species.get("Paha").get_allele_alias("DP1", "06:01") is None


def test_source_audit_has_no_unparseable_name_allowance(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "alias_auditor", Path(__file__).parents[1] / "scripts/validate_alias_sources.py"
    )
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    monkeypatch.setattr(auditor, "allele_aliases", {})
    records = [RegistryRecord("HLA", "CURRENT", "A*02:01", (), "hla")]
    assert auditor.audit_alias_sources(records) == []
    records.append(RegistryRecord("Paha", "NHP10764", "DP1*06:01", (), "ipd"))
    assert auditor.audit_alias_sources(records) == [
        "Unparseable registry names: ['Paha-DP1*06:01']"
    ]


@pytest.mark.parametrize(
    "name,expected",
    [
        ("HLA-A*30:100", "HLA-A*30:100"),
        ("HLA-A*02:01:14", "HLA-A*02:01:14"),
        ("HLA-A*02:01:14Q", "HLA-A*02:01:14"),
        ("HLA-A*02:01:08", "HLA-A*02:1040:01"),
        ("HLA-DRB1*1171", "HLA-DRB1*11:02:01:01"),
    ],
)
def test_accession_backed_source_regressions(name, expected):
    assert parse(name, use_allele_aliases=True).to_string() == expected


def test_current_names_win_through_inheritance_and_alternate_gene_names():
    for name in ["Bogr-NC1*001:01", "Caja-F1*08:01N"]:
        assert parse(name, use_allele_aliases=True) == parse(name)
    # The historical gene spelling remains a valid redirect, without claiming
    # the current F1 identity. NHP records in the pinned IPD XML back both names.
    assert parse("Caja-F*08:01N", use_allele_aliases=True).to_string() == "Caja-F4*08:01N"


def test_sparse_guards_cover_cross_species_and_alternate_gene_collisions():
    records = [
        RegistryRecord("Bogr", "YAK", "NC1*001:01", (), "ipd"),
        RegistryRecord("Caja", "MONKEY", "F1*08:01N", (), "ipd"),
        RegistryRecord("HLA", "OTHER", "A*99:99", (), "hla"),
    ]
    assert generator.protected_current_names(
        records, {"BoLA": {"NC1*001:01": "NC1*001:01:01"}, "Caja": {"F*08:01N": "F4*08:01N"}}
    ) == {"Bogr": ["NC1*001:01"], "Caja": ["F1*08:01N"]}


def test_bare_registry_history_does_not_replace_loci_or_haplotypes():
    aliases, _, audit = generator.resolve_aliases(
        [], [AliasCandidate("Mamu", "B17", "B*017:01", "ipd")]
    )
    assert aliases == {}
    assert audit["sources"]["ipd"]["unchanged_or_unsupported"] == 1
    assert parse("Mamu-B17", use_allele_aliases=True).name == "B17"
    assert type(parse("Gaga-B12", use_allele_aliases=True)).__name__ == "Haplotype"


def test_bola_splice_variant_alias_and_annotation():
    result = parse("BoLA-NC1*00401", use_allele_aliases=True)
    assert result == parse("BoLA-NC1*004:01SV")
    assert result.annotations == ("SV",)
    assert result.annotation_splice_variant
    assert result.annotation_descriptions == {"SV": "splice variant"}
    assert result.cell_surface_expression is None


def test_history_does_not_invent_resolution_or_change_default_padding():
    aliases, _, _ = generator.resolve_aliases(
        [], [AliasCandidate("Mamu", "B*008:01", "B*008:01:01:01", "ipd")]
    )
    assert aliases == {}
    assert parse("Mamu-B*008:01", use_allele_aliases=True).to_string() == "Mamu-B*008:01"
    assert parse("BoLA-DRB3*01:01").to_string() == "BoLA-DRB3*01:01"
    assert parse("Gaga-BF2*0201").to_string() == "Gaga-BF2*02:01"
