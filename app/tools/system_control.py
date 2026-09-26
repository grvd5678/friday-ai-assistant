import os
import subprocess
import ctypes
import pyautogui

# Comprehensive Windows application & URI protocol registry
APP_MAP = {
    # Social & Messaging
    "whatsapp": 'start "" "whatsapp:"',
    "whatsapp desktop": 'start "" "whatsapp:"',
    "telegram": 'start "" "telegram:"',
    "discord": 'start "" "discord:"',
    
    # Music & Media
    "spotify": 'start "" "spotify:"',
    "youtube": 'start https://www.youtube.com',
    "netflix": 'start "" "netflix:"',
    
    # Browsers
    "chrome": 'start chrome',
    "google chrome": 'start chrome',
    "edge": 'start msedge',
    "microsoft edge": 'start msedge',
    "firefox": 'start firefox',
    "brave": 'start brave',
    
    # Developer & Productivity
    "code": 'code',
    "vscode": 'code',
    "vs code": 'code',
    "visual studio code": 'code',
    "notepad": 'notepad',
    "calculator": 'calc',
    "calc": 'calc',
    "paint": 'mspaint',
    "word": 'start winword',
    "excel": 'start excel',
    "powerpoint": 'start powerpnt',
    
    # Windows System Tools & Folders
    "explorer": 'explorer',
    "file explorer": 'explorer',
    "files": 'explorer',
    "downloads": 'explorer shell:Downloads',
    "documents": 'explorer shell:Personal',
    "desktop": 'explorer shell:Desktop',
    "settings": 'start ms-settings:',
    "task manager": 'taskmgr',
    "taskmgr": 'taskmgr',
    "camera": 'start microsoft.windows.camera:',
    "terminal": 'start wt',
    "cmd": 'start cmd',
    "command prompt": 'start cmd',
    "powershell": 'start powershell'
}

# Process mapping for closing apps
PROCESS_MAP = {
    "whatsapp": "WhatsApp.exe",
    "spotify": "Spotify.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "code": "Code.exe",
    "vscode": "Code.exe",
    "vs code": "Code.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "paint": "mspaint.exe",
    "task manager": "taskmgr.exe"
}

def open_app(app_name: str) -> str:
    """Launches local system applications, web portals, or Windows UWP apps."""
    clean = app_name.lower().strip()
    
    # 1. Exact match
    if clean in APP_MAP:
        os.system(APP_MAP[clean])
        return f"Opening {app_name} for you now, Boss."

    # 2. Substring matching
    for key, cmd in APP_MAP.items():
        if key in clean or clean in key:
            os.system(cmd)
            return f"Opening {key.title()} for you now, Boss."

    # 3. Fallback: Direct command launch
    try:
        subprocess.Popen(f'start "" "{clean}"', shell=True)
        return f"Attempting to launch {app_name}, Boss."
    except Exception as e:
        return f"Could not launch {app_name}: {str(e)}"

def close_app(app_name: str) -> str:
    """Closes a running application by name."""
    clean = app_name.lower().strip()
    proc_name = None

    for key, proc in PROCESS_MAP.items():
        if key in clean or clean in key:
            proc_name = proc
            break

    if not proc_name:
        proc_name = f"{clean}.exe"

    try:
        res = subprocess.run(f"taskkill /f /im {proc_name}", shell=True, capture_output=True, text=True)
        if "SUCCESS" in res.stdout.upper() or res.returncode == 0:
            return f"Closed {app_name} successfully, Boss."
        else:
            return f"Could not find or close {app_name}. It might not be running."
    except Exception as e:
        return f"Error closing {app_name}: {str(e)}"

def change_volume(action: str) -> str:
    """Controls master system volume. Action can be 'up', 'down', 'mute', or 'unmute'."""
    act = action.lower().strip()
    try:
        if "up" in act or "increase" in act:
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume increased, Boss."
        elif "down" in act or "decrease" in act or "lower" in act:
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume decreased, Boss."
        elif "mute" in act or "unmute" in act:
            pyautogui.press("volumemute")
            return "Volume toggled, Boss."
        else:
            return f"Unrecognized volume action '{action}'. Use up, down, or mute."
    except Exception as e:
        return f"Volume adjustment failed: {str(e)}"

def media_control(action: str) -> str:
    """Controls background media playback. Action can be 'play', 'pause', 'next', 'previous'."""
    act = action.lower().strip()
    try:
        if "next" in act:
            pyautogui.press("nexttrack")
            return "Skipped to the next track, Boss."
        elif "prev" in act or "back" in act:
            pyautogui.press("prevtrack")
            return "Playing previous track, Boss."
        elif "play" in act or "pause" in act or "stop" in act:
            pyautogui.press("playpause")
            return "Media playback toggled, Boss."
        else:
            return f"Unrecognized media action '{action}'."
    except Exception as e:
        return f"Media control error: {str(e)}"

def lock_screen() -> str:
    """Instantly locks the Windows workstation for security."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked successfully, Boss."
    except Exception as e:
        return f"Failed to lock workstation: {str(e)}"