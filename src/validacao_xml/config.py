"""Configurações globais do aplicativo."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from validacao_xml import __version__

APP_NAME = "ValidacaoXML"
APP_VERSION = __version__
ORG_NAME = "Perseus"

MEC_NAMESPACE = "https://portal.mec.gov.br/diplomadigital/arquivos-em-xsd"
XMLDSIG_NAMESPACE = "https://www.w3.org/2000/09/xmldsig#"

MEC_BASE_URL = "https://www.gov.br/mec/pt-br/diploma-digital/documentos"
MEC_DATA_PAGE = "https://www.gov.br/mec/pt-br/diploma-digital/dados"

DEFAULT_SCHEMA_VERSION = "v1.05"


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_package_dir() -> Path:
    """Diretório do pacote validacao_xml."""
    return Path(__file__).resolve().parent


def get_resource_root() -> Path:
    """Raiz de recursos empacotados (PyInstaller _MEIPASS)."""
    if _is_frozen():
        return Path(sys._MEIPASS)
    return get_package_dir()


def get_app_data_dir() -> Path:
    """Diretório de dados do usuário (%LOCALAPPDATA%\\Perseus\\ValidacaoXML)."""
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    path = Path(base) / ORG_NAME / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_schema_cache_dir() -> Path:
    """Cache local de esquemas XSD."""
    path = get_app_data_dir() / "schemas"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_bundled_schemas_dir() -> Path:
    if _is_frozen():
        return get_resource_root() / "validacao_xml" / "schemas" / "bundled"
    return get_package_dir() / "schemas" / "bundled"


def get_bundled_icp_dir() -> Path:
    if _is_frozen():
        return get_resource_root() / "icp_brasil"
    return get_package_dir().parents[2] / "resources" / "icp_brasil"


def get_manifest_path() -> Path:
    if _is_frozen():
        return get_resource_root() / "validacao_xml" / "schemas" / "manifest.json"
    return get_package_dir() / "schemas" / "manifest.json"
