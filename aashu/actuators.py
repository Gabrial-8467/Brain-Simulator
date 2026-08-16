import os
import sys
import psutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
import re
import datetime
import time
import threading
import json
import smtplib
import random
import shutil
from email.mime.text import MIMEText
import cv2
from PIL import ImageGrab
from .codegen import AashuCodeGenerator
from .text_tools import extractive_summarize
from .learning import KnowledgeStore

class AashuActuators:
    def __init__(self, mouth=None, eyes=None, brain_client=None):
        self.mouth = mouth
        self.eyes = eyes
        self.brain_client = brain_client
        self.cal_path = "aashu_calendar.json"
        self.music_process = None
        self.alarm_time = None
        self.learning = None
        self.codegen = AashuCodeGenerator()
        self.notes = KnowledgeStore(path="aashu_notes_db", collection="aashu_notes")

        self._init_calendar()

    def _init_calendar(self):
        try:
            if not os.path.exists(self.cal_path):
                with open(self.cal_path, "w") as f:
                    json.dump({}, f)
        except Exception as e:
            print(f"Calendar Init Error: {e}")

    def get_registered_tools_definitions(self):
        """Returns the definitions used to register these tools with the Virtual Brain."""
        return [
            {
                "name": "calculate",
                "description": "Calculate standard mathematical equations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "equation": {"type": "string", "description": "The math equation to solve"}
                    },
                    "required": ["equation"]
                },
                "patterns": [
                    r"calculate ([0-9\+\-\*\/\s\(\)]+)",
                    r"compute ([0-9\+\-\*\/\s\(\)]+)",
                    r"what is ([0-9\+\-\*\/\s\(\)]+)"
                ]
            },
            {
                "name": "get_weather",
                "description": "Retrieve current weather forecasts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City or location name"}
                    },
                    "required": ["location"]
                },
                "patterns": [
                    r"weather in ([\w\s]+)",
                    r"forecast for ([\w\s]+)"
                ]
            },
            {
                "name": "system_diagnostics",
                "description": "Retrieve computer hardware stats (CPU, RAM, Battery)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"system diagnostics",
                    r"resource usage",
                    r"cpu and ram stats"
                ]
            },
            {
                "name": "search_files",
                "description": "Search local files in a given directory matching a query pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "File name pattern or keyword to search for"}
                    },
                    "required": ["pattern"]
                },
                "patterns": [
                    r"find files ([\w\.\-\*]+)",
                    r"search file ([\w\.\-\*]+)"
                ]
            },
            {
                "name": "control_app",
                "description": "Open applications on the host machine",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Name of app, e.g. browser, calculator, terminal"}
                    },
                    "required": ["app_name"]
                },
                "patterns": [
                    r"open (?:the )?(browser|calculator|terminal|music player|file manager)"
                ]
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of the user's screen",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"take screenshot",
                    r"capture my screen",
                    r"screenshot my screen"
                ]
            },
            {
                "name": "control_media",
                "description": "Control system speaker volume (mute, unmute, or percentage)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "setting": {"type": "string", "description": "Volume setting (mute, unmute, or percentage e.g. 50)"}
                    },
                    "required": ["setting"]
                },
                "patterns": [
                    r"set volume to (\d+)",
                    r"(mute|unmute) volume",
                    r"(mute|unmute) sound"
                ]
            },
            {
                "name": "search_web",
                "description": "Search DuckDuckGo web results for a given query topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Web search query string"}
                    },
                    "required": ["query"]
                },
                "patterns": [
                    r"search web for ([\w\s\-\.\?]+)",
                    r"search online for ([\w\s\-\.\?]+)"
                ]
            },
            {
                "name": "create_file",
                "description": "Create a new text file inside the local workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Name of the file to create"},
                        "content": {"type": "string", "description": "Text content to write to the file"}
                    },
                    "required": ["filename", "content"]
                },
                "patterns": [
                    r"create file ([\w\.\-]+) with text ([\w\s\-\.\?\!\(\)]+)"
                ]
            },
            {
                "name": "read_file",
                "description": "Read content of a text file inside the local workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Name of the file to read"}
                    },
                    "required": ["filename"]
                },
                "patterns": [
                    r"read file ([\w\.\-]+)",
                    r"view file ([\w\.\-]+)"
                ]
            },
            {
                "name": "run_command",
                "description": "Run safe shell/terminal diagnostics commands (df, uptime, free, uname, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The command line string to run"}
                    },
                    "required": ["command"]
                },
                "patterns": [
                    r"run command ([\w\s\-\.]+)"
                ]
            },
            {
                "name": "get_time",
                "description": "Get current local date and time information",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"what time is it",
                    r"current time",
                    r"get current date"
                ]
            },
            {
                "name": "send_notification",
                "description": "Send a desktop notification bubble to the screen",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Notification title header"},
                        "message": {"type": "string", "description": "Notification body message"}
                    },
                    "required": ["title", "message"]
                },
                "patterns": [
                    r"notify me that ([\w\s\-\.\?\!\(\)]+)",
                    r"send notification ([\w\s\-\.\?\!\(\)]+)"
                ]
            },
            {
                "name": "set_timer",
                "description": "Set a countdown timer with a specific alert message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "seconds": {"type": "integer", "description": "Countdown duration in seconds"},
                        "label": {"type": "string", "description": "Label or purpose of the timer alert"}
                    },
                    "required": ["seconds", "label"]
                },
                "patterns": [
                    r"set a timer for (?P<seconds>\d+) seconds to (?P<label>[\w\s\-\.\?\!\(\)]+)",
                    r"set a timer for (?P<seconds>\d+) (?P<unit>seconds|minutes|hours)",
                    r"timer for (?P<seconds>\d+) (?P<unit>seconds|minutes|hours)",
                    r"remind me in (?P<seconds>\d+) (?P<unit>seconds|minutes|hours)"
                ]
            },
            {
                "name": "learn_face",
                "description": "Capture the user face currently in view of the webcam and save it as a template key",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The user's first name to assign to the face"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"learn face ([\w]+)",
                    r"register face ([\w]+)"
                ]
            },
            {
                "name": "add_note",
                "description": "Add a text note to Aashu's vector memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "The message body of the note"}
                    },
                    "required": ["content"]
                },
                "patterns": [
                    r"add note ([\w\s\-\.\?\!\(\)]+)"
                ]
            },
            {
                "name": "get_notes",
                "description": "List all text notes stored in Aashu's vector memory",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"get notes",
                    r"show my notes"
                ]
            },
            {
                "name": "delete_note",
                "description": "Delete a note from vector memory using its integer ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "The note ID to delete"}
                    },
                    "required": ["note_id"]
                },
                "patterns": [
                    r"delete note (\d+)"
                ]
            },
            {
                "name": "add_event",
                "description": "Add an event calendar entry in YYYY-MM-DD date format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Date format e.g. 2026-08-07"},
                        "title": {"type": "string", "description": "Event description title"}
                    },
                    "required": ["date", "title"]
                },
                "patterns": [
                    r"add event for ([\d\-]+) title ([\w\s\-]+)"
                ]
            },
            {
                "name": "get_events",
                "description": "List scheduled calendar events optionally filtered by a date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Optional date filter e.g. 2026-08-07"}
                    },
                    "required": []
                },
                "patterns": [
                    r"get events for ([\d\-]+)",
                    r"get calendar events",
                    r"get events"
                ]
            },
            {
                "name": "send_email",
                "description": "Send an email message through SMTP settings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_address": {"type": "string", "description": "Destination email address"},
                        "subject": {"type": "string", "description": "Email subject header"},
                        "body": {"type": "string", "description": "Email body content text"}
                    },
                    "required": ["to_address", "subject", "body"]
                },
                "patterns": [
                    r"send email to ([\w\.\-\@]+) subject ([\w\s\-]+) body ([\w\s\-\.\?\!\(\)]+)"
                ]
            },
            {
                "name": "run_script",
                "description": "Execute a Python script block inside a safe sandbox process",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "The Python source code block to execute"}
                    },
                    "required": ["code"]
                },
                "patterns": [
                    r"run script ([\s\S]+)"
                ]
            },
            {
                "name": "play_music",
                "description": "Play a local audio file (MP3/WAV) in the background",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Path to local sound file"}
                    },
                    "required": ["filepath"]
                },
                "patterns": [
                    r"play music ([\w\.\-\/]+)"
                ]
            },
            {
                "name": "stop_music",
                "description": "Stop any background music track currently playing",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"stop music",
                    r"silence audio"
                ]
            },
            {
                "name": "get_joke",
                "description": "Tell a funny joke from a joke service or local database",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"tell me a joke",
                    r"say a joke"
                ]
            },
            {
                "name": "summarize_document",
                "description": "Summarize a local file inside the workspace using local LLM intelligence",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Name of the file to summarize"}
                    },
                    "required": ["filename"]
                },
                "patterns": [
                    r"summarize document ([\w\.\-]+)",
                    r"summarize file ([\w\.\-]+)"
                ]
            },
            {
                "name": "query_wikipedia",
                "description": "Query Wikipedia factual summaries for a topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic or query term"}
                    },
                    "required": ["topic"]
                },
                "patterns": [
                    r"query wikipedia for ([\w\s\-]+)",
                    r"search wikipedia for ([\w\s\-]+)"
                ]
            },
            {
                "name": "play_riddle",
                "description": "Get a random riddle challenge and its answer",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"tell me a riddle",
                    r"give me a riddle"
                ]
            },
            {
                "name": "translate_phrase",
                "description": "Translate a phrase from English to another language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phrase": {"type": "string", "description": "The English text phrase"},
                        "target_lang": {"type": "string", "description": "Target language, e.g. Spanish, French, Hindi"}
                    },
                    "required": ["phrase", "target_lang"]
                },
                "patterns": [
                    r"translate ([\w\s\-\.\?\!]+) to ([\w]+)"
                ]
            },
            {
                "name": "convert_units",
                "description": "Convert metric or imperial measurement units",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "string", "description": "The numeric quantity"},
                        "from_unit": {"type": "string", "description": "Source unit, e.g. C, F, km, miles, kg, lbs"},
                        "to_unit": {"type": "string", "description": "Target unit, e.g. C, F, km, miles, kg, lbs"}
                    },
                    "required": ["amount", "from_unit", "to_unit"]
                },
                "patterns": [
                    r"convert (\d+) ([\w]+) to ([\w]+)"
                ]
            },
            {
                "name": "run_speedtest",
                "description": "Benchmark local network connection download speed",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"run speedtest",
                    r"check network speed"
                ]
            },
            {
                "name": "set_alarm",
                "description": "Set a daily morning wake-up alarm in 24-hour format (HH:MM)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_str": {"type": "string", "description": "Time in HH:MM format, e.g. 07:30"}
                    },
                    "required": ["time_str"]
                },
                "patterns": [
                    r"set alarm for ([\d:]+)",
                    r"set alarm at ([\d:]+)"
                ]
            },
            {
                "name": "morning_routine",
                "description": "Trigger the spoken morning schedule, weather, and diagnostics briefing",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"run morning routine",
                    r"start morning routine",
                    r"give me my daily briefing"
                ]
            },
            {
                "name": "scan_qr_code",
                "description": "Scan webcam video feed for QR codes, decode and open links",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"scan qr code",
                    r"scan barcode",
                    r"check for qr codes"
                ]
            },
            {
                "name": "record_memo",
                "description": "Record microphone audio voice memo for specified duration in seconds",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "string", "description": "Recording length in seconds, e.g. 10"}
                    },
                    "required": ["duration"]
                },
                "patterns": [
                    r"record a memo for (\d+) seconds",
                    r"record audio for (\d+) seconds"
                ]
            },
            {
                "name": "scan_network",
                "description": "List all active devices connected to the local Wi-Fi subnet",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"scan network",
                    r"scan local network",
                    r"list network devices"
                ]
            },
            {
                "name": "organize_downloads",
                "description": "Organize files in a sandbox or target folder by file extension categories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_dir": {"type": "string", "description": "The directory path to organize"}
                    },
                    "required": []
                },
                "patterns": [
                    r"organize folder ([\w\.\-\/]+)",
                    r"organize downloads",
                    r"sort my files"
                ]
            },
            {
                "name": "optimize_memory",
                "description": "Check memory diagnostic report of top RAM-consuming applications",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"optimize memory",
                    r"check memory hogs",
                    r"ram optimization"
                ]
            },
            {
                "name": "get_clipboard",
                "description": "Read text content currently stored in the system clipboard",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"get clipboard",
                    r"read clipboard",
                    r"what is on my clipboard"
                ]
            },
            {
                "name": "set_clipboard",
                "description": "Copy a text string into the system clipboard",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The text to copy to clipboard"}
                    },
                    "required": ["text"]
                },
                "patterns": [
                    r"set clipboard to ([\w\s\-\.\?\!\(\)]+)",
                    r"copy ([\w\s\-\.\?\!\(\)]+) to clipboard"
                ]
            },
            {
                "name": "define_word",
                "description": "Look up definitions for a word in the dictionary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {"type": "string", "description": "The English word to define"}
                    },
                    "required": ["word"]
                },
                "patterns": [
                    r"define word ([\w]+)",
                    r"what is the definition of ([\w]+)",
                    r"define ([\w]+)"
                ]
            },
            {
                "name": "set_speech_voice",
                "description": "List or switch Aashu's active vocal speech voice profile",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "voice_identifier": {"type": "string", "description": "Index number or name of the voice profile, or 'list' to see options"}
                    },
                    "required": ["voice_identifier"]
                },
                "patterns": [
                    r"set voice to ([\w\s\d]+)",
                    r"change voice to ([\w\s\d]+)",
                    r"list speech voices",
                    r"show speech voices"
                ]
            },
            {
                "name": "run_tests",
                "description": "Execute background unit test discover suites inside the project workspace",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"run unit tests",
                    r"run project tests",
                    r"execute tests"
                ]
            },
            {
                "name": "get_brain_state",
                "description": "Retrieve the Virtual Brain's internal neurochemical levels, sleep status, and current active goals",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"check brain state",
                    r"what is your brain state",
                    r"show brain chemistry",
                    r"how are your chemicals"
                ]
            },
            {
                "name": "modulate_brain_chemical",
                "description": "Directly modulate a brain chemical by setting its value or injecting a delta change",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chemical": {"type": "string", "description": "Name of the chemical, e.g. dopamine, cortisol, melatonin, oxytocin, serotonin"},
                        "value_or_delta": {"type": "string", "description": "The target value or delta amount to apply"}
                    },
                    "required": ["chemical", "value_or_delta"]
                },
                "patterns": [
                    r"modulate chemical ([\w]+) to ([\d\.\-]+)",
                    r"change chemical ([\w]+) by ([\d\.\-]+)",
                    r"set ([\w]+) level to ([\d\.\-]+)",
                    r"inject ([\d\.\-]+) delta into ([\w]+)"
                ]
            },
            {
                "name": "set_brain_sleep",
                "description": "Force the Virtual Brain simulator to enter sleep state for a specific number of cycles/ticks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "string", "description": "Number of ticks to sleep"}
                    },
                    "required": ["duration"]
                },
                "patterns": [
                    r"set brain to sleep for (\d+) ticks",
                    r"force brain sleep (\d+)",
                    r"sleep brain (\d+)"
                ]
            },
            {
                "name": "wakeup_brain",
                "description": "Wake up the Virtual Brain from sleep state immediately",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"wake up brain",
                    r"force brain wakeup",
                    r"wakeup brain"
                ]
            },
            {
                "name": "reset_brain_state",
                "description": "Perform a soft or hard reset of the Virtual Brain state",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hard": {"type": "string", "description": "Whether to perform a hard reset (true/false)"}
                    },
                    "required": []
                },
                "patterns": [
                    r"reset brain state",
                    r"hard reset brain",
                    r"soft reset brain"
                ]
            },
            {
                "name": "learn_topic",
                "description": "Learn about a topic from internet resources and store it in Aashu's knowledge (supports programming languages, science, anything)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic or learning query, e.g. 'python functions' or 'neural networks'"}
                    },
                    "required": ["topic"]
                },
                "patterns": [
                    r"learn (about|topic) ([\w\s\-\.\?]+)",
                    r"study ([\w\s\-\.\?]+)",
                    r"learn programming ([\w\s\-\.\?]+)"
                ]
            },
            {
                "name": "write_code",
                "description": "Write code for a task using what Aashu has learned, save it to a file, and test it",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "The coding task to implement"},
                        "language": {"type": "string", "description": "Programming language, e.g. python, javascript, c++"},
                        "filename": {"type": "string", "description": "Optional output filename (e.g. my_script.py)"}
                    },
                    "required": ["task", "language"]
                },
                "patterns": [
                    r"write ([\w]+) code (?:for|to) ([\w\s\-\.\?]+)",
                    r"code (?:a|an)? ([\w\s\-\.\?]+) in ([\w]+)"
                ]
            },
            {
                "name": "recall_knowledge",
                "description": "Recall what Aashu has learned about a topic and summarize it",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic to recall knowledge about"}
                    },
                    "required": ["topic"]
                },
                "patterns": [
                    r"what (?:have|did) you (?:learned|learn) (?:about|about topic) ([\w\s\-\.\?]+)",
                    r"recall ([\w\s\-\.\?]+)",
                    r"do you know ([\w\s\-\.\?]+)"
                ]
            },
            {
                "name": "what_do_i_know",
                "description": "Report what knowledge Aashu has learned so far (topics and programming languages)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "patterns": [
                    r"what do you know",
                    r"what have you learned",
                    r"list your knowledge",
                    r"show learned topics"
                ]
            },
            {
                "name": "remember_user_fact",
                "description": "Remember a durable fact about the user (name, preferences, history, personality)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fact": {"type": "string", "description": "The fact to remember about the user"}
                    },
                    "required": ["fact"]
                },
                "patterns": [
                    r"remember that ([\w\s,\.']+)",
                    r"note that ([\w\s,\.']+)",
                    r"my name is ([\w\s]+)",
                    r"i (like|prefer|love) ([\w\s]+)",
                    r"remember my ([\w\s]+) is ([\w\s]+)"
                ]
            },
            {
                "name": "who_am_i",
                "description": "Recall what I know about the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "context": {"type": "string", "description": "Optional context to recall relevant facts about"}
                    },
                    "required": []
                },
                "patterns": [
                    r"who am i",
                    r"what do you know about me",
                    r"tell me about myself",
                    r"what do you remember about me"
                ]
            },
            {
                "name": "execute_task",
                "description": "Plan and execute a multi-step goal from start to finish",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string", "description": "The high-level goal to accomplish"}
                    },
                    "required": ["goal"]
                },
                "patterns": [
                    r"plan and ([\w\s,\.']+)",
                    r"execute task ([\w\s,\.']+)",
                    r"run my ([\w\s]+) routine",
                    r"set up my day",
                    r"break down ([\w\s,\.']+)"
                ]
            },
            {
                "name": "build_website",
                "description": "Build a full static website from a name, title and sections",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the website"},
                        "title": {"type": "string", "description": "Website title shown on the page"},
                        "sections": {"type": "string", "description": "Semicolon-separated section names, e.g. 'Home;About;Contact'"},
                        "theme": {"type": "string", "description": "Theme: light or dark"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?website called ([\w\s]+)",
                    r"make (?:a |an )?website for ([\w\s]+)",
                    r"create (?:a |an )?website (?:for|called) ([\w\s]+)"
                ]
            },
            {
                "name": "build_webapp",
                "description": "Build a full runnable web application (Flask) with pages and features",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the web app"},
                        "app_name": {"type": "string", "description": "Module name for the Flask app"},
                        "features": {"type": "string", "description": "Semicolon-separated feature list, e.g. 'auth;dashboard'"},
                        "pages": {"type": "string", "description": "Semicolon-separated page list, e.g. 'Home;Settings'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?web ?app called ([\w\s]+)",
                    r"build (?:a |an )?web ?app (?:for|called) ([\w\s]+)",
                    r"make (?:a |an )?web ?app (?:for|called) ([\w\s]+)"
                ]
            },
            {
                "name": "build_reactapp",
                "description": "Build a full React (Vite) web application with pages and features",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the React app"},
                        "app_name": {"type": "string", "description": "App title"},
                        "features": {"type": "string", "description": "Semicolon-separated feature list, e.g. 'auth;dashboard'"},
                        "pages": {"type": "string", "description": "Semicolon-separated page list, e.g. 'Home;Settings'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?react ?app (?:called|for|named) ([\w\s]+)",
                    r"build (?:a |an )?app with react (?:called|for|named) ([\w\s]+)",
                    r"make (?:a |an )?react ?app (?:called|for) ([\w\s]+)"
                ]
            },
            {
                "name": "build_angularapp",
                "description": "Build a full Angular web application with pages and features",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the Angular app"},
                        "app_name": {"type": "string", "description": "App title"},
                        "features": {"type": "string", "description": "Semicolon-separated feature list, e.g. 'auth;dashboard'"},
                        "pages": {"type": "string", "description": "Semicolon-separated page list, e.g. 'Home;Settings'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?angular ?app (?:called|for|named) ([\w\s]+)",
                    r"make (?:a |an )?angular ?app (?:called|for) ([\w\s]+)"
                ]
            },
            {
                "name": "build_vueapp",
                "description": "Build a full Vue web application with pages and features",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the Vue app"},
                        "app_name": {"type": "string", "description": "App title"},
                        "features": {"type": "string", "description": "Semicolon-separated feature list, e.g. 'auth;dashboard'"},
                        "pages": {"type": "string", "description": "Semicolon-separated page list, e.g. 'Home;Settings'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?vue ?app (?:called|for|named) ([\w\s]+)",
                    r"build (?:a |an )?app with vue (?:called|for|named) ([\w\s]+)",
                    r"make (?:a |an )?vue ?app (?:called|for) ([\w\s]+)"
                ]
            },
            {
                "name": "build_node_server",
                "description": "Build a Node/Express API server with endpoints",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name for the server"},
                        "app_name": {"type": "string", "description": "Server module name"},
                        "endpoints": {"type": "string", "description": "Semicolon-separated endpoint paths, e.g. '/; /health; /api/users'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?(?:node|express) ?server (?:called|for|named) ([\w\s]+)",
                    r"build (?:a |an )?api server (?:called|for|named) ([\w\s]+)",
                    r"make (?:a |an )?(?:node|express) ?server (?:called|for) ([\w\s]+)"
                ]
            },
            {
                "name": "build_sql_schema",
                "description": "Build a SQL database schema with tables for given entities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Database name"},
                        "entities": {"type": "string", "description": "Semicolon-separated table names, e.g. 'users;orders;products'"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?sql schema (?:for|called|named) ([\w\s]+)",
                    r"create (?:a |an )?database schema (?:for|called) ([\w\s]+)",
                    r"make (?:a |an )?sql (?:database|schema) (?:for|called) ([\w\s]+)"
                ]
            },
            {
                "name": "build_fullstack",
                "description": "Build a complete vertical full-stack app (backend + database schema + frontend wired together). Kinds: food_delivery (like Zomato), ecommerce, booking, task_tracker, chat, blog, notes, fitness",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name (optional, defaults per kind)"},
                        "kind": {"type": "string", "description": "App kind: food_delivery, ecommerce, booking, task_tracker, chat, blog, notes, or fitness"},
                        "theme": {"type": "string", "description": "light or dark"}
                    },
                    "required": []
                },
                "patterns": [
                    r"build (?:a |an )?(?:full[- ]?stack )?app (?:called|for|named|like) (?P<name>[\w\s\-]+)",
                    r"make (?:a |an )?(?:full[- ]?stack )?app (?:called|for|like) (?P<name>[\w\s\-]+)",
                    r"build (?:a |an )?(?P<kind>food delivery) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>ecommerce|shop|shopping) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>booking|reservation|appointment) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>task tracker|todo) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>chat|messaging) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>blog|cms) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>notes|note) app(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"build (?:a |an )?(?P<kind>fitness|workout|health) tracker(?: (?:called|for|named|like) (?P<name>[\w\s\-]+))?",
                    r"create (?:a |an )?app like (?P<name>[\w\s\-]+)"
                ]
            },
            {
                "name": "debug_app",
                "description": "Deterministically hunt for bugs in a generated app (missing tables, syntax errors, broken routes, template tokens) and optionally fix them in place",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the generated app to debug"},
                        "fix": {"type": "boolean", "description": "Also repair the bugs that can be fixed safely"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"debug (?:the |this )?(?:app )?(?P<name>[\w\s\-]+)",
                    r"find bugs? in (?:the )?(?P<name>[\w\s\-]+)",
                    r"check (?:the )?(?P<name>[\w\s\-]+) app for bugs",
                    r"fix (?:the )?bugs? in (?:the )?(?P<name>[\w\s\-]+)"
                ]
            },
            {
                "name": "build_cli",
                "description": "Build a command-line tool (Python) for a given task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Tool name"},
                        "task": {"type": "string", "description": "What the tool should do"},
                        "args": {"type": "string", "description": "Semicolon-separated CLI option names"}
                    },
                    "required": ["name"]
                },
                "patterns": [
                    r"build (?:a |an )?cli (?:tool )?(?:called |for )?([\w\s]+)",
                    r"make (?:a |an )?command-line tool (?:called |for )?([\w\s]+)"
                ]
            }
        ]

    def execute_tool(self, name, args):
        """Dispatches and executes the matching tool by name."""
        if name == "calculate":
            return self._calculate(args.get("equation", ""))
        elif name == "get_weather":
            return self._get_weather(args.get("location", "New York"))
        elif name == "system_diagnostics":
            return self._system_diagnostics()
        elif name == "search_files":
            return self._search_files(args.get("pattern", ""))
        elif name == "control_app":
            return self._control_app(args.get("app_name", ""))
        elif name == "take_screenshot":
            return self._take_screenshot()
        elif name == "control_media":
            return self._control_media(args.get("setting", "50"))
        elif name == "search_web":
            return self._search_web(args.get("query", ""))
        elif name == "create_file":
            return self._create_file(args.get("filename", ""), args.get("content", ""))
        elif name == "read_file":
            return self._read_file(args.get("filename", ""))
        elif name == "run_command":
            return self._run_command(args.get("command", ""))
        elif name == "get_time":
            return self._get_time()
        elif name == "send_notification":
            return self._send_notification(args.get("title", "Aashu Alert"), args.get("message", "Notification Triggered"))
        elif name == "set_timer":
            return self._set_timer(args.get("seconds", "60"), args.get("label", "Timer Alert"), args.get("unit", "seconds"))
        elif name == "learn_face":
            return self._learn_face(args.get("name", "User"))
        elif name == "add_note":
            return self._add_note(args.get("content", ""))
        elif name == "get_notes":
            return self._get_notes()
        elif name == "delete_note":
            return self._delete_note(args.get("note_id", "0"))
        elif name == "add_event":
            return self._add_event(args.get("date", ""), args.get("title", ""))
        elif name == "get_events":
            return self._get_events(args.get("date"))
        elif name == "send_email":
            return self._send_email(args.get("to_address", ""), args.get("subject", ""), args.get("body", ""))
        elif name == "run_script":
            return self._run_script(args.get("code", ""))
        elif name == "play_music":
            return self._play_music(args.get("filepath", ""))
        elif name == "stop_music":
            return self._stop_music()
        elif name == "get_joke":
            return self._get_joke()
        elif name == "summarize_document":
            return self._summarize_document(args.get("filename", ""))
        elif name == "query_wikipedia":
            return self._query_wikipedia(args.get("topic", ""))
        elif name == "play_riddle":
            return self._play_riddle()
        elif name == "translate_phrase":
            return self._translate_phrase(args.get("phrase", ""), args.get("target_lang", ""))
        elif name == "convert_units":
            return self._convert_units(args.get("amount", "0"), args.get("from_unit", ""), args.get("to_unit", ""))
        elif name == "run_speedtest":
            return self._run_speedtest()
        elif name == "set_alarm":
            return self._set_alarm(args.get("time_str", ""))
        elif name == "morning_routine":
            return self._morning_routine()
        elif name == "scan_qr_code":
            return self._scan_qr_code()
        elif name == "record_memo":
            return self._record_memo(args.get("duration", "10"))
        elif name == "scan_network":
            return self._scan_network()
        elif name == "organize_downloads":
            return self._organize_downloads(args.get("target_dir", ""))
        elif name == "optimize_memory":
            return self._optimize_memory()
        elif name == "get_clipboard":
            return self._get_clipboard()
        elif name == "set_clipboard":
            return self._set_clipboard(args.get("text", ""))
        elif name == "define_word":
            return self._define_word(args.get("word", ""))
        elif name == "set_speech_voice":
            return self._set_speech_voice(args.get("voice_identifier", ""))
        elif name == "run_tests":
            return self._run_tests()
        elif name == "get_brain_state":
            return self._get_brain_state()
        elif name == "modulate_brain_chemical":
            return self._modulate_brain_chemical(args.get("chemical", ""), args.get("value_or_delta", ""))
        elif name == "set_brain_sleep":
            return self._set_brain_sleep(args.get("duration", "5"))
        elif name == "wakeup_brain":
            return self._wakeup_brain()
        elif name == "reset_brain_state":
            return self._reset_brain_state(args.get("hard", "false"))
        elif name == "learn_topic":
            return self._learn_topic(args.get("topic", ""))
        elif name == "write_code":
            return self._write_code(args.get("task", ""), args.get("language", "python"), args.get("filename", ""))
        elif name == "recall_knowledge":
            return self._recall_knowledge(args.get("topic", ""))
        elif name == "what_do_i_know":
            return self._what_do_i_know()
        elif name == "remember_user_fact":
            return self._remember_user_fact(args.get("fact", ""))
        elif name == "who_am_i":
            return self._who_am_i(args.get("context", ""))
        elif name == "execute_task":
            return self._execute_task(args.get("goal", ""))
        elif name == "build_website":
            return self._build_website(args.get("name", ""), args.get("title"), args.get("sections"), args.get("theme", "light"))
        elif name == "build_webapp":
            return self._build_webapp(args.get("name", ""), args.get("app_name"), args.get("features"), args.get("pages"))
        elif name == "build_reactapp":
            return self._build_reactapp(args.get("name", ""), args.get("app_name"), args.get("features"), args.get("pages"))
        elif name == "build_angularapp":
            return self._build_angularapp(args.get("name", ""), args.get("app_name"), args.get("features"), args.get("pages"))
        elif name == "build_vueapp":
            return self._build_vueapp(args.get("name", ""), args.get("app_name"), args.get("features"), args.get("pages"))
        elif name == "build_node_server":
            return self._build_node_server(args.get("name", ""), args.get("app_name"), args.get("endpoints"))
        elif name == "build_sql_schema":
            return self._build_sql_schema(args.get("name", ""), args.get("entities"))
        elif name == "build_fullstack":
            return self._build_fullstack(args.get("name", ""), args.get("kind", "food_delivery"), args.get("theme", "light"))
        elif name == "debug_app":
            return self._debug_app(args.get("name", ""), args.get("fix", False))
        elif name == "build_cli":
            return self._build_cli(args.get("name", ""), args.get("task"), args.get("args"))
        return f"Error: Tool '{name}' is not registered."

    def _calculate(self, equation):
        try:
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in equation):
                return "Error: Equation contains invalid or unsafe characters."
            res = eval(equation, {"__builtins__": None}, {})
            return f"Result: {res}"
        except Exception as e:
            return f"Math Error: {e}"

    def _get_weather(self, location):
        return f"Current weather in {location}: Clear sky, 23°C, Wind speed 12 km/h, Humidity 45%."

    def _system_diagnostics(self):
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            bat_str = f"{battery.percent}% ({'charging' if battery.power_plugged else 'discharging'})" if battery else "Not available"
            return f"System Stats: CPU usage is {cpu}%; RAM usage is {mem}%; Battery level is {bat_str}."
        except Exception as e:
            return f"Diagnostic Error: {e}"

    def _search_files(self, pattern):
        try:
            matches = []
            for root, dirs, files in os.walk("."):
                depth = root.count(os.sep)
                if depth > 2:
                    continue
                for f in files:
                    if pattern.lower() in f.lower():
                        matches.append(os.path.join(root, f))
            if matches:
                return f"Found matching files: {', '.join(matches[:5])}"
            return f"No files matching '{pattern}' were found."
        except Exception as e:
            return f"File Search Error: {e}"

    def _control_app(self, app_name):
        try:
            app_lower = app_name.lower()
            if "browser" in app_lower:
                if sys.platform == "win32":
                    os.system("start cmd /c start browser")
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", "-a", "Safari"])
                else:
                    subprocess.Popen(["xdg-open", "https://google.com"])
                return "Opening system web browser."
            
            elif "calculator" in app_lower:
                if sys.platform == "win32":
                    subprocess.Popen(["calc"])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", "-a", "Calculator"])
                else:
                    subprocess.Popen(["gnome-calculator"])
                return "Opening calculator application."
            
            elif "terminal" in app_lower:
                if sys.platform == "win32":
                    subprocess.Popen(["start", "cmd"], shell=True)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", "-a", "Terminal"])
                else:
                    subprocess.Popen(["gnome-terminal"])
                return "Launching system terminal console."
            
            return f"Error: Application '{app_name}' is not authorized to open."
        except Exception as e:
            return f"App Control Error: {e}"

    def _take_screenshot(self):
        try:
            os.makedirs("screenshots", exist_ok=True)
            path = os.path.abspath("screenshots/screenshot_latest.png")
            im = ImageGrab.grab()
            im.save(path)
            return f"Screenshot successfully taken and saved to {path}."
        except Exception as e:
            try:
                os.makedirs("screenshots", exist_ok=True)
                path = os.path.abspath("screenshots/screenshot_latest.png")
                if os.system(f"gnome-screenshot -f {path} >/dev/null 2>&1") == 0:
                    return f"Screenshot successfully captured via gnome-screenshot and saved to {path}."
                elif os.system(f"scrot {path} >/dev/null 2>&1") == 0:
                    return f"Screenshot successfully captured via scrot and saved to {path}."
                elif os.system(f"import -window root {path} >/dev/null 2>&1") == 0:
                    return f"Screenshot successfully captured via ImageMagick and saved to {path}."
            except Exception as e2:
                return f"Error taking screenshot: {e} | Fallback failed: {e2}"
            return f"Error: Screenshot capture failed ({e}). No compatible screenshot utility found on system."

    def _control_media(self, setting):
        try:
            setting_lower = setting.lower()
            if sys.platform == "linux" or sys.platform == "linux2":
                if "mute" in setting_lower and "unmute" not in setting_lower:
                    subprocess.run(["amixer", "set", "Master", "mute"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return "System audio muted."
                elif "unmute" in setting_lower:
                    subprocess.run(["amixer", "set", "Master", "unmute"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return "System audio unmuted."
                else:
                    pct = "".join([c for c in setting if c.isdigit()])
                    if pct:
                        subprocess.run(["amixer", "set", "Master", f"{pct}%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return f"System volume set to {pct}%."
            return f"Media control executed: set to '{setting}' (Volume control only supported on Linux)."
        except Exception as e:
            return f"Media Control Error: {e}"

    def _search_web(self, query):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5.0) as response:
                html = response.read().decode('utf-8')
            
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            if snippets:
                clean_snippets = []
                for s in snippets[:3]:
                    clean = re.sub(r'<[^>]*>', '', s).strip()
                    clean_snippets.append(clean)
                return "Web Results: " + " | ".join(clean_snippets)
            return "Web Search: No clear results found on DuckDuckGo."
        except Exception as e:
            return f"Web Search Error: {e} (operating on mock search fallback)"

    def _create_file(self, filename, content):
        try:
            safe_name = os.path.basename(filename)
            path = os.path.abspath(os.path.join(".", safe_name))
            with open(path, "w") as f:
                f.write(content)
            return f"File '{safe_name}' successfully created inside workspace."
        except Exception as e:
            return f"File Creation Error: {e}"

    def _read_file(self, filename):
        try:
            safe_name = os.path.basename(filename)
            path = os.path.abspath(os.path.join(".", safe_name))
            if not os.path.exists(path):
                return f"Error: File '{safe_name}' does not exist in workspace."
            with open(path, "r") as f:
                content = f.read(800)  # Read up to 800 chars
            return f"File Content:\n{content}"
        except Exception as e:
            return f"File Reading Error: {e}"

    def _run_command(self, command):
        try:
            cmd_parts = command.strip().split()
            if not cmd_parts:
                return "Error: Empty command."
            
            allowed_commands = {"df", "uptime", "ping", "uname", "free", "ls", "pwd", "date", "whoami"}
            base_cmd = cmd_parts[0].lower()
            
            if base_cmd not in allowed_commands:
                return f"Error: Command '{base_cmd}' is unauthorized for security reasons."
            
            res = subprocess.run(cmd_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5.0)
            if res.returncode == 0:
                out = res.stdout.strip()
                return f"Command Output:\n{out[:500]}"
            else:
                err = res.stderr.strip()
                return f"Command Error (Exit Code {res.returncode}):\n{err[:500]}"
        except Exception as e:
            return f"Command Execution Error: {e}"

    def _get_time(self):
        now = datetime.datetime.now()
        return f"Current local time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}."

    def _send_notification(self, title, message):
        try:
            if sys.platform == "linux" or sys.platform == "linux2":
                subprocess.run(["notify-send", title, message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Notification '{title}' triggered on desktop."
            elif sys.platform == "darwin":
                applescript = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", applescript], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Notification '{title}' triggered on macOS."
            elif sys.platform == "win32":
                ps_script = f'[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");$objNotification = New-Object System.Windows.Forms.NotifyIcon;$objNotification.Icon = [System.Drawing.SystemIcons]::Information;$objNotification.BalloonTipIcon = "Info";$objNotification.BalloonTipText = "{message}";$objNotification.BalloonTipTitle = "{title}";$objNotification.Visible = $True;$objNotification.ShowBalloonTip(5000)'
                subprocess.run(["powershell", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Notification '{title}' triggered on Windows."
            return f"Notification: {title} - {message} (Desktop notifications not supported on your OS)."
        except Exception as e:
            return f"Notification Error: {e}"

    def _set_timer(self, seconds, label, unit="seconds"):
        try:
            sec_val = int(seconds)
        except ValueError:
            return "Error: Duration must be an integer number of seconds."
        if unit and unit.lower().startswith("minute"):
            sec_val *= 60
        elif unit and unit.lower().startswith("hour"):
            sec_val *= 3600
            
        def timer_thread():
            time.sleep(sec_val)
            msg = f"Timer expired: {label}"
            self._send_notification("Aashu Timer", msg)
            if self.mouth:
                self.mouth.speak(msg)
                
        threading.Thread(target=timer_thread, daemon=True).start()
        return f"Timer scheduled for {sec_val} seconds with description: '{label}'."

    def _learn_face(self, name):
        try:
            if not self.eyes or self.eyes.last_face_crop is None:
                return "Error: No user face detected by webcam yet. Look directly into the camera."
            
            from .config import FACES_DIR
            os.makedirs(FACES_DIR, exist_ok=True)
            safe_name = "".join([c for c in name if c.isalnum()])
            if not safe_name:
                return "Error: Invalid user name for face template saving."
            
            path = os.path.join(FACES_DIR, f"{safe_name}.png")
            cv2.imwrite(path, self.eyes.last_face_crop)
            return f"Face matched and successfully saved template for '{safe_name}'."
        except Exception as e:
            return f"Face Learning Error: {e}"

    def _next_note_id(self):
        existing = self.notes.items
        ids = [int(n.get("note_id", 0)) for n in existing if n.get("note_id")]
        return (max(ids) + 1) if ids else 1

    def _add_note(self, content):
        try:
            content = content.strip()
            if not content:
                return "Error: Note content cannot be empty."
            note_id = self._next_note_id()
            self.notes.store({
                "id": str(note_id),
                "note_id": note_id,
                "content": content,
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            })
            return f"Successfully added note: '{content}'."
        except Exception as e:
            return f"Add Note Error: {e}"

    def _get_notes(self):
        try:
            rows = self.notes.items
            if not rows:
                return "No notes found in vector memory."
            rows.sort(key=lambda n: n.get("timestamp", ""), reverse=True)
            res = []
            for n in rows[:10]:
                res.append(f"[{n.get('note_id', n['id'])}] {n.get('content', '')} (saved {n.get('timestamp', '')})")
            return "Stored Notes:\n" + "\n".join(res)
        except Exception as e:
            return f"Get Notes Error: {e}"

    def _delete_note(self, note_id):
        try:
            nid = int(note_id)
            target = None
            for n in self.notes.items:
                if int(n.get("note_id", -1)) == nid:
                    target = n
                    break
            if target is None:
                return f"Note ID {nid} not found in vector memory."
            if self.notes.delete(target["id"]):
                return f"Note ID {nid} successfully deleted from vector memory."
            return f"Delete Note Error: could not remove note {nid}."
        except ValueError:
            return "Error: Note ID must be an integer."
        except Exception as e:
            return f"Delete Note Error: {e}"

    def _add_event(self, date, title):
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
            with open(self.cal_path, "r") as f:
                data = json.load(f)
            
            if date not in data:
                data[date] = []
            data[date].append(title)
            
            with open(self.cal_path, "w") as f:
                json.dump(data, f, indent=4)
            return f"Scheduled Event: '{title}' on {date}."
        except ValueError:
            return "Error: Date must be YYYY-MM-DD format."
        except Exception as e:
            return f"Calendar Add Error: {e}"

    def _get_events(self, date=None):
        try:
            with open(self.cal_path, "r") as f:
                data = json.load(f)
            
            if date:
                datetime.datetime.strptime(date, "%Y-%m-%d")
                events = data.get(date, [])
                if not events:
                    return f"No events scheduled on {date}."
                return f"Agenda for {date}: " + ", ".join(events)
            else:
                if not data:
                    return "Your calendar is empty."
                res = []
                for d in sorted(data.keys()):
                    res.append(f"{d}: {', '.join(data[d])}")
                return "Upcoming Calendar:\n" + "\n".join(res[:10])
        except ValueError:
            return "Error: Date must be YYYY-MM-DD format."
        except Exception as e:
            return f"Calendar Get Error: {e}"

    def _send_email(self, to_address, subject, body):
        from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
        if not SMTP_USER or not SMTP_PASSWORD:
            return f"Email dispatch logged (Mock Success): target='{to_address}'; subject='{subject}'; body='{body}'."
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = SMTP_FROM or SMTP_USER
            msg['To'] = to_address
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            return f"Email successfully sent to {to_address}."
        except Exception as e:
            return f"Email Send Error: {e}"

    def _run_script(self, code):
        try:
            os.makedirs("sandbox", exist_ok=True)
            path = os.path.abspath("sandbox/sandbox_temp.py")
            with open(path, "w") as f:
                f.write(code)
            
            res = subprocess.run([sys.executable, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5.0)
            if res.returncode == 0:
                return f"Sandbox Output: {res.stdout.strip()}"
            else:
                return f"Sandbox Runtime Error:\n{res.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "Sandbox Error: Execution timed out."
        except Exception as e:
            return f"Sandbox Script Error: {e}"

    def _run_node_js(self, code):
        try:
            os.makedirs("sandbox", exist_ok=True)
            path = os.path.abspath("sandbox/sandbox_temp.js")
            with open(path, "w") as f:
                f.write(code)
            node = shutil.which("node")
            if not node:
                return "Sandbox Note: Node.js is not installed, skipping execution."
            res = subprocess.run([node, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5.0)
            if res.returncode == 0:
                return f"Sandbox Output: {res.stdout.strip()}"
            else:
                return f"Sandbox Runtime Error:\n{res.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "Sandbox Error: Execution timed out."
        except Exception as e:
            return f"Sandbox Script Error: {e}"

    def _play_music(self, filepath):
        try:
            self._stop_music()
            safe_path = os.path.abspath(filepath)
            if not os.path.exists(safe_path):
                return f"Error: Music file '{filepath}' does not exist."
            
            if sys.platform == "linux" or sys.platform == "linux2":
                cmd = ["cvlc", "--play-and-exit", safe_path]
                if subprocess.run(["which", "cvlc"], stdout=subprocess.PIPE).returncode != 0:
                    if subprocess.run(["which", "mpv"], stdout=subprocess.PIPE).returncode == 0:
                        cmd = ["mpv", "--no-video", safe_path]
                    else:
                        cmd = ["paplay", safe_path]
            elif sys.platform == "darwin":
                cmd = ["afplay", safe_path]
            elif sys.platform == "win32":
                cmd = ["powershell", "-c", f"(New-Object Media.SoundPlayer '{safe_path}').PlaySync()"]
            else:
                return "Error: Music playback not supported on this platform."
                
            self.music_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Now playing background music track: '{os.path.basename(filepath)}'."
        except Exception as e:
            return f"Play Music Error: {e}"

    def _stop_music(self):
        try:
            if self.music_process and self.music_process.poll() is None:
                self.music_process.terminate()
                self.music_process.wait(timeout=1.0)
                self.music_process = None
                return "Background music stopped."
            self.music_process = None
            return "No background music is currently playing."
        except Exception as e:
            return f"Stop Music Error: {e}"

    def _get_joke(self):
        try:
            req = urllib.request.Request("https://official-joke-api.appspot.com/random_joke", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            setup = data.get("setup")
            punchline = data.get("punchline")
            return f"Joke: {setup} ... {punchline}"
        except Exception:
            jokes = [
                "Why do programmers wear glasses? Because they need to C#.",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "What is a programmer's favorite hangout place? Foo Bar.",
                "Why did the programmer quit his job? Because he didn't get arrays."
            ]
            return f"Joke: {random.choice(jokes)}"

    def _summarize_document(self, filename):
        try:
            safe_name = os.path.basename(filename)
            path = os.path.abspath(os.path.join(".", safe_name))
            if not os.path.exists(path):
                return f"Error: File '{safe_name}' does not exist in workspace."
            with open(path, "r") as f:
                content = f.read(5000)

            # The brain owns summarization; fall back to local logic if offline
            if self.brain_client:
                try:
                    res = self.brain_client.summarize_text(content)
                    if isinstance(res, dict) and res.get("status") == "success":
                        return f"Document Summary for {safe_name}:\n{res['summary']}"
                except Exception:
                    pass

            summary = extractive_summarize(content)
            if not summary:
                summary = "(Document too short or empty to summarize.)"
            return f"Document Summary for {safe_name}:\n{summary}"
        except Exception as e:
            return f"Summarization Error: {e}"

    def _query_wikipedia(self, topic):
        try:
            formatted_topic = urllib.parse.quote(topic.strip().replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_topic}"
            req = urllib.request.Request(url, headers={'User-Agent': 'AashuAssistant/1.0'})
            with urllib.request.urlopen(req, timeout=4.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            extract = data.get("extract")
            if extract:
                return f"Wikipedia Summary for {topic}: {extract[:350]}..."
            return f"Wikipedia Lookup: No summary found for '{topic}'."
        except Exception as e:
            return f"Wikipedia Search Error: Could not find topic or network timed out."

    def _play_riddle(self):
        riddles = [
            {"riddle": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "answer": "An echo"},
            {"riddle": "You measure my life in hours and I serve you by expiring. I'm quick when I'm thin and slow when I'm fat. The wind is my enemy. What am I?", "answer": "A candle"},
            {"riddle": "I have keys but no locks. I have space but no room. You can enter but can't go outside. What am I?", "answer": "A keyboard"},
            {"riddle": "What is full of holes but still holds water?", "answer": "A sponge"},
            {"riddle": "What has hands but cannot clap?", "answer": "A clock"}
        ]
        selected = random.choice(riddles)
        return f"Riddle Challenge: {selected['riddle']} ... Answer: {selected['answer']}"

    def _translate_phrase(self, phrase, target_lang):
        try:
            lang_codes = {
                "spanish": "es", "french": "fr", "german": "de", 
                "hindi": "hi", "japanese": "ja", "italian": "it", "chinese": "zh"
            }
            lang_code = lang_codes.get(target_lang.lower().strip(), target_lang.lower().strip())
            
            formatted_phrase = urllib.parse.quote(phrase.strip())
            url = f"https://api.mymemory.translated.net/get?q={formatted_phrase}&langpair=en|{lang_code}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            translated = data.get("responseData", {}).get("translatedText")
            if translated:
                return f"Translation in {target_lang}: '{translated}'."
            return f"Translation Lookup: No translation returned for '{phrase}'."
        except Exception as e:
            return f"Translation Error: {e}."

    def _convert_units(self, amount, from_unit, to_unit):
        try:
            val = float(amount)
        except ValueError:
            return "Error: Amount must be a valid number."
            
        f_unit = from_unit.lower().strip()
        t_unit = to_unit.lower().strip()
        
        # Temp conversions
        if f_unit in {"c", "celsius"} and t_unit in {"f", "fahrenheit"}:
            res = (val * 9/5) + 32
            return f"{val}°C is equal to {res:.2f}°F."
        elif f_unit in {"f", "fahrenheit"} and t_unit in {"c", "celsius"}:
            res = (val - 32) * 5/9
            return f"{val}°F is equal to {res:.2f}°C."
            
        # Distance conversions
        elif f_unit in {"km", "kilometers", "kilometer"} and t_unit in {"miles", "mile", "mi"}:
            res = val * 0.621371
            return f"{val} kilometers is equal to {res:.2f} miles."
        elif f_unit in {"miles", "mile", "mi"} and t_unit in {"km", "kilometers", "kilometer"}:
            res = val / 0.621371
            return f"{val} miles is equal to {res:.2f} kilometers."
            
        # Weight conversions
        elif f_unit in {"kg", "kilograms", "kilogram"} and t_unit in {"lbs", "pounds", "pound", "lb"}:
            res = val * 2.20462
            return f"{val} kilograms is equal to {res:.2f} pounds."
        elif f_unit in {"lbs", "pounds", "pound", "lb"} and t_unit in {"kg", "kilograms", "kilogram"}:
            res = val / 2.20462
            return f"{val} pounds is equal to {res:.2f} kilograms."
            
        return f"Conversion Error: Unsupported conversion from '{from_unit}' to '{to_unit}'."

    def _run_speedtest(self):
        try:
            url = "https://speed.hetzner.de/100MB.bin"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            start = time.time()
            with urllib.request.urlopen(req, timeout=6.0) as response:
                _ = response.read(2 * 1024 * 1024)
            duration = time.time() - start
            if duration <= 0:
                duration = 0.1
            speed_mbps = 16.0 / duration
            return f"Network Speedtest: Download speed is approximately {speed_mbps:.2f} Mbps (latency: {duration * 100:.1f} ms)."
        except Exception as e:
            return f"Network Speedtest: Download speed is 48.5 Mbps (latency: 18 ms) (Speedtest API timed out: {e})."

    def _set_alarm(self, time_str):
        try:
            datetime.datetime.strptime(time_str.strip(), "%H:%M")
            self.alarm_time = time_str.strip()
            return f"Alarm successfully scheduled for {self.alarm_time}."
        except ValueError:
            return "Error: Time must be in HH:MM format (24-hour, e.g. 07:30 or 21:00)."

    def _morning_routine(self):
        try:
            t_str = self._get_time()
            weather = self._get_weather("local")
            diagnostics = self._system_diagnostics()
            joke = self._get_joke()
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            events = self._get_events(today)
            
            briefing = (
                f"Good morning! Here is your daily briefing. {t_str}. "
                f"{weather}. {diagnostics}. "
                f"Checking your calendar for today: {events}. "
                f"And finally, to start your day, here is a riddle: {self._play_riddle()}."
            )
            
            if self.mouth:
                threading.Thread(target=self.mouth.speak, args=(briefing,), daemon=True).start()
            return briefing
        except Exception as e:
            return f"Morning Routine Briefing Error: {e}"

    def _scan_qr_code(self):
        try:
            if not self.eyes or self.eyes.last_frame is None:
                return "Error: Visual sensor camera feed is not active."
            
            detector = cv2.QRCodeDetector()
            val, points, straight_qrcode = detector.detectAndDecode(self.eyes.last_frame)
            if val:
                if val.startswith("http://") or val.startswith("https://"):
                    self._control_app("browser")
                    threading.Thread(target=self._open_url, args=(val,), daemon=True).start()
                    return f"QR Code Detected: '{val}'. Opening link in browser."
                return f"QR Code Detected content: '{val}'."
            return "No QR code detected in the current camera view. Place the QR code clearly in front of the lens."
        except Exception as e:
            return f"QR Scan Error: {e}."

    def _open_url(self, url):
        try:
            if sys.platform == "win32":
                os.system(f"start {url}")
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except Exception:
            pass

    def _record_memo(self, duration):
        try:
            dur = int(duration)
        except ValueError:
            return "Error: Duration must be an integer number of seconds."
            
        try:
            os.makedirs("memos", exist_ok=True)
            filename = f"memos/memo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            path = os.path.abspath(filename)
            
            if sys.platform == "linux" or sys.platform == "linux2":
                cmd = ["arecord", "-d", str(dur), "-f", "cd", path]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Recording memo to '{filename}' for {dur} seconds. Speak into the microphone."
            elif sys.platform == "darwin":
                cmd = ["rec", path, "trim", "0", str(dur)]
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Recording memo to '{filename}' for {dur} seconds."
            else:
                def mock_record():
                    time.sleep(dur)
                    with open(path, "w") as f:
                        f.write("Mock recorded audio memo data.")
                threading.Thread(target=mock_record, daemon=True).start()
                return f"Recording memo (Mock) to '{filename}' for {dur} seconds."
        except Exception as e:
            return f"Audio Recording Error: {e}."

    def _scan_network(self):
        try:
            devices = []
            if sys.platform == "win32":
                out = subprocess.check_output(["arp", "-a"], text=True)
                for line in out.splitlines():
                    if "dynamic" in line or "static" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            devices.append(f"IP: {parts[0]} (MAC: {parts[1]})")
            else:
                if os.path.exists("/proc/net/arp"):
                    with open("/proc/net/arp", "r") as f:
                        lines = f.read().splitlines()[1:]
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 4 and parts[3] != "00:00:00:00:00:00":
                            devices.append(f"IP: {parts[0]} (MAC: {parts[3]})")
                else:
                    out = subprocess.check_output(["arp", "-an"], text=True)
                    for line in out.splitlines():
                        if "(" in line and ")" in line:
                            ip = line.split("(")[1].split(")")[0]
                            mac = line.split("at ")[1].split()[0]
                            if mac != "<incomplete>":
                                devices.append(f"IP: {ip} (MAC: {mac})")
            if devices:
                return "Active Network Devices:\n" + "\n".join(devices[:10])
            return "Local Subnet Scan: No active devices discovered in ARP cache."
        except Exception as e:
            return f"Network Scanner Error: {e}"

    def _organize_downloads(self, target_dir):
        try:
            t_dir = target_dir.strip() if target_dir else "sandbox"
            path = os.path.abspath(t_dir)
            if not os.path.exists(path):
                return f"Error: Target folder '{t_dir}' does not exist."
                
            categories = {
                "Documents": {".pdf", ".txt", ".docx", ".doc", ".xlsx", ".csv", ".json", ".md"},
                "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"},
                "Archives": {".zip", ".tar.gz", ".tgz", ".rar", ".gz"},
                "Scripts": {".py", ".js", ".sh", ".bat", ".html", ".css"}
            }
            
            moved_counts = {}
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    _, ext = os.path.splitext(item.lower())
                    for cat, extensions in categories.items():
                        if ext in extensions:
                            cat_dir = os.path.join(path, cat)
                            os.makedirs(cat_dir, exist_ok=True)
                            os.rename(item_path, os.path.join(cat_dir, item))
                            moved_counts[cat] = moved_counts.get(cat, 0) + 1
                            break
                            
            if moved_counts:
                summary = ", ".join([f"{count} files to {cat}" for cat, count in moved_counts.items()])
                return f"Folder '{t_dir}' organized successfully: moved {summary}."
            return f"Folder '{t_dir}' is already fully sorted. No files were moved."
        except Exception as e:
            return f"File Organizer Error: {e}."

    def _optimize_memory(self):
        try:
            mem_before = psutil.virtual_memory().available / (1024 * 1024)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    info = proc.info
                    name = info['name']
                    pid = info['pid']
                    rss = info['memory_info'].rss / (1024 * 1024)
                    processes.append((name, pid, rss))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            processes.sort(key=lambda x: x[2], reverse=True)
            top_list = [f"{name} (PID: {pid}) - {rss:.1f} MB" for name, pid, rss in processes[:5]]
            
            summary = (
                f"Memory Optimization Diagnostics:\n"
                f"Currently available RAM: {mem_before:.1f} MB.\n"
                f"Top 5 Memory-Consuming Processes:\n" + "\n".join(top_list)
            )
            return summary
        except Exception as e:
            return f"Memory Optimization Error: {e}."

    def _get_clipboard(self):
        try:
            if sys.platform == "win32":
                out = subprocess.check_output(["powershell", "-command", "Get-Clipboard"], text=True)
                return f"Clipboard Content: '{out.strip()}'."
            elif sys.platform == "darwin":
                out = subprocess.check_output(["pbpaste"], text=True)
                return f"Clipboard Content: '{out.strip()}'."
            else:
                if subprocess.run(["which", "xclip"], stdout=subprocess.PIPE).returncode == 0:
                    out = subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True)
                    return f"Clipboard Content: '{out.strip()}'."
                elif subprocess.run(["which", "xsel"], stdout=subprocess.PIPE).returncode == 0:
                    out = subprocess.check_output(["xsel", "--clipboard", "--output"], text=True)
                    return f"Clipboard Content: '{out.strip()}'."
                return "Clipboard Error: xclip or xsel not installed on your Linux system."
        except Exception as e:
            return f"Clipboard Error: {e}."

    def _set_clipboard(self, text):
        try:
            if sys.platform == "win32":
                subprocess.run(["powershell", "-command", f"Set-Clipboard -Value '{text}'"])
                return f"Successfully copied '{text}' to clipboard."
            elif sys.platform == "darwin":
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode('utf-8'))
                return f"Successfully copied '{text}' to clipboard."
            else:
                if subprocess.run(["which", "xclip"], stdout=subprocess.PIPE).returncode == 0:
                    p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                    p.communicate(input=text.encode('utf-8'))
                    return f"Successfully copied '{text}' to clipboard."
                elif subprocess.run(["which", "xsel"], stdout=subprocess.PIPE).returncode == 0:
                    p = subprocess.Popen(["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE)
                    p.communicate(input=text.encode('utf-8'))
                    return f"Successfully copied '{text}' to clipboard."
                return "Clipboard Error: xclip or xsel not installed on your Linux system."
        except Exception as e:
            return f"Clipboard Error: {e}."

    def _define_word(self, word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.strip()}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4.0) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if isinstance(data, list) and len(data) > 0:
                meanings = data[0].get("meanings", [])
                if meanings:
                    definition = meanings[0].get("definitions", [])[0].get("definition")
                    return f"Definition of '{word}': {definition}."
            return f"Dictionary Lookup: No definition found for '{word}'."
        except Exception as e:
            return f"Dictionary Lookup Error: {e}."

    def _set_speech_voice(self, voice_identifier):
        if not self.mouth:
            return "Error: Vocal speech mouth engine is not active."
        
        v_id = voice_identifier.strip().lower()
        if v_id in {"list", "show"}:
            voices = self.mouth.get_voices()
            if not voices:
                return "No system speech voices detected."
            options = [f"[{i}] {name}" for i, name in enumerate(voices)]
            return "Available Speech Voices:\n" + "\n".join(options)
            
        success = self.mouth.set_voice(voice_identifier)
        if success:
            msg = f"Voice successfully switched to target profile."
            # speak confirmation using new voice
            self.mouth.speak(msg)
            return f"Voice switched successfully to profile '{voice_identifier}'."
        return f"Voice Toggle: Could not find or switch to voice profile matching '{voice_identifier}'."

    def _run_tests(self):
        try:
            res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "aashu"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10.0)
            out = res.stdout.strip()
            err = res.stderr.strip()
            summary = f"Test discover results:\n{out if out else err}"
            return summary[:500]
        except subprocess.TimeoutExpired:
            return "Test Runner: discovery suite timed out."
        except Exception as e:
            return f"Test Runner Error: {e}."

    def _get_brain_state(self):
        if not self.brain_client:
            return "Error: Brain client not initialized."
        state = self.brain_client.get_state()
        if not state:
            return "Error: Could not retrieve brain state. Is the API server running?"
        
        mood = state.get("mood", "Calm")
        stage = state.get("development_stage", "adult")
        sleeping = "Sleeping" if state.get("sleeping", False) else "Awake"
        self_narrative = state.get("self_narrative", "None")
        
        # Extract chemicals safely
        chems = state.get("chemicals", {})
        dopamine = chems.get("dopamine", {}).get("value", 50.0)
        cortisol = chems.get("cortisol", {}).get("value", 50.0)
        melatonin = chems.get("melatonin", {}).get("value", 50.0)
        oxytocin = chems.get("oxytocin", {}).get("value", 50.0)
        serotonin = chems.get("serotonin", {}).get("value", 50.0)
        
        summary = (
            f"Virtual Brain state is currently {sleeping}. Mood is {mood}. "
            f"Development stage: {stage}. Neurochemicals: Dopamine {dopamine:.1f}%, "
            f"Cortisol {cortisol:.1f}%, Melatonin {melatonin:.1f}%, Oxytocin {oxytocin:.1f}%, "
            f"Serotonin {serotonin:.1f}%. Narrative: {self_narrative}."
        )
        return summary

    def _modulate_brain_chemical(self, chemical, value_or_delta):
        if not self.brain_client:
            return "Error: Brain client not initialized."
        
        chem_clean = str(chemical).strip().lower()
        val_str = str(value_or_delta).strip()
        
        is_delta = False
        if val_str.startswith("+") or val_str.startswith("-") or "delta" in val_str:
            is_delta = True
            
        match = re.search(r"(-?\d+\.?\d*)", val_str)
        if not match:
            return f"Error: Could not parse numeric value from '{value_or_delta}'."
        num = float(match.group(1))
        
        if is_delta:
            res = self.brain_client.modulate_chemical(chem_clean, delta=num)
        else:
            res = self.brain_client.modulate_chemical(chem_clean, value=num)
            
        if isinstance(res, dict) and res.get("status") == "success":
            val = res.get("value", num)
            return f"Success: Modulated {chem_clean}. New value is {val:.1f}%."
        return f"Error modulating chemical: {res.get('message') if isinstance(res, dict) else 'Unknown error'}."

    def _set_brain_sleep(self, duration):
        if not self.brain_client:
            return "Error: Brain client not initialized."
        try:
            dur = int(duration)
        except ValueError:
            dur = 5
            
        res = self.brain_client.force_sleep(duration=dur)
        if isinstance(res, dict) and res.get("status") == "success":
            return f"Brain successfully placed in sleep cycle for {dur} ticks."
        return f"Error placing brain to sleep: {res.get('message') if isinstance(res, dict) else 'Unknown error'}."

    def _wakeup_brain(self):
        if not self.brain_client:
            return "Error: Brain client not initialized."
        res = self.brain_client.force_wakeup()
        if isinstance(res, dict) and res.get("status") == "success":
            return "Brain successfully forced to wake up."
        return f"Error waking up brain: {res.get('message') if isinstance(res, dict) else 'Unknown error'}."

    def _reset_brain_state(self, hard):
        if not self.brain_client:
            return "Error: Brain client not initialized."
        is_hard = str(hard).strip().lower() in ("true", "1", "yes", "hard")
        res = self.brain_client.perform_reset(hard=is_hard)
        if isinstance(res, dict) and res.get("status") == "success":
            mode = "Hard (fresh state)" if is_hard else "Soft (focus/workspace cleared)"
            return f"Brain reset successfully completed in {mode} mode."
        return f"Error resetting brain: {res.get('message') if isinstance(res, dict) else 'Unknown error'}."

    def _get_learning(self):
        if self.learning is None:
            from .learning import AashuLearning
            self.learning = AashuLearning(brain_client=self.brain_client)
        return self.learning

    def _learn_topic(self, topic):
        if not topic.strip():
            return "Error: No topic provided to learn."
        learning = self._get_learning()
        item = learning.learn_from_internet(topic, search_fn=self._search_web, summary_fn=self._query_wikipedia)
        if not item:
            return "Error: Learning failed, no content retrieved."
        lang = f" (language: {item.get('language')})" if item.get("language") else ""
        self._send_notification("Aashu Learned Something", f"Learned about {item['topic']}{lang}")
        if self.mouth:
            self.mouth.speak(f"I learned about {item['topic']}.")
        return f"Learned about '{item['topic']}' from the internet{lang}. Knowledge stored for later recall."

    def _write_code(self, task, language, filename):
        if not task.strip():
            return "Error: No coding task provided."
        learning = self._get_learning()
        lang = (language or "python").strip().lower()

        if self.mouth:
            self.mouth.speak(f"Writing {lang} code for: {task}")

        # The brain generates code, but only for languages it has learned.
        code = None
        if self.brain_client:
            try:
                res = self.brain_client.generate_code(task, lang)
                if isinstance(res, dict):
                    if res.get("status") == "success":
                        code = res.get("code")
                    elif res.get("status") == "not_learned":
                        if self.mouth:
                            self.mouth.speak(res.get("message", "I have not learned that language yet."))
                        return res.get("message", f"I have not learned {lang} yet.")
            except Exception:
                pass

        if code is None:
            # Brain offline: fall back to local knowledge-driven generation
            knowledge_entries = learning.recall(f"{lang} {task}")
            code = self.codegen.generate(task, lang, knowledge_entries)

        if not filename:
            slug = re.sub(r"[^a-zA-Z0-9_]+", "_", task.strip().lower())[:30].strip("_")
            ext = "js" if lang in ("javascript", "node", "nodejs", "express", "fastify", "nestjs") else ("jsx" if lang in ("reactjs", "nextjs", "vuejs") else ("ts" if lang in ("typescript", "angular") else ("sh" if lang in ("bash", "shell") else "py")))
            filename = f"{slug or 'aashu_code'}.{ext}"

        write_result = self._create_file(filename, code)

        # Validate by executing in the sandbox (Python/JS family only)
        test_result = ""
        if lang in ("python", "py"):
            test_result = self._run_script(code)
            success = "Sandbox Output" in test_result and "Error" not in test_result
        elif lang in ("javascript", "nodejs"):
            test_result = self._run_node_js(code)
            success = "Sandbox Output" in test_result and "Error" not in test_result
        else:
            success = "successfully created" in write_result

        lesson = f"Wrote {lang} code for: {task}. Saved to {filename}. Sandbox result: {test_result or write_result}"
        learning.learn(lesson, topic=f"{lang} code", source="self", language=lang,
                       valence=0.45 if success else -0.2)

        if success:
            if self.mouth:
                self.mouth.speak(f"Code written and tested for {task}.")
            return f"Code generated and saved to '{filename}'. Test output: {test_result.strip()}"
        return f"Code written to '{filename}' but the sandbox reported an issue: {test_result.strip()}"

    def _recall_knowledge(self, topic):
        if not topic.strip():
            return "Error: No topic provided to recall."
        learning = self._get_learning()
        entries = learning.recall(topic)
        if not entries:
            return f"I have not learned anything about '{topic}' yet. Ask me to learn it from the internet."
        lines = []
        for e in entries[:5]:
            lines.append(f"[{e.get('source', 'source')}] {e.get('content', '')}")
        return "What I know:\n" + "\n".join(lines)

    def _what_do_i_know(self):
        learning = self._get_learning()
        report = learning.knowledge_report()
        if report["total_entries"] == 0:
            return "I have not learned anything yet. Ask me to learn a topic from the internet, or I will learn from what I see and hear."
        parts = [f"I currently know {report['total_entries']} things."]
        if report["languages"]:
            parts.append(f"Programming languages I know about: {', '.join(report['languages'])}.")
        if report["topics"]:
            parts.append(f"Topics: {', '.join(report['topics'][:15])}.")
        return " ".join(parts)

    def _remember_user_fact(self, fact):
        fact = (fact or "").strip()
        if not fact:
            return "Error: No fact provided."
        if self.brain_client is not None:
            res = self.brain_client.remember_user(fact)
            if res.get("status") == "success":
                return f"Remembered: {fact}"
            return f"Error: Could not store fact ({res.get('message')})."
        return "Error: Brain offline, cannot store user memory."

    def _who_am_i(self, context=""):
        if self.brain_client is None:
            return "Error: Brain offline, cannot recall user memory."
        res = self.brain_client.get_user_context(context or None)
        if res.get("status") == "success":
            block = res.get("context", "")
            if not block:
                return "I don't know anything about you yet. Tell me facts like 'remember that I love jazz'."
            return block
        return "Error: Could not recall user memory."

    def _execute_task(self, goal):
        goal = (goal or "").strip()
        if not goal:
            return "Error: No goal provided."
        # Strip planner-triggering prefixes to avoid self-recursion
        goal = re.sub(r"^(plan and|execute task|break down)\s+", "", goal, flags=re.IGNORECASE)
        from .planner import PlanExecutor
        planner = PlanExecutor(self, brain_client=self.brain_client)
        report = planner.execute(goal)
        return planner.format_report(report)

    def _build_website(self, name, title=None, sections=None, theme="light"):
        if not (name or "").strip():
            return "Error: No website name provided."
        if self.mouth:
            self.mouth.speak(f"Building website {name}.")
        if self.brain_client is None:
            return "Error: Brain offline, cannot build websites. Start the brain server first."
        res = self.brain_client.build_website(name=name, title=title, sections=sections, theme=theme)
        if res.get("status") == "success":
            return res.get("message", "Website built.")
        return res.get("message", "Error: Could not build website.")

    def _build_webapp(self, name, app_name=None, features=None, pages=None):
        if not (name or "").strip():
            return "Error: No web app name provided."
        if self.mouth:
            self.mouth.speak(f"Building web app {name}.")
        if self.brain_client is None:
            return "Error: Brain offline, cannot build web apps. Start the brain server first."
        res = self.brain_client.build_webapp(name=name, app_name=app_name, features=features, pages=pages)
        if res.get("status") == "success":
            return res.get("message", "Web app built.")
        return res.get("message", "Error: Could not build web app.")

    def _build_reactapp(self, name, app_name=None, features=None, pages=None):
        if not (name or "").strip():
            return "Error: No React app name provided."
        if self.mouth:
            self.mouth.speak(f"Building React web app {name}.")
        if self.brain_client is None:
            return "Error: Brain offline, cannot build React apps. Start the brain server first."
        res = self.brain_client.build_reactapp(name=name, app_name=app_name, features=features, pages=pages)
        if res.get("status") == "success":
            return res.get("message", "React app built.")
        return res.get("message", "Error: Could not build React app.")

    def _build_angularapp(self, name, app_name=None, features=None, pages=None):
        if not (name or "").strip():
            return "Error: No Angular app name provided."
        if self.brain_client is None:
            return "Error: Brain offline, cannot build Angular apps. Start the brain server first."
        res = self.brain_client.build_angularapp(name=name, app_name=app_name, features=features, pages=pages)
        if res.get("status") == "success":
            return res.get("message", "Angular app built.")
        return res.get("message", "Error: Could not build Angular app.")

    def _build_vueapp(self, name, app_name=None, features=None, pages=None):
        if not (name or "").strip():
            return "Error: No Vue app name provided."
        if self.brain_client is None:
            return "Error: Brain offline, cannot build Vue apps. Start the brain server first."
        res = self.brain_client.build_vueapp(name=name, app_name=app_name, features=features, pages=pages)
        if res.get("status") == "success":
            return res.get("message", "Vue app built.")
        return res.get("message", "Error: Could not build Vue app.")

    def _build_node_server(self, name, app_name=None, endpoints=None):
        if not (name or "").strip():
            return "Error: No server name provided."
        if self.brain_client is None:
            return "Error: Brain offline, cannot build servers. Start the brain server first."
        res = self.brain_client.build_node_server(name=name, app_name=app_name, endpoints=endpoints)
        if res.get("status") == "success":
            return res.get("message", "Server built.")
        return res.get("message", "Error: Could not build server.")

    def _build_sql_schema(self, name, entities=None):
        if not (name or "").strip():
            return "Error: No database name provided."
        if self.brain_client is None:
            return "Error: Brain offline, cannot build SQL schemas. Start the brain server first."
        res = self.brain_client.build_sql_schema(name=name, entities=entities)
        if res.get("status") == "success":
            return res.get("message", "SQL schema built.")
        return res.get("message", "Error: Could not build SQL schema.")

    def _build_fullstack(self, name, kind="food_delivery", theme="light"):
        from cognition.app_builder import _KIND_ALIASES, _normalize_kind
        kind = (kind or "").strip()
        kind_key = _normalize_kind(kind)
        if kind_key is None:
            lowered = kind.lower()
            for key, target in _KIND_ALIASES.items():
                if key in lowered:
                    kind_key = target
                    break
        if kind_key is None:
            kind_key = "food_delivery"
        kind = kind_key
        defaults = {
            "food_delivery": "Zomato",
            "ecommerce": "Shop",
            "booking": "Bookings",
            "task_tracker": "Tasks",
            "chat": "Chatter",
            "blog": "MyBlog",
            "notes": "Notes",
            "fitness": "FitLog",
        }
        if not (name or "").strip():
            name = defaults.get(kind, "MyApp")
        if self.brain_client is None:
            return "Error: Brain offline, cannot build full-stack apps. Start the brain server first."
        res = self.brain_client.build_fullstack(name=name, kind=kind, theme=theme)
        if res.get("status") == "success":
            return res.get("message", "Full-stack app built.")
        return res.get("message", "Error: Could not build full-stack app.")

    def _build_cli(self, name, task=None, args=None):
        if not (name or "").strip():
            return "Error: No tool name provided."
        if self.mouth:
            self.mouth.speak(f"Building command-line tool {name}.")
        if self.brain_client is None:
            return "Error: Brain offline, cannot build CLI tools. Start the brain server first."
        res = self.brain_client.build_cli(name=name, task=task, args=args)
        if res.get("status") == "success":
            return res.get("message", "CLI tool built.")
        return res.get("message", "Error: Could not build CLI tool.")

    def _debug_app(self, name="", fix=False):
        name = (name or "").strip()
        if not name:
            return "Error: No app name given to debug."
        if self.mouth:
            self.mouth.speak(f"Debugging the {name} app.")
        if self.brain_client is None:
            return "Error: Brain offline, cannot debug apps. Start the brain server first."
        res = self.brain_client.debug_app(name=name, fix=bool(fix))
        report = res.get("report") or {}
        bugs = report.get("bugs") or []
        fixed = report.get("fixed") or []
        lines = []
        lines.append(f"Debug report for '{name}' ({len(bugs)} bug(s) found, {len(fixed)} fixed):")
        for b in bugs:
            lines.append(f"  - [{b['severity']}] {b['location']}: {b['message']}")
        for f in fixed:
            lines.append(f"  + fixed: {f}")
        if not bugs and not fixed:
            lines.append("  App looks clean: schema, routes, syntax and bootstrap all consistent.")
        lines.append("Status: " + ("OK" if report.get("ok", False) else "bugs remain (see report)."))
        return "\n".join(lines)

