import os
import sys
import time
import json
import threading
import psutil
import webview

# Ensure Windows terminal handles UTF-8 emojis without charmap encoding crashes
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from app.config import config
from app.brain.llm import ask_friday
from app.audio.speaker import speak, set_speech_callback, set_viseme_callback, set_avatar_video_callback
from app.audio.listener import listen, set_listener_callback
from app.audio.wakeword import wake_listener
from app.brain.greetings import get_startup_greeting, get_wake_acknowledgment, get_arrival_greeting

_global_api = None

class FRIDAY_API:
    """Exposes Python backend methods to the HUD JavaScript frontend."""

    def __init__(self, window_ref=None):
        global _global_api
        self.window = window_ref
        self._is_busy = False
        self._is_widget_mode = False
        _global_api = self

    def set_window(self, window):
        self.window = window

    def toggle_widget_mode(self):
        """Toggles between full tactical HUD (1080x720) and floating mini Arc-Reactor widget (340x360)."""
        if not self.window:
            return False
        self._is_widget_mode = not self._is_widget_mode
        if self._is_widget_mode:
            self.window.resize(340, 360)
            try:
                self.window.on_top = True
            except Exception:
                pass
            self.js_call("document.body.classList.add('widget-mode');")
            return True
        else:
            self.window.resize(1080, 720)
            try:
                self.window.on_top = False
            except Exception:
                pass
            self.js_call("document.body.classList.remove('widget-mode');")
            return False

    def js_call(self, script: str):
        """Safely evaluates JavaScript inside the HUD window."""
        if self.window:
            try:
                self.window.evaluate_js(script)
            except Exception:
                pass

    def update_status(self, state: str, message: str = ""):
        self.js_call(f"window.fridayHUD && window.fridayHUD.setStatus({json.dumps(state)}, {json.dumps(message)});")

    def append_log(self, log_type: str, text: str):
        self.js_call(f"window.fridayHUD && window.fridayHUD.appendLog({json.dumps(log_type)}, {json.dumps(text)});")

    def update_telemetry(self, stats: dict):
        stats_json = json.dumps(stats)
        self.js_call(f'window.fridayHUD && window.fridayHUD.updateTelemetry({stats_json});')

    def select_file(self) -> str:
        """Opens native Windows file dialog allowing user to choose PDF, DOCX, PNG, JPG, or TXT."""
        if not self.window:
            return ""
        try:
            # 1. Try PyWebView native dialog with validated regex-safe filters
            if self.window:
                try:
                    dialog_type = getattr(webview.FileDialog, "OPEN", 10)
                    file_types = (
                        "Supported Files (*.pdf;*.docx;*.doc;*.png;*.jpg;*.jpeg;*.webp;*.txt;*.py;*.csv)",
                        "PDF Documents (*.pdf)",
                        "Word Documents (*.docx;*.doc)",
                        "Images (*.png;*.jpg;*.jpeg;*.webp)",
                        "Text Documents (*.txt;*.py;*.csv;*.json;*.md)",
                        "All Files (*.*)"
                    )
                    res = self.window.create_file_dialog(dialog_type, allow_multiple=False, file_types=file_types)
                    if res and len(res) > 0:
                        selected_path = res[0]
                        file_name = os.path.basename(selected_path)
                        self.append_log("system", f"Attached document: {file_name}")
                        return selected_path
                except Exception as we:
                    print(f"[PyWebView Dialog Notice] {we}. Trying native fallback...")

            # 2. Rock-solid Tkinter native file dialog fallback
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected_path = filedialog.askopenfilename(
                title="Select Document or Image for F.R.I.D.A.Y.",
                filetypes=[
                    ("Supported Files", "*.pdf *.docx *.doc *.png *.jpg *.jpeg *.webp *.txt *.py *.csv"),
                    ("PDF Documents", "*.pdf"),
                    ("Word Documents", "*.docx *.doc"),
                    ("Images", "*.png *.jpg *.jpeg *.webp"),
                    ("Text Files", "*.txt *.py *.csv *.json *.md"),
                    ("All Files", "*.*")
                ]
            )
            root.destroy()
            if selected_path:
                file_name = os.path.basename(selected_path)
                self.append_log("system", f"Attached document: {file_name}")
                return selected_path
        except Exception as e:
            print(f"[File Selection Error] {e}")
        return ""

    def clear_document_session(self):
        """Clears the active document conversation session."""
        try:
            from app.tools.document_tool import clear_active_document
            clear_active_document()
            self.append_log("system", "Document conversation session closed.")
        except Exception:
            pass

    def process_user_query(self, query: str, file_path: str = None):
        """Processes typed or spoken command in background thread, with optional attached file."""
        if not query or self._is_busy:
            return

        def _worker():
            self._is_busy = True
            try:
                from app.tools.document_tool import get_active_document, analyze_document, chat_with_active_document
                active_doc = get_active_document()
                doc_name = os.path.basename(file_path) if file_path else (active_doc.get("name") if active_doc else None)
                display_msg = f"{query} [📎 {doc_name}]" if doc_name else query
                self.update_status("THINKING", f'PROCESSING: "{display_msg}"')
                self.append_log("user", display_msg)

                # Proactive pre-action announcements for Marvel-style realism
                q_lower = query.lower()
                if any(k in q_lower for k in ["look at me", "can you see", "waving", "what am i doing", "take my photo", "take a photo", "selfie"]):
                    self.append_log("assistant", "Activating optical sensors, Boss. Give me a moment...")
                elif any(k in q_lower for k in ["look at my screen", "what am i looking at", "what's on my screen", "inspect my screen", "check my screen"]):
                    self.append_log("assistant", "Capturing your display now, Boss...")
                elif any(k in q_lower for k in ["screenshot", "take a screenshot"]):
                    self.append_log("assistant", "Capturing screenshot, Boss...")
                elif any(k in q_lower for k in ["weather", "forecast"]):
                    self.append_log("assistant", "Pulling live weather telemetry, Boss...")
                elif any(k in q_lower for k in ["morning briefing", "brief me", "briefing"]):
                    self.append_log("assistant", "Compiling your tactical briefing. Stand by, Boss...")
                elif any(k in q_lower for k in ["open ", "launch ", "start "]):
                    self.append_log("assistant", "On it, Boss...")

                if file_path and os.path.exists(file_path):
                    response = analyze_document(file_path, query)
                elif active_doc and active_doc.get("path") and not any(k in query.lower() for k in ["open ", "close ", "screenshot", "weather", "volume", "lock screen", "mute"]):
                    response = chat_with_active_document(query)
                else:
                    response = ask_friday(query)

                self.append_log("assistant", response)
                speak(response)

            except Exception as e:
                err_msg = f"Error: {e}"
                self.append_log("system", err_msg)
                speak("I encountered an issue processing that instruction, Boss.")
            finally:
                self._is_busy = False
                self.update_status("STANDBY", "SYSTEM READY")

        threading.Thread(target=_worker, daemon=True).start()

    def trigger_mic(self):
        """Triggers voice capture."""
        if self._is_busy:
            return

        def _mic_worker():
            self._is_busy = True
            try:
                self.update_status("LISTENING", "LISTENING FOR YOUR VOICE...")
                query = listen()
                if query:
                    from app.tools.document_tool import get_active_document, chat_with_active_document
                    active_doc = get_active_document()
                    doc_name = active_doc.get("name") if active_doc else None
                    display_msg = f"{query} [📎 {doc_name}]" if doc_name else query
                    self.update_status("THINKING", f'PROCESSING: "{display_msg}"')
                    self.append_log("user", display_msg)

                    if active_doc and active_doc.get("path") and not any(k in query.lower() for k in ["open ", "close ", "screenshot", "weather", "volume", "lock screen", "mute"]):
                        response = chat_with_active_document(query)
                    else:
                        response = ask_friday(query)

                    self.append_log("assistant", response)
                    speak(response)
                else:
                    self.update_status("STANDBY", "NO AUDIO DETECTED")
                    time.sleep(1.5)
            except Exception as e:
                print(f"[Mic Worker Error]: {e}")
            finally:
                self._is_busy = False
                self.update_status("STANDBY", "SYSTEM READY")

        threading.Thread(target=_mic_worker, daemon=True).start()

