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
from pathlib import Path

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

    def build_website(self, name="My Website", title=None, sections=None, theme="light"):
        ok, result = self.brain.build_website(name=name, title=title, sections=sections, theme=theme)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_webapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, result = self.brain.build_webapp(name=name, app_name=app_name, features=features, pages=pages)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_reactapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, result = self.brain.build_reactapp(name=name, app_name=app_name, features=features, pages=pages)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_angularapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, result = self.brain.build_angularapp(name=name, app_name=app_name, features=features, pages=pages)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_vueapp(self, name="My App", app_name="app", features=None, pages=None):
        ok, result = self.brain.build_vueapp(name=name, app_name=app_name, features=features, pages=pages)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_node_server(self, name="My Server", app_name="server", endpoints=None):
        ok, result = self.brain.build_node_server(name=name, app_name=app_name, endpoints=endpoints)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_sql_schema(self, name="app", entities=None):
        ok, result = self.brain.build_sql_schema(name=name, entities=entities)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_fullstack(self, name="My App", kind="food_delivery", backend="flask",
                        frontend="single", theme="light"):
        ok, result = self.brain.build_fullstack(name=name, kind=kind, backend=backend,
                                                frontend=frontend, theme=theme)
        return {"status": "success" if ok else "not_learned", "message": result}

    def build_cli(self, name="tool", task=None, args=None):
        ok, result = self.brain.build_cli(name=name, task=task, args=args)
        return {"status": "success" if ok else "not_learned", "message": result}


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
        "set a timer for 90 seconds to take the cookies out",
        "calculate 45 * 3 + 12",
        "what do you know about me",
        "open the browser",
    ]:
        match = brain.resolve_tool(query)
        if match:
            print(f"  '{query}'\n      -> tool={match['name']}  args={match['arguments']}  conf={match['confidence']}  (seconds is {type(match['arguments'].get('seconds')).__name__})")
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
    print("  richer vision now tracks: motion_direction, moving_objects (blobs), time_of_day, last_visual_report()")

    # ---------------------------------------------------------------
    section("6. FULL APP / WEBSITE GENERATION  (brain-owned AppBuilder)")
    print("Gate check: build_website('Portfolio', ...) before learning html")
    ok, msg = brain.build_website("Portfolio", title="Portfolio", sections="Home;About;Contact")
    print(f"  -> ok={ok}, message={msg!r}")

    print("\nAashu learns HTML from the internet:")
    brain.perceive({
        "content": "Learn the programming language html. HTML uses tags like <html>, <body>, <h1> for headings, "
                   "<p> for paragraphs, <a href> for links, <section> for sections, and <style> for CSS.",
        "category": "learning",
        "modality": "experience",
        "valence": 0.4,
        "intensity": 0.6,
        "source": "internet",
    })
    print(f"  known languages: {brain.language_cortex.known_languages()}")

    ok, msg = brain.build_website("Portfolio", title="My Portfolio", sections="Home;About;Contact", theme="dark")
    print(f"\nbuild_website('Portfolio', theme=dark) ->\n  {msg}")
    ok, msg = brain.build_webapp("TaskBoard", app_name="app", features="auth;dashboard", pages="Home;About")
    print(f"\nbuild_webapp('TaskBoard') ->\n  {msg}")
    ok, msg = brain.build_cli("greet", task="print a greeting", args="name")
    print(f"\nbuild_cli('greet') ->\n  {msg}")

    print("\nAppBuilder project list:")
    for p in brain.app_builder.list_projects():
        print(f"  - {p['name']}: {', '.join(p['files'])}")

    print("\nAashu learns the JS ecosystem from the internet:")
    brain.perceive({
        "content": "Learn the programming language reactjs. React uses JSX: components are functions returning JSX, "
                   "props come in as arguments, useState manages state, and the default export is the App component.",
        "category": "learning",
        "modality": "experience",
        "valence": 0.4,
        "intensity": 0.6,
        "source": "internet",
    })
    brain.perceive({
        "content": "Learn the programming language express. Express is a Node.js web framework: "
                   "app.get('/path', handler) defines routes and app.listen(port) starts the server.",
        "category": "learning",
        "modality": "experience",
        "valence": 0.4,
        "intensity": 0.6,
        "source": "internet",
    })
    brain.perceive({
        "content": "Learn the programming language nosql. NoSQL querying uses MongoDB syntax: "
                   "db.collection.find({ field: value }) and db.collection.insertOne({ data: true }).",
        "category": "learning",
        "modality": "experience",
        "valence": 0.4,
        "intensity": 0.6,
        "source": "internet",
    })
    print(f"  known languages: {brain.language_cortex.known_languages()}")

    for task, lang in [("build a hello world component", "reactjs"), ("start an api server", "express"), ("query active users", "nosql")]:
        ok, code = brain.generate_code(task, lang)
        print(f"\n  generate_code({task!r}, '{lang}') -> ok={ok}")
        print("  " + code.splitlines()[0] + ("" if len(code.splitlines()) == 1 else " ..."))

    ok, msg = brain.build_reactapp("Dashboard", app_name="Dashboard", features="auth;charts", pages="Home;About")
    print(f"\nbuild_reactapp('Dashboard') ->\n  {msg}")
    print("\nAppBuilder project list:")
    for p in brain.app_builder.list_projects():
        print(f"  - {p['name']}: {', '.join(p['files'])}")

    # ---------------------------------------------------------------
    section("6b. MORE GENERATORS + FULL-STACK VERTICAL APPS")
    print("Aashu learns the remaining web languages from the internet:")
    for name, snippet in [
        ("angular", "Learn the programming language angular. Angular apps use components with @Component decorators, "
                    "bootstrapApplication mounts the root component, and index.html hosts <app-root>."),
        ("vuejs", "Learn the programming language vuejs. Vue uses single-file components with <template>, <script setup> "
                  "and ref() for reactive state, mounted with createApp(App).mount('#app')."),
        ("nodejs", "Learn the programming language nodejs. Node uses require('express'), app.get('/path', handler) "
                   "routes and app.listen(port)."),
        ("sql", "Learn the programming language sql. SQL defines relational databases: CREATE TABLE IF NOT EXISTS, "
                "SERIAL PRIMARY KEY ids, VARCHAR columns, and TIMESTAMP DEFAULT CURRENT_TIMESTAMP."),
    ]:
        brain.perceive({
            "content": snippet,
            "category": "learning",
            "modality": "experience",
            "valence": 0.4,
            "intensity": 0.6,
            "source": "internet",
        })
    print(f"  known languages: {brain.language_cortex.known_languages()}")

    for name, kind in [("HireMe", "angular"), ("Bloggy", "vuejs"), ("Billing", "nodejs"), ("ZomatoClone", "food_delivery"),
                       ("ShopNow", "ecommerce"), ("BookIt", "booking"), ("TodoPro", "task_tracker"),
                       ("Chatter", "chat"), ("DevBlog", "blog"), ("QuickNotes", "notes"), ("FitLog", "fitness")]:
        builder = {"angular": brain.build_angularapp, "vuejs": brain.build_vueapp,
                   "nodejs": brain.build_node_server, "food_delivery": brain.build_fullstack,
                   "ecommerce": brain.build_fullstack, "booking": brain.build_fullstack,
                   "task_tracker": brain.build_fullstack, "chat": brain.build_fullstack,
                   "blog": brain.build_fullstack, "notes": brain.build_fullstack,
                   "fitness": brain.build_fullstack}[kind]
        fullstack_kinds = {"food_delivery", "ecommerce", "booking", "task_tracker", "chat", "blog", "notes", "fitness"}
        ok, msg = builder(name, kind=kind) if kind in fullstack_kinds else builder(name)
        print(f"\nbuild_{'fullstack' if kind in fullstack_kinds else kind}({name!r}) ->\n  {msg}")

    print("\n  Same vertical app on every backend / frontend (deterministic templates):")
    for name, backend, frontend in [("BookItDj", "django", "single"), ("BookItEx", "express", "react"),
                                    ("BookItFx", "fastify", "react")]:
        ok, msg = brain.build_fullstack(name, kind="booking", backend=backend, frontend=frontend)
        print(f"\nbuild_fullstack({name!r}, kind='booking', backend={backend!r}, frontend={frontend!r}) ->\n  {msg}")
    for name in ("BookItDj", "BookItEx", "BookItFx"):
        rep = brain.debug_app(name)
        print(f"debug_app({name!r}) -> ok={rep['ok']}, bugs={len(rep['bugs'])}")

    ok, msg = brain.build_sql_schema("orders", entities="users;orders;products")
    print(f"\nbuild_sql_schema('orders') ->\n  {msg}")
    print("\nAppBuilder project list:")
    for p in brain.app_builder.list_projects():
        print(f"  - {p['name']}: {', '.join(p['files'])}")

    section("6c. DEBUGGING GENERATED APPS  (deterministic, no LLM)")
    debug_name = "BookIt"
    dbg_root = Path(brain.app_builder._project_path(debug_name))
    for rel in ["backend/schema.sql", "backend/app.py"]:
        p = dbg_root / rel
        p.write_text(p.read_text().replace("CREATE TABLE IF NOT EXISTS orders", "CREATE TABLE IF NOT EXISTS bookings"))
    rep = brain.debug_app(debug_name)
    print(f"\ndebug_app({debug_name!r}) -> {rep['bug_count']} issue(s):")
    for b in rep["bugs"]:
        print(f"  [{b['severity']}] {b['location']}: {b['message']}")
    rep = brain.debug_app(debug_name, fix=True)
    print(f"\ndebug_app({debug_name!r}, fix=True) -> fixed={rep['fixed']}, remaining bugs={rep['bug_count']}")
    assert not rep["bugs"]
    assert "CREATE TABLE IF NOT EXISTS orders" in (dbg_root / "backend/schema.sql").read_text()

    # ---------------------------------------------------------------
    section("7. MEMORY CONSOLIDATION  (traits + forgetting curve)")
    print("Adding several short preference facts:")
    for fact in ["I like tea", "I prefer tea", "I drink tea daily"]:
        client.remember_user(fact, fact_type="preference", importance=0.4)
    before = brain.user_memory.profile()["total_facts"]
    created = brain.consolidate_user_memory()
    print(f"  before={before}, traits_created={created}")
    print("  traits now stored:")
    for f in brain.user_memory.facts():
        if f.get("derived"):
            print(f"    [trait] {f['content']}")
    removed = brain.decay_user_memory()
    print(f"  decay() removed {removed} stale low-importance facts.")

    # ---------------------------------------------------------------
    section("8. SHARPER TOOL CALLING  (named groups + typed args)")
    for query in [
        "set a timer for 45 seconds to brew the tea",
        "build a website called Portfolio",
        "build a web app called TaskBoard",
        "build a react app called Dashboard",
        "build a food delivery app like zomato",
        "build a task tracker app called TodoPro",
        "build a node server called Billing",
        "remind me in 5 minutes",
    ]:
        match = brain.resolve_tool(query)
        if match:
            args_desc = ", ".join(f"{k}={v!r}" for k, v in match["arguments"].items())
            print(f"  '{query}'\n      -> tool={match['name']}  args={{ {args_desc} }}  conf={match['confidence']}")
        else:
            print(f"  '{query}'\n      -> no match")

    print("\nPlanner 'build a website called Portfolio':")
    planner2 = PlanExecutor(actuators, brain_client=client)
    report3 = planner2.execute("build a website called Portfolio")
    print(planner2.format_report(report3))

    print("\nPlanner 'make an ecommerce app like amazon':")
    report4 = planner2.execute("make an ecommerce app like amazon")
    print(planner2.format_report(report4))

    # ---------------------------------------------------------------
    section("SUMMARY")
    print(f"  User profile:      {brain.user_profile()}")
    print(f"  Known languages:   {brain.language_cortex.known_languages()}")
    print(f"  User facts stored: {brain.user_memory.profile()['total_facts']}")
    print(f"  Goal system:       {brain.goal_system.goals}")
    print(f"  Generated apps:    {len(brain.app_builder.list_projects())} project(s) under generated_apps/")
    print(f"  Memory dir:        {tmp_dir}")

    brain.memory_manager.storage.save()
    print("\nDEMO COMPLETE. Brain state checkpoint saved.")


if __name__ == "__main__":
    main()
