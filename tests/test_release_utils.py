from pathlib import Path

import pytest
from release_utils import (
    ReleaseError,
    check_tag_against_version_file,
    ensure_tag_matches_version,
    main,
    parse_version_from_python_file,
    tag_for_version,
)


def write_version_file(tmp_path: Path, contents: str) -> Path:
    path = tmp_path / "version.py"
    path.write_text(contents, encoding="utf-8")
    return path


def test_parse_version_from_python_file_assign(tmp_path: Path):
    path = write_version_file(tmp_path, '__version__ = "3.15.1"\n')
    assert parse_version_from_python_file(path) == "3.15.1"


def test_parse_version_from_python_file_annotated_assign(tmp_path: Path):
    path = write_version_file(tmp_path, '__version__: str = "3.15.1rc1"\n')
    assert parse_version_from_python_file(path) == "3.15.1rc1"


def test_parse_version_from_python_file_rejects_multiple_versions(tmp_path: Path):
    path = write_version_file(tmp_path, '__version__ = "1.0.0"\n__version__ = "1.0.1"\n')
    with pytest.raises(ReleaseError, match="Multiple __version__ assignments"):
        parse_version_from_python_file(path)


def test_parse_version_from_python_file_rejects_non_literal(tmp_path: Path):
    path = write_version_file(tmp_path, "__version__ = VERSION\n")
    with pytest.raises(ReleaseError, match="string literal"):
        parse_version_from_python_file(path)


def test_tag_for_version():
    assert tag_for_version("3.15.1") == "v3.15.1"


def test_ensure_tag_matches_version_accepts_matching_tag():
    ensure_tag_matches_version("v3.15.1", "3.15.1")


def test_ensure_tag_matches_version_rejects_mismatch():
    with pytest.raises(ReleaseError, match="Tag/version mismatch"):
        ensure_tag_matches_version("v3.15.2", "3.15.1")


def test_check_tag_against_version_file(tmp_path: Path):
    path = write_version_file(tmp_path, '__version__ = "3.15.1"\n')
    assert check_tag_against_version_file("v3.15.1", path) == "3.15.1"


def test_release_utils_main_print_version(tmp_path: Path, capsys):
    path = write_version_file(tmp_path, '__version__ = "3.15.1"\n')
    assert main(["print-version", "--version-file", str(path), "--as-tag"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "v3.15.1"


def test_release_utils_main_check_tag_failure(tmp_path: Path, capsys):
    path = write_version_file(tmp_path, '__version__ = "3.15.1"\n')
    assert main(["check-tag", "--version-file", str(path), "--tag", "v3.15.2"]) == 1
    captured = capsys.readouterr()
    assert "Tag/version mismatch" in captured.err
