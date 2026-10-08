import math
import re
from collections import Counter
from typing import Optional

from langchain_core.documents import Document

from app.retrieval.vector_store import load_vector_store


# Words that carry no search value. Left in, they would add noise to
# the keyword score of every chunk.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for",
    "from", "has", "have", "how", "i", "in", "is", "it", "many", "much",
    "of", "on", "or", "show", "tell", "that", "the", "their", "there",
    "this", "to", "was", "were", "what", "when", "where", "which", "who",
    "whom", "with",
}

K1 = 1.5
B = 0.75

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())


def tokenize_query(text: str) -> list[str]:
    tokens = [token for token in tokenize(text) if token not in STOPWORDS]

    # A query made only of stopwords should still search for something.
    return tokens or tokenize(text)


class _KeywordIndex:
    """In-memory BM25 index over every chunk of one organization."""

    def __init__(self, texts: list[str], metadatas: list[dict]):
        self.texts = texts
        self.metadatas = metadatas

        self.term_counts = [Counter(tokenize(text)) for text in texts]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.average_length = (
            sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        )

        self.document_frequency: Counter = Counter()
        for counts in self.term_counts:
            self.document_frequency.update(counts.keys())

    def _idf(self, term: str) -> float:
        total = len(self.texts)
        frequency = self.document_frequency.get(term, 0)

        return math.log(1 + (total - frequency + 0.5) / (frequency + 0.5))

    def search(
        self,
        query_tokens: list[str],
        k: int,
        allowed_sources: Optional[list[str]] = None,
    ) -> list[Document]:
        if not query_tokens or not self.texts:
            return []

        scored = []

        for index, counts in enumerate(self.term_counts):
            if allowed_sources and (
                self.metadatas[index].get("source") not in allowed_sources
            ):
                continue

            length_norm = 1 - B + B * (
                self.lengths[index] / (self.average_length or 1)
            )

            score = 0.0

            for term in set(query_tokens):
                frequency = counts.get(term, 0)

                if frequency:
                    score += self._idf(term) * (
                        frequency * (K1 + 1)
                        / (frequency + K1 * length_norm)
                    )

            if score > 0:
                scored.append((score, index))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [
            Document(
                page_content=self.texts[index],
                metadata=dict(self.metadatas[index]),
            )
            for _, index in scored[:k]
        ]


# org_id -> (signature of the indexed chunks, index)
_INDEX_CACHE: dict[str, tuple[int, _KeywordIndex]] = {}


def _get_index(org_id: str) -> _KeywordIndex:
    """Build the keyword index once, and rebuild it when the chunks change."""

    vector_store = load_vector_store(org_id)
    stored = vector_store.get(include=["documents", "metadatas"])

    signature = hash(tuple(stored["ids"]))
    cached = _INDEX_CACHE.get(org_id)

    if cached and cached[0] == signature:
        return cached[1]

    index = _KeywordIndex(
        texts=stored["documents"] or [],
        metadatas=stored["metadatas"] or [],
    )

    _INDEX_CACHE[org_id] = (signature, index)

    return index


def keyword_search(
    question: str,
    org_id: str,
    k: int = 10,
    allowed_sources: Optional[list[str]] = None,
) -> list[Document]:
    return _get_index(org_id).search(
        tokenize_query(question),
        k=k,
        allowed_sources=allowed_sources,
    )
