import json
import os


class MemoryStorage:
    def __init__(self, file_path="memory_store.json"):
        self.file_path = file_path
        self.memories = []

        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.memories = data
        else:
            self.memories = []

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.memories, f, indent=4)

    def add(self, memory_dict: dict):
        self.memories.append(memory_dict)
        self.save()

    def get_all(self):
        return self.memories

    def update_all(self, updated_memories):
        self.memories = updated_memories
        self.save()
