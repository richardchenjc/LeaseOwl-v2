"""PDF text extraction with explicit failure modes.

v1 returned None on any problem, leaving the user with a generic error.
v2 distinguishes the cases a user can act on: a scanned (image-only) PDF
is reported as such, and extraction quality is measured so downstream
code can warn instead of silently analysing garbage.
"""

from __future__ import annotations

from dataclasses import dataclass

import pdfplumber

# Below this many characters per page, the PDF is almost certainly a
# scan (image-only) rather than digital text.
SCANNED_CHARS_PER_PAGE = 200


@dataclass
class ExtractionResult:
    text: str
    n_pages: int
    chars_per_page: float
    likely_scanned: bool


def extract_text(pdf_path_or_file) -> ExtractionResult:
    """Extract text from a PDF, reporting quality signals.

    Accepts a path or an in-memory file object (Streamlit upload).
    """
    with pdfplumber.open(pdf_path_or_file) as pdf:
        pages = [(page.extract_text() or "") for page in pdf.pages]
    text = "\n".join(pages)
    n_pages = max(len(pages), 1)
    cpp = len(text) / n_pages
    return ExtractionResult(
        text=text,
        n_pages=n_pages,
        chars_per_page=cpp,
        likely_scanned=cpp < SCANNED_CHARS_PER_PAGE,
    )
