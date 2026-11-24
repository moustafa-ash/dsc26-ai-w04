# Retrieval evaluation

Setup: all 8 contracts in `data/contracts/`, `chunk_text(..., max_chars=500, overlap=50)`,
`HashingEmbedder()`, the 12 queries in `data/queries.jsonl`. A hit is relevant when its span
overlaps one of the query's `relevant` ranges in the same document.

| Retriever | recall@3 | queries missed |
|---|---|---|
| BM25 only | 11/12 (91.7%) | q12 |
| Dense only (HashingEmbedder) | 10/12 (83.3%) | q09, q12 |
| Hybrid (RRF) | 11/12 (91.7%) | q12 |

Both missed queries use English to find a clause in a bilingual contract. The hybrid run recovered the distributor territory query (q09) via BM25, but all three missed the agency governing-law query (q12), whose English heading uses “jurisdiction” while the question asks for the “competent court.” Next I would test a multilingual semantic embedder against the same queries and measure whether it improves cases like q12 without losing hits on the other queries.
