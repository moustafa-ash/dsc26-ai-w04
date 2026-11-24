"""Reciprocal rank fusion and the hybrid retriever. You write this file."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from math import fsum

from bayyina.bm25 import BM25Index
from bayyina.types import Chunk, Embedder, Hit, Reranker


def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Ranks start at 1; score = sum of 1 / (k + rank); by score descending, then ID ascending."""
    contributions = defaultdict(list)
    for ranking in rankings:
        seen = set()
        for rank, chunk_id in enumerate(ranking, 1):
            if chunk_id not in seen:
                contributions[chunk_id].append(1 / (k + rank))
                seen.add(chunk_id)
    scores = [(chunk_id, fsum(values)) for chunk_id, values in contributions.items()]
    return sorted(scores, key=lambda result: (-result[1], result[0]))


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], embedder: Embedder, *, k1: float = 1.5,
                 b: float = 0.75, reranker: Reranker | None = None):
        self.chunks = {chunk.chunk_id: chunk for chunk in chunks}
        self.ids = list(self.chunks)
        self.embedder = embedder
        self.embeddings = embedder.embed([self.chunks[chunk_id].text for chunk_id in self.ids]) if self.ids else None
        self.bm25 = BM25Index(k1=k1, b=b)
        self.bm25.add(chunks)
        self.reranker = reranker

    def search(self, query: str, top_k: int = 5, candidates: int = 50) -> list[Hit]:
        if not query.strip() or not self.ids or candidates <= 0 or top_k <= 0:
            return []
        lexical = [chunk_id for chunk_id, _ in self.bm25.search(query, candidates)]
        similarities = self.embeddings @ self.embedder.embed([query])[0]
        dense = sorted(zip(self.ids, similarities), key=lambda item: (-item[1], item[0]))
        fused = rrf([lexical, [chunk_id for chunk_id, _ in dense[:candidates]]])
        hits = []
        for chunk_id, score in fused[:candidates]:
            chunk = self.chunks[chunk_id]
            hits.append(Hit(chunk_id, chunk.doc_id, chunk.start, chunk.end, chunk.text, score))
        if self.reranker is not None:
            scores = self.reranker(query, hits)
            hits = [replace(hit, score=float(score)) for hit, score in zip(hits, scores, strict=True)]
            hits.sort(key=lambda hit: (-hit.score, hit.chunk_id))
        return hits[:top_k]
