"""Normalização de namespaces entre especificação MEC, libxml2 e documentos reais."""

from __future__ import annotations

from lxml import etree

MEC_NAMESPACE_HTTPS = "https://portal.mec.gov.br/diplomadigital/arquivos-em-xsd"
MEC_NAMESPACE_HTTP = "http://portal.mec.gov.br/diplomadigital/arquivos-em-xsd"

XMLDSIG_NAMESPACE_HTTPS = "https://www.w3.org/2000/09/xmldsig#"
XMLDSIG_NAMESPACE_HTTP = "http://www.w3.org/2000/09/xmldsig#"

MEC_NAMESPACE_ALIASES = {MEC_NAMESPACE_HTTPS, MEC_NAMESPACE_HTTP}

W3C_XSD_HTTPS = "https://www.w3.org/2001/XMLSchema"
W3C_XSD_HTTP = "http://www.w3.org/2001/XMLSchema"


def normalize_xsd_bytes(content: bytes) -> bytes:
    """Converte namespaces W3C https->http para compatibilidade com libxml2."""
    text = content.decode("utf-8")
    text = text.replace(W3C_XSD_HTTPS, W3C_XSD_HTTP)
    text = text.replace(XMLDSIG_NAMESPACE_HTTPS, XMLDSIG_NAMESPACE_HTTP)
    return text.encode("utf-8")


def normalize_xsd_text(text: str) -> str:
    return normalize_xsd_bytes(text.encode("utf-8")).decode("utf-8")


def normalize_xml_tree(tree: etree._ElementTree) -> etree._ElementTree:
    """Alinha namespace MEC http->https antes da validação XSD."""
    root = tree.getroot()
    if root.tag.startswith("{"):
        ns, local = root.tag[1:].split("}", 1)
        if ns == MEC_NAMESPACE_HTTP:
            _rewrite_namespace(root, MEC_NAMESPACE_HTTP, MEC_NAMESPACE_HTTPS)
    return tree


def _rewrite_namespace(elem: etree._Element, old_ns: str, new_ns: str) -> None:
    if elem.tag.startswith("{"):
        ns, local = elem.tag[1:].split("}", 1)
        if ns == old_ns:
            elem.tag = f"{{{new_ns}}}{local}"
    for attr_name, value in list(elem.attrib.items()):
        if attr_name.startswith("{"):
            ns, local = attr_name[1:].split("}", 1)
            if ns == old_ns:
                del elem.attrib[attr_name]
                elem.attrib[f"{{{new_ns}}}{local}"] = value
        elif attr_name == "xmlns" and value == old_ns:
            elem.attrib["xmlns"] = new_ns
    for child in elem:
        _rewrite_namespace(child, old_ns, new_ns)


def normalize_schema_version(value: str) -> str:
    """Normaliza versao='1.05' ou 'v1.05' para comparação."""
    value = value.strip()
    if value.startswith("v"):
        return value
    if value and value[0].isdigit():
        return f"v{value}"
    return value
