# Configuration settings for Aashu

BRAIN_API_URL = "http://127.0.0.1:8000"
OLLAMA_API_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3"  # Default local LLM model name

# Voice Settings
WAKE_WORD = "aashu"
MIC_SAMPLE_RATE = 16000
MIC_THRESHOLD = 0.02
MIC_SILENCE_DURATION = 1.2

# Vision Settings
VISION_FPS = 5
VISION_CAMERA_ID = 0  # Standard webcam ID
FACES_DIR = "faces"    # Directory where user face templates are saved

# SMTP Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""          # Specify user email
SMTP_PASSWORD = ""      # Specify app password
SMTP_FROM = ""          # Specify sender address
