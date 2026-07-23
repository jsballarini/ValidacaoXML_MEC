"""Textos de ajuda para avisos e erros de validação."""

from __future__ import annotations

import customtkinter as ctk

from validacao_xml.core.models import ValidationIssue

RULE_EXPLANATIONS: dict[str, str] = {
    "XML-001": (
        "O arquivo não é um XML bem formado (tags abertas/fechadas, encoding, etc.). "
        "Corrija a sintaxe antes de qualquer outra validação."
    ),
    "XML-002": (
        "O aplicativo não conseguiu ler o arquivo selecionado. "
        "Verifique permissões, caminho e se o arquivo ainda existe."
    ),
    "DET-001": (
        "O elemento raiz do XML não corresponde a nenhum dos 6 tipos de documento "
        "do Diploma Digital reconhecidos pelo validador (Diploma, Histórico, etc.)."
    ),
    "XSD-001": (
        "O tipo de documento foi detectado, mas não há esquema XSD associado "
        "no mapeamento interno do validador."
    ),
    "XSD-002": (
        "O esquema XSD oficial não pôde ser carregado ou interpretado. "
        "Tente atualizar os esquemas em 'Atualizar esquemas' ou reinstalar o aplicativo."
    ),
    "XSD-003": (
        "Arquivo XSD esperado não foi encontrado no cache local ou no pacote embutido. "
        "Use 'Atualizar esquemas' para sincronizar com o portal do MEC."
    ),
    "XSD-004": (
        "O conteúdo do XML não obedece à estrutura e aos tipos definidos no pacote XSD "
        "oficial v1.05 do MEC (IN nº 5/2022). Campos, formatos e elementos obrigatórios "
        "devem seguir exatamente o leiaute publicado em portal.mec.gov.br."
    ),
    "XSD-005": (
        "O atributo versao do bloco inf* do documento difere da versão do esquema XSD "
        "usado na validação. Confirme se o XML e os esquemas são da mesma versão (v1.05)."
    ),
    "FMT-001": (
        "A IN v1.05 (item 1.2.2 III) proíbe comentários XML no documento final."
    ),
    "FMT-002": (
        "A IN v1.05 (item 1.2.2 V) exige XML compacto, sem espaços entre tags."
    ),
    "FMT-003": (
        "A IN v1.05 (item 1.2.2 V) proíbe quebras de linha, tabulações e formatação "
        "no XML emitido."
    ),
    "SIG-000": (
        "Nenhum elemento Signature (XMLDSig) foi encontrado. Documentos em produção "
        "devem ser assinados digitalmente conforme a IN."
    ),
    "SIG-RELAX": (
        "O modo homologação está ativo: as assinaturas foram localizadas, mas a "
        "verificação criptográfica detalhada foi omitida de propósito."
    ),
    "DIP-ID-001": (
        "O atributo id de infDiploma deve seguir o padrão VDip + 44 dígitos (IN 2.2.2.1)."
    ),
    "DIP-SIG-001": (
        "O Diploma Digital em ambiente de Produção deve conter ao menos uma assinatura "
        "digital XMLDSig válida."
    ),
    "DOC-ID-001": (
        "O identificador do documento acadêmico não segue o padrão exigido pela IN v1.05."
    ),
    "DOC-SIG-001": (
        "A documentação acadêmica em Produção exige assinaturas digitais conforme a IN."
    ),
    "HIS-SIG-001": (
        "O Histórico Escolar Digital em Produção deve conter assinatura(s) digital(is)."
    ),
    "CUR-SIG-001": (
        "O Currículo Escolar Digital em Produção deve conter assinatura(s) digital(is)."
    ),
    "LST-SIG-001": (
        "A Lista de Diplomas Anulados em Produção deve conter assinatura(s) digital(is)."
    ),
    "FIS-SIG-001": (
        "O Arquivo de Fiscalização em Produção deve conter assinatura(s) digital(is)."
    ),
}

PREFIX_EXPLANATIONS: dict[str, str] = {
    "-AMB-001": (
        "O atributo ambiente do documento indica emissão fora de Produção "
        "(ex.: Homologação). Documentos nesse ambiente não têm validade jurídica "
        "segundo a IN v1.05."
    ),
}

