"""Baixa certificados raiz ICP-Brasil para bundle offline."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

# Repositório oficial AC-Raiz (ITI / ICP-Brasil)
# https://www.gov.br/iti/pt-br/assuntos/repositorio/repositorio-ac-raiz
ICP_RAIZ_BASE = "https://acraiz.icpbrasil.gov.br/credenciadas/RAIZ"

ICP_ROOT_URLS = [
    ("icp_brasil_v10.pem", f"{ICP_RAIZ_BASE}/ICP-Brasilv10.crt"),
    ("icp_brasil_v5.pem", f"{ICP_RAIZ_BASE}/ICP-Brasilv5.crt"),
    ("icp_brasil_v13.pem", f"{ICP_RAIZ_BASE}/ICP-Brasilv13.crt"),
]


def _to_pem(content: bytes) -> bytes:
    if b"BEGIN CERTIFICATE" in content:
        return content
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import Encoding

    cert = x509.load_der_x509_certificate(content, default_backend())
    return cert.public_bytes(Encoding.PEM)


def download_icp_certificates(dest_dir: Path) -> tuple[list[str], list[str]]:
    """Baixa certificados raiz. Retorna (sucesso, falhas)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[str] = []
    failed: list[str] = []

    headers = {"User-Agent": "ValidacaoXML/0.1.0"}
    # acraiz.icpbrasil.gov.br pode falhar verificação TLS com CA padrão do SO.
    with httpx.Client(headers=headers, follow_redirects=True, timeout=60, verify=False) as client:
        for filename, url in ICP_ROOT_URLS:
            print(f"Baixando {filename}...")
            try:
                resp = client.get(url)
                resp.raise_for_status()
                content = _to_pem(resp.content)
                (dest_dir / filename).write_bytes(content)
                downloaded.append(filename)
                print(f"  OK ({len(content)} bytes)")
            except Exception as exc:
                failed.append(filename)
                print(f"  FALHA: {exc}")

    return downloaded, failed


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    dest_dir = root / "resources" / "icp_brasil"

    downloaded, failed = download_icp_certificates(dest_dir)

    if not downloaded and not any(dest_dir.glob("*.pem")) and not any(dest_dir.glob("*.crt")):
        print("Nenhum certificado baixado — criando placeholder README.")
        (dest_dir / "README.txt").write_text(
            "Coloque certificados raiz ICP-Brasil (.pem) neste diretório.\n"
            "Fonte: https://www.gov.br/iti/pt-br/assuntos/repositorio/repositorio-ac-raiz\n",
            encoding="utf-8",
        )
        return 1

    if failed:
        print(f"Aviso: {len(failed)} certificado(s) não baixado(s): {', '.join(failed)}")
    return 0 if downloaded else 0


if __name__ == "__main__":
    sys.exit(main())
