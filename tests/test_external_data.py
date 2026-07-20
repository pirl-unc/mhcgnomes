import hashlib
import io
import json
import urllib.error
from pathlib import Path

import pytest

from mhcgnomes import external_data


def make_source(payload=b"source payload", **overrides):
    values = {
        "id": "example-source",
        "filename": "example.dat",
        "provider": "Example",
        "release": "1",
        "url": "https://official.example/example.dat",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "license_url": "https://official.example/license",
        "groups": ("example-group",),
        "default": True,
    }
    values.update(overrides)
    return external_data.Source(**values)


def write_manifest(path: Path, sources):
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": source.id,
                        "filename": source.filename,
                        "provider": source.provider,
                        "release": source.release,
                        "url": source.url,
                        "sha256": source.sha256,
                        "license_url": source.license_url,
                        "groups": source.groups,
                        "default": source.default,
                    }
                    for source in sources
                ],
            }
        ),
        encoding="utf-8",
    )


def test_shipped_manifest_is_valid_and_uses_official_providers():
    sources = external_data.load_manifest()
    assert len(sources) == 7
    assert {source.provider for source in sources} == {"IPD-IMGT/HLA", "IPD-MHC"}
    assert all("/ANHIG/" in source.url for source in sources)


@pytest.mark.parametrize("arguments", [[], ["list"]])
def test_data_command_lists_sources_by_default_without_downloading(arguments, monkeypatch, capsys):
    monkeypatch.setattr(
        external_data,
        "_download_to_cache",
        lambda *_args, **_kwargs: pytest.fail("listing must not download data"),
    )

    assert external_data.main(arguments) == 0

    output = capsys.readouterr().out
    assert "imgt-hla-allele-history-3.42.0" in output
    assert "ipd-mhc-3.8.0.0-protein" in output


def test_select_sources_defaults_and_unions_explicit_groups():
    default = make_source()
    optional = make_source(
        id="optional", filename="optional.dat", groups=("optional-group",), default=False
    )
    sources = (default, optional)

    assert external_data.select_sources(sources) == (default,)
    assert external_data.select_sources(sources, groups=("optional-group",)) == (optional,)
    assert (
        external_data.select_sources(sources, source_ids=(default.id,), groups=("optional-group",))
        == sources
    )
    assert external_data.select_sources(sources, all_sources=True) == sources


def test_select_sources_rejects_unknown_values():
    source = make_source()
    with pytest.raises(external_data.ExternalDataError, match="Unknown source IDs"):
        external_data.select_sources((source,), source_ids=("missing",))
    with pytest.raises(external_data.ExternalDataError, match="Unknown source groups"):
        external_data.select_sources((source,), groups=("missing",))


def test_verified_destination_avoids_cache_and_network(tmp_path, monkeypatch):
    payload = b"already materialized"
    source = make_source(payload)
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / source.filename).write_bytes(payload)

    monkeypatch.setattr(
        external_data,
        "_download_to_cache",
        lambda *_args, **_kwargs: pytest.fail("network should not be used"),
    )
    path, origin = external_data.resolve_source(
        source, destination_dir=destination, cache_dir=tmp_path / "cache"
    )

    assert path.read_bytes() == payload
    assert origin == "destination"


def test_content_cache_is_materialized_without_network(tmp_path, monkeypatch):
    payload = b"cached content"
    source = make_source(payload)
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / source.sha256).write_bytes(payload)
    monkeypatch.setattr(
        external_data,
        "_download_to_cache",
        lambda *_args, **_kwargs: pytest.fail("network should not be used"),
    )

    path, origin = external_data.resolve_source(
        source, destination_dir=tmp_path / "destination", cache_dir=cache
    )

    assert path.read_bytes() == payload
    assert origin == "cache"


def test_local_mirror_accepts_filename_or_content_hash(tmp_path):
    payload = b"mirrored content"
    source = make_source(payload)
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / source.sha256).write_bytes(payload)

    path, origin = external_data.resolve_source(
        source,
        destination_dir=tmp_path / "destination",
        cache_dir=tmp_path / "cache",
        mirrors=(str(mirror),),
        offline=True,
    )

    assert path.read_bytes() == payload
    assert origin == f"mirror {mirror}"


