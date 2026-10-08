from app.ingestion.loader import load_text_file


file_path = "data/raw/sample_policy.txt"

text = load_text_file(file_path)

print(text)