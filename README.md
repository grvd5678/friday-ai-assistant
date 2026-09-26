# ⚡ F.R.I.D.A.Y. 3.0 — Holographic Tactical AI Desktop Assistant

An advanced, female-voiced personal desktop AI tactical assistant inspired by Marvel's **F.R.I.D.A.Y.**, featuring a futuristic 60-FPS holographic Arc-Reactor HUD, real-time voice conversations, autonomous Windows PC control, background wake-word activation, and persistent long-term memory.

---

## 🔥 Features

* 🎙️ **Real-Time Voice Interaction:** High-fidelity female neural voice (`en-IE-EmilyNeural`) powered by Microsoft Edge Neural TTS with offline Windows SAPI fallback + Google Speech recognition.
* 🖥️ **Sci-Fi Holographic HUD:** 60-FPS animated Arc-Reactor HUD with spinning concentric rings, live telemetry dashboard (CPU %, RAM %, Battery %, Network KB/s, Uptime, Processes), real-time speech subtitles, quick tactical chips, and equalizer waveforms.
* 👂 **Hands-Free Wake Word:** Smart background audio listener triggering automatically on *"Hey Friday"* or *"Friday"*, with automatic self-trigger protection while FRIDAY is speaking.
* 🧠 **Hybrid AI Brain & Tool Execution:**
  * **Primary:** Google Gemini 3.5 Flash / Flash Lite with autonomous tool calling.
  * **Fallback:** Local Ollama (`llama3`) for offline privacy and resilience.
  * **Offline Rule Engine:** Instant offline local response handler for hardware, apps, and controls.
* 💾 **Persistent Long-Term Memory:** Remembers, recalls, and forgets facts, schedule, and preferences across restarts in `friday_memory.json`.
* ⚡ **Autonomous Desktop Tools:**
  * **App Control:** Launch and close apps (WhatsApp, Spotify, Chrome, Edge, VS Code, Notepad, Calculator, File Explorer, Terminal, etc.)
  * **Media & Audio:** Control master volume (mute, unmute, volume up/down) and media tracks (play/pause, next track, previous track).
  * **Hardware Diagnostics:** Live CPU usage, RAM utilization in GB, C: drive disk space, and battery charging state.
  * **Security:** Instantly lock workstation on voice command (`"Lock my PC"`).
  * **Web & Knowledge:** Live weather lookup, Wikipedia summaries, Google search, and YouTube playback.
  * **Productivity:** Timestamped screenshot capture and automated WhatsApp messaging.

---

## 🚀 Getting Started

### 1. Prerequisites
* Windows 10/11
* Python 3.12+
* Working Microphone and Speakers

### 2. Quick Setup

1. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Configure your `.env` file:**
   Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   BOT_NAME=FRIDAY
   FRIDAY_VOICE=en-IE-EmilyNeural
   GEMINI_MODEL=gemini-3.5-flash-lite
   OLLAMA_MODEL=llama3
   MEMORY_FILE=friday_memory.json
   ```

3. **Verify Models & Microphone:**
   ```powershell
   python check_models.py
   python test_mic_audio.py
   ```

---

## 🎯 Launching FRIDAY

### 1. Holographic HUD Mode (Recommended):
Run using the virtual environment's Python directly:
```powershell
.\venv\Scripts\python.exe main.py
```
*Or simply double-click **`run_friday.bat`**.*

### 2. Interactive Terminal / CLI Mode:
```powershell
.\venv\Scripts\python.exe main.py --cli
```
*Or double-click **`run_cli.bat`**.*

### 3. Diagnostics:
```powershell
.\venv\Scripts\python.exe check_models.py
.\venv\Scripts\python.exe test_mic_audio.py
```

---

## 💬 Voice & Command Examples

| Category | Example Phrases |
| :--- | :--- |
| **Wake Word** | *"Hey Friday"* or *"Friday"* |
| **Hardware Diagnostics** | *"Check my system stats"*, *"What is my battery level?"* |
| **Date & Time** | *"What time is it?"*, *"What's today's date?"* |
| **App Launching** | *"Open WhatsApp"*, *"Launch Spotify"*, *"Open VS Code"*, *"Open Calculator"* |
| **App Closing** | *"Close Chrome"*, *"Close Spotify"* |
| **Volume & Media** | *"Increase volume"*, *"Mute volume"*, *"Next track"*, *"Pause music"* |
| **Workstation Security** | *"Lock my screen"*, *"Lock workstation"* |
| **Web & Knowledge** | *"What's the weather in New York?"*, *"Who was Alan Turing?"*, *"Search Google for quantum computing"* |
| **YouTube** | *"Play interstellar soundtrack on YouTube"* |
| **Screenshots** | *"Take a screenshot"* (saved to `screenshots/`) |
| **Memory** | *"Remember that my meeting is at 4 PM"*, *"What do you remember?"*, *"Forget my meeting"* |
