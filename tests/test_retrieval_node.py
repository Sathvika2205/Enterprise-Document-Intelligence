from app.graph.nodes import retrieve_documents


state = {
    "question": "How many days of annual leave do full-time employees receive?"
}

result = retrieve_documents(state)

print("Retrieved documents:", len(result["retrieved_documents"]))

for document in result["retrieved_documents"]:
    print("\n---")
    print("Page:", document.metadata.get("page"))
    print(document.page_content[:300])