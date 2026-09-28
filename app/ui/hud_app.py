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
from app.audio.speaker import speak, set_speech_callback
from app.audio.listener import listen, set_listener_callback
from app.audio.wakeword import wake_listener

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
            try:
                dialog_type = webview.FileDialog.OPEN
            except AttributeError:
                dialog_type = webview.OPEN_DIALOG

            file_types = (
                "All Supported Files (*.pdf;*.docx;*.doc;*.png;*.jpg;*.jpeg;*.webp;*.txt;*.py;*.csv)",
                "PDF Documents (*.pdf)",
                "Word Documents (*.docx;*.doc)",
                "Images (*.png;*.jpg;*.jpeg;*.webp)",
                "Text & Code (*.txt;*.py;*.csv;*.json;*.md)",
                "All Files (*.*)"
            )
            res = self.window.create_file_dialog(dialog_type, allow_multiple=False, file_types=file_types)
            if res and len(res) > 0:
                selected_path = res[0]
                file_name = os.path.basename(selected_path)
                self.append_log("system", f"Attached document: {file_name}")
                return selected_path
        except Exception as e:
            print(f"[File Selection Error] {e}")
        return ""

    def process_user_query(self, query: str, file_path: str = None):
        """Processes typed or spoken command in background thread, with optional attached file."""
        if not query or self._is_busy:
            return

        def _worker():
            self._is_busy = True
            try:
                display_msg = f"{query} [📎 {os.path.basename(file_path)}]" if file_path else query
                self.update_status("THINKING", f'PROCESSING: "{display_msg}"')
                self.append_log("user", display_msg)

                if file_path and os.path.exists(file_path):
                    from app.tools.document_tool import analyze_document
                    response = analyze_document(file_path, query)
                else:
                    response = ask_friday(query)

                self.append_log("assistant", response)
                self.update_status("SPEAKING", response)
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
                    self.update_status("THINKING", f'PROCESSING: "{query}"')
                    self.append_log("user", query)
                    response = ask_friday(query)
                    self.append_log("assistant", response)
                    self.update_status("SPEAKING", response)
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

            stats = {
                "cpu": cpu,
                "mem": mem,
                "bat": bat_str,
                "net": f"{kb_sec} KB/s",
                "temp": "42°C",
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
                reply = "Yes Boss? I'm listening."
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
            greeting = "Welcome back to your workstation, Boss. Systems standing by."
            api.update_status("SPEAKING", greeting)
            api.append_log("system", "[PRESENCE] Welcome back, Boss.")
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
        greeting = f"{config.BOT_NAME} system online and operational. How may I assist you today, Boss?"
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
