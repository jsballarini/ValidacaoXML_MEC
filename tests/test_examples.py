"""Testes com exemplos reais de Histórico Escolar."""

from pathlib import Path

from lxml import etree

from validacao_xml.core.business_rules.base import find_signatures
from validacao_xml.core.models import ValidationOptions
from validacao_xml.core.pipeline import ValidationPipeline

EXAMPLES = Path(__file__).resolve().parents[1] / "exemplos"


def test_unsigned_historico_reports_missing_signature():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(EXAMPLES / "407_Historico NÃO ASSINADO.xml")
    root = etree.parse(str(EXAMPLES / "407_Historico NÃO ASSINADO.xml")).getroot()
    assert any(i.rule_id == "HIS-SIG-001" for i in result.issues)
    assert any(i.rule_id == "SIG-000" for i in result.issues)
    assert not find_signatures(root)


def test_signed_historico_detects_signatures():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(
        EXAMPLES / "393_Historico ASSINADO.xml",
        ValidationOptions(skip_signatures=False),
    )
    root = etree.parse(str(EXAMPLES / "393_Historico ASSINADO.xml")).getroot()
    sig_issues = [i for i in result.issues if i.layer == "signature"]
    assert len(find_signatures(root)) == 2
    assert len(sig_issues) >= 2
    assert not any(i.rule_id == "SIG-000" for i in sig_issues)
    assert not any(i.rule_id == "XSD-002" for i in result.issues)


def test_xsd_schema_loads_for_historico():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(EXAMPLES / "407_Historico NÃO ASSINADO.xml")
    assert not any(i.rule_id == "XSD-002" for i in result.issues)
