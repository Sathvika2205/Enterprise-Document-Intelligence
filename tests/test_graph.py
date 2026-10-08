from app.graph.workflow import build_graph


graph = build_graph()

result = graph.invoke(
    {
        "question": "How many days of annual leave do full-time employees receive?",
        "org_id": "REPLACE_WITH_ORG_ID",
    }
)

print("\nFINAL STATE:")
print(result)

print("\nSources:")
for source in result.get("sources", []):
    print(source)

print("\nEvidence sufficient:")
print(result.get("evidence_sufficient"))