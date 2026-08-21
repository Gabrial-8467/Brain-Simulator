import json
import os
import threading


class MemoryStorage:
    def __init__(self, file_path="memory_store.json"):
        self.file_path = file_path
        self.memories = []
        self._save_lock = threading.Lock()

        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.memories = data
            except (json.JSONDecodeError, OSError):
                self.memories = []
        else:
            self.memories = []

    def save(self):
        # Atomic write: serialize overlapping saves, dump to a temp file, then
        # os.replace() so readers never observe a partially-written checkpoint.
        with self._save_lock:
            directory = os.path.dirname(self.file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            tmp_path = f"{self.file_path}.tmp"
            with open(tmp_path, "w") as f:
                json.dump(self.memories, f, indent=4)
            os.replace(tmp_path, self.file_path)

    def add(self, memory_dict: dict):
        self.memories.append(memory_dict)
        self.save()

    def get_all(self):
        return self.memories

    def update_all(self, updated_memories):
        self.memories = updated_memories
        self.save()
