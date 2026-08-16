import os
import re
import json
import uuid
import datetime
from collections import Counter

KNOWLEDGE_STORE_PATH = "aashu_knowledge.json"

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
    for kw in ALL_KEYWORDS:
        if kw in (text or "").lower() and kw not in filtered:
            filtered.append(kw)
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(limit)]


class KnowledgeStore:
    """Persistent local store of learned knowledge entries."""

    def __init__(self, path=KNOWLEDGE_STORE_PATH):
        self.path = path
        self.items = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        return []

    def _save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.items, f, indent=2)
        os.replace(tmp, self.path)

    def store(self, item):
        item.setdefault("id", uuid.uuid4().hex[:12])
        item.setdefault("timestamp", datetime.datetime.now().isoformat(timespec="seconds"))
        item.setdefault("times_recalled", 0)
        self.items.append(item)
        self._save()
        return item

    def search(self, query, limit=5):
        if not query:
            return []
        q = set(extract_topics(query))
        scored = []
        for item in self.items:
            haystack = set(item.get("keywords", [])) | {item.get("topic", "").lower()}
            overlap = len(q & haystack)
            language = item.get("language")
            if language and language in query.lower():
                overlap += 1
            if overlap > 0 or (language and language in query.lower()):
                scored.append((overlap, item))
        scored.sort(key=lambda t: (-t[0], -t[1].get("times_recalled", 0)))
        return [item for _, item in scored[:limit]]

    def recall(self, query, limit=5):
        results = self.search(query, limit=limit)
        for item in results:
            item["times_recalled"] = int(item.get("times_recalled", 0)) + 1
        if results:
            self._save()
        return results

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
        self.items = []
        self._save()

    def __len__(self):
        return len(self.items)


class AashuLearning:
    """Unified learning cortex: ingests knowledge from any sensory channel,
    stores it persistently, feeds it into the Virtual Brain, and recalls it
    later (e.g. to prime code generation)."""

    def __init__(self, brain_client=None, ollama=None, knowledge_path=KNOWLEDGE_STORE_PATH):
        self.brain_client = brain_client
        self.ollama = ollama
        self.store = KnowledgeStore(knowledge_path)

    def learn(self, content, topic=None, source="manual", language=None, valence=0.35):
        """Store a piece of learned knowledge and push it to the brain."""
        content = (content or "").strip()
        if not content:
            return None
        if not topic:
            topics = extract_topics(content, limit=3)
            topic = topics[0] if topics else "general"
        lang = language or detect_language(content) or detect_language(topic or "")
        keywords = extract_topics(content) or extract_topics(topic or "")
        item = {
            "topic": topic,
            "source": source,
            "language": lang,
            "content": content,
            "keywords": keywords,
            "confidence": 0.6,
        }
        self.store.store(item)

        if self.brain_client is not None:
            try:
                summary = content if len(content) <= 300 else content[:300] + "..."
                self.brain_client.send_perception_raw({
                    "content": f"[Learned from {source}] {summary}",
                    "category": "learning",
                    "modality": "experience",
                    "valence": valence,
                    "intensity": 0.5,
                    "source": source,
                })
            except Exception:
                pass
        return item

    def learn_from_internet(self, query, search_fn=None, summary_fn=None):
        """Learn about a topic by pulling web snippets (and optionally a
        Wikipedia summary) and ingesting them as knowledge."""
        if not query:
            return None
        snippets = []
        if search_fn:
            try:
                raw = search_fn(query)
                if isinstance(raw, str) and "Error" not in raw:
                    snippets.append(raw)
            except Exception:
                pass
        if summary_fn:
            try:
                raw = summary_fn(query)
                if isinstance(raw, str) and "Error" not in raw and "not found" not in raw.lower():
                    snippets.append(raw)
            except Exception:
                pass
        if not snippets:
            snippets.append(f"Notes on {query} (no web snippet retrieved).")
        content = "\n".join(snippets)
        return self.learn(content, topic=query, source="internet")

    def learn_from_hearing(self, transcript, speaker="unknown"):
        if not transcript or len(transcript) < 15:
            return None
        return self.learn(transcript, topic="conversation", source="hearing")

    def learn_from_vision(self, description):
        if not description or len(description) < 10:
            return None
        return self.learn(description, topic="visual observation", source="vision")

    def recall(self, topic, limit=5):
        return self.store.recall(topic, limit=limit)

    def build_knowledge_context(self, topic, limit=5):
        entries = self.recall(topic, limit=limit)
        if not entries:
            return ""
        lines = []
        for e in entries:
            head = f"[{e.get('source')}" + (f" / {e.get('language')}]" if e.get("language") else "]")
            lines.append(f"{head} {e.get('content', '')}")
        return "Known context:\n" + "\n".join(lines)

    def knowledge_report(self):
        return {
            "total_entries": len(self.store),
            "topics": self.store.all_topics(),
            "languages": self.store.all_languages(),
        }