SIGNATURE_EXPLANATION = (
    "Resultado da verificação de assinatura digital XMLDSig/XAdES.\n\n"
    "• Aprovada: integridade criptográfica confirmada.\n"
    "• Indeterminada: certificado ICP-Brasil reconhecido, mas a cadeia ou a "
    "integridade não pôde ser confirmada offline (certificados raiz ausentes, "
    "carimbo de tempo, etc.).\n"
    "• Reprovada: assinatura inválida ou certificado fora da ICP-Brasil."
)


def get_issue_explanation(issue: ValidationIssue) -> str:
    """Retorna texto explicativo para um aviso ou erro."""
    parts: list[str] = []

    if issue.rule_id and issue.rule_id in RULE_EXPLANATIONS:
        parts.append(RULE_EXPLANATIONS[issue.rule_id])
    elif issue.rule_id:
        for suffix, text in PREFIX_EXPLANATIONS.items():
            if issue.rule_id.endswith(suffix):
                parts.append(text)
                break

    if issue.rule_id and issue.rule_id.startswith("SIG-") and issue.rule_id not in {
        "SIG-000",
        "SIG-RELAX",
    }:
        parts.append(SIGNATURE_EXPLANATION)

    contextual = _contextual_explanation(issue)
    if contextual:
        parts.append(contextual)

    if not parts:
        parts.append(_layer_fallback(issue))

    if issue.rule_id:
        parts.append(f"\nCódigo: {issue.rule_id}")

    if issue.details.get("raw_message"):
        parts.append(f"\nDetalhe técnico (libxml2):\n{issue.details['raw_message']}")

    return "\n\n".join(parts)


def _contextual_explanation(issue: ValidationIssue) -> str:
    message = issue.message.lower()

    if "lattes" in message:
        return (
            "Campo Lattes (tipo TLattes em tiposBasicos_v1.05.xsd):\n"
            "• Formato exigido: https://lattes.cnpq.br/ + ID numérico\n"
            "• Deve usar https (não http)\n"
            "• Domínio correto: lattes.cnpq.br (atenção a erros de digitação)\n"
            "• Fonte: pacote XSD oficial MEC v1.05"
        )

    if "http://" in issue.message and "https://" in issue.message:
        return (
            "Muitas IES emitem URLs com http://, mas o XSD do MEC exige https:// "
            "no padrão (facet pattern). Ajuste o valor no XML ou confirme com a "
            "instituição emissora."
        )

    if "filho obrigatório" in message or "missing child" in message.lower():
        return (
            "Um elemento pai está incompleto: falta um filho exigido pelo leiaute XSD. "
            "Verifique a árvore XML na linha indicada e compare com o leiaute oficial."
        )

    if "não atende ao formato exigido" in message:
        return (
            "O valor informado não corresponde ao padrão (regex) definido no XSD para "
            "esse campo. Os caracteres \\ e \\d+ na mensagem técnica são sintaxe de "
            "expressão regular, não fazem parte do valor esperado."
        )

    if "integridade" in message or "indeterminada" in message:
        return SIGNATURE_EXPLANATION

    return ""


def _layer_fallback(issue: ValidationIssue) -> str:
    fallbacks = {
        "xsd": (
            "Erro ou aviso na validação estrutural contra os esquemas XSD oficiais "
            "do Diploma Digital (MEC)."
        ),
        "business": (
            "Regra de negócio da IN nº 5/2022 (v1.05) aplicada além da validação XSD."
        ),
        "signature": SIGNATURE_EXPLANATION,
        "parse": "Problema ao interpretar ou ler o arquivo XML.",
        "detect": "Problema ao identificar o tipo de documento Digital.",
    }
    return fallbacks.get(issue.layer, issue.message)


class IssueHelpDialog(ctk.CTkToplevel):
    """Janela modal com explicação detalhada de um aviso ou erro."""

    def __init__(self, master, issue: ValidationIssue) -> None:
        super().__init__(master)
        title_id = issue.rule_id or issue.layer or "validação"
        self.title(f"Explicação — {title_id}")
        self.geometry("560x360")
        self.minsize(420, 240)
        self.transient(master)
        self.grab_set()

        header = ctk.CTkLabel(
            self,
            text=title_id,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=16, pady=(16, 8))

        textbox = ctk.CTkTextbox(self, wrap="word")
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        textbox.insert("1.0", get_issue_explanation(issue))
        textbox.configure(state="disabled")

        ctk.CTkButton(self, text="Fechar", width=100, command=self.destroy).pack(
            pady=(0, 16)
        )

        self.after(100, self.focus_force)

