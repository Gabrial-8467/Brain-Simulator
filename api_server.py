import os
import sys
import argparse
import copy
import yaml
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.brain import VirtualBrain
from decision.decision_engine import DecisionEngine
from memory.memory_manager import MemoryManager
from utils.logger import BrainLogger

app = FastAPI(
    title="Virtual Brain API Server",
    description="REST API Gateway for the Developmental Cognitive Virtual Brain (Aashu Integration)",
    version="1.0.0"
)

# Logger
logger = BrainLogger()

# Global state
brain: Optional[VirtualBrain] = None
memory_manager: Optional[MemoryManager] = None

# =====================================================
# REQUEST SCHEMAS
# =====================================================

class PerceiveEventRequest(BaseModel):
    content: str
    category: Optional[str] = "experience"
    modality: Optional[str] = "experience"
    valence: Optional[float] = 0.0
    intensity: Optional[float] = 0.5
    source: Optional[str] = "simulated"
    timestamp: Optional[float] = None
    scene: Optional[Dict[str, Any]] = None

class PerceiveTextRequest(BaseModel):
    text: str
    source: Optional[str] = "user"
    modality: Optional[str] = "hearing"

class VisualSignalRequest(BaseModel):
    objects: List[str] = Field(default_factory=list)
    attributes: Dict[str, List[str]] = Field(default_factory=dict)
    relations: List[Dict[str, str]] = Field(default_factory=list)
    motion_level: Optional[float] = 0.0
    confidence: Optional[float] = 0.7
    source: Optional[str] = "vision_sensor"
    timestamp: Optional[float] = None

class SummarizeTextRequest(BaseModel):
    text: str
    max_sentences: Optional[int] = 4

class GenerateCodeRequest(BaseModel):
    task: str
    language: Optional[str] = "python"

class ResolveActionRequest(BaseModel):
    text: str

class RememberUserRequest(BaseModel):
    fact: str
    fact_type: Optional[str] = "general"
    importance: Optional[float] = 0.6

class BuildWebsiteRequest(BaseModel):
    name: Optional[str] = "My Website"
    title: Optional[str] = None
    sections: Optional[str] = None
    theme: Optional[str] = "light"

class BuildWebappRequest(BaseModel):
    name: Optional[str] = "My App"
    app_name: Optional[str] = "app"
    features: Optional[str] = None
    pages: Optional[str] = None

class BuildCliRequest(BaseModel):
    name: Optional[str] = "tool"
    task: Optional[str] = None
    args: Optional[str] = None

class HearingSignalRequest(BaseModel):
    transcript: str
    speaker_type: Optional[str] = "unknown"
    sentiment: Optional[float] = 0.0
    prosody_intensity: Optional[float] = 0.5
    keywords: List[str] = Field(default_factory=list)
    source: Optional[str] = "audio_sensor"
    timestamp: Optional[float] = None

class SpeechRegulationRequest(BaseModel):
    text: str

class ToolRegistrationRequest(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}, "required": []}
    )
    patterns: List[str] = Field(default_factory=list)

class SleepRequest(BaseModel):
    duration: Optional[int] = 5

class ChemicalModulationRequest(BaseModel):
    chemical: str
    value: Optional[float] = None
    delta: Optional[float] = None

class GoalRequest(BaseModel):
    name: str
    value: Optional[float] = None
    reward: Optional[float] = None

class ResetRequest(BaseModel):
    hard_reset: Optional[bool] = False


# =====================================================
# INITIALIZE BRAIN
# =====================================================

