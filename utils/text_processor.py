import re

class TextProcessor:
    def __init__(self):
        self.stopwords = {
            "i", "me", "my", "mine", "myself", "am", "being",
            "a", "an", "the", "is", "are", "was", "were",
            "for", "to", "and", "it", "that", "of", "in",
            "nothing", "something", "with", "be", "have",
            "has", "had", "do", "did", "at", "by", "from",
            "on", "or", "but", "not", "no", "so", "if", "as",
            "you", "your",
            "this", "its", "near", "under",
            "object", "objects", "attribute", "attributes", "relation", "relations",
            "motion", "confidence",
            "speaker", "text", "keyword", "keywords", "sentiment", "prosody",
            "objects", "relations",
        }
        self.concept_aliases = {
            "finger": "fingers",
            "fingers": "fingers",
            "hand": "hand",
            "cat": "cat",
            "cats": "cat",
            "dog": "dog",
            "dogs": "dog",
            "face": "face",
            "eyes": "eyes",
            "eye": "eyes",
            "camera": "camera",
            "light": "light",
            "dark": "darkness",
            "bright": "brightness",
            "person": "person",
            "people": "person",
            "man": "person",
            "woman": "person",
            "child": "person",
            "kitten": "cat",
            "puppy": "dog",
            "room": "room",
            "table": "table",
            "chair": "chair",
            "screen": "screen",
            "monitor": "screen",
            "phone": "phone",
            "bottle": "bottle",
            "book": "book",
            "window": "window",
            "door": "door",
            "left": "left",
            "right": "right",
            "near": "near",
            "behind": "behind",
            "front": "front",
            "red": "red",
            "blue": "blue",
            "green": "green",
            "small": "small",
            "large": "large",
        }

    def normalize_token(self, token: str) -> str:
        base = token.lower().strip()
        if base in self.stopwords:
            return ""
        if base in self.concept_aliases:
            return self.concept_aliases[base]
        if base.endswith("es") and len(base) > 4:
            base = base[:-2]
        elif base.endswith("s") and len(base) > 3:
            base = base[:-1]
        return self.concept_aliases.get(base, base)

    def extract_concepts(self, text: str, modality: str = "experience") -> list[str]:
        tokens = re.findall(r"[a-zA-Z]+", (text or "").lower())
        concepts = []
        for tok in tokens:
            if len(tok) < 3:
                continue
            if tok == "you":
                if modality in {"hearing", "vision"}:
                    concepts.append("you")
                continue
            mapped = self.normalize_token(tok)
            if mapped and len(mapped) >= 3 and mapped not in self.stopwords:
                concepts.append(mapped)
        return concepts
