from collections import deque
import time

from core.attention import GlobalWorkspace, Thought


class AutobiographicalMemory:
    SYSTEM_EVENT_KEYS = {"cycle_step", "internal_process", "tick", "update"}

    def __init__(self, max_events=500):
        self.events = deque(maxlen=max_events)
        self._last_recalled_description = ""

    def record_event(self, description, chemicals, identity_snapshot, metadata=None):
        event = {
            "timestamp": time.time(),
            "description": description,
            "chemicals": chemicals.copy(),
            "identity": identity_snapshot.copy(),
            "metadata": metadata or {},
        }
        self.events.append(event)

    def get_recent_events(self, n=50):
        return list(self.events)[-n:]

    @classmethod
    def _is_system_event(cls, description: str) -> bool:
        text = str(description or "").lower()
        return any(key in text for key in cls.SYSTEM_EVENT_KEYS)

    def _select_recall_event(self):
        if not self.events:
            return None
        latest = self.events[-1]
        if not self._is_system_event(latest.get("description", "")):
            candidates = [ev for ev in reversed(self.events) if not self._is_system_event(ev.get("description", ""))]
        else:
            candidates = [ev for ev in reversed(self.events) if not self._is_system_event(ev.get("description", ""))]
        if candidates:
            recent_candidates = candidates[:120]
            scored = sorted(recent_candidates, key=self._event_salience, reverse=True)
            selected = scored[0]
            for ev in scored:
                if ev.get("description", "") != self._last_recalled_description:
                    selected = ev
                    break
            self._last_recalled_description = str(selected.get("description", ""))
            return selected
        return latest

    @staticmethod
    def _classify_recall_event(event: dict) -> str:
        text = str(event.get("description", "") or "").lower()
        if any(k in text for k in ["threat_detected", "threat", "danger"]):
            return "threat"
        if any(k in text for k in ["failure", "failed", "criticism", "criticized", "mistake"]):
            return "failure"
        if any(k in text for k in ["loneliness", "isolated", "ignored", "no one is listening"]):
            return "social_pain"
        if any(k in text for k in ["success", "praise", "greeted", "proud", "solve", "together", "face_recognized", "good job"]):
            return "positive"
        return "neutral"

    @staticmethod
    def _event_salience(event: dict) -> float:
        metadata = event.get("metadata", {}) or {}
        valence = abs(float(metadata.get("valence", 0.0) or 0.0))
        intensity = float(metadata.get("intensity", 0.0) or 0.0)
        category = str(metadata.get("category", "") or "").lower()
        score = valence * max(0.3, intensity)
        if category in {"failure", "criticism", "threat_detected"}:
            score += 0.35
        elif category in {"ignored", "loneliness"}:
            score += 0.3
        elif category in {"success", "praise", "greeted"}:
            score += 0.25
        return score

    def propose_memory_thought(self, brain) -> None:
        if not self.events:
            return

        ev = self._select_recall_event()
        if not ev:
            return

        description = ev.get("description", "")
        if self._is_system_event(description):
            emo = 0.0
        else:
            emo = 0.0
            for chem in ("dopamine", "oxytocin", "cortisol"):
                val = ev["chemicals"].get(chem, 0)
                if isinstance(val, dict):
                    val = val.get("value", 0)
                if chem == "cortisol":
                    emo += (100 - val) / 100.0
                else:
                    emo += val / 100.0
            emo = min(1.0, emo / 3.0)

        th = Thought(
            content=f"Recall: {description}",
            source="memory",
            emotional_weight=emo,
            novelty=0.4,
            relevance_to_goals=0.3,
            metadata={
                "recalled_description": description,
                "recalled_intensity": (ev.get("metadata", {}) or {}).get("intensity"),
                "recalled_category": (ev.get("metadata", {}) or {}).get("category"),
                "recalled_source": (ev.get("metadata", {}) or {}).get("source"),
            },
        )
        GlobalWorkspace.post(th)
