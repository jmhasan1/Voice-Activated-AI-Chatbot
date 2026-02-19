# Voice-Activated AI Chatbot

A fully-featured, voice-controlled personal assistant built with Python.  
Supports speech recognition, text-to-speech, Wikipedia lookups, web browsing, system automation, notes, to-do lists, and more.

---

## Project Structure

```
voice_chatbot/
├── main.py              ← Main application (all logic lives here)
├── requirements.txt     ← Python dependencies
├── README.md            ← This file
└── data/                ← Auto-created at runtime
    ├── config.json      ← User preferences (name, voice speed, etc.)
    ├── notes.txt        ← Voice-dictated notes
    └── todo.json        ← To-do list items
```

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.8+** — [Download here](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Internet connection** (for Google Speech API & Wikipedia)
- **Microphone** (built-in or USB)

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### PyAudio Installation Notes

PyAudio requires system audio libraries. If `pip install pyaudio` fails:

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu / Debian:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

---

## ▶️ Running the Chatbot

### Voice Mode (default)
```bash
python main.py
```

### Text Mode (no microphone needed)
```bash
python main.py --text
```

---

## 🗣️ Commands Reference

| Category       | What to Say                                                  |
|----------------|--------------------------------------------------------------|
| **Time/Date**  | "What time is it?" · "What's today's date?"                  |
| **Web Browse** | "Open Google" · "Open YouTube" · "Open GitHub"               |
| **Search**     | "Search for Python tutorials" · "Google for weather today"   |
| **YouTube**    | "Play lo-fi music on YouTube" · "YouTube dark mode tutorial" |
| **Wikipedia**  | "Wikipedia Albert Einstein" · "Who is Nikola Tesla?"         |
| **Notes**      | "Write a note: buy milk" · "Read my notes"                   |
| **To-Do**      | "Add task finish homework" · "Read my tasks" · "Complete task"|
| **System**     | "Shutdown" · "Restart" · "Lock screen"                       |
| **Volume**     | "Volume up" · "Volume down"                                  |
| **Apps**       | "Open calculator" · "Open notepad"                           |
| **Fun**        | "Tell me a joke" · "How are you?"                            |
| **Settings**   | "Change your name" · "Change my name"                        |
| **Help**       | "Help" · "What can you do?"                                  |
| **Exit**       | "Exit" · "Goodbye" · "Quit"                                  |

---

## ⚙️ Configuration (`data/config.json`)

The file is auto-generated on first run. You can edit it manually:

```json
{
    "assistant_name": "Aria",
    "user_name": "User",
    "voice_rate": 175,
    "voice_volume": 1.0,
    "language": "en-US",
    "pause_threshold": 0.8,
    "energy_threshold": 300,
    "dynamic_energy": true,
    "timeout": 5,
    "phrase_time_limit": 10
}
```

| Key                | Description                                              |
|--------------------|----------------------------------------------------------|
| `assistant_name`   | What the bot calls itself                                |
| `user_name`        | What the bot calls you                                   |
| `voice_rate`       | Speech speed (words per minute, default 175)             |
| `voice_volume`     | Volume 0.0–1.0                                           |
| `language`         | Recognition language code (e.g., `en-US`, `en-IN`)      |
| `pause_threshold`  | Seconds of silence before speech ends (lower = snappier) |
| `energy_threshold` | Mic sensitivity (raise if too much background noise)     |
| `dynamic_energy`   | Auto-adjust for ambient noise                            |
| `timeout`          | Seconds to wait for speech to start                      |
| `phrase_time_limit`| Max seconds per spoken command                           |

---

## 🛠️ How It Works

```
Microphone Input
      │
      ▼
speech_recognition (Google Web Speech API)
      │  Converts audio → text
      ▼
dispatch() — keyword matching via COMMAND_TABLE
      │  Routes to correct handler function
      ▼
Handler (e.g., cmd_wikipedia, cmd_open_site, cmd_write_note)
      │  Performs the action
      ▼
pyttsx3 — speak() converts response text → audio
      │
      ▼
Speaker Output
```

---

## 🔧 Adding Custom Commands

1. Define your handler function in `main.py`:

```python
def cmd_my_command(query: str) -> None:
    speak("You triggered my custom command!")
```

2. Register it in `COMMAND_TABLE`:

```python
(["my trigger phrase", "alternate phrase"], cmd_my_command),
```

That's it! The dispatcher will automatically pick it up.

---

## 🧩 Troubleshooting

| Problem | Solution |
|---|---|
| "No module named pyaudio" | See PyAudio installation notes above |
| Bot doesn't hear anything | Check mic permissions & `energy_threshold` in config |
| Bot mishears commands | Speak clearly, or lower `pause_threshold` in config |
| Wikipedia errors | Check internet connection |
| Text-mode import errors | Run `python main.py --text` to skip audio entirely |

---

## 📦 Dependencies Summary

| Library           | Purpose                          | Install         |
|-------------------|----------------------------------|-----------------|
| SpeechRecognition | Audio → text conversion          | pip             |
| pyttsx3           | Text → speech (offline)          | pip             |
| pyaudio           | Microphone interface             | pip + OS libs   |
| wikipedia         | Wikipedia article summaries      | pip             |

All other modules (`datetime`, `os`, `webbrowser`, `json`, etc.) are Python standard library — no install needed.

---

## Optional Enhancements

- **OpenAI / Gemini integration** — replace the fallback response with an LLM for open-ended Q&A
- **Hotword detection** — use `pvporcupine` to activate on "Hey Aria" without pressing a button
- **GUI** — wrap with `tkinter` or `PyQt` for a visual interface
- **Reminders / Alarms** — add time-based triggers using `schedule` library
- **Email** — integrate `smtplib` to send emails by voice

---

*Built with ❤️ using Python 3.8+*
