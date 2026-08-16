import re
from collections import Counter

from .learning import STOPWORDS


def extractive_summarize(text, max_sentences=4):
    """Deterministic extractive summarizer: scores sentences by keyword
    frequency and returns the most informative ones in document order."""
    if not text or not text.strip():
        return ""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) >= 20]
    if not sentences:
        sentences = [text.strip()]

    words = re.findall(r"[a-zA-Z]+", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS and len(w) > 1)
    max_freq = max(freq.values()) if freq else 1

    scored = []
    for s in sentences:
        sw = re.findall(r"[a-zA-Z]+", s.lower())
        if not sw:
            continue
        score = sum(freq[w] / max_freq for w in sw if w in freq) / len(sw)
        scored.append((score, len(s), s))
    scored.sort(key=lambda t: (-t[0], t[1]))
    top = [t[2] for t in scored[:max_sentences]]

    ordered = [s for s in sentences if s in top]
    return " ".join(ordered) if ordered else sentences[0][:400]
