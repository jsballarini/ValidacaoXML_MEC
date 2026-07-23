"""Ponto de entrada da aplicação."""

from __future__ import annotations

from validacao_xml.gui.app import run_app
from validacao_xml.schemas.sync import ensure_cache_from_bundled


def main() -> None:
    ensure_cache_from_bundled()
    run_app()


if __name__ == "__main__":
    main()
