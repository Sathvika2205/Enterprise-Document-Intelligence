from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import chunk_documents
from app.retrieval.vector_store import create_vector_store


pdf_path = "data/raw/employee_policy.pdf"

pages = load_pdf(pdf_path)

chunks = chunk_documents(pages)

vector_store = create_vector_store(chunks)

results = vector_store.similarity_search(
    "How many days of annual leave do employees receive?",
    k=3,
)

for i, result in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print(f"Page: {result.metadata['page']}")
    print(f"Source: {result.metadata['source']}")
    print(result.page_content)