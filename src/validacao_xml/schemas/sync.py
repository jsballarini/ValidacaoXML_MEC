"""Sincronização de esquemas XSD com o portal MEC."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from validacao_xml.config import (
    get_bundled_schemas_dir,
    get_manifest_path,
    get_schema_cache_dir,
)

HTTP_HEADERS = {
    "User-Agent": "ValidacaoXML/0.1.0 (schema-sync; Perseus)",
}


@dataclass
class SchemaSyncResult:
    updated_files: list[str]
    failed_files: list[str]
    cache_dir: Path
    schema_version: str
    last_sync: str
    used_bundled_fallback: bool = False

    @property
    def success(self) -> bool:
        return not self.failed_files


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest() -> dict[str, Any]:
    path = get_manifest_path()
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_cache_from_bundled() -> Path:
    """Copia esquemas embutidos para o cache se ainda não existirem."""
    cache = get_schema_cache_dir()
    bundled = get_bundled_schemas_dir()
    marker = cache / ".initialized"
    if marker.exists() and any(cache.glob("*.xsd")):
        return cache
    cache.mkdir(parents=True, exist_ok=True)
    for xsd in bundled.glob("*.xsd"):
        shutil.copy2(xsd, cache / xsd.name)
    manifest = load_manifest()
    (cache / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    marker.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
    return cache


def _looks_like_xsd(content: bytes) -> bool:
    if not content.strip().startswith(b"<?xml"):
        return False
    sample = content[:4000].lower()
    if b"<html" in sample or b"captcha" in sample:
        return False
    return b"schema" in sample


def _fetch_remote_xsd(client: httpx.Client, url: str) -> bytes:
    response = client.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    if _looks_like_xsd(response.content):
        return response.content
    raise ValueError("Resposta não parece ser um arquivo XSD válido")


def sync_schemas(force: bool = False) -> SchemaSyncResult:
    """Atualiza esquemas no cache local comparando hash com o MEC."""
    cache = ensure_cache_from_bundled()
    manifest = load_manifest()
    updated: list[str] = []
    failed: list[str] = []
    used_fallback = False

    with httpx.Client(headers=HTTP_HEADERS) as client:
        for entry in manifest.get("files", []):
            filename = entry["filename"]
            url = entry["url"]
            dest = cache / filename
            expected = entry.get("sha256", "")

            if dest.exists() and not force:
                local_hash = sha256_file(dest)
                if expected and local_hash == expected:
                    continue

            try:
                data = _fetch_remote_xsd(client, url)
                new_hash = hashlib.sha256(data).hexdigest()
                dest.write_bytes(data)
                updated.append(filename)
                entry["sha256"] = new_hash
            except Exception:
                if not dest.exists():
                    bundled = get_bundled_schemas_dir() / filename
                    if bundled.exists():
                        shutil.copy2(bundled, dest)
                        used_fallback = True
                    else:
                        failed.append(filename)
                else:
                    failed.append(filename)

    manifest["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    (cache / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (cache / ".last_sync").write_text(
        datetime.now(timezone.utc).isoformat(),
        encoding="utf-8",
    )
    normalized = cache / ".normalized"
    if normalized.exists():
        shutil.rmtree(normalized, ignore_errors=True)

    return SchemaSyncResult(
        updated_files=updated,
        failed_files=failed,
        cache_dir=cache,
        schema_version=manifest.get("schema_version", "v1.05"),
        last_sync=datetime.now(timezone.utc).isoformat(),
        used_bundled_fallback=used_fallback,
    )


def get_active_schema_dir() -> Path:
    """Retorna diretório de esquemas ativo (cache ou bundled)."""
    cache = ensure_cache_from_bundled()
    if any(cache.glob("*.xsd")):
        return cache
    return get_bundled_schemas_dir()


def get_schema_status() -> dict[str, Any]:
    cache = ensure_cache_from_bundled()
    manifest_path = cache / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else load_manifest()
    last_sync_path = cache / ".last_sync"
    last_sync = last_sync_path.read_text(encoding="utf-8").strip() if last_sync_path.exists() else ""
    return {
        "schema_version": manifest.get("schema_version", "v1.05"),
        "cache_dir": str(cache),
        "file_count": len(list(cache.glob("*.xsd"))),
        "last_sync": last_sync,
    }


def resolve_primary_xsd(root_element: str) -> Path | None:
    manifest = load_manifest()
    schema_dir = get_active_schema_dir()
    for entry in manifest.get("files", []):
        if entry.get("root_element") == root_element and entry.get("primary"):
            path = schema_dir / entry["filename"]
            if path.exists():
                return path
    return None
