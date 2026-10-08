from app.agents.tools import search_documents


documents = search_documents(
    "Who manages Aditi Sharma?"
)

for document in documents:
    print("\n---")
    print("Score:", document.metadata.get("retrieval_score"))
    print("Source:", document.metadata.get("source"))
    print("Content:", document.page_content[:300])