from __future__ import annotations

import base64
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    PdfReader = None

sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_pdf import discover_font, find_known_figures, render_pdf
import render_pdf as renderer


SAMPLE = """# Überblick für München

## Methode & Grenzen < sicher

Ein **fetter** Satz mit `Code`, Umlauten ÄÖÜäöüß und einem [Link](https://example.invalid/?a=1&b=2).

- erster Punkt
- zweiter Punkt

| Achse | Wert |
|---|---|
| Direktheit | 4 |

> Ergebnisse ausstehend.

""" + ("Mehrseitiger Prüftext mit deutscher Zeichensetzung.\n\n" * 90)


class RenderPdfTest(unittest.TestCase):
    def test_renderer_handles_markdown_unicode_and_page_furniture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "PAPER.md"
            output = root / "PAPER_DRAFT_SMOKE.pdf"
            source.write_text(SAMPLE, encoding="utf-8")

            font = render_pdf(source, output, root, draft=True)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 3_000)
            self.assertIn(font.name, {"StudyUnicode", "Helvetica"})

            self.assertTrue(output.read_bytes().startswith(b"%PDF"))
            if PdfReader is None:
                self.skipTest("pypdf fehlt; PDF-Inhaltsprüfung benötigt den gebündelten Test-Interpreter.")
            reader = PdfReader(str(output))
            extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
            self.assertGreaterEqual(len(reader.pages), 2)
            self.assertIn("Überblick für München", extracted)
            self.assertIn("erster Punkt", extracted)
            self.assertIn("Direktheit", extracted)
            self.assertIn("Seite 1/", extracted)
            self.assertIn("DRAFT", extracted)

    def test_known_figures_are_opt_in_and_only_existing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(find_known_figures(root), [])
            figure = root / "main_axis_means.png"
            figure.write_bytes(b"not rendered in this unit test")
            self.assertEqual(find_known_figures(root), [])
            figure.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL9fQAAAABJRU5ErkJggg=="))
            self.assertEqual(find_known_figures(root), [figure])

    def test_invalid_optional_figure_cannot_block_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "PAPER.md"
            source.write_text("# Test\n\nErgebnisse ausstehend.\n", encoding="utf-8")
            (root / "main_axis_means.png").write_bytes(b"invalid")
            output = root / "PAPER_DRAFT_SMOKE.pdf"
            render_pdf(source, output, root)
            self.assertTrue(output.is_file())

    def test_default_rendering_is_a_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            if PdfReader is None:
                self.skipTest("pypdf fehlt; Footer-Prüfung benötigt den gebündelten Test-Interpreter.")
            root = Path(temporary)
            source = root / "PAPER.md"
            source.write_text("# Test\n\nErgebnisse ausstehend.\n", encoding="utf-8")
            output = root / "PAPER_DRAFT_SMOKE.pdf"
            render_pdf(source, output, root)
            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(output)).pages)
            self.assertIn("DRAFT", text)

    def test_font_discovery_requires_a_unicode_ttf(self) -> None:
        choice = discover_font()
        self.assertTrue(choice.name)
        self.assertTrue(choice.supports_unicode)
        self.assertIsNotNone(choice.path)

    def test_bundled_vera_is_a_portable_unicode_fallback(self) -> None:
        bundled_fonts = Path(renderer.reportlab.__file__).resolve().parent / "fonts"
        vera = bundled_fonts / "Vera.ttf"
        if not vera.is_file():
            self.skipTest("Diese ReportLab-Distribution liefert Vera.ttf nicht mit.")
        with patch.dict(renderer.os.environ, {"CHATGPT_VPN_PDF_FONT": ""}), patch.object(
            renderer, "_font_directories", return_value=iter((bundled_fonts,))
        ):
            choice = renderer.discover_font()
        self.assertEqual(choice.path.resolve(), vera.resolve())
        self.assertTrue(choice.supports_unicode)


if __name__ == "__main__":
    unittest.main()
