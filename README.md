# ValidacaoXML — Validador Digital (MEC)

Aplicativo desktop em Python para validar arquivos XML **Digital** conforme a especificação técnica do MEC (pacote XSD v1.05+).

## Funcionalidades

- Validação estrutural (XSD) dos 6 tipos de documento do pacote oficial
- Regras de negócio da IN nº 5/2022 (v1.05)
- Verificação de assinaturas digitais XMLDSig/XAdES (ICP-Brasil)
- Sincronização automática de esquemas XSD com o portal do MEC
- Interface gráfica (CustomTkinter) e executável Windows

## Tipos suportados


| Documento                  | Elemento raiz                   |
| -------------------------- | ------------------------------- |
| Diploma Digital            | `Diploma`                       |
| Documentação Acadêmica     | `DocumentacaoAcademicaRegistro` |
| Histórico Escolar Digital  | `HistoricoEscolar`              |
| Currículo Escolar Digital  | `CurriculoEscolar`              |
| Lista de Diplomas Anulados | `ListaDiplomasAnulados`         |
| Arquivo de Fiscalização    | `ArquivoFiscalizacao`           |




## Requisitos

- Python 3.11+
- Windows 10/11 (executável) ou qualquer SO com Python (modo desenvolvimento)



## Instalação (desenvolvimento)

```powershell
cd C:\Dev\Perseus\ValidacaoXML
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```



## Uso

```powershell
validacao-xml
# ou
python -m validacao_xml.main
```

1. Selecione o arquivo `.xml`
2. (Opcional) Clique em **Atualizar esquemas** para baixar XSDs mais recentes do MEC
3. Clique em **Validar**
4. Revise o relatório (Erros, Avisos, Informações)



## Build do executável Windows

Pasta com executável (inicia mais rápido):

```powershell
.\scripts\build_exe.ps1
```

Saída: `dist\ValidacaoXML\ValidacaoXML.exe`

Arquivo único para distribuição:

```powershell
.\scripts\build_exe_unico.ps1
```

Saída: `dist\ValidacaoXML.exe`

## Cache de esquemas

Esquemas XSD são armazenados em:

`%LOCALAPPDATA%\Perseus\ValidacaoXML\schemas\`

Na primeira execução, o app copia os esquemas embutidos (`bundled`) e tenta sincronizar com o MEC.

## Certificados ICP-Brasil

O build baixa automaticamente as AC-Raiz v5, v10 e v13 do repositório oficial:

`https://acraiz.icpbrasil.gov.br/credenciadas/RAIZ/`

Referência: [Repositório AC-Raiz — ITI](https://www.gov.br/iti/pt-br/assuntos/repositorio/repositorio-ac-raiz)

Arquivos em `resources/icp_brasil/`. Para atualizar manualmente:

```powershell
python scripts/download_icp_certs.py
```

Sem certificados locais, assinaturas podem ser classificadas como **Indeterminada** quando a cadeia não puder ser verificada offline.

## Referências oficiais

- [Pacote XSD v1.05 — MEC](https://www.gov.br/mec/pt-br/diploma-digital/dados)
- [IN nº 5/2022 (v1.05)](https://www.gov.br/mec/pt-br/diploma-digital/documentos/in-05-versao-completa-anexos-i-ii-e-iii-v1-05.pdf)
- [Verificador online MEC](https://verificadordiplomadigital.mec.gov.br/diploma)



## Licença

MIT