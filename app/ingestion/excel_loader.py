import pandas as pd

from app.ingestion.models import DocumentContent


def load_excel(
    file_path: str,
    rows_per_chunk: int = 50,
) -> list[DocumentContent]:
    workbook = pd.ExcelFile(file_path)

    documents = []

    for sheet_name in workbook.sheet_names:
        dataframe = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
        )

        columns = dataframe.columns

        for start in range(
            0,
            len(dataframe),
            rows_per_chunk,
        ):

            batch = dataframe.iloc[
                start:start + rows_per_chunk
            ]

            rows = []

            for row_tuple in batch.itertuples(index=True):

                row_number = row_tuple[0] + 2
                values = row_tuple[1:]

                row_text = " | ".join(
                    f"{column}: {value}"
                    for column, value in zip(columns, values)
                )

                rows.append(
                    f"Row {row_number}: {row_text}"
                )

            documents.append(
                DocumentContent(
                    text="\n".join(rows),
                    source=file_path,
                    file_type="xlsx",
                    sheet=sheet_name,
                    row=start + 2,
                )
            )

    return documents
