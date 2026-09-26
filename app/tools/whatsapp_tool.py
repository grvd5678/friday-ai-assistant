import os
import time
import pyautogui

def send_whatsapp_message(phone_no: str, message: str) -> str:
    """Sends a WhatsApp message using pywhatkit. Phone number must include country code (e.g. +1234567890)."""
    clean_phone = phone_no.strip().replace(" ", "").replace("-", "")
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    try:
        import pywhatkit as pwk  # Lazy import to prevent slow startup
        pwk.sendwhatmsg_instantly(clean_phone, message, wait_time=12, tab_close=True)
        return f"Message transmitted to {clean_phone} successfully, Boss."
    except Exception as e:
        return f"Failed to send WhatsApp message: {str(e)}"

def take_screenshot(filename: str = "") -> str:
    """Captures the current screen and saves it with a timestamp into the screenshots directory."""
    try:
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = filename.strip() if filename.strip() else f"screenshot_{timestamp}.png"
        if not file_name.endswith(".png"):
            file_name += ".png"

        target_path = os.path.join("screenshots", file_name)
        image = pyautogui.screenshot()
        image.save(target_path)
        # Also maintain quick-access root screenshot
        image.save("screenshot.png")
        return f"Screenshot captured successfully and saved to {target_path}, Boss."
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"