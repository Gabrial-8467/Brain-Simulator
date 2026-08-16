import os
import re
import json
import uuid
import hashlib
import datetime
from collections import Counter

import numpy as np
import chromadb
from chromadb.api.types import EmbeddingFunction

KNOWLEDGE_STORE_PATH = "aashu_knowledge_db"
KNOWLEDGE_COLLECTION = "aashu_knowledge"
EMBEDDING_DIM = 384
COSINE_THRESHOLD = 0.15

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "to", "of", "in", "on", "for", "with", "about", "from", "as", "at", "by", "it",
    "its", "this", "that", "these", "those", "you", "your", "i", "we", "they", "he",
    "she", "them", "his", "her", "their", "our", "my", "me", "us", "what", "which",
    "how", "why", "when", "where", "who", "can", "could", "will", "would", "should",
    "do", "does", "did", "has", "have", "had", "not", "no", "yes", "just", "so", "if",
    "then", "than", "too", "very", "also", "any", "all", "each", "some", "such",
    "more", "most", "other", "only", "own", "same", "use", "used", "using", "get",
    "got", "make", "like", "want", "need", "one", "two", "new", "now", "how", "the",
}

LANGUAGES = {
    "python", "javascript", "typescript", "java", "c++", "c#", "csharp", "golang", "go",
    "rust", "ruby", "php", "swift", "kotlin", "html", "css", "sql", "bash", "shell",
    "lua", "dart", "r", "matlab", "scala", "perl", "haskell", "elixir", "cobol",
}

CONCEPT_KEYWORDS = {
    "react", "django", "flask", "node", "pandas", "numpy", "api", "oop", "function",
    "algorithm", "code", "coding", "programming", "variable", "loop", "class", "import",
}

ALL_KEYWORDS = LANGUAGES | CONCEPT_KEYWORDS


def _lang_pattern(lang):
    """Regex that matches a language name as a whole word (handles c++, c#, go, r)."""
    if re.fullmatch(r"[a-zA-Z0-9]+", lang):
        return r"(?<!\w)" + re.escape(lang) + r"(?!\w)"
    return re.escape(lang)


def detect_language(text):
    """Return the programming language mentioned in the text, if any."""
    if not text:
        return None
    lowered = text.lower()
    for lang in sorted(LANGUAGES, key=len, reverse=True):
        if re.search(_lang_pattern(lang), lowered):
            return lang
    for kw in sorted(CONCEPT_KEYWORDS, key=len, reverse=True):
        if kw in lowered:
            return kw
    return None


def extract_topics(text, limit=5):
    """Extract the most informative keywords/topics from a body of text."""
    words = re.findall(r"[a-zA-Z0-9+#.]+", (text or "").lower())
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 1]
    lowered = (text or "").lower()
    for kw in ALL_KEYWORDS:
        if re.search(_lang_pattern(kw), lowered) and kw not in filtered:
            filtered.append(kw)
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(limit)]


class HashedEmbeddingFunction(EmbeddingFunction):
    """Deterministic, offline, local embedding: hashed bag-of-words with
    keyword boosts, normalized to unit length. No external model needed."""

    def __init__(self, dim=EMBEDDING_DIM):
        self.dim = dim

    def __call__(self, input):
        return [self._embed(text) for text in input]

    def _embed(self, text):
        vec = np.zeros(self.dim, dtype=np.float32)
        lowered = (text or "").lower()
        for word in re.findall(r"[a-zA-Z0-9+#.]+", lowered):
            if word in STOPWORDS:
                continue
            vec[self._bucket(word)] += 1.0
        for kw in ALL_KEYWORDS:
            if re.search(_lang_pattern(kw), lowered):
                vec[self._bucket(kw)] += 2.0
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def _bucket(self, token):
        return int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dim


