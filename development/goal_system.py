# development/goal_system.py

class GoalSystem:

    def __init__(self):
        self.goals = {}

    # -----------------------------------------
    # GOAL INSTANTIATION & REINFORCEMENT
    # -----------------------------------------

    def create_or_update_goal(self, goal_name: str, reward: float) -> None:
        """
        Accumulate value/strength for a goal based on simulation rewards.
        
        Formula:
            Goal Value <- Goal Value + Reward * 0.05
        """
        val = self.goals.get(goal_name, 0.0)
        self.goals[goal_name] = val + reward * 0.05

    # -----------------------------------------
    # ACTIVE GOAL RETRIEVAL
    # -----------------------------------------

    def get_active_goal(self) -> str | None:
        """Return the active goal key with the highest value, or None if no goals exist."""
        if not self.goals:
            return None
        return max(self.goals, key=self.goals.get)

    # -----------------------------------------
    # HOMEOSTATIC DECAY
    # -----------------------------------------

    def decay(self) -> None:
        """
        Decay active goals slowly over time.
        
        Formula:
            Goal Value <- Goal Value * 0.999 per simulation cycle.
        """
        for goal in self.goals:
            self.goals[goal] *= 0.999
