"""Verificação de assinaturas digitais XMLDSig/XAdES."""

from __future__ import annotations

import base64

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from lxml import etree
from signxml import XMLVerifier
from signxml.exceptions import InvalidSignature

from validacao_xml.core.business_rules.base import find_signatures
from validacao_xml.core.detector import local_name
from validacao_xml.core.models import (
    Severity,
    SignatureStatus,
    ValidationIssue,
    ValidationOptions,
)
from validacao_xml.core.signature.icp_brasil import (
    certificate_validity_status,
    get_certificate_type,
    is_icp_brasil_certificate,
    is_pessoa_fisica,
    is_pessoa_juridica,
    load_trusted_certificates,
    verify_chain_to_trust_store,
)
from validacao_xml.core.signature.policies import ARCHIVE_POLICIES


def _extract_x509_certificates(signature_elem: etree._Element) -> list[x509.Certificate]:
    certs: list[x509.Certificate] = []
    for cert_node in signature_elem.iter():
        if local_name(cert_node.tag) != "X509Certificate" or not cert_node.text:
            continue
        try:
            der = base64.b64decode(cert_node.text.strip())
            certs.append(x509.load_der_x509_certificate(der, default_backend()))
        except Exception:
            continue
    return certs


def _get_signature_policy_oid(signature_elem: etree._Element) -> str | None:
    for elem in signature_elem.iter():
        tag = local_name(elem.tag)
        if tag == "Identifier" and elem.text:
            text = elem.text.strip()
            if text.startswith("2.16."):
                return text
    return None


def verify_signatures(
    root: etree._Element,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    signatures = find_signatures(root)
    if not signatures:
        if not options.skip_signatures:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    message="Nenhuma assinatura digital XMLDSig encontrada no documento.",
                    rule_id="SIG-000",
                    layer="signature",
                )
            )
        return issues

    if options.relax_homologacao:
        issues.append(
            ValidationIssue(
                severity=Severity.INFO,
                message=(
                    f"{len(signatures)} assinatura(s) digital(is) encontrada(s); "
                    "verificação criptográfica omitida (modo homologação)."
                ),
                rule_id="SIG-RELAX",
                layer="signature",
            )
        )
        return issues

    trust_store = load_trusted_certificates()
    doc_root = _find_document_root(signatures[0])

    for index, sig_elem in enumerate(signatures, start=1):
        status, detail = _verify_single_signature(doc_root, sig_elem, trust_store)
        severity = _status_to_severity(status)
        issues.append(
            ValidationIssue(
                severity=severity,
                message=f"Assinatura #{index}: {status.value} — {detail}",
                rule_id=f"SIG-{index:03d}",
                layer="signature",
                details={"status": status.value, "index": index},
            )
        )
    return issues


def _verify_single_signature(
    doc_root: etree._Element,
    sig_elem: etree._Element,
    trust_store: list[x509.Certificate],
) -> tuple[SignatureStatus, str]:
    certs = _extract_x509_certificates(sig_elem)
    if not certs:
        return SignatureStatus.REJECTED, "Certificado X509 não encontrado na assinatura."

    signer = certs[0]
    details: list[str] = []
    crypto_ok = False

    try:
        XMLVerifier().verify(doc_root, x509_cert=signer)
        crypto_ok = True
        details.append("Integridade criptográfica OK")
    except InvalidSignature as exc:
        details.append(f"Integridade não confirmada offline: {exc}")
    except Exception as exc:
        details.append(f"Verificação criptográfica inconclusiva: {_format_crypto_error(exc)}")

    validity = certificate_validity_status(signer)
    if validity == "expired":
        details.append("Certificado expirado")

    if is_icp_brasil_certificate(signer):
        details.append("Certificado ICP-Brasil identificado")
    elif not verify_chain_to_trust_store(signer, trust_store):
        return SignatureStatus.REJECTED, "Certificado não pertence à ICP-Brasil."

    cert_type = get_certificate_type(signer)
    entity = "PJ" if is_pessoa_juridica(signer) else ("PF" if is_pessoa_fisica(signer) else "?")
    details.append(f"Tipo: {cert_type}, Entidade: {entity}")

    policy = _get_signature_policy_oid(sig_elem)
    if policy:
        details.append(f"Política: {policy}")
        if policy in ARCHIVE_POLICIES:
            details.append("Política de arquivamento AD-RA detectada")

    if crypto_ok:
        return SignatureStatus.APPROVED, "; ".join(details)

    if is_icp_brasil_certificate(signer) or verify_chain_to_trust_store(signer, trust_store):
        return SignatureStatus.INDETERMINATE, "; ".join(details)

    return SignatureStatus.REJECTED, "; ".join(details)


def _format_crypto_error(exc: Exception) -> str:
    message = str(exc)
    if "signxml" in message and "schema" in message.lower():
        return (
            "recursos internos de verificação XMLDSig ausentes no executável "
            "(signxml/schemas). Reconstrua o aplicativo com build_exe.ps1."
        )
    if isinstance(exc, FileNotFoundError):
        return f"arquivo necessário não encontrado: {exc.filename or message}"
    return message


def _find_document_root(elem: etree._Element) -> etree._Element:
    current: etree._Element | None = elem
    while current is not None and current.getparent() is not None:
        current = current.getparent()
    return current if current is not None else elem


def _status_to_severity(status: SignatureStatus) -> Severity:
    if status == SignatureStatus.REJECTED:
        return Severity.ERROR
    if status == SignatureStatus.INDETERMINATE:
        return Severity.WARNING
    return Severity.INFO
