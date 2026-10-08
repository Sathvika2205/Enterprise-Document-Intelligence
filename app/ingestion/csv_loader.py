import pandas as pd

from app.ingestion.models import DocumentContent


def load_csv(
    file_path: str,
    rows_per_chunk: int = 50,
) -> list[DocumentContent]:

    dataframe = pd.read_csv(
        file_path
    )

    columns = dataframe.columns

    documents = []

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
                file_type="csv",
                row=start + 2,
            )
        )

    return documents
