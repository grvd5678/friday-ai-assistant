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
    # Remove horizontal rules
    cleaned = re.sub(r'^\s*[-*_]{3,}\s*$', '', cleaned, flags=re.MULTILINE)
    # Remove table pipes
    cleaned = re.sub(r'\|', ' ', cleaned)
    # Remove bullet symbols
    cleaned = re.sub(r'^\s*[\*\-\+]\s+', '', cleaned, flags=re.MULTILINE)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def prepare_spoken_summary(text: str) -> str:
    """
    Distills long, markdown-heavy, or document analysis responses into a crisp 1-2 sentence
    spoken executive summary for fast TTS audio generation (1-2s response time) and clean
    subtitle presentation that never covers HUD controls.
    """
    if not text or not text.strip():
        return ""

    raw = text.strip()
    words = raw.split()

    # If the text is already punchy and simple without markdown sections or lists
    has_markdown_sections = bool(re.search(r'(#{1,6}\s+|^\s*[\*\-\+]\s+|---|\|)', raw, flags=re.MULTILINE))
    if len(words) <= 35 and len(raw) <= 240 and not has_markdown_sections:
        return clean_speech_text(raw)

    # 1. Extract the introductory opening paragraph before the first section header, HR, or bullet list
    split_match = re.search(r'(?:\n\s*#{1,6}\s+|\n\s*---\s*|\n\s*[\*\-\+]\s+|\n\s*\|)', raw)
    if split_match:
        intro = raw[:split_match.start()].strip()
    else:
        intro = raw

    cleaned_intro = clean_speech_text(intro)

    # 2. Extract first 1-2 complete sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_intro) if s.strip()]
    if sentences:
        spoken_parts = []
        char_count = 0
        for s in sentences[:2]:
            if char_count + len(s) > 220:
                break
            s_clean = s.rstrip(':').strip()
            spoken_parts.append(s_clean)
            char_count += len(s)

        res = " ".join(spoken_parts).strip()
        if res.endswith(':'):
            res = res[:-1].strip()
        if not res.endswith(('.', '!', '?')):
            res += "."

        # If original text had markdown sections or was long, add tactical feed notice if not already present
        if len(words) > 40 or has_markdown_sections:
            if "tactical feed" not in res.lower() and "feed" not in res.lower():
                res += " I've displayed the complete breakdown in your Tactical Feed."
        return res

    return "I have analyzed the document and placed the complete breakdown in your Tactical Feed."

async def _generate_audio(text: str, file_path: str):
    """Generates speech file using Edge-TTS neural female voice with quick retry."""
    voice = config.VOICE_NAME or "en-IE-EmilyNeural"
    for attempt in range(2):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(file_path)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return
        except Exception:
            if attempt == 1:
                raise
            await asyncio.sleep(0.3)

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

def speak(text: str, spoken_text: str = None):
    """Plays generated speech with fast executive summary, lock prevention, and female voice guarantee."""
    if not text or not text.strip():
        return

    # Try pausing wake listener so FRIDAY does not trigger on her own voice
    try:
        from app.audio.wakeword import wake_listener
        wake_listener.pause()
    except Exception:
        pass

    # Determine concise spoken sentence for fast 1-2s audio generation
    speech_line = spoken_text if spoken_text else prepare_spoken_summary(text)
    clean_line = clean_speech_text(speech_line)

    try:
        print(f"\n🤖 {config.BOT_NAME}: {clean_line}\n")
    except Exception:
        print(f"\n[{config.BOT_NAME}]: {clean_line}\n")

    unique_id = uuid.uuid4().hex[:8]
    temp_path = os.path.join(tempfile.gettempdir(), f"{config.BOT_NAME.lower()}_{unique_id}.mp3")

    try:
        # Generate neural speech audio via Edge-TTS (fast 1-2s generation for concise lines)
        asyncio.run(_generate_audio(clean_line, temp_path))

        # Play generated MP3 in perfect sync with HUD subtitle
        if os.path.exists(temp_path):
            _notify("speaking_start", clean_line)
            playsound(temp_path)
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[Speech interrupted]")
    except Exception as e:
        print(f"Edge-TTS Error ({e}). Activating offline female Windows TTS fallback...")
        _notify("speaking_start", clean_line)
        _fallback_windows_tts(clean_line)
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