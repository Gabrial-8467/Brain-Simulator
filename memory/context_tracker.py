class ContextTracker:
    def generate_key(self, event_type, source=None, tags=None):
        parts = [event_type]

        if source:
            parts.append(f"from_{source}")

        if tags:
            parts.extend(tags)

        return "_".join(parts)
