#!/usr/bin/env python3
"""
Shared helpers for local release automation and GitHub Actions release checks.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections.abc import Sequence
from pathlib import Path

VERSION_TAG_PREFIX = "v"
_VERSION_ALLOWED_RE = re.compile(r"^[0-9][0-9A-Za-z.+-]*$")


class ReleaseError(ValueError):
    pass


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseError(message)


def validate_version_string(version: str) -> str:
    value = version.strip()
    _ensure(bool(value), "Version must not be empty.")
    _ensure(
        bool(_VERSION_ALLOWED_RE.match(value)),
        f"Version '{value}' looks invalid (unexpected characters).",
    )
    return value


def parse_version_from_python_file(path: Path) -> str:
    if not path.exists():
        raise ReleaseError(f"Missing version file: {path}")
    if not path.is_file():
        raise ReleaseError(f"Version path is not a regular file: {path}")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReleaseError(f"Failed to read version file {path}: {exc}") from exc

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        raise ReleaseError(f"Version file is not valid Python syntax: {path}: {exc}") from exc

    found: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    found.append(_extract_version_literal(node.value, path))
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__version__"
        ):
            if node.value is None:
                raise ReleaseError(f"{path}: __version__ is annotated but not assigned.")
            found.append(_extract_version_literal(node.value, path))

    _ensure(bool(found), f"Failed to find __version__ assignment in {path}.")
    _ensure(
        len(found) == 1,
        f"Multiple __version__ assignments found in {path}. Refuse to guess.",
    )
    return validate_version_string(found[0])


def _extract_version_literal(node: ast.expr, path: Path) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    raise ReleaseError(f"{path}: __version__ must be a string literal.")


def tag_for_version(version: str, prefix: str = VERSION_TAG_PREFIX) -> str:
    clean_version = validate_version_string(version)
    _ensure(bool(prefix), "Tag prefix must not be empty.")
    return f"{prefix}{clean_version}"


def ensure_tag_matches_version(
    tag: str,
    version: str,
    *,
    prefix: str = VERSION_TAG_PREFIX,
) -> None:
    clean_tag = tag.strip()
    _ensure(bool(clean_tag), "Tag must not be empty.")
    expected = tag_for_version(version, prefix=prefix)
    _ensure(
        clean_tag == expected,
        f"Tag/version mismatch: expected '{expected}' for version '{version}', got '{clean_tag}'.",
    )


def check_tag_against_version_file(
    tag: str,
    version_file: Path,
    *,
    prefix: str = VERSION_TAG_PREFIX,
) -> str:
    version = parse_version_from_python_file(version_file)
    ensure_tag_matches_version(tag, version, prefix=prefix)
    return version


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m release_utils")
    subparsers = parser.add_subparsers(dest="command", required=True)

    print_version = subparsers.add_parser("print-version")
    print_version.add_argument("--version-file", default="mhcgnomes/version.py")
    print_version.add_argument("--as-tag", action="store_true")

    check_tag = subparsers.add_parser("check-tag")
    check_tag.add_argument("--version-file", default="mhcgnomes/version.py")
    check_tag.add_argument("--tag", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        version_file = Path(args.version_file)
        version = parse_version_from_python_file(version_file)

        if args.command == "print-version":
            output = tag_for_version(version) if args.as_tag else version
            print(output)
            return 0

        if args.command == "check-tag":
            check_tag_against_version_file(args.tag, version_file)
            print(f"OK: tag '{args.tag}' matches version '{version}' from {version_file}")
            return 0
    except ReleaseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
