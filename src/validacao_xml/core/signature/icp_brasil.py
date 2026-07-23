"""Utilitários para cadeia de certificados ICP-Brasil."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding

from validacao_xml.config import get_bundled_icp_dir
from validacao_xml.core.signature.policies import ICP_BRASIL_OIDS


def get_icp_ca_dir() -> Path:
    path = get_bundled_icp_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_trusted_certificates() -> list[x509.Certificate]:
    ca_dir = get_icp_ca_dir()
    certs: list[x509.Certificate] = []
    for cert_file in sorted(ca_dir.glob("*.pem")) + sorted(ca_dir.glob("*.crt")):
        cert = _load_certificate_file(cert_file)
        if cert is not None:
            certs.append(cert)
    return certs


def _load_certificate_file(path: Path) -> x509.Certificate | None:
    data = path.read_bytes()
    try:
        return x509.load_pem_x509_certificate(data, default_backend())
    except Exception:
        pass
    try:
        return x509.load_der_x509_certificate(data, default_backend())
    except Exception:
        return None


def certificate_to_pem(cert: x509.Certificate) -> bytes:
    return cert.public_bytes(Encoding.PEM)


def is_icp_brasil_certificate(cert: x509.Certificate) -> bool:
    try:
        for ext in cert.extensions:
            if ext.oid.dotted_string.startswith("2.16.76."):
                return True
    except Exception:
        pass
    subject = cert.subject.rfc4514_string()
    return "ICP-Brasil" in subject or "AC " in subject or "Autoridade Certificadora" in subject


def get_certificate_type(cert: x509.Certificate) -> str:
    try:
        for ext in cert.extensions:
            oid = ext.oid.dotted_string
            for prefix, cert_type in ICP_BRASIL_OIDS.items():
                if oid.startswith(prefix):
                    return cert_type
    except Exception:
        pass
    return "Desconhecido"


def is_pessoa_juridica(cert: x509.Certificate) -> bool:
    subject = cert.subject.rfc4514_string().upper()
    return "CNPJ" in subject or ":PJ" in subject or "OU=PJ" in subject


def is_pessoa_fisica(cert: x509.Certificate) -> bool:
    subject = cert.subject.rfc4514_string().upper()
    return "CPF" in subject or ":PF" in subject or "OU=PF" in subject


def certificate_validity_status(cert: x509.Certificate) -> str:
    now = datetime.now(timezone.utc)
    not_before = cert.not_valid_before_utc if hasattr(cert, "not_valid_before_utc") else cert.not_valid_before.replace(tzinfo=timezone.utc)
    not_after = cert.not_valid_after_utc if hasattr(cert, "not_valid_after_utc") else cert.not_valid_after.replace(tzinfo=timezone.utc)
    if now < not_before:
        return "not_yet_valid"
    if now > not_after:
        return "expired"
    return "valid"


def verify_chain_to_trust_store(
    cert: x509.Certificate,
    trust_store: list[x509.Certificate],
) -> bool:
    """Verifica se o emissor está na trust store ou se é autoassinado confiável."""
    if cert in trust_store:
        return True
    issuer = cert.issuer.rfc4514_string()
    subject = cert.subject.rfc4514_string()
    for trusted in trust_store:
        if trusted.subject.rfc4514_string() == issuer:
            return True
        if trusted.subject.rfc4514_string() == subject and trusted.subject == trusted.issuer:
            return True
    return is_icp_brasil_certificate(cert)
