import json
import os
import time
from memory.schemas import Memory
from memory.storage import MemoryStorage
from memory.vector_store import VectorStore


class MemoryManager:
    """Brain memory manager.

    Episodic memories (created by create_memory) live in a ChromaDB vector
    store for semantic retrieval. The full brain-state snapshot (used by
    save/load for persistence across restarts) stays in a JSON checkpoint."""

    def __init__(self, storage_path="memory_store.json", scoring_config=None):
        self.storage = MemoryStorage(storage_path)

        db_dir = os.path.join(os.path.dirname(os.path.abspath(storage_path)) or ".", "brain_memory_db")
        self.vector_store = VectorStore(path=db_dir, collection="brain_episodic_memory")

        self.pending_memories = []
        self.max_pending_writes = 25

        # Dynamic scoring weights
        self.scoring_config = scoring_config or {
            "importance_weight": 0.5,
            "recency_weight": 0.2,
            "similarity_weight": 0.3
        }

    def create_memory(self, memory_type: str, content: dict, metadata: dict = None):
        memory = Memory(memory_type, content, metadata)
        self.pending_memories.append(memory.to_dict())
        if len(self.pending_memories) >= self.max_pending_writes:
            self.flush_pending()

    def flush_pending(self):
        if not self.pending_memories:
            return

        for mem in self.pending_memories:
            self.vector_store.store({
                "id": mem["id"],
                "memory_type": mem["type"],
                "content": json.dumps(mem["content"]),
                "importance": float(mem.get("importance", 1.0)),
                "reinforcement_count": int(mem.get("reinforcement_count", 0)),
                "created_at": mem["created_at"],
                "last_accessed": mem["last_accessed"],
                "decay_rate": float(mem.get("decay_rate", 0.001)),
                "metadata": json.dumps(mem.get("metadata", {})),
            })
        self.pending_memories = []

    def decay_memories(self):
        self.flush_pending()
        for mem in self.vector_store.items:
            decay_rate = float(mem.get("decay_rate", 0.001))
            importance = float(mem.get("importance", 1.0)) - float(mem.get("importance", 1.0)) * decay_rate
            if importance < 0:
                importance = 0
            mem["importance"] = importance
            self.vector_store.update(mem)

    def retrieve(self, context: dict, limit=5):
        self.flush_pending()
        query = " ".join(f"{k} {v}" for k, v in (context or {}).items())
        candidates = self.vector_store.search(query, limit=max(limit * 3, 10)) if query else self.vector_store.items[:limit]
        if not candidates:
            candidates = self.vector_store.items[:limit]

        scored_memories = []
        for mem in candidates:
            importance_score = float(mem.get("importance", 0.0))
            recency_score = self._calculate_recency(float(mem.get("created_at", 0.0)))
            similarity_score = float(mem.get("_sim", 0.0))

            final_score = (
                self.scoring_config["importance_weight"] * importance_score +
                self.scoring_config["recency_weight"] * recency_score +
                self.scoring_config["similarity_weight"] * similarity_score
            )

            mem_copy = mem.copy()
            mem_copy["retrieval_score"] = final_score
            scored_memories.append(mem_copy)

        scored_memories.sort(key=lambda x: x["retrieval_score"], reverse=True)
        return scored_memories[:limit]

    def save(self, state_dict: dict):
        """Persist the full brain-state checkpoint to JSON storage."""
        self.flush_pending()
        if state_dict is None:
            state_dict = {}
        self.storage.update_all(state_dict)

    def load(self):
        """Load the persisted brain-state checkpoint from JSON storage."""
        self.flush_pending()
        return self.storage.get_all()

    def _calculate_recency(self, timestamp):
        age = time.time() - timestamp
        return 1 / (1 + age)
