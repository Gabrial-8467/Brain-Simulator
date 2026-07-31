import copy

class GoalSystem:
    def __init__(self):
        self.goals = {}

    def create_or_update_goal(self, goal_name: str, reward: float) -> None:
        """Accumulate goal value based on rewards."""
        val = self.goals.get(goal_name, 0.0)
        self.goals[goal_name] = val + reward * 0.05

    def get_active_goal(self) -> str | None:
        """Return the goal name with the highest value, or None if no goals are present."""
        if not self.goals:
            return None
        # Return the key with the highest value
        return max(self.goals, key=self.goals.get)

    def decay(self) -> None:
        """Decay goal values slowly over time."""
        for goal in self.goals:
            self.goals[goal] *= 0.999