def _start_telemetry_loop(api: FRIDAY_API):
    """Periodically streams system telemetry to the HUD."""
    prev_net = psutil.net_io_counters()
    boot_time = psutil.boot_time()

    while True:
        try:
            time.sleep(2)
            # CPU
            cpu = int(psutil.cpu_percent())
            # Memory
            mem = int(psutil.virtual_memory().percent)
            
            # Battery
            bat = psutil.sensors_battery()
            bat_str = f"{bat.percent}%" if bat else "100%"

            # Network speed
            curr_net = psutil.net_io_counters()
            bytes_sec = (curr_net.bytes_recv - prev_net.bytes_recv) + (curr_net.bytes_sent - prev_net.bytes_sent)
            prev_net = curr_net
            kb_sec = int(bytes_sec / 2048)  # Average over 2s
            
            # Processes
            procs = len(psutil.pids())

            # Uptime
            uptime_seconds = int(time.time() - boot_time)
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours:02}:{minutes:02}:{seconds:02}"

            # CPU Temperature (Windows: requires admin or OpenHardwareMonitor WMI bridge)
            temp_str = "N/A"
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for key in ("coretemp", "cpu_thermal", "k10temp", "acpitz"):
                        if key in temps and temps[key]:
                            temp_str = f"{temps[key][0].current:.0f}°C"
                            break
            except Exception:
                pass

            stats = {
                "cpu": cpu,
                "mem": mem,
                "bat": bat_str,
                "net": f"{kb_sec} KB/s",
                "temp": temp_str,
                "uptime": uptime_str,
                "proc": procs,
                "os": "WIN 11"
            }
            api.update_telemetry(stats)
        except Exception:
            pass

