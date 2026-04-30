# ═══════════════════════════════════════════════════════════════
# DOC CONVERTER — PDF↔Word, Excel Generator, File Tools
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import io, logging, tempfile
from pathlib import Path
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger("nexus.doc")


@dataclass
class ConversionResult:
    input_file: str
    output_file: str
    output_format: str
    filesize: int
    status: str


class PDFConverter:
    """Convert between PDF and Word documents."""

    def __init__(self, output_dir: str = "data/converted"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def pdf_to_word(self, pdf_path: str) -> ConversionResult:
        """Convert PDF to Word (.docx)."""
        try:
            from pdf2docx import Converter
            output = self.output_dir / (Path(pdf_path).stem + ".docx")
            cv = Converter(pdf_path)
            cv.convert(str(output))
            cv.close()
            return ConversionResult(pdf_path, str(output), "docx", output.stat().st_size, "success")
        except ImportError:
            try:
                import pdfplumber
                from docx import Document
                doc = Document()
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            doc.add_paragraph(text)
                        doc.add_page_break()
                output = self.output_dir / (Path(pdf_path).stem + ".docx")
                doc.save(str(output))
                return ConversionResult(pdf_path, str(output), "docx", output.stat().st_size, "success")
            except Exception as e:
                return ConversionResult(pdf_path, "", "docx", 0, f"error: {e}")

    async def word_to_pdf(self, docx_path: str) -> ConversionResult:
        """Convert Word to PDF using LibreOffice headless."""
        import asyncio
        output = self.output_dir / (Path(docx_path).stem + ".pdf")
        try:
            proc = await asyncio.create_subprocess_exec(
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", str(self.output_dir), docx_path,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
            if output.exists():
                return ConversionResult(docx_path, str(output), "pdf", output.stat().st_size, "success")
            return ConversionResult(docx_path, "", "pdf", 0, "error: conversion failed")
        except Exception as e:
            return ConversionResult(docx_path, "", "pdf", 0, f"error: {e}")


class ExcelGenerator:
    """Generate Excel files with templates and data."""

    def __init__(self, output_dir: str = "data/excel"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def create_from_data(self, title: str, headers: list[str], rows: list[list], filename: str = "") -> str:
        """Create an Excel file from structured data."""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

            wb = Workbook()
            ws = wb.active
            ws.title = title[:31]

            # Title row
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
            title_cell = ws.cell(row=1, column=1, value=title)
            title_cell.font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
            title_cell.fill = PatternFill(start_color="1a1a2e", end_color="1a1a2e", fill_type="solid")
            title_cell.alignment = Alignment(horizontal="center")

            # Headers
            header_fill = PatternFill(start_color="00ffe0", end_color="00ffe0", fill_type="solid")
            header_font = Font(name="Arial", size=10, bold=True, color="070710")
            thin_border = Border(
                left=Side(style="thin"), right=Side(style="thin"),
                top=Side(style="thin"), bottom=Side(style="thin"),
            )

            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=3, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
                cell.border = thin_border
                ws.column_dimensions[cell.column_letter].width = max(15, len(header) + 5)

            # Data rows
            for row_idx, row_data in enumerate(rows, 4):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="left")

            fname = filename or f"{title.lower().replace(' ', '_')}.xlsx"
            output_path = self.output_dir / fname
            wb.save(str(output_path))
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ Excel generation error: {e}")
            return ""

    async def create_chat_export(self, chat_data: list[dict], filename: str = "chat_export.xlsx") -> str:
        """Export chat/conversation data to Excel dashboard."""
        headers = ["Timestamp", "User", "Message", "Agent Used", "Task Type", "Confidence", "Emotion"]
        rows = [
            [
                d.get("timestamp", ""), d.get("user_id", ""), d.get("input", ""),
                d.get("agent", ""), d.get("task_type", ""),
                d.get("confidence", ""), d.get("emotion", ""),
            ]
            for d in chat_data
        ]
        return await self.create_from_data("Chat Dashboard Export", headers, rows, filename)


class FileTools:
    """Utility tools for file manipulation."""

    async def merge_pdfs(self, pdf_paths: list[str], output_path: str) -> str:
        try:
            from PyPDF2 import PdfMerger
            merger = PdfMerger()
            for path in pdf_paths:
                merger.append(path)
            merger.write(output_path)
            merger.close()
            return output_path
        except Exception as e:
            return f"error: {e}"

    async def split_pdf(self, pdf_path: str, output_dir: str) -> list[str]:
        try:
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(pdf_path)
            outputs = []
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                out = Path(output_dir) / f"page_{i+1}.pdf"
                with open(out, "wb") as f:
                    writer.write(f)
                outputs.append(str(out))
            return outputs
        except Exception as e:
            return [f"error: {e}"]

    async def extract_pdf_text(self, pdf_path: str) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                return "\n\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            return f"error: {e}"
