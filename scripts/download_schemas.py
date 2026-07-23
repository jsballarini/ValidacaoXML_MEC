"""Script para baixar XSDs oficiais do MEC e popular o bundle offline."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import httpx

MEC_BASE = "https://www.gov.br/mec/pt-br/diploma-digital/documentos"

# slug Plone -> nome do arquivo XSD
XSD_FILES: dict[str, str] = {
    "diplomadigital_v1-05.xsd": "DiplomaDigital_v1.05.xsd",
    "documentacaoacademicaregistrodiplomadigital_v1-05.xsd": "DocumentacaoAcademicaRegistroDiplomaDigital_v1.05.xsd",
    "historicoescolardigital_v1-05.xsd": "HistoricoEscolarDigital_v1.05.xsd",
    "curriculoescolardigital_v1-05.xsd": "CurriculoEscolarDigital_v1.05.xsd",
    "listadiplomasanulados_v1-05.xsd": "ListaDiplomasAnulados_v1.05.xsd",
    "arquivofiscalizacao_v1-05.xsd": "ArquivoFiscalizacao_v1.05.xsd",
    "tiposbasicos_v1-05.xsd": "tiposBasicos_v1.05.xsd",
    "leiautediplomadigital_v1-05.xsd": "leiauteDiplomaDigital_v1.05.xsd",
    "leiautedocumentacaoacademicaregistrodiplomadigital_v1-05.xsd": "leiauteDocumentacaoAcademicaRegistroDiplomaDigital_v1.05.xsd",
    "leiautehistoricoescolar_v1-05.xsd": "leiauteHistoricoEscolar_v1.05.xsd",
    "leiautelistadiplomasanulados_v1-05.xsd": "leiauteListaDiplomasAnulados_v1.05.xsd",
    "leiautearquivofiscalizacao_v1-05.xsd": "leiauteArquivoFiscalizacao_v1.05.xsd",
    "leiautecurriculoescolar_v1-05.xsd": "leiauteCurriculoEscolar_v1.05.xsd",
    "xmldsig-core-schema_v1-1.xsd": "xmldsig-core-schema_v1.1.xsd",
}

ROOT_ELEMENTS: dict[str, str] = {
    "DiplomaDigital_v1.05.xsd": "Diploma",
    "DocumentacaoAcademicaRegistroDiplomaDigital_v1.05.xsd": "DocumentacaoAcademicaRegistro",
    "HistoricoEscolarDigital_v1.05.xsd": "HistoricoEscolar",
    "CurriculoEscolarDigital_v1.05.xsd": "CurriculoEscolar",
    "ListaDiplomasAnulados_v1.05.xsd": "ListaDiplomasAnulados",
    "ArquivoFiscalizacao_v1.05.xsd": "ArquivoFiscalizacao",
}

PRIMARY_SCHEMAS = set(ROOT_ELEMENTS.keys())


def download_url(slug: str, filename: str) -> str:
    return f"{MEC_BASE}/{slug}/@@download/file/{filename}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_xsd_content(html_or_xml: str) -> str | None:
    """Extrai XSD de página de visualização gov.br quando download falha."""
    match = re.search(r"```\s*(<\?xml.*?</xs:schema>)\s*```", html_or_xml, re.DOTALL)
    if match:
        return match.group(1).strip()
    if html_or_xml.strip().startswith("<?xml") and "<xs:schema" in html_or_xml:
        start = html_or_xml.find("<?xml")
        end = html_or_xml.rfind("</xs:schema>") + len("</xs:schema>")
        if end > start:
            return html_or_xml[start:end]
    return None


def _looks_like_xsd(content: bytes) -> bool:
    if not content.strip().startswith(b"<?xml"):
        return False
    sample = content[:4000].lower()
    if b"<html" in sample or b"captcha" in sample:
        return False
    return b"schema" in sample


def fetch_xsd(client: httpx.Client, slug: str, filename: str) -> bytes:
    url = download_url(slug, filename)
    response = client.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    content = response.content
    if _looks_like_xsd(content):
        return content
    text = response.text
    extracted = extract_xsd_content(text)
    if extracted:
        return extracted.encode("utf-8")
    view_url = f"{MEC_BASE}/{slug}/view"
    view_resp = client.get(view_url, follow_redirects=True, timeout=60.0)
    view_resp.raise_for_status()
    extracted = extract_xsd_content(view_resp.text)
    if extracted:
        return extracted.encode("utf-8")
    raise RuntimeError(f"Não foi possível obter XSD: {filename}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    bundled_dir = root / "src" / "validacao_xml" / "schemas" / "bundled"
    bundled_dir.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict] = []
    headers = {"User-Agent": "ValidacaoXML/0.1.0 (schema-sync; +https://github.com/perseus)"}

    with httpx.Client(headers=headers) as client:
        for slug, filename in XSD_FILES.items():
            print(f"Baixando {filename}...")
            data = fetch_xsd(client, slug, filename)
            dest = bundled_dir / filename
            dest.write_bytes(data)
            entry = {
                "filename": filename,
                "slug": slug,
                "url": download_url(slug, filename),
                "sha256": sha256_bytes(data),
                "primary": filename in PRIMARY_SCHEMAS,
            }
            if filename in ROOT_ELEMENTS:
                entry["root_element"] = ROOT_ELEMENTS[filename]
            manifest_entries.append(entry)
            print(f"  OK ({len(data)} bytes, sha256={entry['sha256'][:12]}...)")

    manifest = {
        "schema_version": "v1.05",
        "updated_at": "2026-07-22",
        "source": MEC_BASE,
        "files": manifest_entries,
    }
    manifest_path = root / "src" / "validacao_xml" / "schemas" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest gravado em {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
