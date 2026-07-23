"""Orquestrador de regras de negócio por tipo de documento."""

from __future__ import annotations

from lxml import etree

from validacao_xml.core.business_rules.base import check_strict_formatting
from validacao_xml.core.business_rules.curriculo import validate_curriculo_rules
from validacao_xml.core.business_rules.diploma import validate_diploma_rules
from validacao_xml.core.business_rules.doc_academica import validate_doc_academica_rules
from validacao_xml.core.business_rules.fiscalizacao import validate_fiscalizacao_rules
from validacao_xml.core.business_rules.historico import validate_historico_rules
from validacao_xml.core.business_rules.lista_anulados import validate_lista_anulados_rules
from validacao_xml.core.models import DocumentType, ValidationIssue, ValidationOptions

RuleFn = type(validate_diploma_rules)


RULES_BY_TYPE: dict[DocumentType, RuleFn] = {
    DocumentType.DIPLOMA: validate_diploma_rules,
    DocumentType.DOC_ACADEMICA: validate_doc_academica_rules,
    DocumentType.HISTORICO: validate_historico_rules,
    DocumentType.CURRICULO: validate_curriculo_rules,
    DocumentType.LISTA_ANULADOS: validate_lista_anulados_rules,
    DocumentType.FISCALIZACAO: validate_fiscalizacao_rules,
}


def apply_business_rules(
    doc_type: DocumentType,
    root: etree._Element,
    xml_path: str,
    options: ValidationOptions,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if options.strict_formatting:
        issues.extend(check_strict_formatting(xml_path))
    rule_fn = RULES_BY_TYPE.get(doc_type)
    if rule_fn:
        issues.extend(rule_fn(root, options))
    return issues
