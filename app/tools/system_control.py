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
    """Launches local system applications, web portals, or Windows UWP apps safely."""
    import re
    clean = app_name.lower().strip()
    
    # Reject dangerous characters in app_name upfront before any processing
    if not re.match(r"^[a-zA-Z0-9_\-\.\s:]+$", clean):
        return f"Launch request for '{app_name}' rejected due to invalid characters, Boss."

    # 1. Exact match in allowlist
    target_cmd = APP_MAP.get(clean)
    
    # 2. Substring matching in allowlist
    if not target_cmd:
        for key, cmd in APP_MAP.items():
            if key in clean:
                target_cmd = cmd
                break

    if target_cmd:
        try:
            if target_cmd.startswith("http://") or target_cmd.startswith("https://") or target_cmd.endswith(".exe"):
                os.startfile(target_cmd)
            else:
                subprocess.Popen(target_cmd.split(), shell=False)
            return f"Opening {app_name} for you now, Boss."
        except Exception:
            try:
                os.startfile(target_cmd)
                return f"Opening {app_name} for you now, Boss."
            except Exception as e:
                return f"Could not launch {app_name}: {str(e)}"

    try:
        os.startfile(clean)
        return f"Attempting to launch {app_name}, Boss."
    except Exception as e:
        return f"Could not find or launch {app_name}: {str(e)}"

def close_app(app_name: str) -> str:
    """Closes a running application by process name safely without shell injection risks."""
    import re
    clean = app_name.lower().strip()

    # Reject dangerous characters in app_name before any processing
    if not re.match(r"^[a-zA-Z0-9_\-\.\s]+$", clean):
        return f"Process termination rejected: '{app_name}' contains invalid characters, Boss."

    proc_name = None

    for key, proc in PROCESS_MAP.items():
        if key == clean:
            proc_name = proc
            break

    if not proc_name:
        for key, proc in PROCESS_MAP.items():
            if key in clean:
                proc_name = proc
                break

    if not proc_name:
        proc_name = clean if clean.endswith(".exe") else f"{clean}.exe"

    # Strictly validate proc_name (only letters, numbers, dot, dash, underscore)
    if not re.match(r"^[a-zA-Z0-9_\-\.]+\.exe$", proc_name):
        return f"Process termination rejected: '{app_name}' contains invalid characters."

    # Prevent killing critical system processes
    protected_processes = ["csrss.exe", "explorer.exe", "lsass.exe", "smss.exe", "services.exe", "winlogon.exe", "svchost.exe"]
    if proc_name.lower() in protected_processes:
        return f"Cannot terminate protected system process '{proc_name}', Boss."

    try:
        res = subprocess.run(["taskkill", "/f", "/im", proc_name], capture_output=True, text=True, check=False)
        if res.returncode == 0 or "SUCCESS" in res.stdout.upper():
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