class VectorStore:
    """Persistent ChromaDB vector store for embedded text records.

    Every record is embedded and stored for semantic (cosine) recall."""

    def __init__(self, path=None, embedding_function=None, collection=KNOWLEDGE_COLLECTION):
        self.path = path or KNOWLEDGE_STORE_PATH
        self.embedding_function = embedding_function or HashedEmbeddingFunction()
        self._client = chromadb.PersistentClient(path=self.path)
        self._collection = self._client.get_or_create_collection(
            collection,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def _ids(self):
        return set(self._collection.get(include=[])["ids"])

    def _clean_meta(self, item):
        cleaned = {}
        for key, value in item.items():
            if key == "id" or value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, list):
                cleaned[key] = [v for v in value if isinstance(v, (str, int, float, bool))]
            elif isinstance(value, dict):
                cleaned[key] = json.dumps(value)
        return cleaned

    def _search_doc(self, item):
        parts = [str(item.get("content") or ""), str(item.get("topic") or "")]
        parts += [str(k) for k in item.get("keywords", []) if k]
        if item.get("language"):
            parts.append(str(item["language"]))
        return " ".join(p for p in parts if p)

    def _add(self, item):
        self._collection.add(
            ids=[item["id"]],
            documents=[self._search_doc(item)],
            metadatas=[self._clean_meta(item)],
        )
        return item

    def store(self, item):
        item.setdefault("id", uuid.uuid4().hex[:12])
        item.setdefault("timestamp", datetime.datetime.now().isoformat(timespec="seconds"))
        item.setdefault("times_recalled", 0)
        self._add(item)
        return item

    def update(self, item):
        try:
            self._collection.update(
                ids=[item["id"]],
                documents=[self._search_doc(item)],
                metadatas=[self._clean_meta(item)],
            )
            return True
        except Exception:
            return False

    def _item_from_result(self, item_id, meta, doc):
        base = dict(meta) if meta else {}
        base["id"] = item_id
        if "content" not in base and doc is not None:
            base["content"] = doc
        return base

    def _result_items(self, ids, metadatas, documents):
        items = []
        for i, item_id in enumerate(ids):
            items.append(self._item_from_result(item_id, metadatas[i], documents[i]))
        return items

    @property
    def items(self):
        result = self._collection.get()
        return self._result_items(result["ids"], result["metadatas"], result["documents"])

    def search(self, query, limit=5):
        if not query:
            return []
        try:
            result = self._collection.query(
                query_texts=[query],
                n_results=max(self._collection.count(), 1),
                include=["metadatas", "documents", "distances"],
            )
        except Exception:
            return []
        hits = []
        for i, item_id in enumerate(result["ids"][0]):
            distance = result["distances"][0][i]
            similarity = 1.0 - distance
            if similarity >= COSINE_THRESHOLD:
                item = self._item_from_result(
                    item_id, result["metadatas"][0][i], result["documents"][0][i]
                )
                item["_sim"] = similarity
                hits.append(item)
        hits.sort(key=lambda it: (-it.get("_sim", 0.0), -int(it.get("times_recalled", 0))))
        return hits[:limit]

    def recall(self, query, limit=5):
        results = self.search(query, limit=limit)
        for item in results:
            new_count = self._bump_recall(item["id"])
            if new_count is not None:
                item["times_recalled"] = new_count
        return results

    def _bump_recall(self, item_id):
        try:
            got = self._collection.get(ids=[item_id], include=["metadatas"])
            if not got["ids"]:
                return None
            meta = dict(got["metadatas"][0] or {})
            new_count = int(meta.get("times_recalled", 0)) + 1
            meta["times_recalled"] = new_count
            self._collection.update(ids=[item_id], metadatas=[meta])
            return new_count
        except Exception:
            return None

    def all_topics(self):
        topics = []
        for item in self.items:
            t = item.get("topic")
            if t and t not in topics:
                topics.append(t)
        return topics

    def all_languages(self):
        langs = []
        for item in self.items:
            l = item.get("language")
            if l and l not in langs:
                langs.append(l)
        return langs

    def clear(self):
        ids = self._ids()
        if ids:
            self._collection.delete(ids=list(ids))

    def delete(self, item_id):
        try:
            self._collection.delete(ids=[str(item_id)])
            return True
        except Exception:
            return False

    def __len__(self):
        try:
            return self._collection.count()
        except Exception:
            return 0


# Backwards-compatible alias.
KnowledgeStore = VectorStore
