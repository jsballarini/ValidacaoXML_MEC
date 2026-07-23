"""Regras de negócio para Lista de Diplomas Anulados."""

from __future__ import annotations

from lxml import etree

from validacao_xml.core.business_rules.base import (
    check_ambiente_juridico,
    find_signatures,
    is_juridically_valid,
)
from validacao_xml.core.models import Severity, ValidationIssue, ValidationOptions


def validate_lista_anulados_rules(
    root: etree._Element,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues = check_ambiente_juridico(root, "LST")
    if (not options.relax_homologacao or is_juridically_valid(root)) and not find_signatures(root):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                message="Lista de Diplomas Anulados deve conter assinatura digital.",
                rule_id="LST-SIG-001",
                layer="business",
            )
        )
    return issues
