from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.models import DocumentContent


def chunk_documents(
    documents: list[DocumentContent],
) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )

    chunks = []

    for document in documents:
        document_chunks = splitter.split_text(document.text)

        for chunk in document_chunks:
            chunks.append(
                {
                    "text": chunk,
                    "source": document.source,
                    "file_type": document.file_type,
                    "page": document.page,
                    "section": document.section,
                    "sheet": document.sheet,
                    "row": document.row,
                }
            )

    return chunks