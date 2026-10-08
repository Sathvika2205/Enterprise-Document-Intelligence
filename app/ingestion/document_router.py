from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.docx_loader import load_docx
from app.ingestion.csv_loader import load_csv
from app.ingestion.excel_loader import load_excel


def load_document(file_path: str):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)

    elif extension == ".docx":
        return load_docx(file_path)

    elif extension == ".csv":
        return load_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        return load_excel(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )