#!/usr/bin/env python
"""
Live end-to-end demo of the Virtual Brain + Aashu assistant features:

  1. Brain-owned code generation (gated on learned languages)
  2. User long-term memory (vector-backed)
  3. Multi-step planning (deterministic PlanExecutor)
  4. Better tool calling (scoring ToolConnector)
  5. Better vision (person presence tracking)

Runs fully offline / in-process (no camera, no Ollama, no network needed).
"""

import os
import sys
import tempfile
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.brain import VirtualBrain
from decision.decision_engine import DecisionEngine
from aashu.actuators import AashuActuators
from aashu.planner import PlanExecutor


def _load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


class InProcessBrainClient:
    """Adapter exposing the BrainClient-style API directly against an
    in-process VirtualBrain instance, so the demo needs no HTTP server."""

    def __init__(self, brain):
        self.brain = brain

    def send_perception_raw(self, payload):
        self.brain.perceive(payload)
        return {"status": "success"}

    def send_visual_signal(self, objects=None, attributes=None, relations=None,
                           motion_level=0.0, confidence=0.7, source="camera_sensor"):
        payload = {
            "content": f"Visual scene with objects: {objects or []}",
            "category": "vision",
            "modality": "visual",
            "valence": 0.1,
            "intensity": 0.5,
            "source": source,
        }
        self.brain.perceive(payload)
        return {"status": "success"}

    def remember_user(self, fact, fact_type="general", importance=0.6):
        item = self.brain.remember_user(fact, fact_type=fact_type, importance=importance)
        return {"status": "success", "fact": item}

    def get_user_context(self, context=None):
        return {"status": "success", "context": self.brain.user_context(context or None)}

    def get_user_profile(self):
        return {"status": "success", "profile": self.brain.user_profile()}

    def manage_goal(self, name, reward=0.1):
        self.brain.goal_system.create_or_update_goal(name, reward)
        return {"status": "success"}

    def summarize_text(self, text, max_sentences=4):
        return {"status": "success", "summary": self.brain.summarize_text(text, max_sentences=max_sentences)}

    def generate_code(self, task, language="python"):
        ok, result = self.brain.generate_code(task, language)
        return {"status": "success" if ok else "not_learned", "code": result}

    def resolve_action(self, text, min_confidence=0.2):
        match = self.brain.resolve_tool(text, min_confidence=min_confidence)
        if match:
            return {"status": "success", **match}
        return {"status": "no_match"}


def build_brain():
    tmp = tempfile.mkdtemp(prefix="aashu_demo_")
    memory_path = os.path.join(tmp, "memory_store.json")

    decision_config = _load_yaml("config/decision.yaml").get("decision", {})
    chemical_configs = _load_yaml("config/chemicals.yaml")
    brain_config = _load_yaml("config/brain.yaml")

    decision_engine = DecisionEngine(
        decision_config=decision_config,
        deterministic=True,
    )

    brain = VirtualBrain(
        chemical_configs=chemical_configs["chemicals"],
        interaction_matrix=chemical_configs.get("interactions"),
        decision_engine=decision_engine,
        deterministic=True,
        brain_config=brain_config,
        memory_storage_path=memory_path,
    )
    return brain, tmp


def section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    print("AASHU + VIRTUAL BRAIN - LIVE END-TO-END DEMO")
    print("(fully offline, in-process, deterministic)\n")

    brain, tmp_dir = build_brain()
    client = InProcessBrainClient(brain)
    actuators = AashuActuators(mouth=None, eyes=None, brain_client=client)

    # ---------------------------------------------------------------
    section("1. BETTER TOOL CALLING  (scoring ToolConnector)")
    tools = actuators.get_registered_tools_definitions()
    for t in tools:
        brain.tool_connector.register_tool(
            name=t["name"], description=t["description"],
            parameters=t.get("parameters", {}), patterns=t.get("patterns", []),
        )
    print(f"Registered {len(tools)} tools with the brain.")
    for query in [
        "set a timer for 10 minutes",
        "calculate 45 * 3 + 12",
        "what do you know about me",
        "open the browser",
    ]:
        match = brain.resolve_tool(query)
        if match:
            print(f"  '{query}'\n      -> tool={match['name']}  args={match['arguments']}  conf={match['confidence']}")
        else:
            print(f"  '{query}'\n      -> no match")

    # ---------------------------------------------------------------
    section("2. USER LONG-TERM MEMORY  (vector-backed)")
    print("User: 'Remember that my name is Sam'")
    client.remember_user("My name is Sam", fact_type="identity", importance=0.9)
    print("User: 'Remember that I love jazz music'")
    client.remember_user("I love jazz music", fact_type="preference", importance=0.8)
    print("User: 'Remember that my favorite color is blue'")
    client.remember_user("My favorite color is blue", fact_type="preference", importance=0.7)
    print("User: 'Remember that I have a project due on Friday'")
    client.remember_user("I have a project due on Friday", fact_type="event", importance=0.6)

    ctx = client.get_user_context("what music do I like")
    print("\nConversation context for 'what music do I like':\n" + ctx["context"])

    # ---------------------------------------------------------------
    section("3. BRAIN-OWNED CODE GENERATION  (learned-language gated)")
    print("Before learning: generate_code('print hello', 'python')")
    ok, result = brain.generate_code("print hello world", "python")
    print(f"  -> ok={ok}, result={result!r}")

    print("\nAashu learns Python from the internet:")
    brain.perceive({
        "content": "Learn the programming language python. Python syntax: use print() to output text, "
                   "define functions with 'def name(args):', use 'return' to give back a value, "
                   "declare variables with 'x = value', comments start with #.",
        "category": "learning",
        "modality": "experience",
        "valence": 0.4,
        "intensity": 0.6,
        "source": "internet",
    })
    print(f"  known languages: {brain.language_cortex.known_languages()}")

    ok, code = brain.generate_code("write a function that returns the sum of two numbers", "python")
    print(f"\nAfter learning -> generate_code(sum two numbers, python):\n{code}")

    ok2, code2 = brain.generate_code("print hello", "rust")
    print(f"\ngenerate_code(..., 'rust') -> ok={ok2}, result={code2!r}")

    # ---------------------------------------------------------------
    section("4. MULTI-STEP PLANNING  (deterministic PlanExecutor)")
    planner = PlanExecutor(actuators, brain_client=client)
    print("Goal: 'set up my day'")
    steps = planner.plan("set up my day")
    print("  plan steps: " + " -> ".join(s["name"] for s in steps))
    report = planner.execute("set up my day")
    print("\n  execution report:")
    print(planner.format_report(report))
    print(f"  goal system: {brain.goal_system.goals}")

    print("\nGoal: 'learn about neurons'")
    report2 = planner.execute("learn about neurons")
    print(planner.format_report(report2))

    # ---------------------------------------------------------------
    section("5. BETTER VISION  (person presence tracking)")
    eyes = actuators.eyes  # may be None; demonstrate logic via direct state
    print("Camera feed sees the user 'Sam'... (simulated)")
    brain.perceive({
        "content": "The user Sam is now present in front of me",
        "category": "user_presence",
        "modality": "visual",
        "valence": 0.2,
        "intensity": 0.5,
        "source": "eyes",
    })
    print("  scene_summary/recognition hooks available; presence -> user_memory + vision learning pipeline.")
    print("  recent focus after presence event:", brain.current_focus.content if brain.current_focus else None)

    # ---------------------------------------------------------------
    section("SUMMARY")
    print(f"  User profile:      {brain.user_profile()}")
    print(f"  Known languages:   {brain.language_cortex.known_languages()}")
    print(f"  User facts stored: {brain.user_memory.profile()['total_facts']}")
    print(f"  Goal system:       {brain.goal_system.goals}")
    print(f"  Memory dir:        {tmp_dir}")

    brain.memory_manager.storage.save()
    print("\nDEMO COMPLETE. Brain state checkpoint saved.")


if __name__ == "__main__":
    main()
