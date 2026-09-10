"""Render the study manuscript as a self-contained, print-friendly PDF.

The renderer deliberately reads only the Markdown supplied by the caller. It
adds result figures only when known, already-existing PNGs are found; it never
calculates results or creates a figure.

Runtime dependency: ``reportlab``. The accompanying full-content test also
uses ``pypdf``; the bundled project Python provides both packages.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


KNOWN_FIGURES = ("main_axis_means.png", "main_primary_endpoint_rates.png")
FONT_NAME = "StudyUnicode"


@dataclass(frozen=True)
class FontChoice:
    name: str
    path: Path | None
    supports_unicode: bool


def _font_directories() -> Iterable[Path]:
    """Yield platform font directories without embedding a workstation path."""
    configured = os.environ.get("CHATGPT_VPN_PDF_FONT")
    if configured:
        yield Path(configured).expanduser().parent

    if sys.platform.startswith("win"):
        windows_dir = os.environ.get("WINDIR")
        if windows_dir:
            yield Path(windows_dir) / "Fonts"
    else:
        yield from (Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), Path.home() / ".fonts")

    yield Path(reportlab.__file__).resolve().parent / "fonts"
    yield Path(__file__).resolve().parent / "fonts"


def discover_font() -> FontChoice:
    """Use an installed Unicode font; fall back to ReportLab Helvetica safely."""
    configured = os.environ.get("CHATGPT_VPN_PDF_FONT")
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    for directory in _font_directories():
        for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "Vera.ttf"):
            candidates.append(directory / name)
            if directory.is_dir():
                candidates.extend(directory.glob(f"**/{name}"))

    for candidate in candidates:
        if candidate.is_file():
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME, str(candidate)))
                return FontChoice(FONT_NAME, candidate, True)
            except (OSError, ValueError):
                continue

    raise RuntimeError(
        "Keine Unicode-TrueType-Schrift gefunden. Setze CHATGPT_VPN_PDF_FONT "
        "auf eine .ttf-Datei oder installiere eine ReportLab-Distribution mit Vera.ttf."
    )


def _inline(markdown: str, font_name: str) -> str:
    """Convert the intentionally small supported inline Markdown subset to XML."""
    escaped = html.escape(markdown, quote=False)

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        href = html.escape(html.unescape(match.group(2)), quote=True)
        return f'<link href="{href}" color="#1f4e79">{label}</link>'

    escaped = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, escaped)
    escaped = re.sub(r"`([^`]+)`", rf'<font name="{font_name}">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", escaped)
    return escaped


def _is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _table_rows(lines: Sequence[str], font_name: str, cell_style: ParagraphStyle) -> Table:
    parsed = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [parsed[0], *parsed[2:]] if len(parsed) > 1 and _is_table_separator(lines[1]) else parsed
    column_count = max(len(row) for row in rows)
    normalized = [row + [""] * (column_count - len(row)) for row in rows]
    data = [[Paragraph(_inline(cell, font_name), cell_style) for cell in row] for row in normalized]
    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe7f3")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17365d")),
                ("FONTNAME", (0, 0), (-1, 0), font_name),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9fbad0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle(
        "StudyBody", parent=base["BodyText"], fontName=font_name, fontSize=9.5,
        leading=13, spaceAfter=7,
    )
    return {
        "body": body,
        "title": ParagraphStyle(
            "StudyTitle", parent=base["Title"], fontName=font_name, fontSize=20,
            leading=24, textColor=colors.HexColor("#17365d"), spaceAfter=15, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "StudyHeading2", parent=base["Heading2"], fontName=font_name, fontSize=14,
            leading=18, textColor=colors.HexColor("#17365d"), spaceBefore=14, spaceAfter=7, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "StudyHeading3", parent=base["Heading3"], fontName=font_name, fontSize=11,
            leading=14, textColor=colors.HexColor("#385d8a"), spaceBefore=10, spaceAfter=5, keepWithNext=True,
        ),
        "h4": ParagraphStyle(
            "StudyHeading4", parent=base["Heading4"], fontName=font_name, fontSize=10,
            leading=13, textColor=colors.HexColor("#385d8a"), spaceBefore=8, spaceAfter=4, keepWithNext=True,
        ),
        "cell": ParagraphStyle(
            "StudyCell", parent=body, fontName=font_name, fontSize=7.3, leading=9.2, spaceAfter=0,
        ),
        "quote": ParagraphStyle(
            "StudyQuote", parent=body, leftIndent=12, borderColor=colors.HexColor("#9fbad0"),
            borderWidth=2, borderPadding=7, textColor=colors.HexColor("#404040"),
        ),
        "caption": ParagraphStyle(
            "StudyCaption", parent=body, alignment=TA_CENTER, fontSize=8, leading=10,
            textColor=colors.HexColor("#595959"),
        ),
    }


def _flush_paragraph(buffer: list[str], story: list[object], styles: dict[str, ParagraphStyle], font_name: str) -> None:
    if buffer:
        story.append(Paragraph(_inline(" ".join(buffer), font_name), styles["body"]))
        buffer.clear()


def markdown_story(markdown: str, font_name: str) -> tuple[list[object], str]:
    """Build a ReportLab story from headings, paragraphs, bullets, tables and quotes."""
    styles = _styles(font_name)
    story: list[object] = []
    paragraph: list[str] = []
    lines = markdown.splitlines()
    title = "Studienmanuskript"
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            _flush_paragraph(paragraph, story, styles, font_name)
            index += 1
            continue

        table_block = line.lstrip().startswith("|") and index + 1 < len(lines) and _is_table_separator(lines[index + 1])
        if table_block:
            _flush_paragraph(paragraph, story, styles, font_name)
            end = index + 2
            while end < len(lines) and lines[end].lstrip().startswith("|"):
                end += 1
            story.append(_table_rows(lines[index:end], font_name, styles["cell"]))
            story.append(Spacer(1, 8))
            index = end
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            _flush_paragraph(paragraph, story, styles, font_name)
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1:
                title = re.sub(r"[*`]", "", text)
                style = styles["title"]
            else:
                style = styles[f"h{level}"]
            story.append(Paragraph(_inline(text, font_name), style))
            index += 1
            continue

        if line.startswith("> "):
            _flush_paragraph(paragraph, story, styles, font_name)
            story.append(Paragraph(_inline(line[2:], font_name), styles["quote"]))
            index += 1
            continue

        if re.match(r"^\s*[-*]\s+", line):
            _flush_paragraph(paragraph, story, styles, font_name)
            items: list[ListItem] = []
            while index < len(lines) and re.match(r"^\s*[-*]\s+", lines[index]):
                text = re.sub(r"^\s*[-*]\s+", "", lines[index])
                items.append(ListItem(Paragraph(_inline(text, font_name), styles["body"])))
                index += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=16, bulletFontName=font_name))
            story.append(Spacer(1, 5))
            continue

        paragraph.append(line.strip())
        index += 1

    _flush_paragraph(paragraph, story, styles, font_name)
    return story, title


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args: object, header_title: str, font_name: str, draft: bool, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, object]] = []
        self._header_title = header_title
        self._font_name = font_name
        self._draft = draft

    def showPage(self) -> None:  # noqa: N802 - ReportLab API name
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(page_count)
            super().showPage()
        super().save()

    def _draw_header_footer(self, page_count: int) -> None:
        width, height = A4
        self.setStrokeColor(colors.HexColor("#9fbad0"))
        self.line(1.7 * cm, height - 1.45 * cm, width - 1.7 * cm, height - 1.45 * cm)
        self.setFont(self._font_name, 7.5)
        self.setFillColor(colors.HexColor("#595959"))
        self.drawString(1.7 * cm, height - 1.15 * cm, self._header_title[:95])
        self.drawRightString(width - 1.7 * cm, 1.05 * cm, f"Seite {self._pageNumber}/{page_count}")
        if self._draft:
            self.setFillColor(colors.HexColor("#a61c00"))
            self.drawCentredString(width / 2, 1.05 * cm, "DRAFT — Ergebnisse ausstehend")


def find_known_figures(results_dir: Path) -> list[Path]:
    figures: list[Path] = []
    for name in KNOWN_FIGURES:
        candidate = results_dir / name
        if not candidate.is_file():
            continue
        try:
            ImageReader(str(candidate)).getSize()
        except (OSError, ValueError):
            continue
        figures.append(candidate)
    return figures


def render_pdf(markdown_path: Path, output_path: Path, results_dir: Path | None = None, *, draft: bool = True) -> FontChoice:
    markdown_path = markdown_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font = discover_font()
    markdown = markdown_path.read_text(encoding="utf-8")
    story, title = markdown_story(markdown, font.name)

    figures = find_known_figures(results_dir) if results_dir else []
    if figures:
        story.append(Paragraph("Vorliegende Ergebnisabbildungen", _styles(font.name)["h2"]))
        for figure in figures:
            image = Image(str(figure))
            image._restrictSize(16.5 * cm, 22 * cm)
            story.extend([image, Paragraph(figure.stem.replace("_", " "), _styles(font.name)["caption"]), Spacer(1, 10)])

    document = SimpleDocTemplate(
        str(output_path), pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm,
        topMargin=2.0 * cm, bottomMargin=1.7 * cm, title=title, author="",
    )
    document.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(
            *args, header_title=title, font_name=font.name, draft=draft, **kwargs
        ),
    )
    return font


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Render study Markdown as PDF without generating results.")
    parser.add_argument("markdown", nargs="?", type=Path, default=here / "PAPER.md")
    parser.add_argument("--output", type=Path, default=here / "PAPER.pdf")
    parser.add_argument("--results-dir", type=Path, default=here.parent / "results")
    parser.add_argument("--final", action="store_true", help="remove the default DRAFT footer after result finalization")
    args = parser.parse_args()
    font = render_pdf(args.markdown, args.output, args.results_dir, draft=not args.final)
    print(f"Wrote {args.output} (Unicode-TTF: {font.path or font.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
