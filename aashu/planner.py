import re
import datetime

from core.tool_connector import ToolConnector


def _today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")


class PlanExecutor:
    """Deterministic multi-step planner.

    Decomposes a high-level goal into an ordered sequence of tool calls and
    executes them, tracking progress and feeding results back to the brain."""

    def __init__(self, actuators, brain_client=None):
        self.actuators = actuators
        self.brain_client = brain_client

    def _resolver(self):
        connector = ToolConnector()
        for tool in self.actuators.get_registered_tools_definitions():
            connector.register_tool(
                name=tool["name"],
                description=tool["description"],
                parameters=tool.get("parameters", {}),
                patterns=tool.get("patterns", []),
            )
        return connector

    def plan(self, goal):
        """Decompose a goal into an ordered list of steps."""
        goal = (goal or "").strip()
        if not goal:
            return []
        g = goal.lower()

        if any(k in g for k in ("morning briefing", "start my day", "set up my day", "morning routine", "good morning")):
            return [
                {"name": "get_time", "arguments": {}, "description": "Read current time"},
                {"name": "get_events", "arguments": {"date": _today_str()}, "description": "Check today's calendar"},
                {"name": "system_diagnostics", "arguments": {}, "description": "Check system health"},
                {"name": "get_weather", "arguments": {"location": ""}, "description": "Fetch today's weather"},
            ]

        if any(k in g for k in ("plan my day", "my schedule", "today's plan", "what's on today", "whats on today")):
            return [
                {"name": "get_time", "arguments": {}, "description": "Read current time"},
                {"name": "get_events", "arguments": {"date": _today_str()}, "description": "Check today's calendar"},
            ]

        if "diagnostics" in g or "system health" in g or "how is my system" in g:
            return [
                {"name": "system_diagnostics", "arguments": {}, "description": "Gather hardware stats"},
                {"name": "optimize_memory", "arguments": {}, "description": "Free up system memory"},
            ]

        if "learn" in g and "learn about" not in g:
            topic = re.sub(r".*learn\s+", "", goal).strip()
            return [{"name": "learn_topic", "arguments": {"topic": topic}, "description": f"Learn about {topic} from the internet"}]

        if "learn about" in g:
            topic = re.sub(r".*learn about\s+", "", goal).strip()
            return [{"name": "learn_topic", "arguments": {"topic": topic}, "description": f"Learn about {topic} from the internet"}]

        if "code" in g or "write a program" in g:
            task = re.sub(r".*(write|generate|make|create)\s+(a\s+)?", "", goal).strip()
            return [{"name": "write_code", "arguments": {"task": task or goal, "language": "python"}, "description": f"Generate {task or 'code'}"}]

        if "summarize" in g:
            m = re.search(r"summarize\s+([\w\.\-]+)", goal)
            filename = m.group(1) if m else "document.txt"
            return [{"name": "summarize_document", "arguments": {"filename": filename}, "description": "Summarize a document"}]

        if "organize" in g or "clean downloads" in g:
            return [{"name": "organize_downloads", "arguments": {"target_dir": ""}, "description": "Organize download folder"}]

        if "note" in g and "remember" in g:
            return [{"name": "add_note", "arguments": {"content": goal}, "description": "Save a note"}]

        # Generic fallback: best single-tool match from the registry
        resolved = self._resolver().resolve(goal)
        if resolved and resolved["name"] != "execute_task":
            return [{"name": resolved["name"], "arguments": resolved["arguments"], "description": resolved["name"].replace("_", " ")}]

        return []

    def execute(self, goal, record_goal=True):
        """Run a multi-step plan and return a structured report."""
        steps = self.plan(goal)
        if not steps:
            return {
                "goal": goal,
                "status": "no_plan",
                "message": "I could not break that goal into steps.",
                "steps": [],
                "results": [],
                "successes": 0,
                "failures": 0,
            }

        results = []
        successes = 0
        failures = 0

        for step in steps:
            name = step["name"]
            args = step["arguments"]
            try:
                outcome = self.actuators.execute_tool(name, args)
            except Exception as e:
                outcome = f"Execution Error: {e}"
            results.append({"step": name, "arguments": args, "result": outcome})
            if "Error" in str(outcome) and "Error:" in str(outcome):
                failures += 1
            else:
                successes += 1

            if self.brain_client is not None:
                try:
                    self.brain_client.send_perception_raw({
                        "content": f"Plan step '{name}' for goal '{goal}' completed. Result: {outcome}",
                        "category": "plan_step",
                        "modality": "experience",
                        "valence": 0.15 if "Error" not in str(outcome) else -0.3,
                        "intensity": 0.4,
                        "source": "planner",
                    })
                except Exception:
                    pass

        if record_goal and self.brain_client is not None:
            try:
                reward = 0.3 if failures == 0 else 0.1
                self.brain_client.manage_goal("task_mastery", reward=reward)
            except Exception:
                pass

        return {
            "goal": goal,
            "status": "completed" if failures == 0 else "completed_with_errors",
            "steps": [s["name"] for s in steps],
            "results": results,
            "successes": successes,
            "failures": failures,
        }

    def format_report(self, report):
        if report.get("status") == "no_plan":
            return report.get("message", "No plan available.")
        lines = [f"Plan for: {report['goal']}"]
        for res in report["results"]:
            lines.append(f"  -> {res['step']}: {res['result']}")
        lines.append(f"Completed: {report['successes']} steps, {report['failures']} issues.")
        return "\n".join(lines)
