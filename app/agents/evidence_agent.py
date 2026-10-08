from app.rag.models import Source


def build_evidence(state):
    documents = state.get("retrieved_documents", [])

    sources = []

    for document in documents:
        sources.append(
            Source.from_metadata(document.metadata, document.page_content).model_dump()
        )

    return {
        "sources": sources
    }