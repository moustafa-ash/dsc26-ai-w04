"""Offset-preserving chunker. You write this file. See README.md for the seven rules."""
from __future__ import annotations

from bayyina.types import Chunk

_SENTENCE_ENDS = ".!?؟۔\n"


def _preferred_cut(window: str) -> int:
    half = max(1, len(window) // 2)
    last_paragraph = window.rfind("\n\n") + 2
    if last_paragraph >= max(2, half):
        return last_paragraph
    last_space = None
    for cut in range(len(window), half - 1, -1):
        marker = window[cut - 1]
        if marker in _SENTENCE_ENDS:
            return cut
        if last_space is None and marker.isspace():
            last_space = cut
    return last_space if last_space is not None else len(window)


def chunk_text(doc_id: str, text: str, max_chars: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split `text` into chunks whose offsets point into the ORIGINAL text.

    ValueError unless max_chars > 0 and 0 <= overlap < max_chars.
    """
    if max_chars <= 0 or not 0 <= overlap < max_chars:
        raise ValueError("Require max_chars > 0 and 0 <= overlap < max_chars")
    chunks = []
    length = len(text)
    start = 0
    while start < length and text[start].isspace():
        start += 1
    while start < length:
        can_finish = length - start <= max_chars
        cut = length if can_finish else start + _preferred_cut(text[start:start + max_chars])
        span = text[start:cut].rstrip()
        end = start + len(span)
        chunks.append(Chunk(doc_id, f"{doc_id}#{len(chunks)}", start, end, span))
        if can_finish:
            break

        midword = end < length and not text[end - 1].isspace() and not text[end].isspace()
        start = max(start + 1, end - overlap)
        while start < length and (
            text[start].isspace() or (not midword and not text[start - 1].isspace())
        ):
            start += 1
    return chunks
