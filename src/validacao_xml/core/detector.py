"""Detecção do tipo de documento XML pelo elemento raiz."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from validacao_xml.config import MEC_NAMESPACE
from validacao_xml.core.models import DocumentType

ROOT_TO_TYPE: dict[str, DocumentType] = {
    "Diploma": DocumentType.DIPLOMA,
    "DocumentacaoAcademicaRegistro": DocumentType.DOC_ACADEMICA,
    "HistoricoEscolar": DocumentType.HISTORICO,
    "DocumentoHistoricoEscolarParcial": DocumentType.HISTORICO,
    "DocumentoHistoricoEscolarFinal": DocumentType.HISTORICO,
    "DocumentoHistoricoEscolarSegundaViaNatoFisico": DocumentType.HISTORICO,
    "CurriculoEscolar": DocumentType.CURRICULO,
    "ListaDiplomasAnulados": DocumentType.LISTA_ANULADOS,
    "ArquivoFiscalizacao": DocumentType.FISCALIZACAO,
}

ROOT_TO_XSD: dict[str, str] = {
    "Diploma": "DiplomaDigital_v1.05.xsd",
    "DocumentacaoAcademicaRegistro": "DocumentacaoAcademicaRegistroDiplomaDigital_v1.05.xsd",
    "HistoricoEscolar": "HistoricoEscolarDigital_v1.05.xsd",
    "DocumentoHistoricoEscolarParcial": "HistoricoEscolarDigital_v1.05.xsd",
    "DocumentoHistoricoEscolarFinal": "HistoricoEscolarDigital_v1.05.xsd",
    "DocumentoHistoricoEscolarSegundaViaNatoFisico": "HistoricoEscolarDigital_v1.05.xsd",
    "CurriculoEscolar": "CurriculoEscolarDigital_v1.05.xsd",
    "ListaDiplomasAnulados": "ListaDiplomasAnulados_v1.05.xsd",
    "ArquivoFiscalizacao": "ArquivoFiscalizacao_v1.05.xsd",
}


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def detect_from_tree(root: etree._Element) -> tuple[DocumentType, str]:
    name = local_name(root.tag)
    doc_type = ROOT_TO_TYPE.get(name, DocumentType.UNKNOWN)
    return doc_type, name


def load_xml_tree(xml_path: Path | str) -> etree._ElementTree:
    parser = etree.XMLParser(remove_comments=False, recover=False)
    return etree.parse(str(xml_path), parser)


def detect_document(xml_path: Path | str) -> tuple[DocumentType, str, etree._ElementTree]:
    tree = load_xml_tree(xml_path)
    doc_type, root_name = detect_from_tree(tree.getroot())
    return doc_type, root_name, tree


def get_inf_element(root: etree._Element) -> etree._Element | None:
    """Localiza elemento de informações com atributos versao/ambiente/id."""
    for child in root:
        if local_name(child.tag).startswith("inf"):
            return child
    for elem in root.iter():
        tag = local_name(elem.tag)
        if tag.startswith("inf") and (
            elem.get("versao") is not None or elem.get("ambiente") is not None
        ):
            return elem
    return None


def get_document_namespace(root: etree._Element) -> str:
    if root.tag.startswith("{"):
        return root.tag[1:].split("}", 1)[0]
    return MEC_NAMESPACE
