class PatternEngine:
    def __init__(self):
        self.transitions = {}
        self.last_event = None

    def update(self, current_event):
        if self.last_event is not None:

            if self.last_event not in self.transitions:
                self.transitions[self.last_event] = {}

            if current_event not in self.transitions[self.last_event]:
                self.transitions[self.last_event][current_event] = 0

            self.transitions[self.last_event][current_event] += 1

        self.last_event = current_event

    def predict_next(self, current_event):
        if current_event not in self.transitions:
            return None, 0

        next_events = self.transitions[current_event]
        total = sum(next_events.values())

        if total == 0:
            return None, 0

        predicted = max(next_events, key=next_events.get)
        confidence = next_events[predicted] / total

        return predicted, confidence

    def apply_prediction_error(self, previous_event, actual_event):
        if previous_event in self.transitions:
            if actual_event not in self.transitions[previous_event]:
                self.transitions[previous_event][actual_event] = 0

            # strengthen correct predictions
            self.transitions[previous_event][actual_event] += 1
