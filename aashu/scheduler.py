import os
import time
import datetime
import threading
import json

class AashuScheduler(threading.Thread):
    def __init__(self, brain_client, actuators):
        super().__init__()
        self.client = brain_client
        self.actuators = actuators
        self.running = False
        self.daemon = True
        
        self.notified_today = set()
        self.alarm_fired = False
        self.last_checked_day = datetime.datetime.now().date()

    def run(self):
        self.running = True
        print("Autonomous Task Scheduler started.")
        
        # Periodic loop (runs checks every 10 seconds)
        while self.running:
            try:
                now = datetime.datetime.now()
                current_date_str = now.strftime("%Y-%m-%d")
                current_time_str = now.strftime("%H:%M")
                
                # Reset notified list and alarm flags if date changed
                if now.date() != self.last_checked_day:
                    self.notified_today.clear()
                    self.alarm_fired = False
                    self.last_checked_day = now.date()

                # 1. Check Alarm triggers
                if self.actuators.alarm_time == current_time_str and not self.alarm_fired:
                    self.alarm_fired = True
                    print(f"Scheduler Alarm Triggered at {current_time_str}!")
                    
                    # Notify and play alarm ringtone
                    self.actuators._send_notification("Aashu Morning Alarm", "Wake up! Your morning routine is starting.")
                    if self.actuators.mouth:
                        self.actuators.mouth.speak("Rise and shine! Initiating your morning briefing routine.")
                    
                    # Fire morning briefing routine
                    self.actuators._morning_routine()

                # 2. Check Calendar notifications
                if os.path.exists(self.actuators.cal_path):
                    try:
                        with open(self.actuators.cal_path, "r") as f:
                            data = json.load(f)
                            
                        today_events = data.get(current_date_str, [])
                        for event in today_events:
                            event_key = f"{current_date_str}:{event}"
                            if event_key not in self.notified_today:
                                self.notified_today.add(event_key)
                                print(f"Scheduler Alert: Today's event found: '{event}'")
                                
                                # Send desktop alert and speak event details
                                self.actuators._send_notification("Aashu Agenda Reminder", f"Today: {event}")
                                if self.actuators.mouth:
                                    self.actuators.mouth.speak(f"Aashu reminder: you have a calendar event today. {event}.")
                    except Exception as e:
                        print(f"Scheduler Calendar Read Error: {e}")

                # 3. Trigger autonomous cognitive tick
                tick_res = self.client.trigger_tick()
                if isinstance(tick_res, dict) and tick_res.get("status") == "success":
                    tool_call = tick_res.get("tool_call")
                    if tool_call:
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("arguments", {})
                        print(f"\n[Background Action] Brain requested: {tool_name} with args {tool_args}")
                        
                        if self.actuators.mouth:
                            self.actuators.mouth.speak(f"Executing background task {tool_name.replace('_', ' ')}...")
                        
                        tool_outcome = self.actuators.execute_tool(tool_name, tool_args)
                        print(f"[Background Action] Result: {tool_outcome}")
                        
                        feedback = {
                            "content": f"Autonomous tool '{tool_name}' executed. Result: {tool_outcome}",
                            "category": "tool_result",
                            "modality": "experience",
                            "valence": 0.05,
                            "intensity": 0.4,
                            "source": "actuator"
                        }
                        self.client.send_perception_raw(feedback)
                        self.client.trigger_tick()

            except Exception as e:
                print(f"Scheduler Loop Error: {e}")

            time.sleep(10)

    def stop(self):
        self.running = False
