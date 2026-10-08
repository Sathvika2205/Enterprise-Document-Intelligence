from typing import TypedDict, Any, Optional


class GraphState(TypedDict, total=False):
    question: str
    org_id: str
    allowed_sources: Optional[list[str]]
    retrieved_documents: list[Any]
    answer: str
    llm_error: Optional[str]
    sources: list[dict]
    evidence_sufficient: bool
    conflicts: list[str]
    has_conflict: bool
