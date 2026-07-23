"""Testes do download de certificados ICP-Brasil."""

from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from validacao_xml.core.signature.icp_brasil import load_trusted_certificates
from scripts.download_icp_certs import download_icp_certificates


def test_download_icp_certificates(tmp_path: Path):
    downloaded, failed = download_icp_certificates(tmp_path)
    assert downloaded
    assert not failed
    for name in downloaded:
        pem = tmp_path / name
        assert pem.exists()
        cert = x509.load_pem_x509_certificate(pem.read_bytes(), default_backend())
        assert "ICP-Brasil" in cert.subject.rfc4514_string()


def test_load_bundled_icp_if_present():
    certs = load_trusted_certificates()
    if not certs:
        return
    assert all("ICP-Brasil" in c.subject.rfc4514_string() for c in certs)
