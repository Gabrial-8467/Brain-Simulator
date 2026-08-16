from .local_vector_store import (
    KNOWLEDGE_STORE_PATH,
    KNOWLEDGE_COLLECTION,
    STOPWORDS,
    LANGUAGES,
    CONCEPT_KEYWORDS,
    ALL_KEYWORDS,
    detect_language,
    extract_topics,
    HashedEmbeddingFunction,
    KnowledgeStore,
    VectorStore,
)

__all__ = [
    "KNOWLEDGE_STORE_PATH",
    "KNOWLEDGE_COLLECTION",
    "STOPWORDS",
    "LANGUAGES",
    "CONCEPT_KEYWORDS",
    "ALL_KEYWORDS",
    "detect_language",
    "extract_topics",
    "HashedEmbeddingFunction",
    "KnowledgeStore",
    "VectorStore",
]


class AashuLearning:
    """Unified learning cortex: ingests knowledge from any sensory channel,
    stores it persistently in the vector database, feeds it into the Virtual
    Brain, and recalls it later (e.g. to prime code generation)."""

    def __init__(self, brain_client=None, knowledge_path=KNOWLEDGE_STORE_PATH):
        self.brain_client = brain_client
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
        Wikipedia summary) and ingesting them as knowledge.

        If the query itself names a programming language (e.g. "learn
        reactjs", "python"), the web search is steered toward official
        documentation for that language so the learned snippet is usable
        by the code generator."""
        if not query:
            return None
        topic = query.strip()
        detected = detect_language(query) or detect_language(topic)
        search = query
        if detected:
            search = f"{detected} programming language tutorial documentation example"
            topic = f"learn {detected}" if not any(
                w in query.lower() for w in ("learn", "tutorial", "about")) else query
        snippets = []
        if search_fn:
            try:
                raw = search_fn(search)
                if isinstance(raw, str) and "Error" not in raw:
                    snippets.append(raw)
            except Exception:
                pass
        if summary_fn:
            try:
                raw = summary_fn(topic if detected else query)
                if isinstance(raw, str) and "Error" not in raw and "not found" not in raw.lower():
                    snippets.append(raw)
            except Exception:
                pass
        if not snippets:
            snippets.append(f"Notes on {query} (no web snippet retrieved).")
        content = "\n".join(snippets)
        return self.learn(content, topic=topic, source="internet")

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
