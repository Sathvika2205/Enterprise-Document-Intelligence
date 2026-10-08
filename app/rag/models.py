from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

FileType = Literal["pdf", "docx", "xlsx", "csv", "unknown"]


def normalize_file_type(value: Optional[str]) -> FileType:
    if value is None:
        return "unknown"

    normalized = str(value).strip().lower().lstrip(".")
    if normalized in {"pdf", "docx", "xlsx", "csv"}:
        return normalized
    if normalized == "xls":
        return "xlsx"
    return "unknown"


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    content: str = Field(min_length=1)

    file_type: FileType

    page: Optional[int] = Field(default=None, ge=0)
    section: Optional[str] = None
    sheet: Optional[str] = None
    row: Optional[int] = Field(default=None, ge=0)

    @classmethod
    def from_metadata(cls, metadata: dict, content: str) -> "Source":
        file_type = normalize_file_type(metadata.get("file_type"))
        source = metadata.get("source") or metadata.get("file_name") or "Unknown"

        return cls(
            source=source,
            content=content,
            file_type=file_type,
            page=metadata.get("page"),
            section=metadata.get("section"),
            sheet=metadata.get("sheet"),
            row=metadata.get("row"),
        )


class RAGResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    sources: list[Source]
