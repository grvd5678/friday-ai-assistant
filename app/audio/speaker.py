import os
import sys
import re
import json
import uuid
import asyncio
import tempfile
import threading
import subprocess
import edge_tts
from playsound3 import playsound
from app.config import config

# Optional state callback for UI: callback(state: str, text: str = "")
_status_callback = None
_viseme_callback = None        # callback(frame: int) for phonetic lip sync
_avatar_video_callback = None  # callback(video_path: str) for optional video talking head

def set_speech_callback(callback):
    global _status_callback
    _status_callback = callback

def set_viseme_callback(callback):
    """Registers a callback that receives viseme frame index (0-5) at exact phoneme timing."""
    global _viseme_callback
    _viseme_callback = callback

def set_avatar_video_callback(callback):
    """Registers a callback that receives local MP4 path for video avatar head."""
    global _avatar_video_callback
    _avatar_video_callback = callback

def _notify(status: str, text: str = ""):
    if _status_callback:
        try:
            _status_callback(status, text)
        except Exception:
            pass

# Phoneme -> viseme frame mapping (0=closed, 1=slight, 2=medium, 3=wide, 4=O-shape, 5=smile)
# Based on standard English phoneme groups
_PHONEME_TO_FRAME = {
    # Silence / consonants (mouth nearly closed)
    "sil": 0, "_": 0,
    # Bilabial stops — lips together then burst open
    "p": 0, "b": 0, "m": 0,
    # Labiodental
    "f": 1, "v": 1,
    # Dental / alveolar
    "t": 1, "d": 1, "n": 1, "s": 1, "z": 1, "l": 1,
    # Postalveolar
    "sh": 2, "zh": 2, "ch": 2, "jh": 2,
    # Velar
    "k": 1, "g": 1, "ng": 1,
    # Glottal
    "h": 2,
    # Approximants
    "r": 2, "w": 4, "y": 2,
    # Vowels — open mouth
    "aa": 3, "ae": 3, "ah": 3, "aw": 3,
    "ay": 3, "eh": 2, "er": 2, "ey": 2,
    "ih": 2, "iy": 2, "ow": 4, "oy": 4,
    "uh": 2, "uw": 4,
    # Smile/open for common endings
    "th": 1, "dh": 1,
}

# Word-level viseme approximation — maps first char of word to a frame sequence
# Used as fallback when phoneme data isn't available
# Dynamic word-level phonetic viseme mapping
# 0 = Resting / Closed, 1 = Slight parted, 2 = Medium open, 3 = Wide vowel, 4 = Rounded O, 5 = Soft open smile
def _word_to_viseme_sequence(word: str) -> list:
    """Maps a word to a viseme frame sequence matching phonetic aperture and vowel strength."""
    if not word:
        return [0]
    w = word.lower().strip()
    if not w:
        return [0]

    first = w[0]
    # Rounded open vowels / labial-velar ('w', 'o', 'u') -> rounded O then medium
    if first in 'wo':
        return [4, 3, 2, 1]
    # Broad/loud open vowels ('a', 'e', 'i') -> wide open f3/f4, then resolve
    elif first in 'aei':
        return [2, 3, 4, 2] if len(w) > 3 else [2, 3, 1]
    elif first == 'u':
        return [4, 2, 1]
    # Bilabial stops ('b', 'm', 'p') -> lips close together (0) then open
    elif first in 'bmp':
        return [0, 1, 2, 1]
    # Labiodental ('f', 'v') -> teeth on lip (1)
    elif first in 'fv':
        return [1, 2, 1]
    # Sibilants & affricates ('s', 'z', 'x', 'c', 'j') -> tight parted (1)
    elif first in 'szxcj':
        return [1, 2, 1]
    # Alveolar & dental ('t', 'd', 'n', 'l')
    elif first in 'tdnl':
        return [1, 2, 1]
    # Velar & liquids ('k', 'g', 'r')
    elif first in 'kgr':
        return [1, 2, 1]
    # Glottal ('h')
    elif first == 'h':
        return [2, 3, 1]
    return [1, 2, 1]

