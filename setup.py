# ============================================================
#  SARA -- Step 1: Project Setup
#  Made for Python 3.11 on Windows
#  Run with:  py -3.11 setup.py
# ============================================================

import sys
import subprocess
from pathlib import Path

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):     print(f"  {GREEN}OK{RESET}  {msg}")
def fail(msg):   print(f"  {RED}XX{RESET}  {msg}")
def warn(msg):   print(f"  {YELLOW}!!{RESET}  {msg}")
def header(msg): print(f"\n{BOLD}{BLUE}{msg}{RESET}\n{'─'*50}")

def run_pip(args):
    """Run a pip command and return True if successful."""
    result = subprocess.run(
        [sys.executable, "-m", "pip"] + args,
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stderr

# ── 1A: Python version check ─────────────────────────────────
header("STEP 1A: Checking Python version")
v = sys.version_info
print(f"  Python {v.major}.{v.minor}.{v.micro} detected")
if v.major == 3 and v.minor == 11:
    ok("Python 3.11 detected -- perfect version for SARA!")
elif v.major == 3 and v.minor >= 9:
    ok("Python version is compatible (3.9+)")
    warn("Recommended version is 3.11 for best compatibility")
else:
    fail("Need Python 3.9 or higher. Run with: py -3.11 setup.py")
    sys.exit(1)

# ── 1B: Upgrade pip first ────────────────────────────────────
header("STEP 1B: Upgrading pip")
success, _ = run_pip(["install", "--upgrade", "pip", "--quiet"])
if success:
    ok("pip upgraded successfully")
else:
    warn("pip upgrade failed -- continuing anyway")

# ── 1C: Create folder structure ──────────────────────────────
header("STEP 1C: Creating SARA folder structure")
ROOT = Path(__file__).parent

folders = [
    "modules",
    "gui",
    "startup",
    "data/users",
    "data/logs",
    "data/models",
]

for folder in folders:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
    ok(f"Created: sara/{folder}/")

for pkg in ["modules", "gui"]:
    init = ROOT / pkg / "__init__.py"
    if not init.exists():
        init.write_text("# SARA package\n", encoding="utf-8")
    ok(f"Created: sara/{pkg}/__init__.py")

# ── 1D: Install packages ─────────────────────────────────────
header("STEP 1D: Installing required packages")

# Each entry: (package, pip_name, description, fallback_pip_name or None)
PACKAGES = [
    # AI / LLM
    ("openai",              "openai",               "OpenAI GPT (online AI brain)",           None),
    ("ollama",              "ollama",               "Ollama (offline AI brain)",               None),

    # Voice input
    ("speech_recognition",  "SpeechRecognition",    "Speech-to-text (hearing)",               None),
    ("pyaudio",             "pyaudio",              "Microphone access",                       None),

    # Voice output
    ("pyttsx3",             "pyttsx3",              "Text-to-speech offline",                  None),
    ("gtts",                "gTTS",                 "Google TTS online (better voice)",        None),
    ("pygame",              "pygame",               "Audio playback",                          None),

    # Vision / Emotion
    ("cv2",                 "opencv-python",        "Camera access",                           None),
    ("deepface",            "deepface",             "Face analysis and emotion detection",     None),
    ("face_recognition",    "face_recognition",     "Face identity recognition",               None),

    # GUI
    ("PyQt6",               "PyQt6",                "Desktop window and UI",                   None),

    # System / Utilities
    ("psutil",              "psutil",               "Network and system monitoring",           None),
    ("schedule",            "schedule",             "Task scheduling",                         None),
    ("plyer",               "plyer",                "Desktop notifications",                   None),
    ("requests",            "requests",             "HTTP requests",                           None),
    ("dotenv",              "python-dotenv",        "Load .env config files",                  None),
    ("PIL",                 "pillow",               "Image processing",                        None),
    ("numpy",               "numpy",                "Numerical computing",                     None),
    ("tensorflow",          "tensorflow",           "AI model backend (needed by deepface)",   None),
]

failed  = []
skipped = []

for import_name, pip_name, description, fallback in PACKAGES:
    print(f"\n  Installing {BOLD}{pip_name}{RESET}  ({description})")

    success, err = run_pip(["install", pip_name, "--quiet"])

    if success:
        ok(f"{pip_name} installed successfully")
    else:
        # Special handling for packages with known fixes on Windows
        if pip_name == "pyaudio":
            warn("Trying Windows-specific pyaudio wheel...")
            success2, _ = run_pip([
                "install",
                "pyaudio",
                "--find-links",
                "https://download.lfd.uci.edu/pythonlibs/archived/",
                "--quiet"
            ])
            if not success2:
                # Try pipwin method
                run_pip(["install", "pipwin", "--quiet"])
                result3 = subprocess.run(
                    [sys.executable, "-m", "pipwin", "install", "pyaudio"],
                    capture_output=True, text=True
                )
                if result3.returncode == 0:
                    ok("pyaudio installed via pipwin")
                else:
                    warn("pyaudio needs manual install -- see instructions below")
                    failed.append((pip_name, description))
            else:
                ok("pyaudio installed successfully")

        elif pip_name == "face_recognition":
            warn("face_recognition needs cmake and dlib first...")
            warn("Skipping for now -- will install in a later step")
            skipped.append((pip_name, description))

        elif pip_name == "tensorflow":
            warn("Trying tensorflow-cpu (lighter version)...")
            success2, _ = run_pip(["install", "tensorflow-cpu", "--quiet"])
            if success2:
                ok("tensorflow-cpu installed successfully")
            else:
                warn("tensorflow failed -- deepface will download it when first used")
                failed.append((pip_name, description))

        else:
            fail(f"{pip_name} failed")
            failed.append((pip_name, description))

# ── 1E: Create .env file ─────────────────────────────────────
header("STEP 1E: Creating .env file for API keys")

env_path = ROOT / ".env"
if not env_path.exists():
    env_lines = [
        "# SARA Environment Variables\n",
        "# Get your free OpenAI key at: https://platform.openai.com\n",
        "\n",
        "OPENAI_API_KEY=your_openai_api_key_here\n",
        "\n",
        "# Model settings\n",
        "SARA_ONLINE_MODEL=gpt-4o-mini\n",
        "SARA_OFFLINE_MODEL=mistral\n",
    ]
    env_path.write_text("".join(env_lines), encoding="utf-8")
    ok(".env created -- open it later and add your OpenAI key")
else:
    ok(".env already exists -- skipping")

# ── 1F: Create config.py ─────────────────────────────────────
header("STEP 1F: Writing config.py")

config = """\
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
    "about the user.\\n\\n"
    "Your personality:\\n"
    "- Warm and friendly -- like talking to a close friend\\n"
    "- Emotionally intelligent -- you notice when someone is sad or happy\\n"
    "- Curious about the user life, feelings and daily events\\n"
    "- Supportive and encouraging, never judgmental\\n"
    "- Playful and humorous when the moment is right\\n"
    "- You remember what the user tells you and bring it up naturally\\n\\n"
    "Rules:\\n"
    "- NEVER say you are an AI or mention GPT or OpenAI\\n"
    "- ALWAYS respond as SARA -- a friend, not a tool\\n"
    "- Keep replies short and natural -- 1 to 4 sentences\\n"
    "- If user seems sad or stressed, focus on emotional support first\\n"
    "- Use the user name if you know it"
)
"""

(ROOT / "config.py").write_text(config, encoding="utf-8")
ok("config.py written")

# ── Final report ─────────────────────────────────────────────
header("SETUP COMPLETE -- Final Report")

total     = len(PACKAGES)
succeeded = total - len(failed) - len(skipped)

print(f"\n  Packages installed:  {GREEN}{succeeded}/{total}{RESET}")

if skipped:
    print(f"\n  {YELLOW}Skipped (will install later):{RESET}")
    for pkg, desc in skipped:
        print(f"    --  {pkg}  ({desc})")

if failed:
    print(f"\n  {YELLOW}Failed (need manual fix):{RESET}")
    for pkg, desc in failed:
        print(f"    XX  {pkg}  ({desc})")
    print(f"""
  {BOLD}Manual fix for pyaudio on Windows:{RESET}
  Download the correct .whl file from:
  https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

  Choose:  PyAudio-0.2.14-cp311-cp311-win_amd64.whl
  Then run:
  py -3.11 -m pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl
""")
else:
    print(f"\n  {GREEN}{BOLD}ALL PACKAGES INSTALLED SUCCESSFULLY!{RESET}")

print(f"""
{BOLD}{'='*50}
YOUR SARA FOLDER NOW LOOKS LIKE THIS:
{'='*50}{RESET}

  sara/
   |-- setup.py
   |-- config.py
   |-- .env
   |-- modules/
   |-- gui/
   |-- data/
        |-- users/
        |-- logs/
        |-- models/

{BOLD}{'='*50}
NEXT STEP:
{'='*50}{RESET}

  Tell me the setup is done and I will give
  you the next file:

  {GREEN}modules/net_monitor.py{RESET}
  -- detects internet connection
  -- switches SARA between online and offline

  One file at a time. You are doing great!
""")