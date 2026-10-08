from langchain_chroma import Chroma

from app.retrieval.embeddings import get_embedding_model


PERSIST_DIRECTORY = "data/chroma"


def _collection_name(org_id: str) -> str:
    return f"org_{org_id}"


def create_vector_store(chunks: list[dict], org_id: str):
    """
    Rebuild the entire vector store for one organization.
    Use this only for a full reindex of that organization.
    """

    embedding_model = get_embedding_model()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk["source"],
            "file_type": chunk["file_type"],
            "page": chunk["page"],
            "section": chunk["section"],
            "sheet": chunk["sheet"],
            "row": chunk["row"],
        }
        for chunk in chunks
    ]

    vector_store = Chroma(
        collection_name=_collection_name(org_id),
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )

    existing = vector_store.get()

    if existing["ids"]:
        vector_store.delete(
            ids=existing["ids"]
        )

    vector_store.add_texts(
        texts=texts,
        metadatas=metadatas,
    )

    return vector_store


def add_documents_to_vector_store(
    chunks: list[dict],
    org_id: str,
    batch_size: int = 256,
):
    """
    Add document chunks to one organization's Chroma collection, in batches.

    Batching prevents thousands of chunks from being
    processed in one huge operation.
    """

    embedding_model = get_embedding_model()

    vector_store = Chroma(
        collection_name=_collection_name(org_id),
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )

    total_chunks = len(chunks)

    for start in range(
        0,
        total_chunks,
        batch_size,
    ):

        batch = chunks[
            start:start + batch_size
        ]

        texts = [
            chunk["text"]
            for chunk in batch
        ]

        metadatas = [
            {
                "source": chunk["source"],
                "file_type": chunk["file_type"],
                "page": chunk["page"],
                "section": chunk["section"],
                "sheet": chunk["sheet"],
                "row": chunk["row"],
            }
            for chunk in batch
        ]

        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
        )

    return vector_store


def load_vector_store(org_id: str):

    embedding_model = get_embedding_model()

    return Chroma(
        collection_name=_collection_name(org_id),
        embedding_function=embedding_model,
        persist_directory=PERSIST_DIRECTORY,
    )
