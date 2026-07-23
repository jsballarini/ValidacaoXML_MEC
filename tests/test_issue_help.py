"""Testes dos textos de ajuda da interface."""

from validacao_xml.core.models import Severity, ValidationIssue
from validacao_xml.gui.issue_help import get_issue_explanation


def test_lattes_explanation():
    issue = ValidationIssue(
        severity=Severity.ERROR,
        message=(
            "Campo 'Lattes': valor 'http://lates.cnpq.br/00000' "
            "não atende ao formato exigido 'https://lattes.cnpq.br/[números]'."
        ),
        rule_id="XSD-004",
        layer="xsd",
    )
    text = get_issue_explanation(issue)
    assert "TLattes" in text
    assert "https://lattes.cnpq.br" in text


def test_rule_id_explanation():
    issue = ValidationIssue(
        severity=Severity.WARNING,
        message="Nenhuma assinatura digital XMLDSig encontrada no documento.",
        rule_id="SIG-000",
        layer="signature",
    )
    text = get_issue_explanation(issue)
    assert "XMLDSig" in text
    assert "SIG-000" in text
