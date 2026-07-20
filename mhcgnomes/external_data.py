"""Retrieve pinned IMGT/IPD inputs through verified, reusable cache layers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path(__file__).with_name("data") / "external_sources.json"
CACHE_ENV = "MHCGNOMES_DATA_CACHE"
MIRRORS_ENV = "MHCGNOMES_DATA_MIRRORS"
USER_AGENT = "mhcgnomes-external-data/1 (+https://github.com/pirl-unc/mhcgnomes)"


class ExternalDataError(RuntimeError):
    """Raised when an external source cannot be resolved and verified."""


@dataclass(frozen=True)
class Source:
    id: str
    filename: str
    provider: str
    release: str
    url: str
    sha256: str
    license_url: str
    groups: tuple[str, ...]
    default: bool


def default_cache_dir() -> Path:
    configured = os.environ.get(CACHE_ENV)
    if configured:
        return Path(configured).expanduser()
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    cache_root = Path(xdg_cache).expanduser() if xdg_cache else Path.home() / ".cache"
    return cache_root / "mhcgnomes" / "external-data-v1"


def _validate_filename(filename: str, source_id: str) -> None:
    path = Path(filename)
    if path.is_absolute() or len(path.parts) != 1 or filename in {"", ".", ".."}:
        raise ExternalDataError(f"Source {source_id!r} has unsafe filename {filename!r}")


def _parse_source(raw: dict[str, Any]) -> Source:
    if not isinstance(raw, dict):
        raise ExternalDataError("Manifest source entries must be JSON objects")
    required = {
        "id",
        "filename",
        "provider",
        "release",
        "url",
        "sha256",
        "license_url",
        "groups",
        "default",
    }
    missing = required.difference(raw)
    if missing:
        raise ExternalDataError(f"Manifest source is missing fields: {sorted(missing)}")

    if not isinstance(raw["groups"], list) or not all(
        isinstance(group, str) and group for group in raw["groups"]
    ):
        raise ExternalDataError(f"Source {raw['id']!r} must have a list of non-empty groups")
    if not isinstance(raw["default"], bool):
        raise ExternalDataError(f"Source {raw['id']!r} must have a boolean default value")

    source = Source(
        id=str(raw["id"]),
        filename=str(raw["filename"]),
        provider=str(raw["provider"]),
        release=str(raw["release"]),
        url=str(raw["url"]),
        sha256=str(raw["sha256"]).lower(),
        license_url=str(raw["license_url"]),
        groups=tuple(raw["groups"]),
        default=raw["default"],
    )
    if not source.id:
        raise ExternalDataError("Manifest source IDs must not be empty")
    _validate_filename(source.filename, source.id)
    if len(source.sha256) != 64 or any(c not in "0123456789abcdef" for c in source.sha256):
        raise ExternalDataError(f"Source {source.id!r} has invalid SHA-256")
    if urllib.parse.urlparse(source.url).scheme != "https":
        raise ExternalDataError(f"Source {source.id!r} must use an HTTPS primary URL")
    if urllib.parse.urlparse(source.license_url).scheme != "https":
        raise ExternalDataError(f"Source {source.id!r} must use an HTTPS license URL")
    if not source.groups:
        raise ExternalDataError(f"Source {source.id!r} must belong to at least one group")
    return source


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[Source, ...]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExternalDataError(f"Cannot read external-data manifest {path}: {exc}") from exc
    if (
        not isinstance(raw, dict)
        or raw.get("schema_version") != 1
        or not isinstance(raw.get("sources"), list)
    ):
        raise ExternalDataError(f"Unsupported external-data manifest schema in {path}")

    sources = tuple(_parse_source(item) for item in raw["sources"])
    ids = [source.id for source in sources]
    filenames = [source.filename for source in sources]
    if len(ids) != len(set(ids)):
        raise ExternalDataError("External-data manifest contains duplicate source IDs")
    if len(filenames) != len(set(filenames)):
        raise ExternalDataError("External-data manifest contains duplicate filenames")
    return sources


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_verified(path: Path, expected_sha256: str) -> bool:
    try:
        return path.is_file() and sha256_file(path) == expected_sha256
    except OSError:
        return False


def _atomic_copy(source_path: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(source_path, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _download_to_cache(url: str, source: Source, cache_path: Path, retries: int = 3) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(retries):
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{source.sha256}.", suffix=".tmp", dir=cache_path.parent
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            digest = hashlib.sha256()
            with (
                urllib.request.urlopen(request, timeout=60) as response,
                temporary.open("wb") as output,
            ):
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
            actual = digest.hexdigest()
            if actual != source.sha256:
                raise ExternalDataError(
                    f"Checksum mismatch for {source.id}: expected {source.sha256}, got {actual}"
                )
            os.replace(temporary, cache_path)
            return
        except ExternalDataError:
            raise
        except urllib.error.HTTPError as exc:
            last_error = exc
            retryable = exc.code in {408, 425, 429} or exc.code >= 500
            if not retryable:
                break
            if attempt + 1 < retries:
                time.sleep(2**attempt)
        except (OSError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2**attempt)
        finally:
            temporary.unlink(missing_ok=True)
    raise ExternalDataError(f"Failed to download {source.id} from {url}: {last_error}")


def _mirror_url(mirror: str, filename: str) -> str:
    return f"{mirror.rstrip('/')}/{urllib.parse.quote(filename)}"


def _try_local_mirror(mirror: Path, source: Source, cache_path: Path) -> bool:
    for candidate in (mirror / source.filename, mirror / source.sha256):
        if is_verified(candidate, source.sha256):
            _atomic_copy(candidate, cache_path)
            return True
    return False


def _is_network_mirror(mirror: str) -> bool:
    return urllib.parse.urlparse(mirror).scheme in {"http", "https"}


def resolve_source(
    source: Source,
    *,
    destination_dir: Path,
    cache_dir: Path,
    mirrors: Sequence[str] = (),
    offline: bool = False,
) -> tuple[Path, str]:
    destination = destination_dir / source.filename
    if is_verified(destination, source.sha256):
        return destination, "destination"

    cache_path = cache_dir / source.sha256
    origin = "cache"
    if not is_verified(cache_path, source.sha256):
        origin = ""
        for mirror in mirrors:
            if _is_network_mirror(mirror):
                if offline:
                    continue
                for mirror_key in (source.filename, source.sha256):
                    try:
                        _download_to_cache(_mirror_url(mirror, mirror_key), source, cache_path)
                    except ExternalDataError:
                        continue
                    origin = f"mirror {mirror}"
                    break
                if origin:
                    break
            if _try_local_mirror(Path(mirror).expanduser(), source, cache_path):
                origin = f"mirror {mirror}"
                break

        if not origin:
            if offline:
                raise ExternalDataError(
                    f"Offline and no verified cache or local mirror contains {source.id}"
                )
            _download_to_cache(source.url, source, cache_path)
            origin = "official source"

    _atomic_copy(cache_path, destination)
    if not is_verified(destination, source.sha256):
        raise ExternalDataError(f"Failed to materialize verified source {source.id}")
    return destination, origin


def environment_mirrors() -> tuple[str, ...]:
    value = os.environ.get(MIRRORS_ENV, "")
    return tuple(part.strip() for part in value.split(";") if part.strip())


def select_sources(
    sources: Sequence[Source],
    *,
    source_ids: Sequence[str] = (),
    groups: Sequence[str] = (),
    all_sources: bool = False,
) -> tuple[Source, ...]:
    known_ids = {source.id for source in sources}
    known_groups = {group for source in sources for group in source.groups}
    unknown_ids = set(source_ids).difference(known_ids)
    unknown_groups = set(groups).difference(known_groups)
    if unknown_ids:
        raise ExternalDataError(f"Unknown source IDs: {sorted(unknown_ids)}")
    if unknown_groups:
        raise ExternalDataError(f"Unknown source groups: {sorted(unknown_groups)}")

    requested_ids = set(source_ids)
    requested_groups = set(groups)
    return tuple(
        source
        for source in sources
        if all_sources
        or (not requested_ids and not requested_groups and source.default)
        or source.id in requested_ids
        or requested_groups.intersection(source.groups)
    )


def materialize_sources(
    sources: Iterable[Source],
    *,
    destination_dir: Path,
    cache_dir: Path,
    mirrors: Sequence[str] = (),
    offline: bool = False,
) -> tuple[Path, ...]:
    paths = []
    for source in sources:
        path, origin = resolve_source(
            source,
            destination_dir=destination_dir,
            cache_dir=cache_dir,
            mirrors=mirrors,
            offline=offline,
        )
        print(f"{source.id}: {path} ({origin})")
        paths.append(path)
    return tuple(paths)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mhcgnomes-data",
        description="Fetch checksum-pinned IMGT/IPD inputs through local and CI-friendly caches.",
    )
    parser.add_argument("source_ids", nargs="*", help="Source IDs (defaults to maintained inputs)")
    parser.add_argument("--group", action="append", default=[], help="Select a purpose group")
    parser.add_argument("--all", action="store_true", help="Fetch every registered source")
    parser.add_argument("--list", action="store_true", help="List registered sources and exit")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    parser.add_argument("--destination", type=Path, default=Path(".external-data"))
    parser.add_argument(
        "--mirror",
        action="append",
        default=[],
        help="Local directory or HTTP(S) base URL; repeat for fallback order",
    )
    parser.add_argument("--offline", action="store_true", help="Forbid all network access")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        sources = load_manifest(args.manifest)
        if args.list:
            for source in sources:
                groups = ",".join(source.groups)
                default = " default" if source.default else ""
                print(f"{source.id}\t{source.provider} {source.release}\t{groups}{default}")
            return 0
        selected = select_sources(
            sources,
            source_ids=args.source_ids,
            groups=args.group,
            all_sources=args.all,
        )
        if not selected:
            raise ExternalDataError("No external sources selected")
        mirrors = (*args.mirror, *environment_mirrors())
        materialize_sources(
            selected,
            destination_dir=args.destination,
            cache_dir=args.cache_dir,
            mirrors=mirrors,
            offline=args.offline,
        )
        return 0
    except ExternalDataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
