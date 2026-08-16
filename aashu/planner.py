import re
import datetime

from .local_tool_connector import ToolConnector


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

        if "learn about" in g:
            topic = re.sub(r".*learn about\s+", "", goal).strip()
            return [{"name": "learn_topic", "arguments": {"topic": topic}, "description": f"Learn about {topic} from the internet"}]

        if "learn" in g:
            topic = re.sub(r".*learn\s+", "", goal).strip()
            return [{"name": "learn_topic", "arguments": {"topic": topic}, "description": f"Learn about {topic} from the internet"}]

        # ---- Debug / repair generated apps ----
        m = re.search(r"(?:debug|find bugs in|check .* for bugs|fix .*bugs in)\s+(?:the |this )?(?:app )?(?:called |named )?([\w\s\-]+)", goal, re.IGNORECASE)
        if m and re.search(r"debug|bugs|fix", goal, re.IGNORECASE):
            app_name = re.sub(r"\s+(?:app|application)$", "", m.group(1).strip(), flags=re.IGNORECASE)
            wants_fix = bool(re.search(r"fix|repair|solve", goal, re.IGNORECASE))
            return [{"name": "debug_app",
                     "arguments": {"name": app_name, "fix": wants_fix},
                     "description": f"{'Fix' if wants_fix else 'Debug'} the {app_name} app"}]

        # ---- Vertical full-stack apps (food delivery, ecommerce, tracker, chat, ...) ----
        fullstack_kinds = {
            "food_delivery": ["food delivery", "zomato", "swiggy", "restaurant ordering", "delivery app", "like zomato"],
            "ecommerce": ["ecommerce", "e-commerce", "online store", "shop app", "shopping app"],
            "booking": ["booking app", "reservation app", "appointment app", "bookings"],
            "task_tracker": ["task tracker", "task app", "todo app", "to-do app"],
            "chat": ["chat app", "messaging app", "chatroom"],
            "blog": ["blog app", "blog", "cms", "articles app"],
            "notes": ["notes app", "note taking app", "notebook app"],
            "fitness": ["fitness tracker", "workout tracker", "health tracker", "workout app"],
        }
        for kind, keys in fullstack_kinds.items():
            if any(k in goal for k in keys):
                m = re.search(r"(?:called|named)\s+(?:a\s+)?([\w\s\-]+)", goal, re.IGNORECASE)
                if not m:
                    m = re.search(r"(?:like|for)\s+(?:a\s+)?([\w\s\-]+)", goal, re.IGNORECASE)
                full_name = m.group(1).strip() if m else "myapp"
                backend = "flask"
                for token, name in [("django", "django"), ("express", "express"), ("fastify", "fastify")]:
                    if token in goal.lower():
                        backend = name
                        break
                frontend = "single"
                if re.search(r"\breact\b", goal.lower()):
                    frontend = "react"
                return [{"name": "build_fullstack", "arguments": {"name": full_name, "kind": kind,
                                                                  "backend": backend, "frontend": frontend,
                                                                  "theme": "light"},
                         "description": f"Build a {kind} full-stack app named {full_name} "
                                        f"({backend} backend, {frontend} frontend)"}]

        # ---- App / website / CLI generation ----
        m = re.search(r"build\s+(?:a|an)?\s*(react ?app|angular ?app|vue ?app|node ?server|express ?server|api ?server|sql schema|sql database|website|c#|web ?app|webapp|cli|tool|app)\s+(?:called|for|named)?\s*([\w\s\-]+)", goal, re.IGNORECASE)
        kind = m.group(1).lower().replace(" ", "") if m else None
        target = m.group(2).strip() if m and m.group(2) else goal
        if kind in ("website",):
            return [{"name": "build_website", "arguments": {"name": target, "title": target, "sections": "Home;About;Contact"}, "description": f"Build website for {target}"}]
        if kind in ("webapp",):
            return [{"name": "build_webapp", "arguments": {"name": target, "app_name": "app", "features": "Home", "pages": "Home;About"}, "description": f"Build web app for {target}"}]
        if kind in ("reactapp",):
            return [{"name": "build_reactapp", "arguments": {"name": target, "app_name": "app", "features": "Home", "pages": "Home;About"}, "description": f"Build React app for {target}"}]
        if kind in ("angularapp",):
            return [{"name": "build_angularapp", "arguments": {"name": target, "app_name": "app", "features": "Home", "pages": "Home;About"}, "description": f"Build Angular app for {target}"}]
        if kind in ("vueapp",):
            return [{"name": "build_vueapp", "arguments": {"name": target, "app_name": "app", "features": "Home", "pages": "Home;About"}, "description": f"Build Vue app for {target}"}]
        if kind in ("nodeserver", "expressserver", "apiserver"):
            return [{"name": "build_node_server", "arguments": {"name": target, "app_name": "server", "endpoints": "/;/health"}, "description": f"Build Node/Express server for {target}"}]
        if kind in ("sqlschema", "sqldatabase"):
            return [{"name": "build_sql_schema", "arguments": {"name": target, "entities": "users;orders"}, "description": f"Build SQL schema for {target}"}]
        if kind in ("cli", "tool", "app"):
            return [{"name": "build_cli", "arguments": {"name": target, "task": target, "args": ""}, "description": f"Build CLI tool for {target}"}]

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

        if "timer" in g or "remind me in" in g:
            m = re.search(r"(\d+)\s*(second|seconds|minute|minutes|hour|hours)?", g)
            amount = int(m.group(1)) if m else 60
            unit = (m.group(2) or "seconds").lower()
            if unit.startswith("minute"):
                amount *= 60
            elif unit.startswith("hour"):
                amount *= 3600
            label = re.sub(r".*(timer|remind me)\s+", "", goal).strip().capitalize() or "Timer Alert"
            return [{"name": "set_timer", "arguments": {"seconds": str(amount), "label": label}, "description": f"Set a timer for {amount} seconds"}]

        if "email" in g:
            return [{"name": "send_email", "arguments": {"to_address": "", "subject": goal, "body": ""}, "description": "Compose and send an email"}]

        if "music" in g or "play a song" in g or "play some" in g:
            return [{"name": "play_music", "arguments": {"filepath": ""}, "description": "Play music"}]

        if "weather" in g or "forecast" in g:
            m = re.search(r"(?:in|for)\s+([\w\s\-]+)", goal)
            location = m.group(1).strip() if m else ""
            return [{"name": "get_weather", "arguments": {"location": location}, "description": f"Fetch weather for {location or 'current location'}"}]

        if "joke" in g:
            return [{"name": "get_joke", "arguments": {}, "description": "Tell a joke"}]

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
            if "Error" in str(outcome) and "Error:" in str(outcome):
                # Re-plan this single step: try an alternative tool that
                # matches the same intent before counting it as a failure.
                alternative = self._find_alternative(goal, name, step.get("description", ""))
                if alternative:
                    results.append({"step": name, "arguments": args,
                                    "result": outcome, "retried_as": alternative["name"],
                                    "retry_result": alternative["outcome"]})
                    if "Error" not in str(alternative["outcome"]):
                        successes += 1
                        self._report_step(goal, alternative["name"], alternative["outcome"])
                        continue
                    outcome = f"{outcome} Retry via {alternative['name']} also failed: {alternative['outcome']}"
                failures += 1
            else:
                successes += 1
            results.append({"step": name, "arguments": args, "result": outcome})
            self._report_step(goal, name, outcome)

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

    def _find_alternative(self, goal, failed_name, description=""):
        """Try to find a different tool that can satisfy the same intent."""
        if self.actuators is None:
            return None
        probe = f"{description} {goal}"
        try:
            resolved = self._resolver().resolve(probe)
        except Exception:
            return None
        if not resolved or resolved["name"] == failed_name or resolved["name"] == "execute_task":
            return None
        try:
            outcome = self.actuators.execute_tool(resolved["name"], resolved["arguments"])
        except Exception as e:
            outcome = f"Execution Error: {e}"
        return {"name": resolved["name"], "outcome": outcome}

    def _report_step(self, goal, name, outcome):
        if self.brain_client is None:
            return
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

    def format_report(self, report):
        if report.get("status") == "no_plan":
            return report.get("message", "No plan available.")
        lines = [f"Plan for: {report['goal']}"]
        for res in report["results"]:
            if res.get("retried_as"):
                lines.append(f"  -> {res['step']}: failed, retried as {res['retried_as']} -> {res.get('retry_result')}")
            else:
                lines.append(f"  -> {res['step']}: {res['result']}")
        lines.append(f"Completed: {report['successes']} steps, {report['failures']} issues.")
        return "\n".join(lines)
