"""PDF text extraction.

Reads every page of a PDF and keeps the source file and page number next to
the text, so that later steps can cite exactly where an answer comes from.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import pdfplumber

# Footer printed on every page of the Bulletin officiel, e.g. "esr.gouv.fr BO n° 9 12".
# It carries no meaning and can cut a sentence in half between two pages.
FOOTER_PATTERN = re.compile(r"^esr\.gouv\.fr BO n° \d+ \d+$", re.MULTILINE)


@dataclass
class Page:
    source: str
    page: int
    text: str


def clean_text(text: str) -> str:
    """Remove the running footer and surrounding whitespace."""
    return FOOTER_PATTERN.sub("", text).strip()


def extract_pages(pdf_path: Path) -> list[Page]:
    """Return one Page per PDF page, in order. Empty pages keep an empty text."""
    pages: list[Page] = []
    with pdfplumber.open(pdf_path) as pdf:
        for pdf_page in pdf.pages:
            raw_text = pdf_page.extract_text() or ""  # extract_text() returns None on empty pages
            pages.append(
                Page(source=pdf_path.name, page=pdf_page.page_number, text=clean_text(raw_text))
            )
    return pages


def save_jsonl(pages: list[Page], output_path: Path) -> None:
    """Write one JSON object per line, so files can be read page by page."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for page in pages:
            f.write(json.dumps(asdict(page), ensure_ascii=False) + "\n")


def main() -> None:
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")

    for pdf_path in sorted(raw_dir.glob("*.pdf")):
        pages = extract_pages(pdf_path)
        output_path = processed_dir / f"{pdf_path.stem}.jsonl"
        save_jsonl(pages, output_path)

        empty_pages = sum(1 for p in pages if not p.text)
        print(f"{pdf_path.name}: {len(pages)} pages -> {output_path} ({empty_pages} empty)")


if __name__ == "__main__":
    main()