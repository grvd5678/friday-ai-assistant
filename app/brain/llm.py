import os
import re
import ollama
from google import genai
from google.genai import types

from app.config import config
from app.brain.prompts import FRIDAY_SYSTEM_PROMPT
from app.brain.memory import memory, remember_fact, recall_memories, forget_memory
from app.tools.sys_info import get_system_stats, get_battery_status, get_datetime_info
from app.tools.system_control import open_app, close_app, change_volume, media_control, lock_screen
from app.tools.web_search import search_web, play_youtube, get_wikipedia_summary, get_weather
from app.tools.whatsapp_tool import send_whatsapp_message
from app.tools.screenshot_tool import take_screenshot, open_screenshots_folder
from app.tools.vision_tool import inspect_screen, inspect_webcam
from app.tools.document_tool import analyze_document
from app.tools.briefing_tool import get_morning_briefing
from app.tools.modes import activate_developer_mode, activate_movie_mode, activate_lockdown_mode, activate_focus_mode
from app.tools.file_tool import find_files, organize_folder, open_folder
from app.audio.live_stream import start_live_mode, stop_live_mode
from app.vision.face_presence import check_user_present

# Registered action tools for autonomous function calling
FRIDAY_TOOLS = [
    open_app,
    close_app,
    analyze_document,
    get_system_stats,
    get_battery_status,
    get_datetime_info,
    change_volume,
    media_control,
    lock_screen,
    search_web,
    play_youtube,
    get_wikipedia_summary,
    get_weather,
    send_whatsapp_message,
    take_screenshot,
    open_screenshots_folder,
    inspect_screen,
    inspect_webcam,
    get_morning_briefing,
    activate_developer_mode,
    activate_movie_mode,
    activate_lockdown_mode,
    activate_focus_mode,
    find_files,
    organize_folder,
    open_folder,
    start_live_mode,
    stop_live_mode,
    check_user_present,
    remember_fact,
    recall_memories,
    forget_memory
]

_gemini_client = None
_gemini_chat = None

def _get_gemini_chat():
    """Initializes or returns active Gemini chat session with tools and system instruction."""
    global _gemini_client, _gemini_chat
    if not config.GEMINI_API_KEY:
        return None

    if _gemini_chat is None:
        try:
            _gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
            
            # Combine system prompt with persistent memory context
            memory_context = memory.get_memory_context_prompt()
            full_system_instruction = f"{FRIDAY_SYSTEM_PROMPT}\n\n{memory_context}"

            _gemini_chat = _gemini_client.chats.create(
                model=config.GEMINI_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    tools=FRIDAY_TOOLS,
                    temperature=0.7,
                )
            )
        except Exception as e:
            print(f"[Gemini Init Error] {e}")
            _gemini_chat = None

    return _gemini_chat

