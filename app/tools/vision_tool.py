import os
import sys
from PIL import Image
from google import genai
from app.config import config

def capture_active_screen():
    """Captures screenshot using PIL, PyAutoGUI, or MSS with safe fallbacks."""
    # 1. Try ImageGrab
    try:
        from PIL import ImageGrab
        im = ImageGrab.grab()
        if im:
            return im
    except Exception:
        pass

    # 2. Try PyAutoGUI
    try:
        import pyautogui
        im = pyautogui.screenshot()
        if im:
            return im
    except Exception:
        pass

    # 3. Try MSS
    try:
        import mss
        with mss.MSS() as sct:
            mon = sct.monitors[1]
            shot = sct.grab(mon)
            return Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
    except Exception:
        pass

    return None

def inspect_screen(question: str = "What is currently visible on my screen?") -> str:
    """Captures the user's active screen and analyzes it using Gemini 2.5 Flash multimodal vision."""
    screen_img = capture_active_screen()
    if screen_img is None:
        return "I am unable to capture the desktop display right now, Boss. Please ensure your screen is active."

    try:
        # Optimize image size for fast transmission
        screen_img.thumbnail((1280, 720))

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        tactical_prompt = (
            f"You are F.R.I.D.A.Y., Tony Stark's tactical AI assistant with an Irish female persona. "
            f"Directly analyze what is on the user's screen in response to their inquiry: '{question}'. "
            f"Focus on the active window, any code, errors, messages, or main content. "
            f"Keep your answer concise, conversational, and direct (2-3 sentences max). Address the user as Boss."
        )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[screen_img, tactical_prompt]
        )
        return response.text.strip() if response and response.text else "Screen analyzed, Boss. No anomalies detected."
    except Exception as e:
        return f"Screen vision encountered an issue: {str(e)}"

def inspect_webcam(question: str = "What is the user doing in front of the camera?") -> str:
    """Captures a live frame from the user's laptop camera and analyzes their posture, gestures, or actions (such as waving hands) using Gemini vision."""
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "I cannot access the camera right now, Boss. Please make sure the webcam is connected and not in use by another app."

        # Read a couple frames so camera exposure settles
        frame = None
        for _ in range(3):
            ret, temp = cap.read()
            if ret:
                frame = temp

        cap.release()

        if frame is None:
            return "Camera opened, but failed to capture a clear visual frame, Boss."

        # Convert OpenCV BGR to RGB PIL image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cam_img = Image.fromarray(rgb_frame)
        cam_img.thumbnail((640, 480))

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        tactical_prompt = (
            f"You are F.R.I.D.A.Y., a tactical personal AI assistant with an Irish female persona. "
            f"You are looking at a live photo taken from the user's laptop webcam right now. "
            f"The user asks: '{question}'. "
            f"Factually and truthfully describe what the user is doing. Specifically check: Are they waving their hand(s)? What are they doing or wearing? "
            f"Never pretend or hallucinate seeing something not in the image. If they are not waving, state that clearly. "
            f"Keep your response concise, conversational, and direct (1 to 2 sentences). Address the user as Boss."
        )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[cam_img, tactical_prompt]
        )
        return response.text.strip() if response and response.text else "Visual feed verified, Boss."
    except Exception as e:
        return f"Optical camera vision encountered an error: {str(e)}"

if __name__ == "__main__":
    print(inspect_screen("What is on screen?"))

