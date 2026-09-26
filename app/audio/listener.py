import os
import sys
import speech_recognition as sr
from app.config import config

# Optional UI state callback: callback(status: str, data: str = "")
_listener_callback = None

def set_listener_callback(callback):
    """Allows UI to register callbacks for microphone events ('listening_start', 'transcribing', 'listening_end')."""
    global _listener_callback
    _listener_callback = callback

def _notify(status: str, data: str = ""):
    if _listener_callback:
        try:
            _listener_callback(status, data)
        except Exception:
            pass

def listen(timeout: int = 8, phrase_time_limit: int = 15) -> str:
    """Captures microphone input with sensitive threshold detection and responsive listening."""
    # Temporarily pause wake word listener to avoid audio contention
    try:
        from app.audio.wakeword import wake_listener
        wake_listener.pause()
    except Exception:
        pass

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.non_speaking_duration = 0.4

    target_index = config.MIC_INDEX
    device_label = f"Device {target_index}" if target_index is not None else "Windows Default Microphone"

    _notify("listening_start", "Listening for your voice...")
    print(f"\n🎙️ Listening on {device_label}... (Speak now!)")

    try:
        # Create microphone with fallback
        try:
            mic = sr.Microphone(device_index=target_index)
        except Exception:
            mic = sr.Microphone()

        with mic as source:
            # Calibrate dynamically to ambient room acoustics
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.25)
                # Keep sensitivity high enough for quiet conversational voice
                if recognizer.energy_threshold > 300:
                    recognizer.energy_threshold = 250
                elif recognizer.energy_threshold < 30:
                    recognizer.energy_threshold = 30
            except Exception:
                recognizer.energy_threshold = config.MIC_THRESHOLD if config.MIC_THRESHOLD else 35

            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        _notify("transcribing", "Transcribing speech...")
        print("⚡ Transcribing speech...")
        query = recognizer.recognize_google(audio_data)

        if query:
            print(f"👤 You (Spoken): '{query}'")
            _notify("listening_end", query)
            return query
        else:
            _notify("listening_end", "")
            return ""

    except sr.WaitTimeoutError:
        print("Listening timed out... (No speech heard)")
        _notify("listening_end", "")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio... (Audio unclear)")
        _notify("listening_end", "")
        return ""
    except Exception as e:
        print(f"Listener Error: {e}")
        _notify("listening_end", "")
        return ""
    finally:
        # Resume background wake listener
        try:
            from app.audio.wakeword import wake_listener
            wake_listener.resume()
        except Exception:
            pass

if __name__ == "__main__":
    text = listen()
    print(f"\nFinal Transcribed Result: '{text}'")