from app.ingestion.document_router import load_document


files = [
    "data/raw/employee_policy.pdf",
    "data/raw/sample.docx",
    "data/raw/employees.csv",
    "data/raw/employees.xlsx",
]


for file_path in files:
    print(f"\n{'=' * 60}")
    print(f"FILE: {file_path}")

    documents = load_document(file_path)

    print(f"Loaded sections/rows: {len(documents)}")

    if documents:
        print("First item:")
        print(documents[0].text[:300])