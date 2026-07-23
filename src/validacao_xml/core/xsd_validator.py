"""Validação estrutural XSD com lxml."""

from __future__ import annotations

import shutil
from pathlib import Path

from lxml import etree

from validacao_xml.core.detector import ROOT_TO_XSD, get_inf_element, local_name
from validacao_xml.core.models import Severity, ValidationIssue
from validacao_xml.core.xsd_messages import humanize_xsd_error
from validacao_xml.schemas.normalize import normalize_schema_version, normalize_xsd_bytes, normalize_xml_tree
from validacao_xml.schemas.sync import get_active_schema_dir


class XsdValidator:
    """Valida XML contra esquema XSD oficial do MEC."""

    def __init__(self, schema_dir: Path | None = None) -> None:
        self.schema_dir = schema_dir or get_active_schema_dir()
        self.normalized_dir = self.schema_dir / ".normalized"
        self._schema_cache: dict[str, etree.XMLSchema] = {}
        self._ensure_normalized_schemas()

    def _ensure_normalized_schemas(self) -> None:
        """Gera cópia normalizada dos XSDs (namespaces W3C http) para libxml2."""
        self.normalized_dir.mkdir(parents=True, exist_ok=True)
        marker = self.normalized_dir / ".ready"
        source_files = sorted(self.schema_dir.glob("*.xsd"))
        if marker.exists() and len(list(self.normalized_dir.glob("*.xsd"))) >= len(source_files):
            return
        for xsd in source_files:
            normalized = normalize_xsd_bytes(xsd.read_bytes())
            (self.normalized_dir / xsd.name).write_bytes(normalized)
        marker.write_text("ok", encoding="utf-8")

    def _load_schema(self, xsd_filename: str) -> etree.XMLSchema:
        if xsd_filename in self._schema_cache:
            return self._schema_cache[xsd_filename]
        xsd_path = self.normalized_dir / xsd_filename
        if not xsd_path.exists():
            xsd_path = self.schema_dir / xsd_filename
        if not xsd_path.exists():
            raise FileNotFoundError(f"Esquema XSD não encontrado: {xsd_filename}")
        parser = etree.XMLParser()
        schema_doc = etree.parse(str(xsd_path), parser)
        schema = etree.XMLSchema(schema_doc)
        self._schema_cache[xsd_filename] = schema
        return schema

    def validate(self, root_name: str, tree: etree._ElementTree) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        xsd_file = ROOT_TO_XSD.get(root_name)
        if not xsd_file:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Elemento raiz '{root_name}' não possui esquema XSD mapeado.",
                    rule_id="XSD-001",
                    layer="xsd",
                )
            )
            return issues

        try:
            schema = self._load_schema(xsd_file)
        except etree.XMLSchemaParseError as exc:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Erro ao carregar XSD '{xsd_file}': {exc}",
                    rule_id="XSD-002",
                    layer="xsd",
                )
            )
            return issues
        except FileNotFoundError as exc:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=str(exc),
                    rule_id="XSD-003",
                    layer="xsd",
                )
            )
            return issues

        normalized_tree = normalize_xml_tree(tree)
        valid = schema.validate(normalized_tree)
        if not valid:
            for error in schema.error_log:
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        message=humanize_xsd_error(error.message),
                        rule_id="XSD-004",
                        layer="xsd",
                        details={
                            "line": error.line,
                            "column": error.column,
                            "raw_message": error.message,
                        },
                    )
                )

        inf = get_inf_element(tree.getroot())
        if inf is not None:
            xml_version = normalize_schema_version(inf.get("versao", ""))
            schema_version = normalize_schema_version(
                xsd_file.split("_v")[-1].replace(".xsd", "") if "_v" in xsd_file else ""
            )
            if xml_version and schema_version and xml_version != schema_version:
                issues.append(
                    ValidationIssue(
                        severity=Severity.WARNING,
                        message=(
                            f"Atributo versao='{inf.get('versao', '')}' pode não corresponder "
                            f"ao esquema '{xsd_file}'."
                        ),
                        rule_id="XSD-005",
                        xpath=self._element_path(inf),
                        layer="xsd",
                    )
                )

        return issues

    @staticmethod
    def _element_path(elem: etree._Element) -> str:
        parts: list[str] = []
        current: etree._Element | None = elem
        while current is not None:
            parts.append(local_name(current.tag))
            current = current.getparent()
        return "/" + "/".join(reversed(parts))

    def refresh_schemas(self) -> None:
        """Recria cache normalizado após sync de esquemas."""
        if self.normalized_dir.exists():
            shutil.rmtree(self.normalized_dir, ignore_errors=True)
        self._schema_cache.clear()
        self._ensure_normalized_schemas()
