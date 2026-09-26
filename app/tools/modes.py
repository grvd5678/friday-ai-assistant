import os
import sys
import subprocess
import webbrowser
from app.tools.system_control import change_volume, close_app, lock_screen

def activate_developer_mode() -> str:
    """Activates Developer Mode: opens VS Code, Windows Terminal, and tunes audio for programming."""
    try:
        # Launch VS Code
        subprocess.Popen(["code", "."], shell=True)
    except Exception:
        pass

    try:
        # Launch Windows Terminal or PowerShell
        subprocess.Popen(["wt.exe"], shell=True)
    except Exception:
        try:
            subprocess.Popen(["powershell.exe"], shell=True)
        except Exception:
            pass

    # Set comfortable programming volume
    change_volume("down")
    change_volume("down")

    # Launch Spotify or Lo-Fi Coding Music
    try:
        webbrowser.open("https://open.spotify.com/playlist/0vvXsWCC9xrXsKd4FyS8kM")
    except Exception:
        pass

    return "Developer Mode activated, Boss. VS Code, tactical terminal, and lo-fi audio are online. Volume calibrated."

def activate_movie_mode() -> str:
    """Activates Movie Mode: opens entertainment media and calibrates audio volume."""
    try:
        webbrowser.open("https://www.netflix.com")
    except Exception:
        webbrowser.open("https://www.youtube.com")

    # Set immersive audio volume
    for _ in range(4):
        change_volume("up")

    return "Movie Mode engaged, Boss. Streaming portal launched and audio calibrated for entertainment. Enjoy the show."

def activate_lockdown_mode() -> str:
    """Executes Protocol Lockdown: closes sensitive apps and immediately locks the workstation."""
    # Close sensitive communications
    for app_name in ["WhatsApp", "Telegram", "Discord"]:
        try:
            close_app(app_name)
        except Exception:
            pass

    # Lock Windows
    lock_screen()
    return "Protocol Lockdown executed, Boss. Communications closed and workstation locked."

def activate_focus_mode() -> str:
    """Activates Focus Mode: closes media and distractions to optimize deep work productivity."""
    for app in ["Spotify", "Discord", "WhatsApp", "Steam"]:
        try:
            close_app(app)
        except Exception:
            pass

    change_volume("mute")
    return "Focus Mode engaged, Boss. Background distractions terminated and audio muted for deep concentration."
