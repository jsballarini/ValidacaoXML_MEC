"""Utilitários compartilhados para regras de negócio."""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from validacao_xml.core.detector import get_inf_element, local_name
from validacao_xml.core.models import Severity, ValidationIssue

PRODUCTION_ENV = "Produção"


def element_path(elem: etree._Element) -> str:
    parts: list[str] = []
    current: etree._Element | None = elem
    while current is not None:
        parts.append(local_name(current.tag))
        current = current.getparent()
    return "/" + "/".join(reversed(parts))


def check_ambiente_juridico(
    root: etree._Element,
    rule_prefix: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    inf = get_inf_element(root)
    if inf is None:
        return issues
    ambiente = inf.get("ambiente", PRODUCTION_ENV)
    if ambiente != PRODUCTION_ENV:
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                message=(
                    f"Documento emitido em ambiente '{ambiente}' — "
                    "não possui validade jurídica (IN v1.05)."
                ),
                rule_id=f"{rule_prefix}-AMB-001",
                xpath=element_path(inf),
                layer="business",
                details={"ambiente": ambiente, "juridically_valid": False},
            )
        )
    return issues


def check_strict_formatting(xml_path: Path | str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    raw = Path(xml_path).read_bytes()
    text = raw.decode("utf-8", errors="replace")

    if "<!--" in text:
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                message="XML contém comentários (vedado pela IN 1.2.2 III).",
                rule_id="FMT-001",
                layer="business",
            )
        )
    if re.search(r">\s+<", text):
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                message="XML contém espaços entre tags (vedado pela IN 1.2.2 V).",
                rule_id="FMT-002",
                layer="business",
            )
        )
    if "\n" in text or "\r" in text or "\t" in text:
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                message="XML contém caracteres de formatação (vedado pela IN 1.2.2 V).",
                rule_id="FMT-003",
                layer="business",
            )
        )
    return issues


def find_signatures(root: etree._Element) -> list[etree._Element]:
    """Localiza assinaturas XMLDSig independentemente do prefixo/namespace."""
    signatures: list[etree._Element] = []
    for elem in root.iter():
        if local_name(elem.tag) == "Signature":
            signatures.append(elem)
    return signatures


def is_juridically_valid(root: etree._Element) -> bool:
    inf = get_inf_element(root)
    if inf is None:
        return True
    return inf.get("ambiente", PRODUCTION_ENV) == PRODUCTION_ENV
