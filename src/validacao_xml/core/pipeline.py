"""Pipeline de validação completa."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from validacao_xml.core.business_rules import apply_business_rules
from validacao_xml.core.detector import detect_document
from validacao_xml.core.models import DocumentType, Severity, ValidationIssue, ValidationOptions, ValidationResult
from validacao_xml.core.signature.verifier import verify_signatures
from validacao_xml.core.xsd_validator import XsdValidator
from validacao_xml.schemas.sync import ensure_cache_from_bundled, get_schema_status


class ValidationPipeline:
    """Orquestra validação XSD, regras de negócio e assinaturas."""

    def __init__(self) -> None:
        ensure_cache_from_bundled()
        self.xsd_validator = XsdValidator()

    def validate_file(
        self,
        xml_path: Path | str,
        options: ValidationOptions | None = None,
    ) -> ValidationResult:
        options = options or ValidationOptions()
        path = Path(xml_path)
        result = ValidationResult(xml_path=str(path.resolve()))

        try:
            doc_type, root_name, tree = detect_document(path)
        except etree.XMLSyntaxError as exc:
            result.is_valid = False
            result.add(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"XML malformado: {exc}",
                    rule_id="XML-001",
                    layer="parse",
                )
            )
            return result
        except OSError as exc:
            result.is_valid = False
            result.add(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Erro ao ler arquivo: {exc}",
                    rule_id="XML-002",
                    layer="parse",
                )
            )
            return result

        result.document_type = doc_type
        status = get_schema_status()
        result.schema_version = status.get("schema_version", "")

        if doc_type == DocumentType.UNKNOWN:
            result.add(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Tipo de documento não reconhecido (raiz: {root_name}).",
                    rule_id="DET-001",
                    layer="detect",
                )
            )
            return result

        root = tree.getroot()
        for issue in self.xsd_validator.validate(root_name, tree):
            result.add(issue)

        for issue in apply_business_rules(doc_type, root, str(path), options):
            result.add(issue)

        if not options.skip_signatures:
            for issue in verify_signatures(root, options):
                result.add(issue)

        return result
