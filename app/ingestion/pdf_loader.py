import pymupdf

from app.ingestion.models import DocumentContent


def load_pdf(file_path: str) -> list[DocumentContent]:
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text.strip():
            pages.append(
                DocumentContent(
                    text=text,
                    source=file_path,
                    file_type="pdf",
                    page=page_number,
                )
            )

    document.close()

    return pages