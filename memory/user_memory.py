import os
import datetime
import uuid

from memory.vector_store import VectorStore


def _now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


class UserMemory:
    """Vector-backed long-term memory about the user.

    Stores facts about the user (preferences, relationships, history, traits)
    as embeddings for semantic recall, and can build a compact profile summary
    used to personalise conversation.

    The ChromaDB store is initialized lazily so constructing the object has no
    side effects (and does not disturb a seeded RNG stream)."""

    def __init__(self, path=None, user_name=None):
        if path is None:
            base = os.getenv("AASHU_MEMORY_DIR", ".")
            path = os.path.join(base, "aashu_user_db")
        self.path = path
        self.user_name = user_name
        self._store = None

    @property
    def store(self):
        if self._store is None:
            self._store = VectorStore(path=self.path, collection="user_profile")
        return self._store

    def set_user_name(self, name):
        if name and name.strip():
            self.user_name = name.strip().lower().capitalize()

    def remember(self, fact, fact_type="general", importance=0.6):
        """Store a durable fact about the user."""
        fact = (fact or "").strip()
        if not fact:
            return None
        item = {
            "id": uuid.uuid4().hex[:12],
            "content": fact,
            "fact_type": fact_type,
            "importance": float(importance),
            "timestamp": _now_iso(),
        }
        self.store.store(item)
        return item

    def forget(self, fact_type=None, fact=None):
        removed = []
        for item in self.store.items:
            if fact_type and item.get("fact_type") != fact_type:
                continue
            if fact and fact.lower() not in item.get("content", "").lower():
                continue
            if self.store.delete(item["id"]):
                removed.append(item)
        return removed

    def recall(self, context, limit=5):
        """Semantically recall facts relevant to the given context.

        Falls back to the most recently stored facts when the hashed
        embedding finds no shared vocabulary with the context."""
        if not context or not context.strip():
            return self.store.items[:limit]
        results = self.store.search(context, limit=limit)
        hits = [r for r in results if r.get("content")]
        if hits:
            return hits
        return self.store.items[:limit]

    def facts(self):
        return self.store.items

    def all_facts(self, limit=20):
        return self.store.items[:limit]

    def profile(self):
        facts = self.store.items
        types = {}
        for f in facts:
            t = f.get("fact_type", "general")
            types[t] = types.get(t, 0) + 1
        return {
            "user_name": self.user_name,
            "total_facts": len(facts),
            "fact_types": types,
            "last_updated": facts[0]["timestamp"] if facts else None,
        }

    def context_for_conversation(self, context=None, limit=6):
        """Compact 'Known about <user>' block used to personalise responses."""
        if self.user_name:
            header = f"Known about {self.user_name}:"
        else:
            header = "Known about the user:"
        facts = self.recall(context, limit=limit) if context else self.store.items[:limit]
        if not facts:
            return ""
        lines = [header]
        for f in facts:
            content = f.get("content", "").strip()
            if not content:
                continue
            prefix = f.get("fact_type", "fact")
            lines.append(f"- [{prefix}] {content}")
        return "\n".join(lines)

    def consolidate(self):
        """Derive durable traits from repeated facts.

        Groups stored facts by type and content pattern; when several facts
        agree, a single consolidated 'trait' fact is stored and the individual
        low-importance sources are removed."""
        facts = self.store.items
        if len(facts) < 3:
            return 0
        traits = {}
        for f in facts:
            if f.get("derived"):
                continue
            content = (f.get("content") or "").lower().strip()
            if len(content.split()) > 4:
                continue
            t = f.get("fact_type", "general")
            traits.setdefault(t, []).append(f)
        created = 0
        for ftype, group in traits.items():
            if len(group) < 2:
                continue
            contents = {f["content"].strip().lower() for f in group}
            if len(contents) < 2:
                continue
            for f in group:
                if f.get("importance", 0.6) < 0.5:
                    self.store.delete(f["id"])
            trait_content = "; ".join(f["content"].strip() for f in group)
            trait = {
                "id": uuid.uuid4().hex[:12],
                "content": f"Traits ({ftype}): {trait_content}",
                "fact_type": "trait",
                "importance": 0.9,
                "timestamp": _now_iso(),
                "derived": True,
            }
            self.store.store(trait)
            created += 1
        return created

    def decay(self, half_life_days=90):
        """Importance-weighted forgetting.

        Older, low-importance facts decay until they fall below the retention
        floor and are removed. Deterministic — no randomness involved."""
        now = datetime.datetime.now()
        removed = 0
        for f in self.store.items:
            importance = float(f.get("importance", 0.6))
            try:
                ts = datetime.datetime.fromisoformat(f.get("timestamp", _now_iso()))
            except ValueError:
                ts = now
            age_days = max(0.0, (now - ts).total_seconds() / 86400.0)
            if importance >= 1.0:
                continue
            decayed = importance * 0.5 ** (age_days / max(1.0, half_life_days * importance))
            if decayed < 0.15:
                if self.store.delete(f["id"]):
                    removed += 1
            elif abs(decayed - importance) > 1e-9:
                f["importance"] = round(decayed, 3)
                f["content"] = f.get("content", "")
                self.store.update(f)
        return removed

    def to_state(self):
        return {
            "user_name": self.user_name,
            "facts": [
                {
                    "id": f.get("id"),
                    "content": f.get("content"),
                    "fact_type": f.get("fact_type", "general"),
                    "importance": f.get("importance"),
                    "timestamp": f.get("timestamp"),
                }
                for f in self.store.items
            ],
        }

    def load_state(self, state):
        if not isinstance(state, dict):
            return
        self.set_user_name(state.get("user_name"))
        for fact in state.get("facts", []) or []:
            if not isinstance(fact, dict) or not fact.get("content"):
                continue
            self.store.store({
                "id": fact.get("id") or uuid.uuid4().hex[:12],
                "content": fact["content"],
                "fact_type": fact.get("fact_type", "general"),
                "importance": fact.get("importance", 0.6),
                "timestamp": fact.get("timestamp") or _now_iso(),
            })
