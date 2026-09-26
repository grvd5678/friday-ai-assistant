import os
import sys
import time
import subprocess
from PIL import Image

def get_screenshots_folder() -> str:
    """Finds the active Windows Screenshots folder, respecting OneDrive sync and user libraries."""
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    onedrive_pics = os.path.join(user_profile, "OneDrive", "Pictures")
    if os.path.exists(onedrive_pics):
        for name in os.listdir(onedrive_pics):
            if "screenshot" in name.lower():
                candidate = os.path.join(onedrive_pics, name)
                if os.path.isdir(candidate):
                    return candidate
        # Fallback to standard Screenshots inside OneDrive Pictures
        sc_dir = os.path.join(onedrive_pics, "Screenshots")
        os.makedirs(sc_dir, exist_ok=True)
        return sc_dir

    # Standard Windows Pictures
    std_pics = os.path.join(user_profile, "Pictures", "Screenshots")
    os.makedirs(std_pics, exist_ok=True)
    return std_pics

def capture_screen_image():
    """Captures the desktop screen using PIL, PyAutoGUI, or MSS with multiple fallback strategies."""
    # 1. PIL ImageGrab
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(all_screens=True)
        if img:
            return img
    except Exception:
        pass

    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        if img:
            return img
    except Exception:
        pass

    # 2. PyAutoGUI
    try:
        import pyautogui
        img = pyautogui.screenshot()
        if img:
            return img
    except Exception:
        pass

    # 3. MSS
    try:
        import mss
        with mss.MSS() as sct:
            mon = sct.monitors[0] if len(sct.monitors) > 0 else sct.monitors[1]
            shot = sct.grab(mon)
            return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    except Exception:
        pass

    return None

def take_screenshot(filename: str = "") -> str:
    """Captures a screenshot of the user's active screen and saves it directly into their Windows Screenshots folder and project directory."""
    try:
        # Determine target paths
        primary_folder = get_screenshots_folder()
        project_folder = os.path.abspath("screenshots")
        os.makedirs(primary_folder, exist_ok=True)
        os.makedirs(project_folder, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = filename.strip() if filename.strip() else f"screenshot_{timestamp}.png"
        if not file_name.endswith(".png"):
            file_name += ".png"

        primary_path = os.path.join(primary_folder, file_name)
        project_path = os.path.join(project_folder, file_name)

        # Capture image
        img = capture_screen_image()
        if img is None:
            return "I was unable to capture the desktop display right now, Boss. Please make sure the display is awake."

        # Save to user's Windows Pictures/Screenshots
        img.save(primary_path)

        # Save duplicate copy in project folder for quick access
        try:
            img.save(project_path)
            img.save("screenshot.png")
        except Exception:
            pass

        return f"Screenshot captured successfully, Boss! Saved to your Pictures folder at: {primary_path}"

    except Exception as e:
        return f"Encountered an issue capturing screenshot: {str(e)}"

def open_screenshots_folder() -> str:
    """Opens the user's active Windows Screenshots folder in Windows File Explorer."""
    try:
        folder = get_screenshots_folder()
        os.startfile(folder)
        return f"Opening your Screenshots folder now, Boss: {folder}"
    except Exception as e:
        return f"Could not open screenshots folder: {str(e)}"
