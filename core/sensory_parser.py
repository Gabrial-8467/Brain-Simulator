import re
from typing import Any

class SensoryParser:
    def __init__(self, text_processor):
        self.text_processor = text_processor
        self.scene_counts = {}

    def analyze_perception(
        self,
        modality: str,
        content: str,
        valence: float = 0.0,
        provided_scene: dict | None = None,
    ) -> dict:
        text = (content or "").lower()
        tokens = [self.text_processor.normalize_token(t) for t in re.findall(r"[a-zA-Z]+", text)]
        provided_scene = provided_scene or {}

        entity_vocab = {
            "person", "cat", "dog", "hand", "fingers", "face", "eyes",
            "camera", "room", "table", "chair", "screen", "phone",
            "bottle", "book", "window", "door",
        }
        attribute_vocab = {
            "bright", "brightness", "dark", "darkness", "red", "blue", "green",
            "small", "large", "near", "behind", "front", "left", "right",
        }
        relation_markers = {"near", "behind", "front", "left", "right", "with", "on", "under"}

        entities = [t for t in tokens if t in entity_vocab]
        attributes = [t for t in tokens if t in attribute_vocab]
        entities.extend([self.text_processor.normalize_token(x) for x in provided_scene.get("objects", []) if self.text_processor.normalize_token(x)])
        for attrs in provided_scene.get("attributes", {}).values():
            attributes.extend([self.text_processor.normalize_token(a) for a in attrs if self.text_processor.normalize_token(a)])

        relations = []
        for i, tok in enumerate(tokens):
            if tok in relation_markers and i > 0 and i < len(tokens) - 1:
                left = tokens[i - 1]
                right = tokens[i + 1]
                if left in entity_vocab and right in entity_vocab:
                    relations.append({"from": left, "rel": tok, "to": right})
        for rel in provided_scene.get("relations", []):
            left = self.text_processor.normalize_token(str(rel.get("from", "")))
            edge = self.text_processor.normalize_token(str(rel.get("rel", "")))
            right = self.text_processor.normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                relations.append({"from": left, "rel": edge, "to": right})

        fingerprint = f"{modality}:{' '.join([t for t in tokens if t])}".strip()
        seen_count = self.scene_counts.get(fingerprint, 0)
        novelty = 0.8 if seen_count == 0 else max(0.02, 0.8 / (seen_count + 1))
        self.scene_counts[fingerprint] = seen_count + 1

        salience_structural = min(
            1.0,
            (len(set(entities)) * 0.2) + (len(relations) * 0.15) + (len(set(attributes)) * 0.1),
        )
        salience = max(abs(valence), salience_structural, float(provided_scene.get("salience", 0.0)))
        task_relevance = min(1.0, (0.3 if "person" in entities else 0.0) + (0.2 if "camera" in entities else 0.0))
        confidence = min(
            1.0,
            max(
                float(provided_scene.get("confidence", 0.0)),
                0.4 + 0.1 * len(set(entities)) + 0.1 * len(relations),
            ),
        )

        summary_parts = []
        if entities:
            summary_parts.append("entities=" + ",".join(sorted(set(entities))[:4]))
        if attributes:
            summary_parts.append("attributes=" + ",".join(sorted(set(attributes))[:4]))
        if relations:
            r = relations[0]
            summary_parts.append(f"relation={r['from']} {r['rel']} {r['to']}")
        summary = "; ".join(summary_parts) if summary_parts else content[:120]

        return {
            "modality": modality,
            "tokens": tokens,
            "entities": sorted(set(entities)),
            "attributes": sorted(set(attributes)),
            "relations": relations,
            "novelty": float(provided_scene.get("novelty", novelty)),
            "salience": salience,
            "task_relevance": task_relevance,
            "confidence": confidence,
            "summary": summary,
        }

    def parse_visual_signal(self, signal: Any) -> dict[str, Any] | None:
        def _read(name: str, default: Any):
            if hasattr(signal, name):
                return getattr(signal, name)
            if isinstance(signal, dict):
                return signal.get(name, default)
            return default

        objects = [str(x).strip().lower() for x in (_read("objects", []) or []) if str(x).strip()]
        attributes = _read("attributes", {}) or {}
        relations = _read("relations", []) or []
        motion_level = float(_read("motion_level", 0.0))
        confidence = float(_read("confidence", 0.7))
        source = str(_read("source", "vision_sensor"))

        if not objects and not attributes and not relations:
            return None

        motion_level = max(0.0, min(1.0, motion_level))
        confidence = max(0.0, min(1.0, confidence))

        parts = []
        if objects:
            parts.append("objects: " + ", ".join(objects))

        attr_descriptions = []
        for obj, attrs in attributes.items():
            norm_obj = self.text_processor.normalize_token(str(obj))
            norm_attrs = [self.text_processor.normalize_token(str(a)) for a in (attrs or []) if self.text_processor.normalize_token(str(a))]
            if norm_obj and norm_attrs:
                attr_descriptions.append(f"{norm_obj} is " + "/".join(norm_attrs))
        if attr_descriptions:
            parts.append("attributes: " + "; ".join(attr_descriptions))

        normalized_relations = []
        for rel in relations:
            left = self.text_processor.normalize_token(str(rel.get("from", "")))
            edge = self.text_processor.normalize_token(str(rel.get("rel", "")))
            right = self.text_processor.normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                if edge == "threat" and left == right:
                    continue
                normalized_relations.append({"from": left, "rel": edge, "to": right})

        relation_labels = {str(rel.get("rel", "")).lower() for rel in normalized_relations}
        category = "environment_scan"
        valence = 0.1
        intensity = 0.28 + (motion_level * 0.18)
        if "threat" in relation_labels or motion_level > 0.9:
            category = "threat_detected"
            valence = -0.8
            intensity = max(0.8, 0.65 + motion_level * 0.2)
        elif "face" in objects and confidence >= 0.75:
            category = "face_recognized"
            valence = 0.5
            intensity = 0.42 + (motion_level * 0.2)
        elif "face" in objects:
            category = "face_unknown"
            valence = 0.2
            intensity = 0.5 + (motion_level * 0.18)

        if category == "threat_detected":
            relations_for_scene = [r for r in normalized_relations if r.get("rel") != "threat"]
            unique_objects = []
            for obj in objects:
                if obj not in unique_objects:
                    unique_objects.append(obj)
            if len(unique_objects) >= 2:
                relations_for_scene.append(
                    {
                        "from": unique_objects[0],
                        "rel": "threat",
                        "to": unique_objects[1],
                    }
                )
        else:
            relations_for_scene = [r for r in normalized_relations if r.get("rel") != "threat"]

        rel_descriptions = []
        for rel in relations_for_scene:
            left = self.text_processor.normalize_token(str(rel.get("from", "")))
            edge = self.text_processor.normalize_token(str(rel.get("rel", "")))
            right = self.text_processor.normalize_token(str(rel.get("to", "")))
            if left and edge and right:
                rel_descriptions.append(f"{left} {edge} {right}")
        if rel_descriptions:
            parts.append("relations: " + "; ".join(rel_descriptions))

        parts.append(f"motion={motion_level:.2f}")
        parts.append(f"confidence={confidence:.2f}")
        scene_text = " | ".join(parts)

        return {
            "modality": "vision",
            "content": scene_text,
            "category": category,
            "source": source,
            "valence": valence,
            "intensity": max(0.2, min(0.95, intensity)),
            "scene": {
                "objects": objects,
                "attributes": attributes,
                "relations": relations_for_scene,
                "confidence": confidence,
            },
        }

    def parse_hearing_signal(self, signal: Any) -> dict[str, Any] | None:
        def _read(name: str, default: Any):
            if hasattr(signal, name):
                return getattr(signal, name)
            if isinstance(signal, dict):
                return signal.get(name, default)
            return default

        transcript = str(_read("transcript", "")).strip()
        speaker_type = str(_read("speaker_type", "unknown")).strip().lower()
        sentiment = float(_read("sentiment", 0.0))
        prosody_intensity = float(_read("prosody_intensity", 0.5))
        keywords = [str(k).strip().lower() for k in (_read("keywords", []) or []) if str(k).strip()]
        source = str(_read("source", "audio_sensor"))

        if not transcript:
            return None

        sentiment = max(-1.0, min(1.0, sentiment))
        prosody_intensity = max(0.0, min(1.0, prosody_intensity))

        text_lower = transcript.lower()
        if "why did you do that" in text_lower and "accountability" not in keywords:
            keywords.append("accountability")
        category = "speech_detected"
        valence = 0.2
        intensity = 0.3 + (prosody_intensity * 0.25)
        if not transcript.strip() or "silence" in keywords:
            category = "boredom"
            valence = -0.2
            intensity = 0.22
        elif "loud_noise" in keywords or "bang" in text_lower or "alarm" in text_lower:
            category = "loud_noise"
            valence = -0.4
            intensity = max(0.75, prosody_intensity)
        elif speaker_type in {"caregiver", "teacher", "peer"}:
            category = "voice_recognized"
            valence = self._voice_valence_from_keywords(keywords)
            intensity = 0.35 + (prosody_intensity * 0.25)

        salience = 0.4 if {"accountability", "confrontation"} & set(keywords) else abs(valence)

        hearing_text = (
            f"speaker={speaker_type} | text={transcript if transcript else 'silence'} | "
            f"sentiment={sentiment:.2f} | prosody={prosody_intensity:.2f} | "
            f"keywords={','.join(keywords)}"
        )

        return {
            "modality": "hearing",
            "content": hearing_text,
            "category": category,
            "source": source,
            "valence": valence,
            "intensity": max(0.2, min(0.95, intensity)),
            "scene": {
                "speaker_type": speaker_type,
                "keywords": keywords,
                "prosody_intensity": prosody_intensity,
                "sentiment": sentiment,
                "salience": salience,
            },
        }

    def _voice_valence_from_keywords(self, keywords: list[str] | set[str]) -> float:
        keyword_set = {str(k).strip().lower() for k in (keywords or []) if str(k).strip()}
        if "accountability" in keyword_set or "confrontation" in keyword_set:
            return -0.2
        if "criticism" in keyword_set:
            return -0.5
        if "lonely" in keyword_set or "ignored" in keyword_set:
            return -0.4
        if "question" in keyword_set:
            return 0.0
        if {"praise", "support", "effort"} & keyword_set:
            return 0.5
        if "collaboration" in keyword_set:
            return 0.3
        if {"social", "greeted"} & keyword_set:
            return 0.4
        return 0.1
