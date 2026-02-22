# core/development.py

class DynamicDevelopment:

    def __init__(self):

        # Growth based on lived experience
        self.experience_points = 0
        self.emotional_weight = 0
        self.stress_exposure = 0
        self.success_exposure = 0
        self.reflection_depth = 0

        self.maturity = 0.1

    # -----------------------------------------
    # EXPERIENCE OBSERVATION
    # -----------------------------------------

    def observe_event(self, event_type, chemical_state):

        cortisol = chemical_state.get("cortisol", 0)
        dopamine = chemical_state.get("dopamine", 0)

        intensity = abs(dopamine - cortisol)

        self.experience_points += 1
        self.emotional_weight += intensity * 0.01

        if cortisol > 60:
            self.stress_exposure += 1

        if dopamine > 65:
            self.success_exposure += 1

    # -----------------------------------------
    # REFLECTION PROCESS
    # -----------------------------------------

    def reflect(self, intelligence_level):

        growth = self.emotional_weight * intelligence_level * 0.001
        self.reflection_depth += growth

    # -----------------------------------------
    # MATURITY UPDATE
    # -----------------------------------------

    def update(self):

        experience_factor = min(1.0, self.experience_points / 500)
        emotional_factor = min(1.0, self.reflection_depth / 50)

        stress_balance = min(1.0, self.stress_exposure / 100)
        success_balance = min(1.0, self.success_exposure / 100)

        balance_factor = abs(success_balance - stress_balance)

        self.maturity = (
            experience_factor * 0.4 +
            emotional_factor * 0.4 +
            (1 - balance_factor) * 0.2
        )

        self.maturity = min(1.0, self.maturity)

    def get_snapshot(self):
        return {
            "maturity": self.maturity,
            "experience_points": self.experience_points,
            "reflection_depth": self.reflection_depth
        }
