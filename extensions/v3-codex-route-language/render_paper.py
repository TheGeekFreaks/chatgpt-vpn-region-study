"""Render the V3 pilot manuscript to a local, print-friendly PDF.

The renderer reads only the supplied Markdown and linked local figures.  It
does not calculate scores, access private captures, or fetch network content.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path
from typing import Iterable

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
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


FONT_NAME = "CodexV3Unicode"
ACCENT = colors.HexColor("#214E78")
LIGHT_ACCENT = colors.HexColor("#E6F0F8")
PAGE_WIDTH, PAGE_HEIGHT = A4


def font_families() -> Iterable[tuple[Path, Path, Path, Path]]:
    """Yield complete Unicode font families without embedding a workstation path."""
    bundled = Path(__file__).resolve().parent / "fonts"
    if sys.platform.startswith("win"):
        windows = Path(os.environ.get("WINDIR", ""))
        if windows:
            fonts = windows / "Fonts"
            yield (fonts / "arial.ttf", fonts / "arialbd.ttf", fonts / "ariali.ttf", fonts / "arialbi.ttf")
            yield (fonts / "Arial.ttf", fonts / "Arialbd.ttf", fonts / "Ariali.ttf", fonts / "Arialbi.ttf")
    reportlab_fonts = Path(reportlab.__file__).resolve().parent / "fonts"
    yield (reportlab_fonts / "Vera.ttf", reportlab_fonts / "VeraBd.ttf", reportlab_fonts / "VeraIt.ttf", reportlab_fonts / "VeraBI.ttf")
    yield (bundled / "Vera.ttf", bundled / "VeraBd.ttf", bundled / "VeraIt.ttf", bundled / "VeraBI.ttf")


def register_font() -> str:
    for regular, bold, italic, bold_italic in font_families():
        if all(candidate.is_file() for candidate in (regular, bold, italic, bold_italic)):
            pdfmetrics.registerFont(TTFont(FONT_NAME, str(regular)))
            pdfmetrics.registerFont(TTFont("CodexV3Bold", str(bold)))
            pdfmetrics.registerFont(TTFont("CodexV3Italic", str(italic)))
            pdfmetrics.registerFont(TTFont("CodexV3BoldItalic", str(bold_italic)))
            pdfmetrics.registerFontFamily(
                FONT_NAME,
                normal=FONT_NAME,
                bold="CodexV3Bold",
                italic="CodexV3Italic",
                boldItalic="CodexV3BoldItalic",
            )
            return FONT_NAME
    raise RuntimeError("Keine vollständige Unicode-Schriftfamilie für den PDF-Bericht gefunden.")


def inline(markdown: str, font_name: str) -> str:
    escaped = html.escape(markdown, quote=False)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda match: f'<link href="{html.escape(html.unescape(match.group(2)), quote=True)}" color="#214E78">{match.group(1)}</link>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", rf'<font name="{font_name}">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", escaped)
    return escaped


def is_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def styles(font_name: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    body = ParagraphStyle("V3Body", parent=base["BodyText"], fontName=font_name, fontSize=9.2, leading=12.6, spaceAfter=6)
    return {
        "body": body,
        "title": ParagraphStyle("V3Title", parent=base["Title"], fontName=font_name, fontSize=19, leading=23, textColor=ACCENT, spaceAfter=12, keepWithNext=True),
        "h2": ParagraphStyle("V3H2", parent=base["Heading2"], fontName=font_name, fontSize=13.4, leading=17, textColor=ACCENT, spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "h3": ParagraphStyle("V3H3", parent=base["Heading3"], fontName=font_name, fontSize=10.8, leading=13, textColor=ACCENT, spaceBefore=9, spaceAfter=4, keepWithNext=True),
        "cell": ParagraphStyle("V3Cell", parent=body, fontName=font_name, fontSize=7.2, leading=8.8, spaceAfter=0),
        "caption": ParagraphStyle("V3Caption", parent=body, alignment=TA_CENTER, fontSize=7.8, leading=9.5, textColor=colors.HexColor("#555555")),
    }


def flush_paragraph(buffer: list[str], story: list[object], style: ParagraphStyle, font_name: str) -> None:
    if buffer:
        story.append(Paragraph(inline(" ".join(buffer), font_name), style))
        buffer.clear()


def table_from_lines(lines: list[str], cell_style: ParagraphStyle, font_name: str, available_width: float) -> Table:
    parsed = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [parsed[0], *parsed[2:]] if len(parsed) > 1 and is_separator(lines[1]) else parsed
    count = max(len(row) for row in rows)
    normalized = [row + [""] * (count - len(row)) for row in rows]
    cells = [[Paragraph(inline(value, font_name), cell_style) for value in row] for row in normalized]
    table = Table(cells, colWidths=[available_width / count] * count, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT),
        ("FONTNAME", (0, 0), (-1, 0), font_name),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#A9C2D7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def story_from_markdown(markdown: str, root: Path, font_name: str) -> list[object]:
    style = styles(font_name)
    story: list[object] = []
    paragraph: list[str] = []
    lines = markdown.splitlines()
    index = 0
    available_width = PAGE_WIDTH - 3.6 * cm
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            flush_paragraph(paragraph, story, style["body"], font_name)
            index += 1
            continue
        if line.lstrip().startswith("|") and index + 1 < len(lines) and is_separator(lines[index + 1]):
            flush_paragraph(paragraph, story, style["body"], font_name)
            end = index + 2
            while end < len(lines) and lines[end].lstrip().startswith("|"):
                end += 1
            story.extend((table_from_lines(lines[index:end], style["cell"], font_name, available_width), Spacer(1, 8)))
            index = end
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line.strip())
        if image:
            flush_paragraph(paragraph, story, style["body"], font_name)
            reference = Path(image.group(2))
            if reference.is_absolute():
                raise ValueError(f"Figure path must be relative to the manuscript directory: {reference}")
            allowed_root = root.resolve()
            target = (allowed_root / reference).resolve()
            try:
                target.relative_to(allowed_root)
            except ValueError as exc:
                raise ValueError(f"Figure path escapes manuscript directory: {reference}") from exc
            if not target.is_file():
                raise FileNotFoundError(f"Referenced figure does not exist: {target} (Markdown line {index + 1})")
            figure = Image(str(target))
            figure._restrictSize(available_width, 14.5 * cm)
            story.extend((figure, Paragraph(inline(image.group(1), font_name), style["caption"]), Spacer(1, 6)))
            index += 1
            continue
        heading = re.fullmatch(r"(#{1,3})\s+(.+)", line)
        if heading:
            flush_paragraph(paragraph, story, style["body"], font_name)
            level = len(heading.group(1))
            story.append(Paragraph(inline(heading.group(2), font_name), style["title" if level == 1 else f"h{level}"],))
            index += 1
            continue
        if re.fullmatch(r"\s*[-*]\s+.+", line):
            flush_paragraph(paragraph, story, style["body"], font_name)
            items: list[ListItem] = []
            while index < len(lines) and re.fullmatch(r"\s*[-*]\s+.+", lines[index]):
                items.append(ListItem(Paragraph(inline(re.sub(r"^\s*[-*]\s+", "", lines[index]), font_name), style["body"])))
                index += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=16))
            continue
        if line.startswith("*") and line.endswith("*"):
            flush_paragraph(paragraph, story, style["body"], font_name)
            story.append(Paragraph(inline(line, font_name), style["caption"]))
            index += 1
            continue
        paragraph.append(line.strip())
        index += 1
    flush_paragraph(paragraph, story, style["body"], font_name)
    return story


class NumberedCanvas(canvas.Canvas):
    """Add a concise footer after ReportLab has counted all pages."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.pages: list[dict[str, object]] = []

    def showPage(self) -> None:  # noqa: N802 - ReportLab API name
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total = len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.setStrokeColor(colors.HexColor("#B7C9D9"))
            self.line(1.8 * cm, 1.35 * cm, PAGE_WIDTH - 1.8 * cm, 1.35 * cm)
            self.setFillColor(colors.HexColor("#5B6F82"))
            self.setFont(FONT_NAME, 7.5)
            self.drawString(1.8 * cm, 0.9 * cm, "Codex-Astra-Pilot | öffentliche Methoden- und Aggregatansicht")
            self.drawRightString(PAGE_WIDTH - 1.8 * cm, 0.9 * cm, f"Seite {self._pageNumber} von {total}")
            super().showPage()
        super().save()


def render(markdown_path: Path, output_path: Path) -> None:
    font = register_font()
    document = SimpleDocTemplate(
        str(output_path), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.65 * cm, bottomMargin=1.8 * cm, title="Codex-Astra-Pilot",
        author="Lokale Studienartefakte",
    )
    document.build(story_from_markdown(markdown_path.read_text(encoding="utf-8"), markdown_path.parent, font), canvasmaker=NumberedCanvas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the public V3 pilot manuscript without calculating results.")
    parser.add_argument("markdown", nargs="?", type=Path, default=Path(__file__).with_name("PAPER.md"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("PAPER.pdf"))
    args = parser.parse_args()
    render(args.markdown.resolve(), args.output.resolve())
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