def _local_rule_fallback(prompt: str) -> str:
    """Offline rule-based fallback execution if both Gemini and Ollama are unavailable."""
    p = prompt.lower().strip()
    
    # Datetime / Time
    if any(k in p for k in ["what time", "what date", "current time", "today's date", "day is it"]):
        return get_datetime_info()

    # System stats & Hardware
    if any(k in p for k in ["system stat", "cpu", "ram", "hardware", "diagnostic"]):
        return get_system_stats()
    
    # Battery
    if "battery" in p:
        return get_battery_status()

    # Screenshot
    if "screenshot" in p or "screen shot" in p:
        return take_screenshot()

    # Lock workstation
    if any(k in p for k in ["lock screen", "lock workstation", "lock pc", "lock computer"]):
        return lock_screen()

    # Volume control
    if any(k in p for k in ["volume", "mute", "unmute"]):
        if "mute" in p:
            return change_volume("mute")
        elif any(k in p for k in ["up", "increase", "raise"]):
            return change_volume("up")
        elif any(k in p for k in ["down", "decrease", "lower"]):
            return change_volume("down")

    # Media control
    if any(k in p for k in ["pause", "resume song", "play music", "next song", "next track", "skip"]):
        if any(k in p for k in ["next", "skip"]):
            return media_control("next")
        elif any(k in p for k in ["prev", "back"]):
            return media_control("prev")
        else:
            return media_control("play")

    # Weather
    if "weather" in p:
        loc_match = re.search(r"weather (?:in|for|at) (.+)", p)
        target_city = loc_match.group(1).strip() if loc_match else ""
        return get_weather(target_city)

    # Close app
    close_match = re.search(r"close (?:app )?([a-zA-Z0-9\s]+)", p)
    if close_match:
        target_app = close_match.group(1).strip()
        return close_app(target_app)

    # Open app
    open_match = re.search(r"(?:open|launch|start) (?:app )?([a-zA-Z0-9\s]+)", p)
    if open_match:
        target_app = open_match.group(1).strip()
        return open_app(target_app)

    # YouTube
    yt_match = re.search(r"(?:play|search) (.+) on youtube", p)
    if yt_match:
        return play_youtube(yt_match.group(1))

    # Wikipedia lookup
    wiki_match = re.search(r"(?:who is|what is|tell me about) (.+)", p)
    if wiki_match:
        return get_wikipedia_summary(wiki_match.group(1))

    # Web search
    search_match = re.search(r"(?:search|google) (.+)", p)
    if search_match:
        return search_web(search_match.group(1))

    # Remember fact
    if p.startswith("remember that ") or p.startswith("remember "):
        fact = prompt[9:].strip() if p.startswith("remember ") else prompt[14:].strip()
        return remember_fact(fact)

    # Forget fact
    if p.startswith("forget that ") or p.startswith("forget "):
        query = prompt[7:].strip() if p.startswith("forget ") else prompt[12:].strip()
        return forget_memory(query)

    # Recall fact
    if any(k in p for k in ["what do you remember", "recall", "memory"]):
        return recall_memories(prompt)

    # Screen Vision
    if any(k in p for k in ["look at my screen", "what am i looking at", "what's on my screen", "inspect screen", "check my screen", "read my screen", "what is on screen"]):
        return inspect_screen(prompt)

    # Morning Tactical Briefing
    if any(k in p for k in ["morning briefing", "daily briefing", "tactical briefing", "brief me", "good morning"]):
        return get_morning_briefing()

    # Tactical Work Modes
    if any(k in p for k in ["developer mode", "dev mode", "coding mode"]):
        return activate_developer_mode()
    if any(k in p for k in ["movie mode", "cinema mode"]):
        return activate_movie_mode()
    if any(k in p for k in ["lockdown", "protocol lockdown", "lock down"]):
        return activate_lockdown_mode()
    if any(k in p for k in ["focus mode", "deep work"]):
        return activate_focus_mode()

    # File & Folder Management
    if "organize" in p and any(k in p for k in ["download", "desktop", "folder"]):
        target = "Downloads" if "download" in p else ("Desktop" if "desktop" in p else "Downloads")
        return organize_folder(target)

    if any(k in p for k in ["open folder", "open downloads", "open documents", "open desktop"]):
        target = "Downloads" if "download" in p else ("Desktop" if "desktop" in p else "Documents")
        return open_folder(target)

    if any(k in p for k in ["find pdf", "find file", "search file", "look for file"]):
        ext = "pdf" if "pdf" in p else ""
        return find_files(extension=ext, folder="Downloads")

    # Floating Arc-Reactor Widget Toggle
    if any(k in p for k in ["widget mode", "mini widget", "floating widget", "compact widget", "expand hud", "restore hud", "full dashboard"]):
        try:
            from app.ui.hud_app import toggle_hud_widget
            is_mini = toggle_hud_widget()
            return "Switching to floating Arc-Reactor widget mode, Boss." if is_mini else "Restoring full tactical HUD interface, Boss."
        except Exception:
            return "HUD widget toggle commanded, Boss."

    # Gemini Live Streaming Mode
    if any(k in p for k in ["start live mode", "activate live mode", "live stream", "live voice mode"]):
        return start_live_mode()
    if any(k in p for k in ["stop live mode", "exit live mode", "deactivate live mode"]):
        return stop_live_mode()

    # Face Presence Scan
    if any(k in p for k in ["can you see me", "scan my face", "am i visible", "detect face", "look for me"]):
        return check_user_present()

    return "I heard you, Boss. All local offline systems are standing by."

