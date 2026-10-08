from app.graph.workflow import build_graph
from app.evaluation.dataset import EVALUATION_DATASET


def run_evaluation(org_id: str):
    """Score retrieval: does the expected text/source appear in the passages?"""
    graph = build_graph()

    total = len(EVALUATION_DATASET)
    answer_correct_count = 0
    source_correct_count = 0

    print("=" * 70)
    print("ENTERPRISE DOCUMENT INTELLIGENCE EVALUATION")
    print("=" * 70)

    for item in EVALUATION_DATASET:
        question = item["question"]

        print("\n" + "-" * 70)
        print(f"QUESTION: {question}")

        result = graph.invoke(
            {
                "question": question,
                "org_id": org_id,
            }
        )

        sources = result.get("sources", [])
        passages = "\n".join(source.get("content", "") for source in sources)

        expected_answer = item.get("expected_answer")
        expected_source = item.get("expected_source")

        # -------------------------------------------------
        # Answer evaluation
        # -------------------------------------------------

        if expected_answer is None:
            answer_correct = not result.get("evidence_sufficient", False)
        else:
            answer_correct = (
                expected_answer.lower() in passages.lower()
            )

        # -------------------------------------------------
        # Source evaluation
        # -------------------------------------------------

        source_correct = False

        if expected_source:
            source_correct = any(
                expected_source.lower()
                in source.get("source", "").lower()
                for source in sources
            )

        if answer_correct:
            answer_correct_count += 1

        if source_correct:
            source_correct_count += 1

        print(f"EXPECTED TEXT RETRIEVED: {answer_correct}")
        print(f"SOURCE CORRECT: {source_correct}")
        print(f"CONFLICT: {result.get('has_conflict')}")

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    answer_accuracy = answer_correct_count / total
    source_accuracy = source_correct_count / total

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Text retrieval accuracy: "
        f"{answer_correct_count}/{total} "
        f"({answer_accuracy:.1%})"
    )

    print(
        f"Source accuracy: "
        f"{source_correct_count}/{total} "
        f"({source_accuracy:.1%})"
    )


if __name__ == "__main__":
    import sys

    run_evaluation(sys.argv[1])