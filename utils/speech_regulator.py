class SpeechRegulator:
    @staticmethod
    def regulate(text: str, fatigue: float, cortisol: float, oxytocin: float, stage: str) -> str:
        if not text:
            return text

        controlled = text.strip()

        if fatigue > 0.7 or cortisol > 70:
            parts = controlled.split(".")
            controlled = parts[0].strip()
            if not controlled.endswith((".", "!", "?")):
                controlled += "."

        if stage == "child":
            words = controlled.split()
            controlled = " ".join(words[:28]).strip()
            if controlled and not controlled.endswith((".", "!", "?")):
                controlled += "."

        trailing_bad = {"and", "or", "but", "so", "because"}
        tokens = controlled.rstrip(".!? ").split()
        if tokens and tokens[-1].lower() in trailing_bad:
            tokens = tokens[:-1]
            if tokens:
                controlled = " ".join(tokens).strip()
                if not controlled.endswith((".", "!", "?")):
                    controlled += "."

        if oxytocin > 70 and not any(
            controlled.lower().startswith(prefix)
            for prefix in ("i ", "we ", "let", "you're", "you are")
        ):
            controlled = "I hear you. " + controlled

        return controlled
