"""Mensagens XSD legíveis para o usuário."""

from __future__ import annotations

import re

PATTERN_ERROR = re.compile(
    r"Element '\{[^}]+\}(?P<element>[^']+)': \[facet 'pattern'\] "
    r"The value '(?P<value>[^']*)' is not accepted by the pattern '(?P<pattern>[^']*)'\."
)

MISSING_CHILD = re.compile(
    r"Element '\{[^}]+\}(?P<element>[^']+)': Missing child element\(s\)\. Expected is .*"
)


def simplify_xsd_pattern(pattern: str) -> str:
    """Converte regex XSD em texto legível (remove escapes visíveis ao usuário)."""
    readable = pattern
    readable = readable.replace(r"\\.", ".")
    readable = readable.replace(r"\.", ".")
    readable = readable.replace(r"\d+", "[números]")
    readable = readable.replace(r"\d*", "[números]")
    readable = readable.replace(r"\s+", " ")
    readable = readable.replace(r"\s", " ")
    readable = readable.replace(r"\\", "\\")
    return readable


def humanize_xsd_error(message: str) -> str:
    """Traduz mensagens técnicas do libxml2 para linguagem clara."""
    pattern_match = PATTERN_ERROR.search(message)
    if pattern_match:
        element = pattern_match.group("element")
        value = pattern_match.group("value")
        expected = simplify_xsd_pattern(pattern_match.group("pattern"))
        hint = _pattern_hint(value, expected)
        return (
            f"Campo '{element}': valor '{value}' não atende ao formato exigido "
            f"'{expected}'.{hint}"
        )

    missing_match = MISSING_CHILD.search(message)
    if missing_match:
        element = missing_match.group("element")
        return f"Elemento '{element}': filho obrigatório ausente ou incompleto."

    if "Missing child element(s)" in message and "Expected is" in message:
        return message.split("Expected is")[0].strip().rstrip(".") + "."

    return message


def _pattern_hint(value: str, expected: str) -> str:
    if value.startswith("http://") and expected.startswith("https://"):
        return " O XML usa http://, mas o XSD exige https://."
    return ""
