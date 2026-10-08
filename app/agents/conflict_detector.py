def detect_conflicts(state):
    documents = state.get("retrieved_documents", [])

    conflicts = []

    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            first = documents[i].page_content.lower()
            second = documents[j].page_content.lower()

            if (
                "annual leave" in first
                and "annual leave" in second
                and "18" in first
                and "20" in second
            ) or (
                "annual leave" in first
                and "annual leave" in second
                and "20" in first
                and "18" in second
            ):
                conflicts.append(
                    "Conflicting annual leave values found: "
                    "18 days vs 20 days."
                )

    return {
        "conflicts": conflicts,
        "has_conflict": bool(conflicts),
    }