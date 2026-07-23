"""Testes do detector de tipo de documento."""

from pathlib import Path

import pytest

from validacao_xml.core.detector import detect_document
from validacao_xml.core.models import DocumentType

FIXTURES = Path(__file__).parent / "fixtures"


def test_detect_diploma_homologacao():
    doc_type, root_name, _ = detect_document(FIXTURES / "diploma_homologacao.xml")
    assert doc_type == DocumentType.DIPLOMA
    assert root_name == "Diploma"


def test_detect_unknown_root():
    doc_type, root_name, _ = detect_document(FIXTURES / "unknown_root.xml")
    assert doc_type == DocumentType.UNKNOWN
    assert root_name == "Desconhecido"


def test_malformed_xml_raises():
    with pytest.raises(Exception):
        detect_document(FIXTURES / "malformed.xml")
