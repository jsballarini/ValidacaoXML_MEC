"""Testes do pipeline de validação."""

from pathlib import Path

from validacao_xml.core.models import DocumentType, ValidationOptions
from validacao_xml.core.pipeline import ValidationPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def test_malformed_xml():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(FIXTURES / "malformed.xml")
    assert not result.is_valid
    assert any(i.rule_id == "XML-001" for i in result.issues)


def test_unknown_document():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(FIXTURES / "unknown_root.xml")
    assert not result.is_valid
    assert result.document_type == DocumentType.UNKNOWN


def test_diploma_homologacao_warning():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(
        FIXTURES / "diploma_homologacao.xml",
        ValidationOptions(relax_homologacao=True),
    )
    assert result.document_type == DocumentType.DIPLOMA
    assert any("validade jurídica" in i.message.lower() for i in result.warnings + result.infos)


def test_diploma_invalid_id_business_rule():
    pipeline = ValidationPipeline()
    result = pipeline.validate_file(
        FIXTURES / "diploma_invalid_id.xml",
        ValidationOptions(relax_homologacao=True, skip_signatures=True),
    )
    assert any(i.rule_id == "DIP-ID-001" for i in result.issues)