async def _generate_audio_with_visemes(text: str, file_path: str) -> list:
    """
    Generates speech MP3 via Edge-TTS and captures WordBoundary events
    with their exact audio_offset (in 100-nanosecond units).
    Returns list of (offset_ms, viseme_frames) tuples.
    """
    voice = config.VOICE_NAME or "en-IE-EmilyNeural"
    viseme_schedule = []  # [(offset_ms, [frame, frame, ...])

    for attempt in range(2):
        try:
            communicate = edge_tts.Communicate(text, voice)
            audio_chunks = []

            async for event in communicate.stream():
                if event["type"] == "audio":
                    audio_chunks.append(event["data"])
                elif event["type"] == "WordBoundary":
                    # audio_offset is in 100-nanosecond ticks -> convert to ms
                    offset_ms = event["audio_offset"] / 10000
                    word = event.get("text", "")
                    frames = _word_to_viseme_sequence(word)
                    viseme_schedule.append((offset_ms, frames))

            # Write audio file
            with open(file_path, "wb") as f:
                for chunk in audio_chunks:
                    f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return viseme_schedule
        except Exception:
            if attempt == 1:
                raise
            await asyncio.sleep(0.3)

    return viseme_schedule

def _fire_viseme_schedule(schedule: list, stop_event: threading.Event):
    """
    Fires viseme frame callbacks at exact word boundary offsets.
    Pauses and silence between words automatically return to resting frame (0).
    Runs in a background thread alongside audio playback with 0ms lag.
    """
    if not schedule or not _viseme_callback:
        return

    import time
    start_time = time.perf_counter()

    for i, (offset_ms, frames) in enumerate(schedule):
        if stop_event.is_set():
            break

        # Wait until this word's offset
        target = start_time + (offset_ms / 1000.0)
        now = time.perf_counter()
        wait = target - now

        if wait > 0:
            # Silence / natural pause between words -> immediately close lips to resting frame 0
            if wait > 0.04:
                try:
                    _viseme_callback(0)
                except Exception:
                    pass
            stop_event.wait(timeout=wait)

        if stop_event.is_set():
            break

        # Fire each frame in the word's viseme sequence (approx 65ms per frame)
        frame_duration = 0.065
        for frame in frames:
            if stop_event.is_set():
                break
            try:
                _viseme_callback(frame)
            except Exception:
                pass
            stop_event.wait(timeout=frame_duration)

    # Return to resting frame immediately when speech finishes
    try:
        _viseme_callback(0)
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
    """Plays generated speech with phonetic viseme lip sync driven by Edge-TTS WordBoundary events."""
    if not text or not text.strip():
        return

    try:
        from app.audio.wakeword import wake_listener
        wake_listener.pause()
    except Exception:
        pass

    speech_line = spoken_text if spoken_text else prepare_spoken_summary(text)
    clean_line = clean_speech_text(speech_line)

    try:
        print(f"\n🤖 {config.BOT_NAME}: {clean_line}\n")
    except Exception:
        print(f"\n[{config.BOT_NAME}]: {clean_line}\n")

    unique_id = uuid.uuid4().hex[:8]
    temp_path = os.path.join(tempfile.gettempdir(), f"{config.BOT_NAME.lower()}_{unique_id}.mp3")
    stop_event = threading.Event()

    try:
        # Generate audio + capture WordBoundary viseme schedule simultaneously
        viseme_schedule = asyncio.run(_generate_audio_with_visemes(clean_line, temp_path))

        if os.path.exists(temp_path):
            _notify("speaking_start", clean_line)

            # Optional D-ID background talking video generator (if configured)
            if _avatar_video_callback and os.getenv("DID_API_KEY") and os.getenv("FRIDAY_FACE_URL"):
                def _bg_avatar(src_audio):
                    try:
                        from app.tools.avatar_tool import generate_talking_avatar
                        vid = generate_talking_avatar(src_audio)
                        if vid and _avatar_video_callback:
                            _avatar_video_callback(vid)
                    except Exception:
                        pass
                threading.Thread(target=_bg_avatar, args=(temp_path,), daemon=True).start()

            # Fire viseme frames in background thread, perfectly timed to audio
            if viseme_schedule and _viseme_callback:
                viseme_thread = threading.Thread(
                    target=_fire_viseme_schedule,
                    args=(viseme_schedule, stop_event),
                    daemon=True
                )
                viseme_thread.start()

            playsound(temp_path)  # blocks until audio finishes
            stop_event.set()      # stop viseme thread when audio ends

    except (KeyboardInterrupt, asyncio.CancelledError):
        stop_event.set()
        print("\n[Speech interrupted]")
    except Exception as e:
        stop_event.set()
        print(f"Edge-TTS Error ({e}). Activating offline Windows TTS fallback...")
        _notify("speaking_start", clean_line)
        _fallback_windows_tts(clean_line)
    finally:
        stop_event.set()
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        _notify("speaking_end", "")
        try:
            from app.audio.wakeword import wake_listener
            wake_listener.resume()
        except Exception:
            pass