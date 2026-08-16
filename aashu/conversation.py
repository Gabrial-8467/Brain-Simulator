import os
import json
import datetime


class ConversationHistory:
    """Rolling, persisted memory of recent assistant-user turns.

    Keeps the last ``max_turns`` exchanges so the assistant can maintain
    conversational context across turns and across restarts. Stored as a
    plain JSON file (no embedding store involved)."""

    def __init__(self, path="aashu_conversation_history.json", max_turns=12):
        self.path = path
        self.max_turns = max_turns
        self.turns = []
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r") as f:
                    data = json.load(f)
                self.turns = [t for t in data.get("turns", []) if isinstance(t, dict)][-self.max_turns:]
        except Exception:
            self.turns = []

    def _save(self):
        try:
            with open(self.path, "w") as f:
                json.dump({"turns": self.turns}, f, indent=2)
        except Exception:
            pass

    def add_turn(self, user, assistant=""):
        self.turns.append({
            "user": (user or "").strip()[:500],
            "assistant": (assistant or "").strip()[:1500],
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        self.turns = self.turns[-self.max_turns:]
        self._save()

    def recent(self, limit=6):
        """The last ``limit`` turns as (role, content) tuples."""
        out = []
        for t in self.turns[-limit:]:
            if t.get("user"):
                out.append(("user", t["user"]))
            if t.get("assistant"):
                out.append(("assistant", t["assistant"]))
        return out

    def to_prompt_block(self, limit=6):
        """Compact multi-line block for inclusion in a system prompt."""
        lines = []
        for role, content in self.recent(limit=limit):
            lines.append(f"[{role}] {content}")
        return "\n".join(lines)
