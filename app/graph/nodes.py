from app.retrieval.vector_store import load_vector_store


def retrieve_documents(state):
    question = state["question"]

    vector_store = load_vector_store()

    results = vector_store.similarity_search_with_score(
        question,
        k=3,
    )

    documents = []

    for document, score in results:
        document.metadata["retrieval_score"] = score
        documents.append(document)

    return {
        "retrieved_documents": documents
    }


def check_evidence(state):
    documents = state.get("retrieved_documents", [])

    if not documents:
        return {"evidence_sufficient": False}

    # Chroma's raw L2 distance score doesn't have a fixed meaningful scale
    # across different content/questions (relevant matches have scored
    # anywhere from ~1.0 to ~1.5), so a hard absolute cutoff here produces
    # false negatives. The retrieved top-k are already the closest matches
    # available; the user judges relevance from the returned passages and
    # their scores.
    return {
        "evidence_sufficient": True,
        "retrieved_documents": documents,
    }