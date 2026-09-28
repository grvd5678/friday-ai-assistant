import os
import sys
import re
import uuid
import asyncio
import tempfile
import subprocess
import edge_tts
from playsound3 import playsound
from app.config import config

# Optional state callback for UI: callback(state: str, text: str = "")
_status_callback = None

def set_speech_callback(callback):
    """Allows UI or HUD to register a callback for speech events ('speaking_start', 'speaking_end')."""
    global _status_callback
    _status_callback = callback

def _notify(status: str, text: str = ""):
    if _status_callback:
        try:
            _status_callback(status, text)
        except Exception:
            pass

def clean_speech_text(text: str) -> str:
    """Strips Markdown syntax, symbols, and formatting for natural TTS pronunciation."""
    if not text:
        return ""
    # Remove code blocks
    cleaned = re.sub(r'```[\s\S]*?```', ' [Code block omitted] ', text)
    # Remove inline code
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
    # Remove markdown links [text](url) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
    # Remove markdown bold/italics
    cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
    cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)
    cleaned = re.sub(r'_([^_]+)_', r'\1', cleaned)
    # Remove header hashes
    cleaned = re.sub(r'#{1,6}\s*', '', cleaned)
    # Remove bullet symbols
    cleaned = re.sub(r'^\s*[\*\-\+]\s+', '', cleaned, flags=re.MULTILINE)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

async def _generate_audio(text: str, file_path: str):
    """Generates speech file using Edge-TTS neural female voice."""
    voice = config.VOICE_NAME or "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)

def _fallback_windows_tts(text: str):
    """Offline TTS fallback using Windows SAPI SpeechSynthesizer with strictly female voice."""
    try:
        safe_text = text.replace("'", "''").replace('"', '\"')
        # Select strictly female voice (e.g. Microsoft Zira)
        ps_cmd = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"try {{ $synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female) }} catch {{}}; "
            f"$synth.Rate = 0; "
            f"$synth.Speak('{safe_text}');"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            timeout=15
        )
    except Exception as e:
        print(f"[Offline TTS Fallback Error]: {e}")

def speak(text: str):
    """Plays generated speech with markdown cleanup, lock prevention, and female voice guarantee."""
    if not text or not text.strip():
        return

    # Try pausing wake listener so FRIDAY does not trigger on her own voice
    try:
        from app.audio.wakeword import wake_listener
        wake_listener.pause()
    except Exception:
        pass

    spoken_text = clean_speech_text(text)
    print(f"\n🤖 {config.BOT_NAME}: {text}\n")

    unique_id = uuid.uuid4().hex[:8]
    temp_path = os.path.join(tempfile.gettempdir(), f"{config.BOT_NAME.lower()}_{unique_id}.mp3")

    try:
        # Generate neural speech audio via Edge-TTS
        asyncio.run(_generate_audio(spoken_text, temp_path))

        # Play generated MP3 in perfect sync with HUD subtitle
        if os.path.exists(temp_path):
            _notify("speaking_start", text)
            playsound(temp_path)
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[Speech interrupted]")
    except Exception as e:
        print(f"Edge-TTS Error ({e}). Activating offline female Windows TTS fallback...")
        _notify("speaking_start", text)
        _fallback_windows_tts(spoken_text)
    finally:
        # Clean up temporary audio file safely
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        _notify("speaking_end", "")
        # Resume background wake listener
        try:
            from app.audio.wakeword import wake_listener
            wake_listener.resume()
        except Exception:
            pass