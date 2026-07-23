# Build do executável Windows em arquivo único — ValidacaoXML
# Requer: pip install -e ".[dev]"
# Saída: dist\ValidacaoXML.exe

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
$Manifest = Join-Path $ProjectRoot "src\validacao_xml\schemas\manifest.json"
$OutputExe = Join-Path $ProjectRoot "dist\ValidacaoXML.exe"

Write-Host "Gerando executável único com PyInstaller..."
.\.venv\Scripts\pyinstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name ValidacaoXML `
    --add-data "$BundledSchemas;validacao_xml/schemas/bundled" `
    --add-data "$IcpBrasil;icp_brasil" `
    --add-data "$Manifest;validacao_xml/schemas" `
    --hidden-import xml.etree.ElementTree `
    --collect-submodules lxml `
    --collect-submodules signxml `
    --collect-data signxml `
    --collect-submodules customtkinter `
    --hidden-import darkdetect `
    src/validacao_xml/main.py

if (-not (Test-Path $OutputExe)) {
    throw "Executável não encontrado após o build: $OutputExe"
}

$SizeMb = [math]::Round((Get-Item $OutputExe).Length / 1MB, 1)
Write-Host ""
Write-Host "Build concluído: $OutputExe ($SizeMb MB)"
Write-Host "Distribua apenas este arquivo. Na primeira execução, o Windows pode demorar alguns segundos para extrair os recursos."
