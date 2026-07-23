"""Modelos de dados para resultados de validação."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SignatureStatus(str, Enum):
    APPROVED = "Aprovada"
    REJECTED = "Reprovada"
    INDETERMINATE = "Indeterminada"


class DocumentType(str, Enum):
    DIPLOMA = "Diploma Digital"
    DOC_ACADEMICA = "Documentação Acadêmica para Emissão e Registro"
    HISTORICO = "Histórico Escolar Digital"
    CURRICULO = "Currículo Escolar Digital"
    LISTA_ANULADOS = "Lista de Diplomas Anulados"
    FISCALIZACAO = "Arquivo de Fiscalização"
    UNKNOWN = "Desconhecido"


@dataclass
class ValidationIssue:
    severity: Severity
    message: str
    rule_id: str = ""
    xpath: str = ""
    layer: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def is_error(self) -> bool:
        return self.severity == Severity.ERROR


@dataclass
class ValidationOptions:
    relax_homologacao: bool = False
    strict_formatting: bool = False
    skip_signatures: bool = False


@dataclass
class ValidationResult:
    document_type: DocumentType = DocumentType.UNKNOWN
    schema_version: str = ""
    xml_path: str = ""
    issues: list[ValidationIssue] = field(default_factory=list)
    is_valid: bool = True

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.is_error:
            self.is_valid = False

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def infos(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.INFO]

    def summary(self) -> str:
        status = "VÁLIDO" if self.is_valid else "INVÁLIDO"
        return (
            f"{status} — {self.document_type.value} "
            f"({len(self.errors)} erro(s), {len(self.warnings)} aviso(s), "
            f"{len(self.infos)} info(s))"
        )
