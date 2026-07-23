"""Testes de regras de negócio."""

from pathlib import Path

from lxml import etree

from validacao_xml.core.business_rules.base import check_ambiente_juridico, check_strict_formatting
from validacao_xml.core.business_rules.diploma import validate_diploma_rules
from validacao_xml.core.models import ValidationOptions

FIXTURES = Path(__file__).parent / "fixtures"
NS = {"m": "https://portal.mec.gov.br/diplomadigital/arquivos-em-xsd"}


def _load(name: str) -> etree._Element:
    return etree.parse(str(FIXTURES / name)).getroot()


def test_ambiente_homologacao_warning():
    root = _load("diploma_homologacao.xml")
    issues = check_ambiente_juridico(root, "DIP")
    assert len(issues) == 1
    assert "Homologação" in issues[0].message


def test_diploma_invalid_id():
    root = _load("diploma_invalid_id.xml")
    issues = validate_diploma_rules(root, ValidationOptions(relax_homologacao=True))
    assert any(i.rule_id == "DIP-ID-001" for i in issues)


def test_strict_formatting_detects_comments(tmp_path):
    xml = tmp_path / "with_comment.xml"
    xml.write_text(
        '<?xml version="1.0"?><root><!-- comment --><a>1</a></root>',
        encoding="utf-8",
    )
    issues = check_strict_formatting(xml)
    assert any(i.rule_id == "FMT-001" for i in issues)
