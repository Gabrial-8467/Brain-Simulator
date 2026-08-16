import os
import sys
import time
import threading
import psutil
from .config import WAKE_WORD
from .brain_client import BrainClient
from .ollama_client import OllamaClient
from .learning import AashuLearning
from .ears import AashuEars
from .mouth import AashuMouth
from .eyes import AashuEyes
from .actuators import AashuActuators
from .scheduler import AashuScheduler

# Hardware monitoring thread
class HardwareMonitor(threading.Thread):
    def __init__(self, brain_client, poll_interval=15.0):
        super().__init__()
        self.client = brain_client
        self.poll_interval = poll_interval
        self.running = False
        self.daemon = True

    def run(self):
        self.running = True
        print("Hardware Monitor Thread started.")
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                battery = psutil.sensors_battery()
                
                # Check for critical triggers
                threats = []
                if cpu > 85.0:
                    threats.append(f"CPU load is critically high at {cpu}%")
                
                if battery:
                    if battery.percent < 20.0 and not battery.power_plugged:
                        threats.append(f"Battery is critically low at {battery.percent}%")

                if threats:
                    # Ingest somatic threat signal into the brain
                    threat_msg = " | ".join(threats)
                    payload = {
                        "content": f"Somatic Warning: {threat_msg}",
                        "category": "somatic_sensation",
                        "modality": "experience",
                        "valence": -0.5,      # High negative valence (induces stress)
                        "intensity": 0.8,     # High intensity trigger
                        "source": "body_diagnostics"
                    }
                    self.client.send_perception_raw(payload)
                    # Trigger an immediate tick so the brain handles the somatic warning
                    self.client.trigger_tick()
                    
            except Exception as e:
                print(f"Hardware Monitor Warning: {e}")
                
            time.sleep(self.poll_interval)

    def stop(self):
        self.running = False


