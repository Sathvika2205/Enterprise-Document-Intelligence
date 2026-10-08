from app.ingestion.docx_loader import load_docx


docx_path = "data/raw/sample.docx"

sections = load_docx(docx_path)

print(f"Total sections: {len(sections)}")

for section in sections:
    print("\n--- Section ---")
    print(f"Source: {section.source}")
    print(f"Page/Section: {section.page}")
    print(section.text[:1000])