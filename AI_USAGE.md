# AI usage

## Tools I used, and for what

Codex drafted the Python modules and a verification script. Python and pytest checked the code against the starter tests and computed recall on the supplied queries.

## Where AI-written chunking or BM25 code broke one of the spec's rules

I checked a fixed-stride chunking draft against `alpha beta gamma. delta epsilon zeta eta.` with a 20-character window and no overlap. The preferred sentence cut stops at the period, but restarting at offset 20 skips the first two letters of `delta`, violating the coverage rule. The final loop advances from the actual cut, and the checked output starts its next chunk at `delta`. I also checked coverage, offsets and cut preference on 1,500 generated inputs.

## My recall@3 table (from EVAL.md) and why hybrid did or did not win

| Retriever | Recall@3 |
|---|---:|
| BM25 only | 11/12 (91.7%) |
| Dense only | 10/12 (83.3%) |
| Hybrid | 11/12 (91.7%) |

Hybrid tied BM25 because fusion carried forward the lexical hit for q09, but neither retriever placed the right q12 span high enough for fusion to recover it.
