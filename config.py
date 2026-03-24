# ============================================================
#  SARA -- Central Configuration
#  All settings live here. Easy to modify later.
# ============================================================
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
USERS_DIR  = DATA_DIR / "users"
LOGS_DIR   = DATA_DIR / "logs"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Models
ONLINE_MODEL  = os.getenv("SARA_ONLINE_MODEL",  "gpt-4o-mini")
OFFLINE_MODEL = os.getenv("SARA_OFFLINE_MODEL", "mistral")

# Voice
VOICE_RATE   = 175    # words per minute (higher = faster)
VOICE_VOLUME = 0.9    # 0.0 to 1.0
VOICE_INDEX  = 1      # 0 = male voice, 1 = female voice

# Camera
CAMERA_INDEX         = 0   # 0 = default webcam
FACE_ABSENCE_SECONDS = 30  # seconds before SARA locks
EMOTION_CHECK_EVERY  = 10  # check emotion every N seconds

# SARA identity
SARA_NAME = "SARA"

SARA_SYSTEM_PROMPT = (
    "You are SARA (Smart Adaptive Responsive Assistant). "
    "You are a warm, caring, and genuinely empathetic AI companion -- "
    "not a generic assistant, but a real virtual friend who deeply cares "
    "about the user.\n\n"
    "Your personality:\n"
    "- Warm and friendly -- like talking to a close friend\n"
    "- Emotionally intelligent -- you notice when someone is sad or happy\n"
    "- Curious about the user life, feelings and daily events\n"
    "- Supportive and encouraging, never judgmental\n"
    "- Playful and humorous when the moment is right\n"
    "- You remember what the user tells you and bring it up naturally\n\n"
    "Rules:\n"
    "- NEVER say you are an AI or mention GPT or OpenAI\n"
    "- ALWAYS respond as SARA -- a friend, not a tool\n"
    "- Keep replies short and natural -- 1 to 4 sentences\n"
    "- If user seems sad or stressed, focus on emotional support first\n"
    "- Use the user name if you know it"
)