def test_http_mirror_precedes_official_source(tmp_path, monkeypatch):
    payload = b"HTTP mirror content"
    source = make_source(payload)
    requested_urls = []

    def fake_download(url, _source, cache_path, retries=3):
        requested_urls.append(url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(payload)

    monkeypatch.setattr(external_data, "_download_to_cache", fake_download)
    path, origin = external_data.resolve_source(
        source,
        destination_dir=tmp_path / "destination",
        cache_dir=tmp_path / "cache",
        mirrors=("https://cache.example/base",),
    )

    assert path.read_bytes() == payload
    assert requested_urls == ["https://cache.example/base/example.dat"]
    assert origin == "mirror https://cache.example/base"


def test_http_mirror_can_expose_content_by_hash(tmp_path, monkeypatch):
    payload = b"content-addressed HTTP mirror"
    source = make_source(payload)
    requested_urls = []

    def fake_download(url, _source, cache_path, retries=3):
        requested_urls.append(url)
        if not url.endswith(source.sha256):
            raise external_data.ExternalDataError("filename not present")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(payload)

    monkeypatch.setattr(external_data, "_download_to_cache", fake_download)
    path, origin = external_data.resolve_source(
        source,
        destination_dir=tmp_path / "destination",
        cache_dir=tmp_path / "cache",
        mirrors=("https://cache.example/base",),
    )

    assert path.read_bytes() == payload
    assert requested_urls == [
        "https://cache.example/base/example.dat",
        f"https://cache.example/base/{source.sha256}",
    ]
    assert origin == "mirror https://cache.example/base"


def test_offline_mode_skips_network_mirror_and_primary(tmp_path, monkeypatch):
    source = make_source()
    monkeypatch.setattr(
        external_data,
        "_download_to_cache",
        lambda *_args, **_kwargs: pytest.fail("network should not be used"),
    )
    with pytest.raises(external_data.ExternalDataError, match="Offline"):
        external_data.resolve_source(
            source,
            destination_dir=tmp_path / "destination",
            cache_dir=tmp_path / "cache",
            mirrors=("https://cache.example",),
            offline=True,
        )


def test_primary_download_is_verified_and_reused(tmp_path, monkeypatch):
    payload = b"official content"
    source = make_source(payload)
    requests = []

    def fake_urlopen(request, timeout):
        requests.append((request.full_url, request.headers["User-agent"], timeout))
        return io.BytesIO(payload)

    monkeypatch.setattr(external_data.urllib.request, "urlopen", fake_urlopen)
    cache = tmp_path / "cache"
    first, origin = external_data.resolve_source(
        source, destination_dir=tmp_path / "first", cache_dir=cache
    )
    second, second_origin = external_data.resolve_source(
        source, destination_dir=tmp_path / "second", cache_dir=cache
    )

    assert first.read_bytes() == payload
    assert second.read_bytes() == payload
    assert origin == "official source"
    assert second_origin == "cache"
    assert requests == [(source.url, external_data.USER_AGENT, 60)]


def test_checksum_mismatch_is_rejected_without_poisoning_cache(tmp_path, monkeypatch):
    source = make_source(b"expected")
    monkeypatch.setattr(
        external_data.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: io.BytesIO(b"tampered"),
    )
    cache_path = tmp_path / "cache" / source.sha256

    with pytest.raises(external_data.ExternalDataError, match="Checksum mismatch"):
        external_data._download_to_cache(source.url, source, cache_path)

    assert not cache_path.exists()


def test_nontransient_http_error_is_not_retried(tmp_path, monkeypatch):
    source = make_source()
    requests = []

    def not_found(request, timeout):
        requests.append((request.full_url, timeout))
        raise urllib.error.HTTPError(request.full_url, 404, "not found", {}, None)

    monkeypatch.setattr(external_data.urllib.request, "urlopen", not_found)
    monkeypatch.setattr(
        external_data.time,
        "sleep",
        lambda *_args: pytest.fail("a permanent HTTP error must not be retried"),
    )

    with pytest.raises(external_data.ExternalDataError, match="Failed to download"):
        external_data._download_to_cache(source.url, source, tmp_path / "cache" / source.sha256)

    assert requests == [(source.url, 60)]


def test_cli_can_materialize_from_local_mirror_offline(tmp_path, capsys):
    payload = b"CLI payload"
    source = make_source(payload)
    manifest = tmp_path / "manifest.json"
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / source.filename).write_bytes(payload)
    write_manifest(manifest, (source,))
    destination = tmp_path / "destination"

    result = external_data.main(
        [
            "download",
            "--manifest",
            str(manifest),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--destination",
            str(destination),
            "--mirror",
            str(mirror),
            "--offline",
        ]
    )

    assert result == 0
    assert (destination / source.filename).read_bytes() == payload
    assert "mirror" in capsys.readouterr().out
