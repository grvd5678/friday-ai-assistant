import os
import time
import threading
import speech_recognition as sr
from app.config import config

class WakeWordListener:
    """Continuous background listener for detecting FRIDAY activation phrase."""

    def __init__(self, wake_keywords=None):
        bot_lower = config.BOT_NAME.lower()
        default_keywords = [
            bot_lower,
            f"hey {bot_lower}",
            f"hi {bot_lower}",
            f"ok {bot_lower}",
            f"hello {bot_lower}",
            "friday",
            "hey friday",
            "hello friday",
            "hi friday",
            "ok friday",
            "hello",
            "hey",
            "wake up",
            "are you there"
        ]
        self.wake_keywords = list(set(wake_keywords or default_keywords))
        self.running = False
        self.paused = False
        self.thread = None
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.MIC_THRESHOLD if config.MIC_THRESHOLD else 35
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        self.callback = None

    def start(self, callback):
        """Starts background thread to continuously listen for wake words."""
        if self.running:
            return
        self.callback = callback
        self.running = True
        self.paused = False
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print(f"👂 [WakeWord] Background listener active. Say 'Hey {config.BOT_NAME}' or 'Hello' anytime!")

    def stop(self):
        """Stops the background listening thread."""
        self.running = False

    def pause(self):
        """Temporarily pauses listening (e.g. while FRIDAY is speaking or transcribing)."""
        self.paused = True

    def resume(self):
        """Resumes background listening."""
        self.paused = False

    def _listen_loop(self):
        target_index = config.MIC_INDEX

        # Prepare microphone device once with fallback to default
        try:
            mic = sr.Microphone(device_index=target_index)
        except Exception:
            mic = sr.Microphone()

        # Dynamic calibration on start
        try:
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                if self.recognizer.energy_threshold > 300:
                    self.recognizer.energy_threshold = 250
                elif self.recognizer.energy_threshold < 30:
                    self.recognizer.energy_threshold = 30
        except Exception:
            pass

        while self.running:
            if self.paused:
                time.sleep(0.3)
                continue

            try:
                with mic as source:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)

                if self.paused:
                    continue

                try:
                    text = self.recognizer.recognize_google(audio).lower().strip()
                    for keyword in self.wake_keywords:
                        if keyword in text:
                            print(f"\n✨ [Wake Word Detected]: '{text}'")
                            self.pause()
                            if self.callback:
                                try:
                                    self.callback(text)
                                except Exception as cb_err:
                                    print(f"[Wake Callback Error]: {cb_err}")
                            self.resume()
                            break
                except (sr.UnknownValueError, sr.WaitTimeoutError):
                    pass
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                time.sleep(1)

wake_listener = WakeWordListener()
