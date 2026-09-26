import os
import sys
import time
import threading
import cv2

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class FacePresenceDetector:
    """
    Monitors the webcam periodically in a low-overhead background thread.
    Detects when the user returns to their desk after being away, and triggers a greeting callback.
    """

    def __init__(self, camera_index: int = 0, check_interval: float = 3.5, away_threshold: float = 25.0, cooldown: float = 90.0):
        self.camera_index = camera_index
        self.check_interval = check_interval
        self.away_threshold = away_threshold
        self.cooldown = cooldown

        self._running = False
        self._thread = None
        self._on_arrival_callback = None
        self._on_status_callback = None

        self.is_present = False
        self.last_seen_time = time.time()
        self.last_greeting_time = 0

        # Load OpenCV frontal face cascade
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def start(self, on_arrival=None, on_status=None):
        """Starts background face presence monitoring."""
        if on_arrival:
            self._on_arrival_callback = on_arrival
        if on_status:
            self._on_status_callback = on_status

        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            print("👁️ [FacePresence] Background optical presence detector active.")

    def stop(self):
        """Halts face presence monitoring."""
        self._running = False

    def scan_now(self) -> bool:
        """Performs a single immediate face detection check."""
        try:
            # Use CAP_DSHOW for rapid acquisition on Windows
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                return False

            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                return False

            # Resize to 320x240 for 2ms detection
            small = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))

            return len(faces) > 0
        except Exception:
            return False

    def _monitor_loop(self):
        """Background sampling loop."""
        while self._running:
            time.sleep(self.check_interval)
            try:
                face_detected = self.scan_now()
                now = time.time()

                if face_detected:
                    time_away = now - self.last_seen_time

                    # Trigger arrival greeting if user was away for > away_threshold
                    if time_away > self.away_threshold and (now - self.last_greeting_time > self.cooldown):
                        self.last_greeting_time = now
                        print("\n✨ [FacePresence] Boss detected returning to workstation!")
                        if self._on_arrival_callback:
                            try:
                                self._on_arrival_callback()
                            except Exception as e:
                                print(f"[FacePresence Callback Error] {e}")

                    self.last_seen_time = now
                    if not self.is_present:
                        self.is_present = True
                        if self._on_status_callback:
                            self._on_status_callback(True)
                else:
                    if now - self.last_seen_time > self.away_threshold:
                        if self.is_present:
                            self.is_present = False
                            if self._on_status_callback:
                                self._on_status_callback(False)
            except Exception:
                pass

# Global singleton
face_presence = FacePresenceDetector()

def check_user_present() -> str:
    """Manual voice tool to check if user is visible to camera."""
    detected = face_presence.scan_now()
    if detected:
        return "Visual confirmation confirmed, Boss. You are clearly visible at your workstation."
    return "I am currently unable to detect your face in the optical feed, Boss."
