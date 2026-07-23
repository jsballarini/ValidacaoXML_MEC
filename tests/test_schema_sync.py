"""Testes de sincronização de esquemas."""

from validacao_xml.schemas.sync import (
    ensure_cache_from_bundled,
    get_active_schema_dir,
    get_schema_status,
    load_manifest,
)


def test_manifest_has_14_files():
    manifest = load_manifest()
    assert manifest["schema_version"] == "v1.05"
    assert len(manifest["files"]) == 14


def test_ensure_cache_from_bundled():
    cache = ensure_cache_from_bundled()
    assert cache.exists()
    assert len(list(cache.glob("*.xsd"))) >= 14


def test_get_active_schema_dir():
    schema_dir = get_active_schema_dir()
    assert (schema_dir / "DiplomaDigital_v1.05.xsd").exists()


def test_schema_status():
    status = get_schema_status()
    assert status["file_count"] >= 14
    assert "cache_dir" in status
