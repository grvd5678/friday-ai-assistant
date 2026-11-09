import os
import subprocess
import ctypes
import pyautogui

import webbrowser

# Comprehensive Windows application, URL & URI protocol registry
APP_MAP = {
    # Social & Messaging
    "whatsapp": ("uri", "whatsapp:"),
    "whatsapp desktop": ("uri", "whatsapp:"),
    "telegram": ("uri", "telegram:"),
    "discord": ("uri", "discord:"),
    
    # Music & Media
    "spotify": ("uri", "spotify:"),
    "youtube": ("url", "https://www.youtube.com"),
    "netflix": ("url", "https://www.netflix.com"),
    
    # Browsers
    "chrome": ("cmd", "chrome"),
    "google chrome": ("cmd", "chrome"),
    "edge": ("cmd", "msedge"),
    "microsoft edge": ("cmd", "msedge"),
    "firefox": ("cmd", "firefox"),
    "brave": ("cmd", "brave"),
    
    # Developer & Productivity
    "code": ("cmd", "code"),
    "vscode": ("cmd", "code"),
    "vs code": ("cmd", "code"),
    "visual studio code": ("cmd", "code"),
    "notepad": ("cmd", "notepad"),
    "calculator": ("cmd", "calc"),
    "calc": ("cmd", "calc"),
    "paint": ("cmd", "mspaint"),
    "word": ("cmd", "winword"),
    "excel": ("cmd", "excel"),
    "powerpoint": ("cmd", "powerpnt"),
    "wispr flow": ("exe", os.path.join(os.environ.get("LOCALAPPDATA", ""), "WisprFlow", "Wispr Flow.exe")),
    "wispr": ("exe", os.path.join(os.environ.get("LOCALAPPDATA", ""), "WisprFlow", "Wispr Flow.exe")),
    "flow": ("exe", os.path.join(os.environ.get("LOCALAPPDATA", ""), "WisprFlow", "Wispr Flow.exe")),
    
    # Windows System Tools & Folders
    "explorer": ("cmd", "explorer"),
    "file explorer": ("cmd", "explorer"),
    "files": ("cmd", "explorer"),
    "downloads": ("folder", "shell:Downloads"),
    "documents": ("folder", "shell:Personal"),
    "desktop": ("folder", "shell:Desktop"),
    "settings": ("uri", "ms-settings:"),
    "task manager": ("cmd", "taskmgr"),
    "taskmgr": ("cmd", "taskmgr"),
    "camera": ("uri", "microsoft.windows.camera:"),
    "terminal": ("cmd", "wt"),
    "cmd": ("cmd", "cmd"),
    "command prompt": ("cmd", "cmd"),
    "powershell": ("cmd", "powershell")
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
    "task manager": "taskmgr.exe",
    "wispr flow": "Wispr Flow.exe",
    "wispr": "Wispr Flow.exe",
    "flow": "Wispr Flow.exe"
}

def open_app(app_name: str) -> str:
    """Launches local system applications, web portals, or Windows UWP apps safely."""
    import re
    clean = app_name.lower().strip()
    
    # Reject dangerous characters in app_name upfront before any processing
    if not re.match(r"^[a-zA-Z0-9_\-\.\s:]+$", clean):
        return f"Launch request for '{app_name}' rejected due to invalid characters, Boss."

    # 1. Exact match in allowlist
    target_entry = APP_MAP.get(clean)
    
    # 2. Substring matching in allowlist
    if not target_entry:
        for key, entry in APP_MAP.items():
            if key in clean:
                target_entry = entry
                break

    if target_entry:
        kind, target = target_entry
        try:
            if kind == "url":
                webbrowser.open(target)
                return f"Opening {app_name} for you now."
            elif kind == "uri":
                try:
                    os.startfile(target)
                except Exception:
                    subprocess.Popen(f'start "" "{target}"', shell=True)
                return f"Opening {app_name} for you now."
            elif kind == "exe":
                if os.path.exists(target):
                    os.startfile(target)
                    return f"Opening {app_name} for you now."
                else:
                    subprocess.Popen(f'start "" "{target}"', shell=True)
                    return f"Attempting to launch {app_name}."
            elif kind == "folder":
                subprocess.Popen(f'explorer {target}', shell=True)
                return f"Opening {app_name} folder for you now."
            elif kind == "cmd":
                subprocess.Popen(target, shell=True)
                return f"Opening {app_name} for you now."
        except Exception as e:
            return f"Could not launch {app_name}: {str(e)}"

    # Fallback to direct Windows launch
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