"""Citation checks. You write this file."""
from __future__ import annotations

from bayyina.types import Hit


def verify_citation(quote: str, document: str, start: int, end: int) -> bool:
    collapsed = " ".join(quote.split())
    return 0 <= start < end <= len(document) and bool(collapsed) and collapsed in " ".join(document[start:end].split())


def format_citation(hit: Hit, max_quote: int = 160) -> str:
    """[doc_id:start-end] "quote" """
    quote = " ".join(hit.text.split())
    if len(quote) > max_quote:
        prefix = quote[:max_quote]
        boundary = prefix.rfind(" ")
        quote = (prefix[:boundary] if boundary >= 0 else prefix) + "…"
    return f'[{hit.doc_id}:{hit.start}-{hit.end}] "{quote}"'
