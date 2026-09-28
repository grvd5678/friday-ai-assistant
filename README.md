# ⚡ F.R.I.D.A.Y. 3.0 — Holographic Tactical AI Desktop Assistant

An advanced, female-voiced personal desktop AI tactical assistant inspired by Marvel's **F.R.I.D.A.Y.**, featuring a futuristic 60-FPS holographic Arc-Reactor HUD, real-time voice conversations with an authentic Irish accent, autonomous Windows PC control, multimodal screen and camera vision, tactical work modes, and persistent long-term memory.

---

## 🔥 Features & Capabilities

### 🎙️ 1. Real-Time Voice Interaction & Persona
* **Authentic Irish Accent:** High-fidelity neural voice (`en-IE-EmilyNeural`) powered by Microsoft Edge Neural TTS with offline Windows SAPI fallback.
* **Lips-Sync Viseme Avatar:** 6-frame dynamic mouth aperture animation (`f0` through `f5`) reacting to speech cadence in real time.
* **Hands-Free Wake Word:** Smart background audio listener responding to *"Hey Friday"*, *"Hello Friday"*, or *"Hello"*, with automatic acoustic room calibration and self-trigger prevention.

### 🖥️ 2. Holographic Arc-Reactor HUD & Widget Mode
* **Sci-Fi Tactical Interface:** 60-FPS animated Arc-Reactor HUD with spinning concentric rings, glowing energy arcs, and audio waveforms.
* **Live System Telemetry:** Real-time stats for CPU %, RAM %, Battery %, Network I/O (KB/s), Uptime, and active Processes.
* **🪟 Compact Floating Widget:** One-click toggle between full 1080x720 tactical dashboard and an always-on-top, borderless 340x360 floating Arc-Reactor widget.

### 👁️ 3. Multimodal Vision Systems
* **Screen Vision & Code Q&A:** *"FRIDAY, look at my screen"* or *"What am I looking at?"* captures active desktop display and analyzes code, charts, UI elements, or error messages via Gemini 2.5 Flash.
* **Webcam Optical Vision & Gesture Recognition:** *"FRIDAY, can you see I'm waving hands?"* or *"Look at me"* takes a live snapshot from your laptop camera and factually describes physical actions, gestures, and attire without hallucinating.
* **Face Presence Arrival Detection:** Background optical monitor detecting when you sit down in front of your laptop and greeting you: *"Welcome back to your workstation, Boss."*

### ⚡ 4. Tactical Work Modes (One-Command Workflows)
* **Developer Mode:** *"FRIDAY, activate Developer Mode"* — Launches VS Code, Windows Terminal, starts a coding playlist on Spotify, and optimizes volume.
* **Movie Mode:** *"FRIDAY, activate Movie Mode"* — Closes distracting applications, lowers volume, and opens Netflix / YouTube.
* **Lockdown Mode:** *"FRIDAY, Protocol Lockdown"* — Closes sensitive applications (WhatsApp, Chrome) and locks the Windows workstation immediately.
* **Focus Mode:** *"FRIDAY, activate Focus Mode"* — Mutes notifications, plays ambient lo-fi, and sets up deep-work environment.

### ☀️ 5. Morning Tactical Briefing
* Say *"Morning briefing, Boss"* or *"Good morning"* for a smooth 30-second audio summary:
  * Current date & live time
  * Local temperature & weather conditions
  * Laptop battery health and charging state
  * Top world & technology news headlines via Google News RSS
  * Pending tasks and reminders saved in memory

### 📁 6. Smart File & Folder Management
* **Search:** *"FRIDAY, find all PDFs downloaded this week"*
* **Auto-Organize:** *"FRIDAY, clean up my Downloads folder"* (categorizes files automatically into Documents, Images, Videos, Music, Installers, and Archives).
* **Navigation:** *"FRIDAY, open my Downloads / Desktop / Documents folder"*

### 📄 7. Document & Multimodal File Analysis (PDF, Word, Images, Code)
* **📎 Native HUD Attachment & Drag-and-Drop:** Click the **📎** button or drag-and-drop any `.pdf`, `.docx`, `.png`, `.jpg`, `.txt`, `.py`, or `.csv` directly onto F.R.I.D.A.Y.'s HUD.
* **Deep Document Understanding:**
  * **PDFs:** Multimodal document ingestion and text parsing via `pypdf`.
  * **Word Documents:** Paragraph and table extraction via `python-docx`.
  * **Images & Diagrams:** High-resolution visual understanding via Gemini 2.5 Flash Vision.
  * **Code & Data:** Text, CSV, JSON, and source code inspection.
* **Commands:** *"Summarize this document"*, *"What does this contract say?"*, *"Extract key points from this PDF"*, *"Explain what is shown in this PNG"*.

### 📸 8. Integrated Screenshots & Windows Pictures Library
* Automatically saves high-resolution timestamped screenshots directly to your Windows Pictures directory:
  `OneDrive\Pictures\Screenshots 1` (with duplicate local backup in `screenshots/`).
* Instant folder access: *"FRIDAY, open screenshots folder"* or *"Where did you save the screenshot?"*

### 🧠 9. Hybrid AI Brain & Memory
* **Primary:** Google Gemini 3.5 Flash / Flash Lite with autonomous function calling.
* **Local Fallback:** Local Ollama (`llama3`) for offline privacy and resilience.
* **Offline Rule Engine:** Instant deterministic fallback for core system controls.
* **Persistent Memory:** Saves, recalls, and updates facts, habits, and preferences across reboots in `friday_memory.json`.

---

## 📁 Project Architecture