def init_brain(deterministic: bool = False):
    global brain, memory_manager
    
    # 1. Configs
    try:
        with open("config/chemicals.yaml", "r") as f:
            chemical_configs = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load chemicals config: {e}")
        sys.exit(1)

    try:
        with open("config/decision.yaml", "r") as f:
            payload = yaml.safe_load(f) or {}
            decision_config = payload.get("decision", payload)
    except Exception as e:
        logger.error(f"Failed to load decision config: {e}")
        sys.exit(1)

    brain_config = {}
    try:
        with open("config/brain.yaml", "r") as f:
            brain_config = yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"Failed to load brain config: {e}. Using defaults.")

    # 2. Memory
    memory_manager = MemoryManager(storage_path="memory_store.json")
    loaded_state = None
    if os.path.exists("memory_store.json"):
        try:
            payload = memory_manager.load()
            if isinstance(payload, dict):
                loaded_state = payload
                logger.info("Loaded persisted brain state from memory_store.json")
        except Exception as e:
            logger.warning(f"Failed to load state: {e}. Starting fresh.")

    # 3. Engines
    decision_engine = DecisionEngine(
        decision_config=decision_config,
        deterministic=deterministic
    )

    brain = VirtualBrain(
        chemical_configs=chemical_configs["chemicals"],
        interaction_matrix=chemical_configs.get("interactions"),
        decision_engine=decision_engine,
        deterministic=deterministic,
        brain_config=brain_config,
    )

    if loaded_state:
        brain.set_state(loaded_state)

    # Register some default helper tools for out-of-the-box system control
    register_default_tools()
    logger.info("Virtual Brain initialized successfully.")

def register_default_tools():
    if brain and hasattr(brain, "tool_connector"):
        # 1. Weather API
        brain.tool_connector.register_tool(
            name="get_weather",
            description="Fetch the weather details for a specific location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city name"}
                },
                "required": ["location"]
            },
            patterns=[
                r"weather in ([a-zA-Z\s]+)",
                r"weather for ([a-zA-Z\s]+)",
                r"temperature in ([a-zA-Z\s]+)"
            ]
        )
        
        # 2. Web Search API
        brain.tool_connector.register_tool(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query terms"}
                },
                "required": ["query"]
            },
            patterns=[
                r"search for (.+)",
                r"look up (.+)",
                r"google (.+)"
            ]
        )
        
        # 3. System Control / Device Control
        brain.tool_connector.register_tool(
            name="control_device",
            description="Turn on/off devices or configure setting variables",
            parameters={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "on or off"},
                    "device": {"type": "string", "description": "device name"}
                },
                "required": ["action", "device"]
            },
            patterns=[
                r"turn (on|off) the ([a-zA-Z\s]+)",
                r"switch (on|off) ([a-zA-Z\s]+)"
            ]
        )

# =====================================================
# REST ENDPOINTS
# =====================================================

@app.get("/")
def get_root():
    return {
        "status": "online",
        "brain_loaded": brain is not None,
        "mode": "deterministic" if (brain and brain.deterministic) else "stochastic",
        "message": "Welcome to Aashu Virtual Brain API server!"
    }

