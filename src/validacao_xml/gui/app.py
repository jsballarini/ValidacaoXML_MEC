"""Janela principal do validador."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from validacao_xml import __version__
from validacao_xml.config import APP_NAME
from validacao_xml.core.models import ValidationOptions
from validacao_xml.core.pipeline import ValidationPipeline
from validacao_xml.gui.components import ResultsPanel
from validacao_xml.schemas.sync import get_schema_status, sync_schemas


class ValidacaoApp(ctk.CTk):
    """Aplicativo desktop de validação XML Digital."""

    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} — Validador Digital v{__version__}")
        self.geometry("960x720")
        self.minsize(800, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.pipeline = ValidationPipeline()
        self.selected_file: Path | None = None
        self._build_ui()
        self._refresh_schema_status()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=12, pady=12)

        ctk.CTkLabel(
            header,
            text="Validador XML — Digital (MEC)",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=8)

        controls = ctk.CTkFrame(self)
        controls.pack(fill="x", padx=12, pady=(0, 8))

        self.file_label = ctk.CTkLabel(controls, text="Nenhum arquivo selecionado", anchor="w")
        self.file_label.pack(fill="x", padx=8, pady=(8, 4))

        btn_row = ctk.CTkFrame(controls, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=4)

        ctk.CTkButton(btn_row, text="Selecionar XML...", command=self._select_file).pack(
            side="left", padx=(0, 8)
        )
        self.validate_btn = ctk.CTkButton(
            btn_row, text="Validar", command=self._validate, state="disabled"
        )
        self.validate_btn.pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Atualizar esquemas", command=self._sync_schemas).pack(
            side="left"
        )

        options = ctk.CTkFrame(self)
        options.pack(fill="x", padx=12, pady=(0, 8))

        self.relax_var = ctk.BooleanVar(value=False)
        self.strict_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options,
            text="Modo homologação (omitir verificação criptográfica de assinaturas)",
            variable=self.relax_var,
        ).pack(anchor="w", padx=8, pady=2)
        ctk.CTkCheckBox(
            options,
            text="Validação estrita de formatação XML (IN 1.2.2)",
            variable=self.strict_var,
        ).pack(anchor="w", padx=8, pady=2)

        schema_frame = ctk.CTkFrame(self)
        schema_frame.pack(fill="x", padx=12, pady=(0, 8))
        self.schema_status_label = ctk.CTkLabel(schema_frame, text="", anchor="w")
        self.schema_status_label.pack(fill="x", padx=8, pady=8)

        self.results = ResultsPanel(self)
        self.results.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.status_bar = ctk.CTkLabel(
            self,
            text=f"Versão {__version__}",
            anchor="w",
        )
        self.status_bar.pack(fill="x", padx=12, pady=(0, 12))

    def _refresh_schema_status(self) -> None:
        status = get_schema_status()
        last_sync = status.get("last_sync") or "nunca"
        if last_sync and "T" in last_sync:
            last_sync = last_sync.replace("T", " ").split(".")[0] + " UTC"
        self.schema_status_label.configure(
            text=(
                f"Esquemas: {status.get('schema_version', '?')} | "
                f"{status.get('file_count', 0)} arquivos | "
                f"Última sync: {last_sync} | "
                f"Cache: {status.get('cache_dir', '')}"
            )
        )

    def _select_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar XML",
            filetypes=[("XML", "*.xml"), ("Todos", "*.*")],
        )
        if path:
            self.selected_file = Path(path)
            self.file_label.configure(text=str(self.selected_file))
            self.validate_btn.configure(state="normal")

    def _validate(self) -> None:
        if not self.selected_file:
            return
        self.validate_btn.configure(state="disabled")
        self.status_bar.configure(text="Validando...")

        options = ValidationOptions(
            relax_homologacao=self.relax_var.get(),
            strict_formatting=self.strict_var.get(),
        )

        def run() -> None:
            try:
                result = self.pipeline.validate_file(self.selected_file, options)
                self.after(0, lambda: self._show_validation_result(result))
            except Exception as exc:
                self.after(
                    0,
                    lambda: messagebox.showerror("Erro", f"Falha na validação: {exc}"),
                )
            finally:
                self.after(0, lambda: self.validate_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

    def _show_validation_result(self, result) -> None:
        self.results.show_result(result)
        self.status_bar.configure(text=result.summary())

    def _sync_schemas(self) -> None:
        self.status_bar.configure(text="Sincronizando esquemas XSD...")

        def run() -> None:
            try:
                sync_result = sync_schemas(force=True)
                msg = (
                    f"Atualizados: {len(sync_result.updated_files)} arquivo(s).\n"
                    f"Falhas: {len(sync_result.failed_files)}."
                )
                if sync_result.failed_files:
                    msg += "\n" + ", ".join(sync_result.failed_files)
                self.after(0, lambda: messagebox.showinfo("Esquemas XSD", msg))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Erro", str(exc)))
            finally:
                self.after(0, self._refresh_schema_status)
                self.after(0, lambda: self.status_bar.configure(text=f"Versão {__version__}"))

        threading.Thread(target=run, daemon=True).start()


def run_app() -> None:
    app = ValidacaoApp()
    app.mainloop()
