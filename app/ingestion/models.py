from pydantic import BaseModel
from typing import Optional


class DocumentContent(BaseModel):
    text: str
    source: str
    file_type: str

    page: Optional[int] = None
    section: Optional[str] = None
    sheet: Optional[str] = None
    row: Optional[int] = None