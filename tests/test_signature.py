"""Testes do verificador de assinaturas."""

from pathlib import Path

from lxml import etree

from validacao_xml.core.business_rules.base import find_signatures
from validacao_xml.core.models import ValidationOptions
from validacao_xml.core.signature.verifier import verify_signatures

FIXTURES = Path(__file__).parent / "fixtures"
EXAMPLES = Path(__file__).resolve().parents[1] / "exemplos"


def _load(name: str) -> etree._Element:
    return etree.parse(str(FIXTURES / name)).getroot()


def test_no_signatures_warning():
    root = _load("diploma_homologacao.xml")
    assert len(find_signatures(root)) == 0
    issues = verify_signatures(root, ValidationOptions())
    assert any(i.rule_id == "SIG-000" for i in issues)


def test_skip_signatures():
    root = _load("diploma_homologacao.xml")
    issues = verify_signatures(root, ValidationOptions(skip_signatures=True))
    assert issues == []


def test_relax_homologacao_skips_crypto_verification():
    diploma = EXAMPLES / "63918690552035173275109456493267453396054534_Diploma.xml"
    if not diploma.exists():
        return
    root = etree.parse(str(diploma)).getroot()
    assert len(find_signatures(root)) > 0
    issues = verify_signatures(root, ValidationOptions(relax_homologacao=True))
    assert len(issues) == 1
    assert issues[0].rule_id == "SIG-RELAX"
    assert issues[0].severity.value == "info"
