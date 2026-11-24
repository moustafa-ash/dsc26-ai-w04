"""BM25, written by hand. You write this file (no search libraries)."""
from __future__ import annotations

from collections import Counter, defaultdict
from math import log1p

from bayyina.normalize import tokenize
from bayyina.types import Chunk


class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._lengths = {}
        self._postings = defaultdict(dict)

    def add(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            terms = tokenize(chunk.text)
            self._lengths[chunk.chunk_id] = len(terms)
            for term, frequency in Counter(terms).items():
                self._postings[term][chunk.chunk_id] = frequency

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """[(chunk_id, score), ...] with score > 0, by score descending then chunk ID ascending."""
        count = len(self._lengths)
        if not count or top_k <= 0:
            return []
        avgdl = sum(self._lengths.values()) / count
        scores = defaultdict(float)
        for term in sorted(set(tokenize(query))):
            posting = self._postings.get(term)
            if not posting:
                continue
            df = len(posting)
            idf = log1p((count - df + 0.5) / (df + 0.5))
            for chunk_id, frequency in posting.items():
                norm = 1 - self.b + self.b * self._lengths[chunk_id] / avgdl
                scores[chunk_id] += idf * frequency * (self.k1 + 1) / (frequency + self.k1 * norm)
        positive = [(chunk_id, score) for chunk_id, score in scores.items() if score > 0]
        return sorted(positive, key=lambda result: (-result[1], result[0]))[:top_k]
