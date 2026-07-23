"""Regras de negócio para Diploma Digital."""

from __future__ import annotations

import re

from lxml import etree

from validacao_xml.core.business_rules.base import (
    check_ambiente_juridico,
    element_path,
    find_signatures,
)
from validacao_xml.core.models import Severity, ValidationIssue, ValidationOptions


def validate_diploma_rules(
    root: etree._Element,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues = check_ambiente_juridico(root, "DIP")
    inf = root.find(".//{*}infDiploma")
    if inf is not None:
        doc_id = inf.get("id", "")
        if doc_id and not re.fullmatch(r"VDip[0-9]{44}", doc_id):
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        "Atributo id de infDiploma deve seguir o padrão "
                        "VDip + 44 dígitos numéricos (IN 2.2.2.1)."
                    ),
                    rule_id="DIP-ID-001",
                    xpath=element_path(inf),
                    layer="business",
                )
            )
    if not options.relax_homologacao or _is_production(root):
        sig_count = len(find_signatures(root))
        if sig_count == 0:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message="Diploma Digital deve conter ao menos uma assinatura digital.",
                    rule_id="DIP-SIG-001",
                    layer="business",
                )
            )
    return issues


def _is_production(root: etree._Element) -> bool:
    from validacao_xml.core.business_rules.base import is_juridically_valid

    return is_juridically_valid(root)