def launch_hud():
    """Starts the FRIDAY Sci-Fi HUD window and background threads."""
    api = FRIDAY_API()

    # Wire up speech & listening callbacks
    def on_speech(event_type, text):
        if event_type == "speaking_start":
            api.update_status("SPEAKING", text)
        elif event_type == "speaking_end":
            api.update_status("STANDBY", "SYSTEM READY")

    def on_listener(event_type, data):
        if event_type == "listening_start":
            api.update_status("LISTENING", "MIC ACTIVE...")
        elif event_type == "transcribing":
            api.update_status("THINKING", "TRANSCRIBING...")
        elif event_type == "listening_end" and data:
            api.update_status("THINKING", f'HEARD: "{data}"')

    set_speech_callback(on_speech)
    set_listener_callback(on_listener)

    # 0ms real-time phonetic viseme sync callback
    def on_viseme(frame_idx: int):
        api.js_call(f"window.fridayHUD && window.fridayHUD.setVisemeFrame({frame_idx});")

    set_viseme_callback(on_viseme)

    # Optional talking video avatar callback
    def on_avatar_video(video_path: str):
        safe_path = json.dumps(video_path)
        api.js_call(f"window.fridayHUD && window.fridayHUD.setAvatarVideo({safe_path});")

    set_avatar_video_callback(on_avatar_video)

    # Wake word detection callback
    def on_wake_word(detected_phrase):
        print(f"\n⚡ Wake word triggered: '{detected_phrase}'")
        clean = detected_phrase.lower().strip()
        pure_greetings = {"hello", "hey", "hi", "friday", "hey friday", "hi friday", "hello friday", "ok friday", "wake up", "are you there"}

        if clean not in pure_greetings and len(clean.split()) > 2:
            # User spoke an entire instruction alongside wake word
            api.process_user_query(detected_phrase)
        else:
            # User greeted F.R.I.D.A.Y. ("Hello", "Hey Friday") -> respond and activate mic
            def _greet_and_listen():
                reply = get_wake_acknowledgment()
                api.update_status("SPEAKING", reply)
                api.append_log("assistant", reply)
                speak(reply)
                api.trigger_mic()
            threading.Thread(target=_greet_and_listen, daemon=True).start()

    wake_listener.start(on_wake_word)

    # Optical Face Presence Detection
    try:
        from app.vision.face_presence import face_presence
        def on_user_arrival():
            greeting = get_arrival_greeting()
            api.update_status("SPEAKING", greeting)
            api.append_log("system", f"[PRESENCE] {greeting}")
            speak(greeting)

        face_presence.start(on_arrival=on_user_arrival)
    except Exception as e:
        print(f"[Face Presence Warning] Could not start optical detector: {e}")

    # Telemetry background thread
    threading.Thread(target=_start_telemetry_loop, args=(api,), daemon=True).start()

    # Create Webview window
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")

    window = webview.create_window(
        title="F.R.I.D.A.Y. - Holographic Tactical Interface",
        url=html_path,
        js_api=api,
        width=1080,
        height=720,
        resizable=True,
        frameless=False,
        background_color="#03070d",
        easy_drag=True
    )
    api.set_window(window)

    # Initial greeting speech in separate thread
    def _greet():
        time.sleep(2)
        greeting = get_startup_greeting()
        api.update_status("SPEAKING", greeting)
        api.append_log("system", greeting)
        speak(greeting)

    threading.Thread(target=_greet, daemon=True).start()

    print("\n" + "="*58)
    print("🚀 LAUNCHING F.R.I.D.A.Y. HOLOGRAPHIC TACTICAL INTERFACE")
    print("="*58 + "\n")

    try:
        webview.start(debug=False)
    finally:
        wake_listener.stop()
        try:
            face_presence.stop()
        except Exception:
            pass

def toggle_hud_widget() -> bool:
    """Toggles HUD between full dashboard and mini floating widget."""
    global _global_api
    if _global_api:
        return _global_api.toggle_widget_mode()
    return False

if __name__ == "__main__":
    launch_hud()
