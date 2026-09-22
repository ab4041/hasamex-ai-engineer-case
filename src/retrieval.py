import re
from collections import Counter

STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","is","are","was","were",
    "how","what","why","do","does","would","you","your","it","this","that","with",
    "their","they","be","as","by","from","at","about","into","can","will","i"
}

def tokenize(text):
    return [t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t not in STOPWORDS]

def score(query, text):
    q = Counter(tokenize(query))
    d = Counter(tokenize(text))
    if not q:
        return 0.0
    # Simple transparent lexical relevance: weighted overlap + phrase bonus.
    overlap = sum(min(q[t], d[t]) for t in q)
    phrase_bonus = 2.0 if query.lower() in text.lower() else 0.0
    return overlap + phrase_bonus

def retrieve(query, chunks, k=6, market=None):
    candidates = [c for c in chunks if not market or c["market"] == market]
    ranked = sorted(
        candidates,
        key=lambda c: score(query, c["text"]),
        reverse=True
    )
    return [c for c in ranked if score(query, c["text"]) > 0][:k]