def run_agent():
    print("Initializing Aashu Assistant...")

    # 1. Initialize core layers
    brain = BrainClient()
    ollama = OllamaClient()
    ears = AashuEars()
    mouth = AashuMouth()
    actuators = AashuActuators(mouth=mouth, brain_client=brain)
    learning = AashuLearning(brain_client=brain)
    actuators.learning = learning

    # Verify REST Server connection
    if not brain.check_connection():
        print("Error: The Virtual Brain API server is offline. Please run the server first!")
        return

    # 2. Register tools with Virtual Brain
    print("Registering system actuators with the Virtual Brain...")
    tools = actuators.get_registered_tools_definitions()
    for t in tools:
        res = brain.register_action(
            name=t["name"],
            description=t["description"],
            parameters=t["parameters"],
            patterns=t["patterns"]
        )
        if res.get("status") == "success":
            print(f" -> Registered tool: {t['name']}")
        else:
            print(f" -> Failed to register {t['name']}: {res.get('message')}")

    # 3. Start Visual Sensory Feed
    print("Starting OpenCV visual perception thread...")
    eyes = AashuEyes(brain_client=brain)
    eyes.start()
    actuators.eyes = eyes

    # 4. Start Hardware Monitor Feed
    print("Starting system hardware monitor alerts...")
    hw_monitor = HardwareMonitor(brain_client=brain)
    hw_monitor.start()

    # 5. Start Autonomous Scheduler Thread
    print("Starting autonomous task scheduler...")
    scheduler = AashuScheduler(brain_client=brain, actuators=actuators)
    scheduler.start()

    print("\nAashu is fully initialized and operational!")
    mouth.speak("Aashu system online.")

    # 5. Main Agent Loop
    try:
        while True:
            print(f"\n[Listening for wake word: '{WAKE_WORD}']")
            
            # Record voice input and transcribe it
            transcript = ears.listen_and_transcribe()
            if not transcript:
                continue

            print(f"Heard: '{transcript}'")
            
            # Check for wake-word trigger
            text_lower = transcript.lower()
            if WAKE_WORD not in text_lower:
                # Log general background speech to the brain but do not respond proactively
                brain.send_hearing_signal(transcript=transcript, speaker_type="unknown", source="background")
                # Passive learning from background conversation
                learning.learn_from_hearing(transcript, speaker="unknown")
                brain.trigger_tick()
                continue

            # Extract user query after the wake word
            query = transcript
            wake_idx = text_lower.find(WAKE_WORD)
            if wake_idx != -1:
                # Remove wake word
                query = transcript[wake_idx + len(WAKE_WORD):].strip(", ").strip()
            
            # If no query followed the wake-word, prompt the user
            if not query:
                mouth.speak("Yes? I am listening.")
                continue

            print(f"Processing Query: '{query}'")

            # Simple keyword-based sentiment and keyword extraction
            sentiment_val = 0.0
            keywords_extracted = []
            
            positive_words = {"good", "great", "excellent", "happy", "yes", "nice", "love", "thanks", "thank"}
            negative_words = {"bad", "poor", "sad", "no", "hate", "error", "fail", "wrong", "annoyed", "stop"}
            
            words = text_lower.split()
            for w in words:
                w_clean = w.strip(".,!?\"'")
                if w_clean in positive_words:
                    sentiment_val += 0.25
                elif w_clean in negative_words:
                    sentiment_val -= 0.25
                    
            sentiment_val = max(-1.0, min(1.0, sentiment_val))
            
            # Simple keyword detection for topics
            possible_keywords = ["weather", "system", "file", "media", "screenshot", "timer", "alarm", "cal", "calendar", "note", "brain", "dopamine", "cortisol", "melatonin", "sleep"]
            for pk in possible_keywords:
                if pk in text_lower:
                    keywords_extracted.append(pk)

            # Ingest query perception to the brain via structured hearing endpoint
            brain.send_hearing_signal(
                transcript=query,
                speaker_type="user",
                sentiment=sentiment_val,
                prosody_intensity=0.6,
                keywords=keywords_extracted,
                source="microphone"
            )
            
            # Trigger cognitive tick
            tick_res = brain.trigger_tick()
            if tick_res.get("status") != "success":
                print(f"Brain Tick failed: {tick_res.get('message')}")
                continue

            decision = tick_res.get("decision", {})
            action = decision.get("action", "none") if isinstance(decision, dict) else str(decision)
            focus = tick_res.get("focus", {})
            focus_content = focus.get("content", "None") if focus else "None"
            
            print(f" -> Brain Focus: {focus_content}")
            print(f" -> Decision Action: {action}")

            # Deterministic tool resolution straight from the raw query.
            # Faster and more reliable than matching the brain's internal focus.
            direct_tool = None
            try:
                resolved = brain.resolve_action(query)
                if resolved.get("status") == "success" and float(resolved.get("confidence", 0)) >= 0.5:
                    direct_tool = {"name": resolved["name"], "arguments": resolved["arguments"]}
                    print(f" -> Direct tool match (confidence {resolved.get('confidence')}): {resolved['name']}")
            except Exception:
                direct_tool = None

            tool_call = None
            tool_outcome = None

            # Execute the directly resolved tool first, if any
            if direct_tool:
                tool_name = direct_tool["name"]
                tool_args = direct_tool["arguments"]
                mouth.speak(f"Executing {tool_name.replace('_', ' ')}...")
                tool_outcome = actuators.execute_tool(tool_name, tool_args)
                print(f" -> Direct tool result: {tool_outcome}")

                feedback = {
                    "content": f"Tool '{tool_name}' executed. Result: {tool_outcome}",
                    "category": "tool_result",
                    "modality": "experience",
                    "valence": 0.05,
                    "intensity": 0.4,
                    "source": "actuator"
                }
                brain.send_perception_raw(feedback)

                # Re-tick to process tool outcome
                tick_res = brain.trigger_tick()
                focus = tick_res.get("focus", {})
                focus_content = focus.get("content", "None") if focus else "None"

            # Check for brain-initiated tool call (only if none executed directly)
            if not direct_tool:
                tool_call = tick_res.get("tool_call")
                if tool_call:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("arguments", {})
                    print(f" -> Brain requested tool call: {tool_name} with args {tool_args}")
                    
                    # Execute actuator
                    mouth.speak(f"Executing {tool_name.replace('_', ' ')}...")
                    tool_outcome = actuators.execute_tool(tool_name, tool_args)
                    print(f" -> Tool result: {tool_outcome}")
                    
                    # Feed result back to brain as experience perception
                    feedback = {
                        "content": f"Tool '{tool_name}' executed. Result: {tool_outcome}",
                        "category": "tool_result",
                        "modality": "experience",
                        "valence": 0.05,
                        "intensity": 0.4,
                        "source": "actuator"
                    }
                    brain.send_perception_raw(feedback)
                    
                    # Re-tick to process tool outcome
                    tick_res = brain.trigger_tick()
                    focus = tick_res.get("focus", {})
                    focus_content = focus.get("content", "None") if focus else "None"

            # 3. Generate response using Local Ollama LLM
            state = brain.get_state() or {}
            self_narrative = state.get("self_narrative", "None")
            mood = state.get("mood", "Calm")
            
            # Dynamic personality directives based on chemical metrics
            personality_directives = ""
            cortisol = state.get("cortisol", 0.0)
            dopamine = state.get("dopamine", 0.0)
            melatonin = state.get("melatonin", 0.0)
            
            if cortisol > 70.0:
                personality_directives = "You are experiencing high Cortisol (anxiety/stress). Answer with urgent, cautious, and short warnings."
            elif melatonin > 70.0:
                personality_directives = "You are experiencing high Melatonin (extreme fatigue). Answer slowly, use sleep-related cues, and suggest resting the brain."
            elif dopamine > 75.0:
                personality_directives = "You are experiencing high Dopamine (pleasure/reward). Answer with highly optimistic, enthusiastic, and creative expressions."
            else:
                personality_directives = "Maintain a steady, professional, helpful assistant voice."

            # Construct system prompt based on active brain states
            user_context = ""
            try:
                ctx = brain.get_user_context(query)
                if ctx.get("status") == "success":
                    user_context = ctx.get("context", "")
            except Exception:
                user_context = ""

            system_prompt = f"""
You are Aashu, the physical voice and assistant body of a Virtual Brain simulator.
Current Brain Focus: {focus_content}
Current Internal Self-Narrative: {self_narrative}
Current Emotional Mood: {mood}
Personality Directive: {personality_directives}
{user_context}

Your response must be short, helpful, and strictly align with your current emotional mood ({mood}) and active personality directives. Speak as an active assistant.
"""
            # If a tool was executed, include the result in the prompt
            user_prompt = query
            if tool_outcome:
                user_prompt += f"\n(Context: The tool executed successfully and returned: {tool_outcome})"

            print("Querying local LLM reasoning...")
            raw_response = ollama.generate_response(user_prompt, system_prompt=system_prompt)
            print(f"Raw Response: {raw_response}")

            # 4. Regulate response voice through brain personality channels
            regulated_response = brain.regulate_speech(raw_response)
            
            # 5. Speak the response out loud
            mouth.speak(regulated_response)

    except KeyboardInterrupt:
        print("\nShutting down Aashu Assistant...")
    finally:
        eyes.stop()
        eyes.join()
        hw_monitor.stop()
        hw_monitor.join()
        mouth.speak("Aashu system offline.")
        print("Shutdown complete.")

if __name__ == "__main__":
    run_agent()
