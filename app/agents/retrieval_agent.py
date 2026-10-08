from app.agents.tools import search_documents


def retrieval_agent(state):
    question = state["question"]

    documents = search_documents(
        question=question,
        org_id=state["org_id"],
        k=5,
        allowed_sources=state.get("allowed_sources"),
    )

    return {
        "retrieved_documents": documents
    }