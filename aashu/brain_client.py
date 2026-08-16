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

    def summarize_text(self, text, max_sentences=4):
        try:
            r = requests.post(f"{self.base_url}/brain/summarize", json={
                "text": text,
                "max_sentences": max_sentences,
            }, timeout=5.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def resolve_action(self, text, min_confidence=0.2):
        try:
            r = requests.post(f"{self.base_url}/brain/resolve", json={
                "text": text,
                "min_confidence": min_confidence,
            }, timeout=3.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def remember_user(self, fact, fact_type="general", importance=0.6):
        try:
            r = requests.post(f"{self.base_url}/user_memory/remember", json={
                "fact": fact,
                "fact_type": fact_type,
                "importance": importance,
            }, timeout=3.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_user_context(self, context=None):
        try:
            r = requests.get(f"{self.base_url}/user_memory/context", params={"context": context or ""}, timeout=3.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_user_profile(self):
        try:
            r = requests.get(f"{self.base_url}/user_memory/profile", timeout=3.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_website(self, name="My Website", title=None, sections=None, theme="light"):
        try:
            r = requests.post(f"{self.base_url}/brain/build_website", json={
                "name": name, "title": title, "sections": sections, "theme": theme,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_webapp(self, name="My App", app_name="app", features=None, pages=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_webapp", json={
                "name": name, "app_name": app_name, "features": features, "pages": pages,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_reactapp(self, name="My App", app_name="app", features=None, pages=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_reactapp", json={
                "name": name, "app_name": app_name, "features": features, "pages": pages,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_angularapp(self, name="My App", app_name="app", features=None, pages=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_angularapp", json={
                "name": name, "app_name": app_name, "features": features, "pages": pages,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_vueapp(self, name="My App", app_name="app", features=None, pages=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_vueapp", json={
                "name": name, "app_name": app_name, "features": features, "pages": pages,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_node_server(self, name="My Server", app_name="server", endpoints=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_node_server", json={
                "name": name, "app_name": app_name, "endpoints": endpoints,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_sql_schema(self, name="app", entities=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_sql_schema", json={
                "name": name, "entities": entities,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_fullstack(self, name="My App", kind="food_delivery", theme="light"):
        try:
            r = requests.post(f"{self.base_url}/brain/build_fullstack", json={
                "name": name, "kind": kind, "theme": theme,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def build_cli(self, name="tool", task=None, args=None):
        try:
            r = requests.post(f"{self.base_url}/brain/build_cli", json={
                "name": name, "task": task, "args": args,
            }, timeout=10.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def debug_app(self, name="", fix=False):
        try:
            r = requests.post(f"{self.base_url}/brain/debug_app", json={
                "name": name, "fix": fix,
            }, timeout=30.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_apps(self):
        try:
            r = requests.get(f"{self.base_url}/brain/apps", timeout=3.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_code(self, task, language="python"):
        try:
            r = requests.post(f"{self.base_url}/brain/generate_code", json={
                "task": task,
                "language": language,
            }, timeout=5.0)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
