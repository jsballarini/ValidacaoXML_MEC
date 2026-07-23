"""Regras de negócio para Arquivo de Fiscalização."""

from __future__ import annotations

from lxml import etree

from validacao_xml.core.business_rules.base import (
    check_ambiente_juridico,
    find_signatures,
    is_juridically_valid,
)
from validacao_xml.core.models import Severity, ValidationIssue, ValidationOptions


def validate_fiscalizacao_rules(
    root: etree._Element,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues = check_ambiente_juridico(root, "FIS")
    if (not options.relax_homologacao or is_juridically_valid(root)) and not find_signatures(root):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                message="Arquivo de Fiscalização deve conter assinatura digital.",
                rule_id="FIS-SIG-001",
                layer="business",
            )
        )
    return issues
