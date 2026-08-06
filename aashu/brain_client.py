import requests
from .config import BRAIN_API_URL

class BrainClient:
    def __init__(self, base_url=BRAIN_API_URL):
        self.base_url = base_url

    def check_connection(self):
        try:
            r = requests.get(self.base_url, timeout=1.5)
            return r.status_code == 200
        except Exception:
            return False

    def get_state(self):
        try:
            r = requests.get(f"{self.base_url}/state", timeout=1.5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def get_goals(self):
        try:
            r = requests.get(f"{self.base_url}/goals", timeout=1.5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def send_perception_text(self, text, source="user", modality="hearing"):
        try:
            r = requests.post(f"{self.base_url}/perceive/text", json={
                "text": text,
                "source": source,
                "modality": modality
            }, timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_perception_raw(self, payload):
        try:
            r = requests.post(f"{self.base_url}/perceive", json=payload, timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_visual_signal(self, objects, attributes=None, relations=None, motion_level=0.0, confidence=0.7, source="vision_sensor"):
        payload = {
            "objects": objects,
            "attributes": attributes or {},
            "relations": relations or [],
            "motion_level": motion_level,
            "confidence": confidence,
            "source": source
        }
        try:
            r = requests.post(f"{self.base_url}/perceive/visual", json=payload, timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_hearing_signal(self, transcript, speaker_type="unknown", sentiment=0.0, prosody_intensity=0.5, keywords=None, source="audio_sensor"):
        payload = {
            "transcript": transcript,
            "speaker_type": speaker_type,
            "sentiment": sentiment,
            "prosody_intensity": prosody_intensity,
            "keywords": keywords or [],
            "source": source
        }
        try:
            r = requests.post(f"{self.base_url}/perceive/hearing", json=payload, timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def trigger_tick(self):
        try:
            r = requests.post(f"{self.base_url}/tick", timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def regulate_speech(self, text):
        try:
            r = requests.post(f"{self.base_url}/regulate_speech", json={"text": text}, timeout=1.5)
            if r.status_code == 200:
                return r.json().get("output", text)
        except Exception:
            pass
        return text

    def force_sleep(self, duration=5):
        try:
            r = requests.post(f"{self.base_url}/sleep", json={"duration": duration}, timeout=1.5)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def force_wakeup(self):
        try:
            r = requests.post(f"{self.base_url}/wakeup", timeout=1.5)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def modulate_chemical(self, name, value=None, delta=None):
        payload = {"chemical": name}
        if value is not None:
            payload["value"] = value
        if delta is not None:
            payload["delta"] = delta
        try:
            r = requests.post(f"{self.base_url}/state/chemicals", json=payload, timeout=1.5)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def manage_goal(self, name, value=None, reward=None):
        payload = {"name": name}
        if value is not None:
            payload["value"] = value
        if reward is not None:
            payload["reward"] = reward
        try:
            r = requests.post(f"{self.base_url}/goals", json=payload, timeout=1.5)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def perform_reset(self, hard=False):
        try:
            r = requests.post(f"{self.base_url}/reset", json={"hard_reset": hard}, timeout=5.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def register_action(self, name, description, parameters=None, patterns=None):
        if parameters is None:
            parameters = {"type": "object", "properties": {}, "required": []}
        if patterns is None:
            patterns = []
        payload = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "patterns": patterns
        }
        try:
            r = requests.post(f"{self.base_url}/actions/register", json=payload, timeout=2.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
