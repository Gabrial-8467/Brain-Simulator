import time
from memory.schemas import Memory
from memory.storage import MemoryStorage


class MemoryManager:
    def __init__(self, storage_path="memory_store.json", scoring_config=None):
        self.storage = MemoryStorage(storage_path)
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

        existing = self.storage.get_all()
        if not isinstance(existing, list):
            existing = []

        existing.extend(self.pending_memories)
        self.pending_memories = []
        self.storage.update_all(existing)

    def decay_memories(self):
        self.flush_pending()
        memories = self.storage.get_all()

        for mem in memories:
            decay_rate = mem.get("decay_rate", 0.001)
            mem["importance"] -= mem["importance"] * decay_rate
            if mem["importance"] < 0:
                mem["importance"] = 0

        self.storage.update_all(memories)

    def retrieve(self, context: dict, limit=5):
        self.flush_pending()
        memories = self.storage.get_all()
        scored_memories = []

        for mem in memories:
            importance_score = mem["importance"]
            recency_score = self._calculate_recency(mem["created_at"])
            similarity_score = self._calculate_similarity(mem["content"], context)

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
        """Persist an arbitrary state payload to storage."""
        self.flush_pending()
        if state_dict is None:
            state_dict = {}
        self.storage.update_all(state_dict)

    def load(self):
        """Load persisted state payload from storage."""
        self.flush_pending()
        return self.storage.get_all()

    def _calculate_recency(self, timestamp):
        age = time.time() - timestamp
        return 1 / (1 + age)

    def _calculate_similarity(self, content: dict, context: dict):
        # Simple keyword overlap similarity
        score = 0
        for key in context:
            if key in content and content[key] == context[key]:
                score += 1

        return score
