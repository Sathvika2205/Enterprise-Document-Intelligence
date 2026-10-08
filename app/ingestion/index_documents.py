from app.organizations import organization_raw_dir
from app.ingestion.document_router import load_document
from app.ingestion.chunker import chunk_documents
from app.retrieval.vector_store import create_vector_store


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".csv", ".xlsx", ".xls"}


def index_documents(org_id: str):
    raw_dir = organization_raw_dir(org_id)

    all_documents = []

    for file_path in raw_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            print(f"Loading: {file_path}")

            documents = load_document(str(file_path))
            all_documents.extend(documents)

            print(f"  Loaded: {len(documents)} sections/rows")

    if not all_documents:
        raise ValueError(f"No supported documents found for organization '{org_id}'.")

    chunks = chunk_documents(all_documents)

    print(f"\nTotal documents/rows: {len(all_documents)}")
    print(f"Total chunks: {len(chunks)}")

    vector_store = create_vector_store(chunks, org_id)

    print(f"Documents successfully indexed into Chroma for organization '{org_id}'.")

    return vector_store


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.ingestion.index_documents <org_id>")

    index_documents(sys.argv[1])
