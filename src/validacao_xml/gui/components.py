"""Componentes reutilizáveis da interface."""

from __future__ import annotations

import customtkinter as ctk

from validacao_xml.core.models import Severity, ValidationIssue, ValidationResult
from validacao_xml.gui.issue_help import IssueHelpDialog

SEVERITY_COLORS = {
    Severity.ERROR: "#ff6b6b",
    Severity.WARNING: "#ffd166",
    Severity.INFO: "#06d6a0",
}

SEVERITY_LABELS = {
    Severity.ERROR: "ERRO",
    Severity.WARNING: "AVISO",
    Severity.INFO: "INFO",
}


def format_issue_text(issue: ValidationIssue) -> str:
    """Texto completo do aviso para exibição e cópia."""
    text_parts = [issue.message]
    if issue.rule_id:
        text_parts.append(f"[{issue.rule_id}]")
    if issue.xpath:
        text_parts.append(f"({issue.xpath})")
    if issue.layer:
        text_parts.append(f"{{{issue.layer}}}")
    return " ".join(text_parts)


class ResultsPanel(ctk.CTkScrollableFrame):
    """Painel scrollável com resultados de validação."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._rows: list[ctk.CTkFrame] = []

    def clear(self) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()

    def show_result(self, result: ValidationResult) -> None:
        self.clear()
        summary = ctk.CTkLabel(
            self,
            text=result.summary(),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        summary.pack(fill="x", padx=8, pady=(8, 4))
        self._rows.append(summary)

        meta = ctk.CTkLabel(
            self,
            text=(
                f"Tipo: {result.document_type.value} | "
                f"Esquema: {result.schema_version} | "
                f"Arquivo: {result.xml_path}"
            ),
            anchor="w",
            wraplength=700,
        )
        meta.pack(fill="x", padx=8, pady=(0, 8))
        self._rows.append(meta)

        if not result.issues:
            ok = ctk.CTkLabel(self, text="Nenhum problema encontrado.", anchor="w")
            ok.pack(fill="x", padx=8, pady=4)
            self._rows.append(ok)
            return

        for issue in result.issues:
            self._add_issue_row(issue)

    def _add_issue_row(self, issue: ValidationIssue) -> None:
        frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        frame.pack(fill="x", padx=8, pady=4)
        self._rows.append(frame)

        color = SEVERITY_COLORS.get(issue.severity, "#cccccc")
        badge = ctk.CTkLabel(
            frame,
            text=SEVERITY_LABELS.get(issue.severity, "?"),
            width=60,
            fg_color=color,
            text_color="black",
            corner_radius=4,
        )
        badge.pack(side="left", padx=(8, 8), pady=8)

        issue_text = format_issue_text(issue)

        label = ctk.CTkLabel(
            frame,
            text=issue_text,
            anchor="w",
            justify="left",
            wraplength=480,
        )
        label.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)

        help_btn = ctk.CTkButton(
            frame,
            text="?",
            width=32,
            command=lambda current_issue=issue: self._show_issue_help(current_issue),
        )
        help_btn.pack(side="right", padx=(0, 4), pady=8)

        copy_btn = ctk.CTkButton(
            frame,
            text="Copiar",
            width=72,
        )
        copy_btn.configure(
            command=lambda text=issue_text, btn=copy_btn: self._copy_issue(text, btn)
        )
        copy_btn.pack(side="right", padx=(0, 8), pady=8)

    def _show_issue_help(self, issue: ValidationIssue) -> None:
        IssueHelpDialog(self.winfo_toplevel(), issue)

    def _copy_issue(self, text: str, button: ctk.CTkButton) -> None:
        root = self.winfo_toplevel()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update_idletasks()

        original_text = button.cget("text")
        button.configure(text="Copiado!")
        root.after(1500, lambda: button.configure(text=original_text))
