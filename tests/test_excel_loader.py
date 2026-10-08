from app.ingestion.excel_loader import load_excel


excel_path = "data/raw/employees.xlsx"

rows = load_excel(excel_path)

print(f"Total rows: {len(rows)}")

for row in rows:
    print("\n--- Row ---")
    print(f"Source: {row.source}")
    print(f"Row: {row.page}")
    print(row.text)