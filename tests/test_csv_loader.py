from app.ingestion.csv_loader import load_csv


csv_path = "data/raw/employees.csv"

rows = load_csv(csv_path)

print(f"Total rows: {len(rows)}")

for row in rows:
    print("\n--- Row ---")
    print(f"Source: {row.source}")
    print(f"Row: {row.page}")
    print(row.text)