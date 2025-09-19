# test_chunk_text.py
# Adjust this import to match where you put the function.
from chunk_text import chunk_text

import re
import pytest


def normalize(s: str) -> str:
    """Mirror the function's whitespace normalization for comparisons."""
    return re.sub(r"\s+", " ", s).strip()


def test_empty_and_whitespace_only():
    assert chunk_text("") == []
    assert chunk_text("   \n\t  ") == []


def test_invalid_params():
    with pytest.raises(ValueError):
        chunk_text("text", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("text", overlap=-1)


def test_whitespace_is_collapsed_and_stripped():
    doc = "Line 1.\n\n   Line\t\t2.   Line  3."
    chunks = chunk_text(doc, chunk_size=50, overlap=0)
    assert all(ch == normalize(ch) for ch in chunks)
    assert "  " not in chunks[0]  # no double spaces
    assert chunks[0].startswith("Line 1.")
    # With chunk_size big enough, everything stays in one chunk
    one = chunk_text(doc, chunk_size=10_000, overlap=0)
    assert one == [normalize(doc)]


def test_never_exceeds_chunk_size_even_with_overlap():
    doc = "A" * 1500 + " " + "B" * 1500 + " " + "C" * 1500
    size = 1000
    ov = 200
    chunks = chunk_text(doc, chunk_size=size, overlap=ov)
    assert len(chunks) >= 3
    assert all(len(c) <= size for c in chunks)


def test_long_single_word_hard_cuts():
    # No whitespace to backtrack to -> must hard-cut
    long = "X" * 2500
    size = 700
    chunks = chunk_text(long, chunk_size=size, overlap=0)
    assert len(chunks) == 4  # 700 + 700 + 700 + 400
    assert all(len(c) <= size for c in chunks)
    # Reassemble should match normalized original (which is same)
    assert "".join(chunks) == long


def test_sentence_boundary_preference():
    # 3 short sentences; choose boundaries when adding next would overflow
    s1 = "This is sentence one."
    s2 = "This is sentence two."
    s3 = "This is sentence three."
    doc = f"{s1} {s2} {s3}"
    # Force a break after s2 by setting chunk_size between len(s1+s2) and len(s1+s2+s3)
    target_len = len(normalize(f"{s1} {s2}"))
    size = target_len + 1  # fits s1+s2, but not s1+s2+s3
    chunks = chunk_text(doc, chunk_size=size, overlap=0)
    assert chunks[0] == normalize(f"{s1} {s2}")
    assert chunks[1] == normalize(s3)


def test_sentence_longer_than_chunk_gets_split_cleanly_on_space_if_possible():
    # A single "sentence" that exceeds chunk_size but has spaces inside
    sentence = "word " * 600  # ~3000 chars
    size = 1000
    chunks = chunk_text(sentence, chunk_size=size, overlap=0)
    # Should break on spaces rather than mid-word
    assert all(not c.startswith(" ") and not c.endswith(" ") for c in chunks)
    assert all(len(c) <= size for c in chunks)
    # Join should equal normalized original
    assert " ".join(c.strip() for c in chunks) == normalize(sentence)


def test_cjk_sentence_boundaries():
    doc = "这是第一句。 这是第二句！这是第三句？这是第四句。"
    # Set size to fit two sentences per chunk if possible
    # Rough heuristic: ensure 1–2 sentences fit but not all
    size = len(normalize("这是第一句。 这是第二句！")) + 1
    chunks = chunk_text(doc, chunk_size=size, overlap=0)
    # Expect chunks to align with sentence ends when feasible
    assert "。" in chunks[0] or "！" in chunks[0] or "？" in chunks[0]
    # Ensure we didn't split inside a CJK sentence when not necessary
    for ch in chunks:
        assert not ch.startswith(" ")
        assert not ch.endswith(" ")


def test_overlap_prefix_matches_prev_suffix_when_no_truncation():
    sents = [
        "Alpha is here.",
        "Bravo is there.",
        "Charlie is everywhere.",
    ]
    doc = " ".join(sents)
    # Make chunk_size large to avoid any truncation after adding overlap
    size = 10_000
    ov = 10
    chunks = chunk_text(doc, chunk_size=size, overlap=ov)
    assert len(chunks) == 1  # with size this big, no split -> no overlap applied

    # Force two chunks by shrinking chunk_size, but keep large enough so the
    # overlapped chunk doesn't need trimming.
    size = len(normalize(" ".join(sents[:2])))
    # This size fits first two sentences exactly; third will be its own chunk
    chunks = chunk_text(doc, chunk_size=size, overlap=ov)
    assert len(chunks) == 2
    prev = normalize(" ".join(sents[:2]))
    nxt = chunks[1]
    # The second chunk should start with the normalized suffix of previous chunk
    expected_prefix = prev[-ov:]
    assert normalize(nxt).startswith(normalize(expected_prefix))


def test_overlap_never_breaks_chunk_size_and_keeps_words_when_possible():
    # Create three chunks and verify the backtrack-to-space trimming path
    s1 = "A" * 950 + "."
    s2 = " " + "B" * 900 + "."
    s3 = " " + "C" * 900 + "."
    doc = s1 + s2 + s3
    size = 1000
    ov = 200
    chunks = chunk_text(doc, chunk_size=size, overlap=ov)
    # After overlap, chunks must still respect size
    assert all(len(c) <= size for c in chunks)
    # Verify that when trimming happened, we didn't end with a trailing space
    assert all(not c.endswith(" ") for c in chunks)


@pytest.mark.parametrize(
    "chunk_size,overlap",
    [
        (50, 0),
        (80, 10),
        (120, 30),
    ],
)
def test_roundtrip_no_overlap_equals_normalized_original_when_large_enough(
    chunk_size, overlap
):
    # Build a medium doc with punctuation and whitespace variety
    doc = "Para 1.\n\nPara 2 is here!  \tNewline?  Yes.\nAnd more…  End."
    if overlap != 0:
        pytest.skip("This test asserts a no-overlap property.")
    chunks = chunk_text(doc, chunk_size=10_000, overlap=overlap)
    assert chunks == [normalize(doc)]
