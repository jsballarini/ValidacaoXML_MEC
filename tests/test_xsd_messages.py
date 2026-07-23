"""Testes de mensagens XSD humanizadas."""

from validacao_xml.core.xsd_messages import humanize_xsd_error, simplify_xsd_pattern


def test_simplify_lattes_pattern():
    assert simplify_xsd_pattern(r"https://lattes\.cnpq\.br/\d+") == "https://lattes.cnpq.br/[números]"


def test_humanize_lattes_pattern_error():
    raw = (
        "Element '{https://portal.mec.gov.br/diplomadigital/arquivos-em-xsd}Lattes': "
        "[facet 'pattern'] The value 'http://lattes.cnpq.br/0518139208464605' "
        "is not accepted by the pattern 'https://lattes\\.cnpq\\.br/\\d+'."
    )
    msg = humanize_xsd_error(raw)
    assert "Campo 'Lattes'" in msg
    assert "https://lattes.cnpq.br/[números]" in msg
    assert "http://" in msg
    assert "exige https://" in msg
    assert r"\." not in msg