@app.post("/perceive")
def post_perceive(req: PerceiveEventRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    
    event_dict = req.model_dump()
    if event_dict.get("timestamp") is None:
        import time
        event_dict["timestamp"] = time.time()

    brain.perceive(event_dict)
    return {"status": "success", "message": f"Ingested perception event: {req.content[:50]}"}

@app.post("/perceive/text")
def post_perceive_text(req: PerceiveTextRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    
    # Observe perception directly into sensory channel
    brain.observe_perception(req.modality, req.text, req.source)
    return {"status": "success", "message": f"Ingested text perception: {req.text[:50]}"}

@app.post("/perceive/visual")
def post_perceive_visual(req: VisualSignalRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
        
    signal = req.model_dump()
    if signal.get("timestamp") is None:
        import time
        signal["timestamp"] = time.time()
        
    # We call receive_visual_signal if it exists, otherwise fall back to sensory_parser mapping
    if hasattr(brain, "receive_visual_signal"):
        brain.receive_visual_signal(signal)
    else:
        # Fallback to parser and perceive
        parsed = brain.sensory_parser.parse_visual_signal(signal)
        if parsed:
            brain.perceive(parsed)
            
    return {"status": "success", "message": "Ingested visual signal"}

@app.post("/perceive/hearing")
def post_perceive_hearing(req: HearingSignalRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
        
    signal = req.model_dump()
    if signal.get("timestamp") is None:
        import time
        signal["timestamp"] = time.time()
        
    # We call receive_hearing_signal if it exists, otherwise fall back to sensory_parser mapping
    if hasattr(brain, "receive_hearing_signal"):
        brain.receive_hearing_signal(signal)
    else:
        # Fallback to parser and perceive
        parsed = brain.sensory_parser.parse_hearing_signal(signal)
        if parsed:
            brain.perceive(parsed)
            
    return {"status": "success", "message": "Ingested hearing signal"}

@app.post("/tick")
def post_tick(background_tasks: BackgroundTasks):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")

    decision = brain.tick()
    
    # Auto-save state in background to avoid blocking API response
    if memory_manager:
        background_tasks.add_task(memory_manager.save, brain.get_state())

    return {
        "status": "success",
        "asleep": getattr(brain, "sleeping", False),
        "decision": decision,
        "focus": {
            "content": brain.current_focus.content,
            "source": brain.current_focus.source,
            "emotional_weight": brain.current_focus.emotional_weight,
            "novelty": brain.current_focus.novelty,
            "relevance_to_goals": brain.current_focus.relevance_to_goals
        } if brain.current_focus else None,
        "tool_call": getattr(brain, "latest_tool_call", None),
        "step_counter": brain.step_counter
    }

@app.get("/state")
def get_state():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    return brain.get_state()

@app.post("/regulate_speech")
def post_regulate_speech(req: SpeechRegulationRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    regulated = brain.regulate_speech(req.text)
    return {"input": req.text, "output": regulated}

# =====================================================
# BRAIN COGNITION ENDPOINTS (summarization / code generation)
# =====================================================

@app.post("/brain/summarize")
def post_brain_summarize(req: SummarizeTextRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    summary = brain.summarize_text(req.text, max_sentences=req.max_sentences)
    return {"status": "success", "summary": summary}

@app.post("/brain/generate_code")
def post_brain_generate_code(req: GenerateCodeRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    ok, result = brain.generate_code(req.task, req.language)
    if ok:
        return {"status": "success", "code": result}
    return {"status": "not_learned", "message": result}

@app.post("/brain/resolve")
def post_brain_resolve(req: ResolveActionRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    match = brain.resolve_tool(req.text)
    if match:
        return {"status": "success", **match}
    return {"status": "no_match"}

@app.post("/user_memory/remember")
def post_user_memory_remember(req: RememberUserRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    item = brain.remember_user(req.fact, fact_type=req.fact_type, importance=req.importance)
    return {"status": "success", "fact": item}

@app.get("/user_memory/context")
def get_user_memory_context(context: str = ""):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    return {"status": "success", "context": brain.user_context(context or None)}

@app.post("/user_memory/consolidate")
def post_user_memory_consolidate():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    created = brain.consolidate_user_memory()
    removed = brain.decay_user_memory()
    return {"status": "success", "traits_created": created, "facts_decayed": removed}

@app.get("/user_memory/profile")
def get_user_memory_profile():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    return {"status": "success", "profile": brain.user_profile()}

@app.post("/brain/build_website")
def post_brain_build_website(req: BuildWebsiteRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    ok, result = brain.build_website(name=req.name, title=req.title, sections=req.sections, theme=req.theme)
    return {"status": "success" if ok else "not_learned", "message": result}

@app.post("/brain/build_webapp")
def post_brain_build_webapp(req: BuildWebappRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    ok, result = brain.build_webapp(name=req.name, app_name=req.app_name, features=req.features, pages=req.pages)
    return {"status": "success" if ok else "not_learned", "message": result}

@app.post("/brain/build_reactapp")
def post_brain_build_reactapp(req: BuildWebappRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    ok, result = brain.build_reactapp(name=req.name, app_name=req.app_name, features=req.features, pages=req.pages)
    return {"status": "success" if ok else "not_learned", "message": result}

@app.post("/brain/build_cli")
def post_brain_build_cli(req: BuildCliRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    ok, result = brain.build_cli(name=req.name, task=req.task, args=req.args)
    return {"status": "success" if ok else "not_learned", "message": result}

@app.get("/brain/apps")
def get_brain_apps():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    return {"status": "success", "apps": brain.list_apps()}

# =====================================================
# ACTION/TOOL REGISTRY ENDPOINTS
# =====================================================

@app.post("/actions/register")
def post_register_tool(req: ToolRegistrationRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    
    brain.tool_connector.register_tool(
        name=req.name,
        description=req.description,
        parameters=req.parameters,
        patterns=req.patterns
    )
    logger.info(f"Registered external API tool: {req.name}")
    return {"status": "success", "message": f"Tool '{req.name}' registered successfully"}

@app.post("/actions/deregister/{name}")
def post_deregister_tool(name: str):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    
    success = brain.tool_connector.deregister_tool(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Tool '{name}' not found")
    logger.info(f"Deregistered external API tool: {name}")
    return {"status": "success", "message": f"Tool '{name}' deregistered successfully"}

@app.get("/actions")
def get_tools():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    return brain.tool_connector.list_tools()

# =====================================================
# ADVANCED CONTROL ENDPOINTS
# =====================================================

@app.post("/sleep")
def post_sleep(req: SleepRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    brain.sleeping = True
    brain.sleep_ticks_left = req.duration
    logger.info(f"Forced brain to sleep state for {req.duration} ticks.")
    return {"status": "success", "message": f"Brain set to sleep for {req.duration} ticks"}

@app.post("/wakeup")
def post_wakeup():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    brain.sleeping = False
    brain.sleep_ticks_left = 0
    logger.info("Forced brain to wake state.")
    return {"status": "success", "message": "Brain forced to wake up"}

@app.post("/state/chemicals")
def post_modulate_chemicals(req: ChemicalModulationRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    chem_name = req.chemical.lower()
    if chem_name not in brain.chemicals:
        raise HTTPException(status_code=404, detail=f"Chemical '{req.chemical}' not found in registry")
        
    if req.value is not None:
        brain.chemicals[chem_name] = req.value
        brain._clamp()
        logger.info(f"Set chemical '{chem_name}' value directly to {req.value}")
        return {"status": "success", "chemical": chem_name, "value": brain.chemicals[chem_name].value}
    elif req.delta is not None:
        brain.chemicals[chem_name].inject(req.delta)
        brain._clamp()
        logger.info(f"Injected delta {req.delta} into chemical '{chem_name}'")
        return {"status": "success", "chemical": chem_name, "value": brain.chemicals[chem_name].value}
    else:
        raise HTTPException(status_code=400, detail="Must specify either 'value' or 'delta'")

@app.post("/goals")
def post_manage_goals(req: GoalRequest):
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    if not hasattr(brain, "goal_system") or not brain.goal_system:
        raise HTTPException(status_code=500, detail="Goal system not initialized in brain")
        
    goal_name = req.name.strip().lower()
    if req.value is not None:
        brain.goal_system.goals[goal_name] = req.value
        logger.info(f"Set goal '{goal_name}' value directly to {req.value}")
        return {"status": "success", "goal": goal_name, "value": brain.goal_system.goals[goal_name]}
    elif req.reward is not None:
        brain.goal_system.create_or_update_goal(goal_name, req.reward)
        logger.info(f"Reinforced goal '{goal_name}' with reward {req.reward}")
        return {"status": "success", "goal": goal_name, "value": brain.goal_system.goals[goal_name]}
    else:
        raise HTTPException(status_code=400, detail="Must specify either 'value' or 'reward'")

@app.get("/goals")
def get_goals():
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
    if not hasattr(brain, "goal_system") or not brain.goal_system:
        return {}
    return {
        "goals": brain.goal_system.goals,
        "active_goal": brain.goal_system.get_active_goal()
    }

@app.post("/reset")
def post_reset(req: ResetRequest):
    global brain
    if not brain:
        raise HTTPException(status_code=500, detail="Brain not initialized")
        
    if req.hard_reset:
        logger.info("Performing hard reset...")
        for file_path in ["memory_store.json", "memory_events.json"]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete {file_path}: {e}")
        init_brain(deterministic=getattr(brain, "deterministic", False))
        return {"status": "success", "message": "Hard reset completed. Brain reinitialized fresh."}
    else:
        brain.current_focus = None
        brain.latest_tool_call = None
        if hasattr(brain, "global_workspace") and brain.global_workspace:
            brain.global_workspace.reset()
        brain._step_perception_valences = []
        brain._step_perception_signals = []
        brain._step_perception_novelty = 0.0
        brain._step_adversity_intensity = 0.0
        logger.info("Soft reset of active workspace state completed.")
        return {"status": "success", "message": "Soft reset of workspace and focus completed"}

# =====================================================
# CLI PARSER & RUN
# =====================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Virtual Brain API Server Launcher")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run API server on")
    parser.add_argument("--deterministic", action="store_true", help="Run brain without stochastic noise")
    args = parser.parse_args()

    # Initialize brain before starting FastAPI web server
    init_brain(deterministic=args.deterministic)

    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port)
