"""Regras de negócio para Documentação Acadêmica."""

from __future__ import annotations

import re

from lxml import etree

from validacao_xml.core.business_rules.base import (
    check_ambiente_juridico,
    element_path,
    find_signatures,
    is_juridically_valid,
)
from validacao_xml.core.models import Severity, ValidationIssue, ValidationOptions

MIN_SIGNATURES = 3


def validate_doc_academica_rules(
    root: etree._Element,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues = check_ambiente_juridico(root, "DOC")
    inf = root.find(".//{*}RegistroReq") or root.find(".//{*}infRegistroReq")
    if inf is None:
        for elem in root.iter():
            if elem.get("id", "").startswith("ReqDip"):
                inf = elem
                break
    if inf is not None:
        doc_id = inf.get("id", "")
        if doc_id and not re.fullmatch(r"ReqDip[0-9]{44}", doc_id):
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        "Atributo id deve seguir o padrão ReqDip + 44 dígitos "
                        "numéricos."
                    ),
                    rule_id="DOC-ID-001",
                    xpath=element_path(inf),
                    layer="business",
                )
            )

    signatures = find_signatures(root)
    if not options.relax_homologacao or is_juridically_valid(root):
        if len(signatures) < MIN_SIGNATURES:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        f"Documentação Acadêmica deve ter ao menos {MIN_SIGNATURES} "
                        f"assinaturas (1 PF + 2 PJ) — encontradas: {len(signatures)} "
                        "(IN 3.6)."
                    ),
                    rule_id="DOC-SIG-001",
                    layer="business",
                )
            )
    return issues
