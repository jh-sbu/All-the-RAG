# test_chunk_text.py
import itertools
import re
import random

# If the function lives elsewhere, replace the import below accordingly:
from chunk_docs import chunk_text  # or: from chunker import chunk_text


def _reconstruct_from_chunks(chunks: list[str]) -> str:
    """
    Rebuild the original text from overlapping chunks by
    removing the maximal exact overlap between consecutive chunks.
    """
    if not chunks:
        return ""
    out = chunks[0]
    for nxt in chunks[1:]:
        # find the largest k such that out[-k:] == nxt[:k]
        max_k = min(len(out), len(nxt))
        k = 0
        for kk in range(max_k, 0, -1):
            if out[-kk:] == nxt[:kk]:
                k = kk
                break
        out += nxt[k:]
    return out


def _assert_common_invariants(
    doc: str, chunks: list[str], chunk_size: int, overlap: int
):
    # Non-empty chunks and never exceed chunk_size
    assert all(chunks), "No chunk should be empty."
    assert all(len(c) <= chunk_size for c in chunks), (
        "Chunks must not exceed chunk_size."
    )

    # Overlap should be at most requested (effective overlap may be smaller near edges/cuts)
    for a, b in zip(chunks, chunks[1:]):
        # compute actual overlap
        k = min(len(a), len(b), overlap)
        actual = 0
        for kk in range(k, 0, -1):
            if a[-kk:] == b[:kk]:
                actual = kk
                break
        assert actual <= overlap, "Overlap should not exceed the requested amount."

    # Reconstruction should match original for whitespace-stable docs
    # (All tests that call this helper use docs without leading/trailing chunk whitespaces)
    rebuilt = _reconstruct_from_chunks(chunks)
    assert rebuilt == doc, "Reconstructed text should equal original."


def test_empty_document():
    assert chunk_text("") == []


def test_smaller_than_chunk_size_no_overlap():
    doc = "Short doc."
    chunks = chunk_text(doc, chunk_size=100, overlap=0)
    assert chunks == [doc]


def test_exact_chunk_size():
    doc = "a" * 50
    chunks = chunk_text(doc, chunk_size=50, overlap=10)
    assert chunks == [doc]


def test_sentence_boundary_preference():
    # Choose a size that would cut mid-sentence if not respecting punctuation.
    doc = "First sentence. Second sentence is longer, indeed! Third one?"
    chunks = chunk_text(doc, chunk_size=30, overlap=5)

    # Ensure the first cut ends at the period of the first sentence (or right after quotes/brackets if any)
    # The regex in implementation allows closing quotes, so accept that window.
    first = chunks[0]
    assert first.endswith("First sentence."), "Chunk should prefer sentence boundary."

    # General invariants (doc has stable whitespace)
    _assert_common_invariants(doc, chunks, chunk_size=30, overlap=5)


def test_whitespace_fallback_when_no_sentence_punct():
    # No .,!? in the first window -> should fall back to last whitespace.
    words = ["alpha"] * 40  # creates spaces but no sentence punctuation
    doc = " ".join(words)
    chunks = chunk_text(doc, chunk_size=50, overlap=10)

    # The first chunk should end on a space boundary (so it shouldn't cut a word)
    assert chunks[0].endswith("alpha"), "Should cut at word boundary when possible."
    _assert_common_invariants(doc, chunks, chunk_size=50, overlap=10)


def test_hard_split_when_no_whitespace_or_punct():
    doc = "a" * 120  # a single long token
    chunks = chunk_text(doc, chunk_size=50, overlap=10)
    # Expect hard split: 50, then overlaps applied
    assert len(chunks[0]) == 50
    assert len(chunks) >= 3  # 120 with overlap should need at least 3 parts
    _assert_common_invariants(doc, chunks, chunk_size=50, overlap=10)


def test_overlap_zero_means_butted_chunks():
    # Construct a clean doc with simple words and punctuation, no extra edge spaces.
    doc = " ".join([f"word{i}." for i in range(60)])
    chunks = chunk_text(doc, chunk_size=60, overlap=0)

    # Adjacent chunks should not share any common prefix/suffix when overlap=0
    for a, b in zip(chunks, chunks[1:]):
        max_k = min(len(a), len(b))
        assert all(a[-k:] != b[:k] for k in range(1, max_k + 1)), (
            "No overlap expected when overlap=0."
        )

    _assert_common_invariants(doc, chunks, chunk_size=60, overlap=0)


def test_overlap_greater_than_chunk_size_is_capped_and_terminates():
    # If overlap >= chunk_size, implementation caps it to chunk_size-1 to ensure progress
    doc = " ".join(f"token{i}" for i in range(200))
    chunk_size = 40
    overlap = 1000  # intentionally huge

    chunks = chunk_text(doc, chunk_size=chunk_size, overlap=overlap)
    # Should terminate and obey length constraint
    assert len(chunks) > 1
    assert all(1 <= len(c) <= chunk_size for c in chunks)
    # Still reconstructable
    _assert_common_invariants(
        doc, chunks, chunk_size=chunk_size, overlap=min(overlap, chunk_size - 1)
    )


def test_unicode_cjk_sentence_endings_and_ellipsis():
    # Includes CJK punctuation and unicode ellipsis
    doc = "你好世界。接下来测试！是不是？还有省略号……好的。"
    chunks = chunk_text(doc, chunk_size=10, overlap=2)

    # Check at least one chunk ends exactly at a CJK sentence boundary
    assert any(c.endswith(("。", "！", "？", "…", "……")) for c in chunks), (
        "Should recognize CJK/ellipsis sentence boundaries."
    )
    _assert_common_invariants(doc, chunks, chunk_size=10, overlap=2)


def test_trailing_and_leading_quotes_on_sentence_end():
    doc = 'He said, "Stop now." Then we left.'
    chunks = chunk_text(doc, chunk_size=20, overlap=4)
    # First chunk should include the closing quote after the period
    assert chunks[0].endswith('"'), (
        "Closing quotes should be included with sentence end."
    )
    _assert_common_invariants(doc, chunks, chunk_size=20, overlap=4)


def test_progress_guarantee_on_tiny_chunks():
    # Stress case: tiny chunk_size with nonzero overlap
    doc = "abcdefghij" * 5
    chunks = chunk_text(doc, chunk_size=3, overlap=2)
    # Ensure we made forward progress (no infinite loop / identical consecutive chunks)
    for a, b in zip(chunks, chunks[1:]):
        assert a != b, "Consecutive chunks should not be identical."
    # Length constraint
    assert all(1 <= len(c) <= 3 for c in chunks)
    # Reconstruction holds for this clean doc
    _assert_common_invariants(doc, chunks, chunk_size=3, overlap=2)


def test_various_randomized_documents_still_reconstruct():
    # Light fuzz with controlled alphabet to avoid ambiguous whitespace stripping
    rnd = random.Random(1337)
    alphabet = "abcdefghijklmnopqrstuvwxyz .!?"
    for _ in range(20):
        length = rnd.randint(200, 600)
        # generate doc without doubled spaces at ends of sentences to keep boundaries stable
        doc = re.sub(
            r"\s+", " ", "".join(rnd.choice(alphabet) for _ in range(length)).strip()
        )
        chunk_size = rnd.randint(20, 80)
        overlap = rnd.randint(0, 20)
        chunks = chunk_text(doc, chunk_size=chunk_size, overlap=overlap)
        # Basic invariants
        assert all(len(c) <= chunk_size for c in chunks)
        # Reconstruction check (doc is whitespace-stable)
        rebuilt = _reconstruct_from_chunks(chunks)
        assert rebuilt == doc
