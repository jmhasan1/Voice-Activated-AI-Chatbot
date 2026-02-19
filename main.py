"""
Voice-Activated AI Chatbot
==========================
A fully-featured voice assistant built with Python.
Uses speech_recognition, pyttsx3, Wikipedia API, and more.
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sys
import time
import subprocess
import wikipedia
import json
import re
import threading
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
CONFIG_FILE = Path(__file__).parent / "data" / "config.json"
NOTES_FILE  = Path(__file__).parent / "data" / "notes.txt"
TODO_FILE   = Path(__file__).parent / "data" / "todo.json"

DEFAULT_CONFIG = {
    "assistant_name": "Aria",
    "user_name": "User",
    "voice_rate": 175,
    "voice_volume": 1.0,
    "language": "en-US",
    "pause_threshold": 0.8,
    "energy_threshold": 300,
    "dynamic_energy": True,
    "timeout": 5,
    "phrase_time_limit": 10
}


# ──────────────────────────────────────────────
# INITIALISATION
# ──────────────────────────────────────────────
def load_config() -> dict:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        # Fill in any missing keys from defaults
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    return DEFAULT_CONFIG.copy()


CONFIG = load_config()

# Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate",   CONFIG["voice_rate"])
engine.setProperty("volume", CONFIG["voice_volume"])

# Choose a voice (prefer a female voice if available)
voices = engine.getProperty("voices")
for v in voices:
    if "female" in v.name.lower() or "zira" in v.name.lower() or "samantha" in v.name.lower():
        engine.setProperty("voice", v.id)
        break

# Speech recogniser
recogniser = sr.Recognizer()
recogniser.pause_threshold   = CONFIG["pause_threshold"]
recogniser.energy_threshold  = CONFIG["energy_threshold"]
recogniser.dynamic_energy_threshold = CONFIG["dynamic_energy"]


# ──────────────────────────────────────────────
# CORE I/O
# ──────────────────────────────────────────────
def speak(text: str) -> None:
    """Convert text to audible speech and print it."""
    print(f"\n🤖 {CONFIG['assistant_name']}: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(prompt: str = "") -> str:
    """
    Capture microphone input and return the recognised text.
    Returns an empty string on failure.
    """
    if prompt:
        speak(prompt)

    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recogniser.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recogniser.listen(
                source,
                timeout=CONFIG["timeout"],
                phrase_time_limit=CONFIG["phrase_time_limit"]
            )
        except sr.WaitTimeoutError:
            print("⚠️  No speech detected (timeout).")
            return ""

    try:
        query = recogniser.recognize_google(audio, language=CONFIG["language"])
        print(f"👤 {CONFIG['user_name']}: {query}")
        return query.lower().strip()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat?")
        return ""
    except sr.RequestError as e:
        speak("I'm having trouble reaching the speech service. Please check your internet.")
        print(f"   [RequestError] {e}")
        return ""


def take_text_input(prompt: str = "Type your command: ") -> str:
    """Fallback: get command from keyboard."""
    return input(f"\n⌨️  {prompt}").lower().strip()


# ──────────────────────────────────────────────
# GREETINGS
# ──────────────────────────────────────────────
def wish_me() -> None:
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Hello"

    speak(
        f"{greeting}, {CONFIG['user_name']}! I'm {CONFIG['assistant_name']}, your voice assistant. "
        "How can I help you today? Say 'help' for a list of commands."
    )


# ──────────────────────────────────────────────
# COMMAND HANDLERS
# ──────────────────────────────────────────────

# --- Time & Date ---
def cmd_time(_: str) -> None:
    t = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The current time is {t}.")


def cmd_date(_: str) -> None:
    d = datetime.datetime.now().strftime("%A, %B %d, %Y")
    speak(f"Today is {d}.")


# --- Web Browsing ---
SITES = {
    "google":   "https://www.google.com",
    "youtube":  "https://www.youtube.com",
    "github":   "https://www.github.com",
    "gmail":    "https://mail.google.com",
    "maps":     "https://maps.google.com",
    "linkedin": "https://www.linkedin.com",
    "twitter":  "https://www.twitter.com",
    "reddit":   "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
}

def cmd_open_site(query: str) -> None:
    for site, url in SITES.items():
        if site in query:
            speak(f"Opening {site}.")
            webbrowser.open(url)
            return
    speak("Which website would you like me to open?")


def cmd_search_google(query: str) -> None:
    # Extract search term after "search" / "google"
    term = re.sub(r"(search|google|for|on)", "", query).strip()
    if not term:
        term = listen("What would you like me to search for?")
    if term:
        speak(f"Searching Google for: {term}")
        webbrowser.open(f"https://www.google.com/search?q={term.replace(' ', '+')}")


def cmd_search_youtube(query: str) -> None:
    term = re.sub(r"(youtube|search|play|video|for)", "", query).strip()
    if not term:
        term = listen("What would you like to search on YouTube?")
    if term:
        speak(f"Searching YouTube for: {term}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={term.replace(' ', '+')}")


# --- Wikipedia ---
def cmd_wikipedia(query: str) -> None:
    topic = re.sub(r"(wikipedia|wiki|who is|what is|tell me about|search)", "", query).strip()
    if not topic:
        topic = listen("What topic would you like me to look up on Wikipedia?")
    if not topic:
        return
    speak(f"Searching Wikipedia for: {topic}")
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(topic, sentences=3, auto_suggest=True)
        speak(summary)
    except wikipedia.DisambiguationError as e:
        options = e.options[:4]
        speak(f"There are multiple results. Did you mean: {', '.join(options)}?")
    except wikipedia.PageError:
        speak("I couldn't find a Wikipedia page for that topic.")
    except Exception as e:
        speak("Something went wrong while fetching Wikipedia.")
        print(f"   [WikiError] {e}")


# --- Notes ---
def cmd_write_note(query: str) -> None:
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    note = re.sub(r"(write|take|make|a|note|saying|that)", "", query).strip()
    if not note:
        note = listen("What would you like to note down?")
    if note:
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M]")
        with open(NOTES_FILE, "a") as f:
            f.write(f"{timestamp} {note}\n")
        speak("Note saved!")


def cmd_read_notes(_: str) -> None:
    if not NOTES_FILE.exists() or NOTES_FILE.stat().st_size == 0:
        speak("You have no notes saved.")
        return
    with open(NOTES_FILE) as f:
        notes = f.readlines()
    speak(f"You have {len(notes)} note(s).")
    for i, note in enumerate(notes[-5:], 1):   # read last 5
        speak(f"Note {i}: {note.strip()}")


# --- To-Do List ---
def _load_todos() -> list:
    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    if TODO_FILE.exists():
        with open(TODO_FILE) as f:
            return json.load(f)
    return []


def _save_todos(todos: list) -> None:
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def cmd_add_todo(query: str) -> None:
    task = re.sub(r"(add|to do|todo|task|reminder|remind me to)", "", query).strip()
    if not task:
        task = listen("What task would you like to add?")
    if task:
        todos = _load_todos()
        todos.append({"task": task, "done": False, "added": str(datetime.datetime.now())})
        _save_todos(todos)
        speak(f"Added to your to-do list: {task}")


def cmd_read_todos(_: str) -> None:
    todos = _load_todos()
    pending = [t for t in todos if not t["done"]]
    if not pending:
        speak("Your to-do list is empty.")
        return
    speak(f"You have {len(pending)} pending task(s).")
    for i, t in enumerate(pending, 1):
        speak(f"{i}. {t['task']}")


def cmd_complete_todo(_: str) -> None:
    todos = _load_todos()
    pending = [t for t in todos if not t["done"]]
    if not pending:
        speak("No pending tasks.")
        return
    cmd_read_todos("")
    response = listen("Which task number did you complete?")
    try:
        num = int(re.search(r"\d+", response).group()) - 1
        todos[num]["done"] = True
        _save_todos(todos)
        speak(f"Great job! Marked '{pending[num]['task']}' as done.")
    except (AttributeError, IndexError, ValueError):
        speak("I couldn't identify that task number.")


# --- System Commands ---
def cmd_shutdown(_: str) -> None:
    confirm = listen("Are you sure you want to shut down?")
    if "yes" in confirm:
        speak("Shutting down. Goodbye!")
        if sys.platform == "win32":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")
    else:
        speak("Shutdown cancelled.")


def cmd_restart(_: str) -> None:
    confirm = listen("Are you sure you want to restart?")
    if "yes" in confirm:
        speak("Restarting. See you soon!")
        if sys.platform == "win32":
            os.system("shutdown /r /t 5")
        else:
            os.system("shutdown -r now")
    else:
        speak("Restart cancelled.")


def cmd_lock(_: str) -> None:
    speak("Locking the screen.")
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.LockWorkStation()
    elif sys.platform == "darwin":
        os.system("pmset displaysleepnow")
    else:
        os.system("gnome-screensaver-command -l 2>/dev/null || xdg-screensaver lock")


def cmd_volume_up(_: str) -> None:
    if sys.platform == "win32":
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
    else:
        os.system("amixer -D pulse sset Master 10%+ 2>/dev/null")
    speak("Volume increased.")


def cmd_volume_down(_: str) -> None:
    if sys.platform == "win32":
        speak("Volume down not supported without pycaw on Windows. Please adjust manually.")
    else:
        os.system("amixer -D pulse sset Master 10%- 2>/dev/null")
    speak("Volume decreased.")


# --- App Launchers ---
APP_COMMANDS = {
    "calculator": ("calc" if sys.platform == "win32" else "gnome-calculator"),
    "notepad":    ("notepad" if sys.platform == "win32" else "gedit"),
    "paint":      ("mspaint" if sys.platform == "win32" else "kolourpaint"),
    "file manager": ("explorer" if sys.platform == "win32" else "nautilus"),
}

def cmd_open_app(query: str) -> None:
    for app, cmd in APP_COMMANDS.items():
        if app in query:
            speak(f"Opening {app}.")
            subprocess.Popen(cmd, shell=True)
            return
    speak("I don't know how to open that application.")


# --- Jokes ---
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer go to the doctor? Because it had a virus!",
    "How many programmers does it take to change a lightbulb? None — that's a hardware problem.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why is Python so popular? Because it never lets whitespace go unnoticed.",
]

def cmd_joke(_: str) -> None:
    import random
    speak(random.choice(JOKES))


# --- Small Talk ---
def cmd_how_are_you(_: str) -> None:
    speak(f"I'm doing great, thank you for asking! Ready to help you, {CONFIG['user_name']}.")


def cmd_name(_: str) -> None:
    speak(f"My name is {CONFIG['assistant_name']}. I'm your personal voice assistant!")


def cmd_creator(_: str) -> None:
    speak("I was built by a Python developer using speech recognition, NLP, and automation tools.")


# --- Help ---
HELP_TEXT = """
Here are some things I can do:
Time and Date: 'what time is it', 'what's today's date'
Web: 'open Google', 'search for Python tutorials', 'play music on YouTube'
Knowledge: 'wikipedia Albert Einstein', 'who is Elon Musk'
Notes: 'write a note', 'read my notes'
To-Do: 'add task buy groceries', 'read my tasks', 'complete task'
System: 'shutdown', 'restart', 'lock screen', 'volume up', 'volume down'
Apps: 'open calculator', 'open notepad'
Fun: 'tell me a joke', 'how are you'
Settings: 'change name', 'change my name'
Exit: 'exit', 'quit', 'goodbye'
"""

def cmd_help(_: str) -> None:
    print(HELP_TEXT)
    speak("I've printed the full command list on the screen for you.")


# --- Settings ---
def cmd_change_assistant_name(_: str) -> None:
    new_name = listen("What would you like to call me?")
    if new_name:
        CONFIG["assistant_name"] = new_name.title()
        with open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG, f, indent=4)
        speak(f"Okay! You can now call me {CONFIG['assistant_name']}.")


def cmd_change_user_name(_: str) -> None:
    new_name = listen("What's your name?")
    if new_name:
        CONFIG["user_name"] = new_name.title()
        with open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG, f, indent=4)
        speak(f"Got it! I'll call you {CONFIG['user_name']} from now on.")


# ──────────────────────────────────────────────
# COMMAND ROUTING TABLE
# Each entry: (keywords_list, handler_function)
# ──────────────────────────────────────────────
COMMAND_TABLE = [
    # Time / Date
    (["what time",  "current time", "time is it"],         cmd_time),
    (["what date",  "today's date", "what day"],            cmd_date),

    # Web
    (["open google", "open youtube", "open github",
      "open gmail",  "open maps",    "open reddit",
      "open twitter", "open linkedin", "open stackoverflow"],cmd_open_site),
    (["search for", "google for", "search google"],         cmd_search_google),
    (["youtube",    "play on youtube", "search youtube"],   cmd_search_youtube),

    # Knowledge
    (["wikipedia",  "wiki", "who is", "tell me about",
      "what is",    "explain"],                             cmd_wikipedia),

    # Notes
    (["write a note", "take a note", "make a note",
      "note that",    "note down"],                         cmd_write_note),
    (["read my notes", "show notes", "my notes"],           cmd_read_notes),

    # To-Do
    (["add task", "add to do", "remind me",
      "add reminder", "new task"],                          cmd_add_todo),
    (["read my tasks", "my tasks", "show tasks",
      "to do list",    "todo list"],                        cmd_read_todos),
    (["complete task", "mark done", "finished task"],       cmd_complete_todo),

    # System
    (["shut down", "shutdown", "power off"],                cmd_shutdown),
    (["restart",   "reboot"],                               cmd_restart),
    (["lock screen", "lock computer", "lock the screen"],   cmd_lock),
    (["volume up",  "increase volume", "louder"],           cmd_volume_up),
    (["volume down","decrease volume", "quieter"],          cmd_volume_down),

    # Apps
    (["open calculator", "open notepad", "open paint",
      "open file manager"],                                 cmd_open_app),

    # Fun / Small talk
    (["tell me a joke", "joke", "make me laugh"],           cmd_joke),
    (["how are you",   "how do you do"],                    cmd_how_are_you),
    (["your name",     "who are you", "what are you called"], cmd_name),
    (["who made you",  "who created you", "your creator"],  cmd_creator),

    # Settings
    (["change your name", "rename yourself"],               cmd_change_assistant_name),
    (["change my name",   "my name is"],                    cmd_change_user_name),

    # Help
    (["help", "what can you do", "commands", "features"],   cmd_help),
]

EXIT_KEYWORDS = ["exit", "quit", "goodbye", "bye", "stop", "shut up"]


# ──────────────────────────────────────────────
# COMMAND DISPATCHER
# ──────────────────────────────────────────────
def dispatch(query: str) -> bool:
    """
    Match a query to a handler and run it.
    Returns False if the user wants to exit.
    """
    if not query:
        return True

    # Exit check
    if any(kw in query for kw in EXIT_KEYWORDS):
        speak(f"Goodbye, {CONFIG['user_name']}! Have a wonderful day.")
        return False

    # Find matching command
    for keywords, handler in COMMAND_TABLE:
        if any(kw in query for kw in keywords):
            try:
                handler(query)
            except Exception as e:
                speak("Sorry, something went wrong with that command.")
                print(f"   [Error] {e}")
            return True

    # Fallback — try Wikipedia for unknown queries
    if len(query.split()) >= 3:
        speak(f"I'm not sure about that, but let me check Wikipedia.")
        cmd_wikipedia(query)
    else:
        speak("I didn't understand that command. Try saying 'help' to see what I can do.")

    return True


# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────
def run(use_voice: bool = True) -> None:
    """Main event loop."""
    wish_me()

    while True:
        query = listen() if use_voice else take_text_input()
        if not dispatch(query):
            break


if __name__ == "__main__":
    # Pass --text flag to use keyboard input (useful on systems without a mic)
    use_voice = "--text" not in sys.argv
    run(use_voice=use_voice)
