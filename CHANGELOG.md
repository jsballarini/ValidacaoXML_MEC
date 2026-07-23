# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Mensagens de erro XSD (padrão `pattern`) exibidas em português, sem escapes de regex (`\.`, `\d+`), com dica quando o valor usa `http://` e o XSD exige `https://`
- Script `scripts/build_exe_unico.ps1` para gerar executável único (`dist\ValidacaoXML.exe`)
- Build PyInstaller passa a incluir schemas XMLDSig do signxml (`--collect-data signxml`)
- Modo homologação omite verificação criptográfica de assinaturas (INFO em vez de avisos)
- Download ICP-Brasil corrigido para URLs atuais do repositório AC-Raiz (v5, v10, v13)

## [0.1.0] - 2026-07-22

### Added

- Validação XSD dos 6 tipos de documento Digital (v1.05)
- Sincronização de esquemas XSD com portal MEC e cache local
- Regras de negócio da IN v1.05 (ambiente, versão, formatação, assinaturas)
- Verificação de assinaturas digitais XMLDSig com classificação ICP-Brasil
- Interface gráfica CustomTkinter
- Script de build PyInstaller para Windows
- Testes automatizados com pytest
