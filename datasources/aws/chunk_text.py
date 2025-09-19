import re
from typing import List

_SENTENCE_BOUNDARY_RE = re.compile(
    r"""
    # Split after a sentence ender (., !, ?, or common CJK enders)
    (?<=[.!?]|[。！？])
    # Optional closing quotes/brackets right after the ender
    [\'")\]\u3001\u3002\u300D\u300F\uFF09\uFF3D\u201D\u2019]*
    # Followed by whitespace (space/newline) before the next sentence
    \s+
    """,
    re.VERBOSE,
)


def _normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def _split_into_sentences(text: str) -> List[str]:
    """
    Heuristic sentence splitter:
    - Splits on . ! ? and common CJK terminators.
    - Keeps the punctuation with the sentence.
    - Works on whitespace-normalized text.
    """
    text = _normalize_whitespace(text)
    if not text:
        return []
    parts = _SENTENCE_BOUNDARY_RE.split(text)
    # The regex split keeps the separators out; parts are sentences already.
    # Extra guard to ensure we don't emit empties.
    return [p for p in (s.strip() for s in parts) if p]


def _chunk_long_span(span: str, chunk_size: int) -> List[str]:
    """
    Break a single long span (sentence or leftover) into <= chunk_size pieces.
    Prefer to cut on whitespace nearest to the boundary; if none, hard-cut.
    """
    out = []
    start = 0
    n = len(span)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:  # try to backtrack to nearest space for a clean cut
            cut = span.rfind(" ", start, end)
            if cut == -1 or cut <= start + max(0, chunk_size // 2 - 1):
                # If no reasonable space found, accept a hard cut at `end`
                cut = end
        else:
            cut = end
        piece = _normalize_whitespace(span[start:cut])
        if piece:
            out.append(piece)
        start = cut
        # Skip any spaces at the new start
        while start < n and span[start].isspace():
            start += 1
    return out


def chunk_text(document: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Chunk a text document for RAG:
      - Collapses excess whitespace inside chunks.
      - Prefers splitting on sentence boundaries when reasonable.
      - Ensures each chunk is <= `chunk_size` characters.
      - Adds up to `overlap` trailing characters from the previous chunk
        to the beginning of the next (for retrieval context continuity).

    Args:
        document: Input text.
        chunk_size: Maximum characters per chunk (after normalization).
        overlap: Desired overlapping context in characters between adjacent chunks.

    Returns:
        List of chunk strings.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    # Normalize the entire document once for cleaner sentence splitting
    doc = _normalize_whitespace(document)
    if not doc:
        return []

    sentences = _split_into_sentences(doc)
    if not sentences:
        sentences = [doc]

    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    def flush_current():
        nonlocal current, current_len
        if not current:
            return
        span = _normalize_whitespace(" ".join(current))
        # If the assembled span is still too long, break it further.
        if len(span) > chunk_size:
            pieces = _chunk_long_span(span, chunk_size)
            chunks.extend(pieces)
        else:
            chunks.append(span)
        current = []
        current_len = 0

    for sent in sentences:
        s = _normalize_whitespace(sent)
        if not s:
            continue
        # If a single sentence is longer than chunk_size, split it directly.
        if len(s) > chunk_size:
            flush_current()
            chunks.extend(_chunk_long_span(s, chunk_size))
            continue

        # Consider adding this sentence to the current chunk.
        sep = 1 if current else 0  # account for a space if joining
        if current_len + sep + len(s) <= chunk_size:
            current.append(s)
            current_len += sep + len(s)
        else:
            flush_current()
            current = [s]
            current_len = len(s)

    flush_current()

    if not chunks:
        return []

    # Apply overlap (character-based). We prepend up to `overlap` trailing chars
    # from the previous chunk, then trim to `chunk_size`.
    if overlap > 0 and len(chunks) > 1:
        with_overlap: List[str] = []
        prev = None
        for i, ch in enumerate(chunks):
            if i == 0:
                with_overlap.append(ch)
                prev = ch
                continue
            prefix = prev[-overlap:] if prev else ""
            merged = _normalize_whitespace(f"{prefix} {ch}") if prefix else ch
            if len(merged) > chunk_size:
                merged = merged[:chunk_size]
                # avoid cutting mid-word too awkwardly: backtrack to space if feasible
                back = merged.rfind(" ")
                if back >= max(0, chunk_size - 40):  # small tolerance near the end
                    merged = merged[:back]
                merged = merged.rstrip()
            with_overlap.append(merged)
            prev = ch
        chunks = with_overlap

    return chunks
