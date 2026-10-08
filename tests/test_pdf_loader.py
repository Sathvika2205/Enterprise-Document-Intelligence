from app.ingestion.pdf_loader import load_pdf


pdf_path = "data/raw/employee_policy.pdf"

pages = load_pdf(pdf_path)

print(f"Total pages: {len(pages)}")

for page in pages:
    print(page.page)
    print(page.text)