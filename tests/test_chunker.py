from app.ingestion.pdf_loader import load_pdf
from app.ingestion.chunker import chunk_documents


pdf_path = "data/raw/employee_policy.pdf"

pages = load_pdf(pdf_path)

chunks = chunk_documents(pages)

print(f"Total chunks: {len(chunks)}")

for i, chunk in enumerate(chunks[:5], start=1):
    print(f"\n--- Chunk {i} ---")
    print(f"Source: {chunk['source']}")
    print(f"Page: {chunk['page']}")
    print(f"Text: {chunk['text']}")