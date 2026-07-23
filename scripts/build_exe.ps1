# Build do executável Windows — ValidacaoXML
# Requer: pip install -e ".[dev]"

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -e ".[dev]" -q
}

Write-Host "Baixando esquemas XSD..."
.\.venv\Scripts\python scripts\download_schemas.py

Write-Host "Baixando certificados ICP-Brasil..."
.\.venv\Scripts\python scripts\download_icp_certs.py

Write-Host "Instalando dependências de build..."
.\.venv\Scripts\pip install -e ".[dev]" -q

$BundledSchemas = Join-Path $ProjectRoot "src\validacao_xml\schemas\bundled"
$IcpBrasil = Join-Path $ProjectRoot "resources\icp_brasil"

Write-Host "Gerando executável com PyInstaller..."
.\.venv\Scripts\pyinstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name ValidacaoXML `
    --add-data "$BundledSchemas;validacao_xml/schemas/bundled" `
    --add-data "$IcpBrasil;icp_brasil" `
    --add-data "$(Join-Path $ProjectRoot 'src\validacao_xml\schemas\manifest.json');validacao_xml/schemas" `
    --hidden-import xml.etree.ElementTree `
    --collect-submodules lxml `
    --collect-submodules signxml `
    --collect-data signxml `
    --collect-submodules customtkinter `
    --hidden-import darkdetect `
    src/validacao_xml/main.py

Write-Host "Build concluído: $ProjectRoot\dist\ValidacaoXML\ValidacaoXML.exe"