def _ask_ollama_fallback(prompt: str) -> str:
    """Queries local Ollama model if running."""
    try:
        messages = [
            {"role": "system", "content": f"{FRIDAY_SYSTEM_PROMPT}\n\n{memory.get_memory_context_prompt()}"}
        ]
        # Append recent history
        for msg in memory.get_history()[-4:]:
            messages.append(msg)
        messages.append({"role": "user", "content": prompt})

        response = ollama.chat(
            model=config.OLLAMA_MODEL,
            messages=messages
        )
        return response.message.content or "Action confirmed, Boss."
    except Exception as e:
        print(f"[Ollama Error] {e}. Falling back to offline rule handler.")
        return _local_rule_fallback(prompt)

def ask_friday(prompt: str) -> str:
    """Primary reasoning engine: Gemini (Primary + Autonomous Tools) -> Ollama (Local) -> Rule Fallback."""
    if not prompt or not prompt.strip():
        return ""

    # Check for direct local memory operations first if explicit
    p_lower = prompt.lower().strip()
    if p_lower.startswith("remember that "):
        fact = prompt[14:].strip()
        result = remember_fact(fact)
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    if p_lower.startswith("forget that ") or p_lower.startswith("forget "):
        query = prompt[7:].strip() if p_lower.startswith("forget ") else prompt[12:].strip()
        result = forget_memory(query)
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Screen Vision
    if any(k in p_lower for k in ["look at my screen", "what am i looking at", "what's on my screen", "inspect my screen", "check my screen", "read my screen", "analyze my screen", "what is on screen"]):
        result = inspect_screen(prompt)
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Morning Tactical Briefing
    if any(k in p_lower for k in ["morning briefing", "daily briefing", "tactical briefing", "brief me"]):
        result = get_morning_briefing()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Floating Widget Mode
    if any(k in p_lower for k in ["widget mode", "mini widget", "floating widget", "compact widget", "expand hud", "restore hud", "full dashboard"]):
        try:
            from app.ui.hud_app import toggle_hud_widget
            is_mini = toggle_hud_widget()
            result = "Switching to floating Arc-Reactor widget mode, Boss." if is_mini else "Restoring full tactical HUD interface, Boss."
        except Exception:
            result = "HUD widget toggle commanded, Boss."
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Gemini Live Streaming Mode
    if any(k in p_lower for k in ["start live mode", "activate live mode", "live stream", "live voice mode"]):
        result = start_live_mode()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    if any(k in p_lower for k in ["stop live mode", "exit live mode", "deactivate live mode"]):
        result = stop_live_mode()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Webcam Optical Vision (e.g. waving hands, physical gestures, camera look)
    if any(k in p_lower for k in ["wave", "waving", "look at me", "look through my camera", "see me waving", "what am i doing", "see through camera", "inspect camera", "check camera", "can you see me waving", "see my hand", "am i waving"]):
        result = inspect_webcam(prompt)
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Screenshot Capture
    if any(k in p_lower for k in ["capture screenshot", "take a screenshot", "take screenshot", "capture the screen", "save screenshot", "take screen shot"]):
        result = take_screenshot()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Opening Screenshots Folder / Locating Screenshots
    if any(k in p_lower for k in ["open screenshot", "open screenshots", "where is screenshot", "where is the screenshot", "where are screenshots", "where did you save", "where did she save"]):
        result = open_screenshots_folder()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # Fast path for Face Presence
    if any(k in p_lower for k in ["can you see me", "scan my face", "am i visible", "detect face", "look for me"]):
        result = check_user_present()
        memory.add_message("user", prompt)
        memory.add_message("assistant", result)
        return result

    # 1. Attempt Primary: Gemini with automatic tool execution
    chat = _get_gemini_chat()
    if chat:
        try:
            response = chat.send_message(prompt)
            reply = response.text.strip() if (response and response.text) else ""
            if not reply:
                reply = "Action executed successfully, Boss."
            
            # Record in memory
            memory.add_message("user", prompt)
            memory.add_message("assistant", reply)
            return reply
        except Exception as e:
            print(f"[Gemini Error] {e}. Switching to Ollama local backup...")
            # If error is due to session state or token expiry, reset chat for next attempt
            global _gemini_chat
            _gemini_chat = None

    # 2. Fallback: Ollama Local
    reply = _ask_ollama_fallback(prompt)
    memory.add_message("user", prompt)
    memory.add_message("assistant", reply)
    return reply

# Backward compatibility alias
ask_jarvis = ask_friday