```
friday-ai-assistant/
│
├── app/
│   ├── audio/
│   │   ├── listener.py        # Dynamic microphone audio capture & Google STT
│   │   ├── speaker.py         # Neural Edge-TTS (en-IE-EmilyNeural) & viseme bridge
│   │   ├── wakeword.py        # Background wake word listener ("Hey FRIDAY", "Hello")
│   │   └── live_stream.py     # Gemini Live WebSockets streaming engine
│   │
│   ├── brain/
│   │   ├── llm.py             # Brain orchestrator: Gemini + Function Calling + Ollama
│   │   ├── prompts.py         # Irish tactical assistant system instructions
│   │   └── memory.py          # Persistent JSON facts and chat history store
│   │
│   ├── tools/
│   │   ├── briefing_tool.py   # Morning tactical briefing generator
│   │   ├── file_tool.py       # File search and folder cleanup
│   │   ├── modes.py           # Tactical work modes (Dev, Movie, Lockdown, Focus)
│   │   ├── screenshot_tool.py # OneDrive Screenshots integration
│   │   ├── sys_info.py        # CPU, RAM, Disk, and Battery diagnostics
│   │   ├── system_control.py  # App launcher/closer, volume, screen lock
│   │   ├── vision_tool.py     # Multimodal Screen Vision & Laptop Webcam Vision
│   │   ├── web_search.py      # Google search, Wikipedia, YouTube, Weather
│   │   └── whatsapp_tool.py   # WhatsApp automated messaging
│   │
│   ├── ui/
│   │   ├── index.html         # Futuristic HUD layout and widget structure
│   │   ├── style.css          # Holographic sci-fi animations & theme
│   │   ├── hud.js             # 6-frame Viseme lip-sync engine & telemetry
│   │   └── hud_app.py         # PyWebView desktop window manager
│   │
│   └── vision/
│       └── face_presence.py   # OpenCV optical presence arrival detector
│
├── main.py                    # Unified application entry point (HUD / CLI)
├── create_desktop_shortcut.py # Standalone desktop icon installer (Ctrl+Alt+F)
├── check_models.py            # API key & Gemini model connection diagnostic
├── test_mic_audio.py          # Microphone energy and device index tester
├── .env.example               # Safe environment configuration template
├── friday_memory.example.json # Safe memory schema template
├── requirements.txt           # Python dependencies
└── run_friday.bat             # One-click launcher script
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
* Windows 10 or 11
* Python 3.10+ (Recommended: Python 3.12)
* Built-in or external Microphone, Speakers, and Webcam

### 2. Setup Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file from the provided template:
```powershell
copy .env.example .env
```
Open `.env` and insert your **Google Gemini API Key** (obtainable free from [Google AI Studio](https://aistudio.google.com)):
```env
GEMINI_API_KEY=your_gemini_api_key_here
BOT_NAME=FRIDAY
FRIDAY_VOICE=en-IE-EmilyNeural
GEMINI_MODEL=gemini-3.5-flash-lite
OLLAMA_MODEL=llama3
MEMORY_FILE=friday_memory.json
MIC_INDEX=
MIC_THRESHOLD=35
```

---

## 🎯 Launching F.R.I.D.A.Y.

### Option A: Desktop Shortcut (Silent One-Click)
Run the shortcut creator once:
```powershell
.\venv\Scripts\python.exe create_desktop_shortcut.py
```
This places a **`F.R.I.D.A.Y.`** shortcut on your Desktop with an Arc-Reactor icon and hotkey <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>F</kbd>. Double-clicking it launches the HUD silently with zero console windows.

### Option B: Terminal Launch
```powershell
# Holographic HUD Mode
.\venv\Scripts\python.exe main.py

# Interactive Terminal CLI Mode
.\venv\Scripts\python.exe main.py --cli
```

---

## 💬 Command Reference

| Category | Example Voice & Text Commands |
| :--- | :--- |
| **Wake & Greeting** | *"Hey Friday"*, *"Hello Friday"*, *"Hello"* |
| **Screen Vision** | *"Look at my screen"*, *"What am I looking at?"*, *"Explain this error on screen"* |
| **Webcam Vision** | *"Can you see I'm waving hands?"*, *"Look at me"*, *"What am I doing?"* |
| **Morning Briefing**| *"Morning briefing, Boss"*, *"Brief me"* |
| **Work Modes** | *"Activate Developer Mode"*, *"Movie Mode"*, *"Protocol Lockdown"*, *"Focus Mode"* |
| **File Management** | *"Find all PDFs"*, *"Organize my Downloads folder"*, *"Open Downloads folder"* |
| **Screenshots** | *"Take a screenshot"*, *"Open screenshots folder"*, *"Where is the screenshot?"* |
| **Hardware Stats** | *"Check system stats"*, *"What is my battery level?"*, *"Hardware diagnostic"* |
| **App Management** | *"Open VS Code"*, *"Launch Spotify"*, *"Close Chrome"*, *"Open WhatsApp"* |
| **Media & Volume** | *"Increase volume"*, *"Mute volume"*, *"Next track"*, *"Play Interstellar on YouTube"* |
| **Security** | *"Lock my PC"*, *"Lock workstation"* |
| **Information** | *"What's the weather in Tokyo?"*, *"Who was Alan Turing?"*, *"Search Google for quantum AI"* |
| **Memory** | *"Remember that my meeting is at 4 PM"*, *"What do you remember?"*, *"Forget my meeting"* |
| **HUD Controls** | *"Toggle widget mode"*, *"Expand HUD"*, *"Full dashboard"* |

---

## 🔒 Security & Privacy Notes

* **API Keys:** Never commit your `.env` file to version control. The `.gitignore` is pre-configured to exclude `.env` and `friday_memory.json`.
* **Hardware Access:** Webcam and microphone access are initiated only during active commands or configured background monitors and are kept strictly local.
