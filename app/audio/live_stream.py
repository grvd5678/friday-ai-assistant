import os
import sys
import time
import queue
import asyncio
import threading
import sounddevice as sd
from google import genai
from google.genai import types

from app.config import config
from app.brain.prompts import FRIDAY_SYSTEM_PROMPT

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class GeminiLiveStreamer:
    """
    Manages full-duplex bidirectional audio streaming with Gemini 3.1 Flash Live API.
    Supports real-time user interruptions and native 24kHz PCM audio playback.
    """

    def __init__(self, status_callback=None, text_callback=None):
        self.status_callback = status_callback
        self.text_callback = text_callback
        self._is_running = False
        self._thread = None
        self._loop = None
        self.audio_out_queue = queue.Queue()

    def start(self):
        """Starts live stream session in a background thread."""
        if not self._is_running:
            self._is_running = True
            self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """Halts the live stream session."""
        self._is_running = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    def _run_async_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._stream_session())
        except Exception as e:
            print(f"[Live Stream Loop Error]: {e}")
        finally:
            self._is_running = False
            if self.status_callback:
                self.status_callback("STANDBY", "LIVE MODE ENDED")

    async def _stream_session(self):
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        live_config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(
                parts=[types.Part(text=f"{FRIDAY_SYSTEM_PROMPT}\nYou are in LIVE CONVERSATION mode. Keep all spoken answers to 1-2 sharp, conversational sentences. Address the user as Boss.")]
            ),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                )
            )
        )

        audio_in_queue = asyncio.Queue()
        audio_out_queue = queue.Queue()

        # Mic input callback (16kHz PCM)
        def mic_callback(indata, frames, time_info, status):
            if self._is_running:
                # Put raw 16kHz PCM bytes into async queue
                audio_in_queue.put_nowait(bytes(indata))

        # Audio playback worker (24kHz PCM)
        def playback_worker():
            try:
                with sd.RawOutputStream(samplerate=24000, channels=1, dtype='int16') as out_stream:
                    while self._is_running:
                        try:
                            data = audio_out_queue.get(timeout=0.2)
                            if data:
                                out_stream.write(data)
                        except queue.Empty:
                            continue
            except Exception as e:
                print(f"[Playback Worker Error]: {e}")

        playback_thread = threading.Thread(target=playback_worker, daemon=True)
        playback_thread.start()

        if self.status_callback:
            self.status_callback("LISTENING", "LIVE DUPLEX STREAM ACTIVE")

        # Select mic device
        device_idx = int(config.MIC_INDEX) if config.MIC_INDEX and config.MIC_INDEX.isdigit() else None

        print("\n" + "="*58)
        print("🎙️ GEMINI LIVE STREAM ONLINE — REAL-TIME DUPLEX VOICE")
        print("⚡ Speak naturally. You can interrupt FRIDAY anytime mid-sentence.")
        print("="*58 + "\n")

        try:
            with sd.RawInputStream(samplerate=16000, channels=1, dtype='int16', device=device_idx, blocksize=1024, callback=mic_callback):
                async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=live_config) as session:
                    
                    # Task 1: Continuously stream microphone to Gemini
                    async def send_mic():
                        while self._is_running:
                            try:
                                chunk = await audio_in_queue.get()
                                await session.send_realtime_input(
                                    audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                                )
                            except Exception:
                                break

                    # Task 2: Continuously receive response from Gemini
                    async def receive_stream():
                        async for response in session.receive():
                            if not self._is_running:
                                break

                            server_content = response.server_content
                            if server_content:
                                # Interruption: clear audio playback queue immediately!
                                if server_content.interrupted:
                                    print("\n⚡ [Live] Interruption detected. Pivoting to user...")
                                    while not audio_out_queue.empty():
                                        try:
                                            audio_out_queue.get_nowait()
                                        except Exception:
                                            break
                                    if self.status_callback:
                                        self.status_callback("LISTENING", "LISTENING...")
                                    continue

                                # Audio turn
                                if server_content.model_turn:
                                    if self.status_callback:
                                        self.status_callback("SPEAKING", "FRIDAY IS SPEAKING...")
                                    for part in server_content.model_turn.parts:
                                        if part.inline_data and part.inline_data.data:
                                            audio_out_queue.put(part.inline_data.data)

                                # Transcriptions
                                if server_content.output_transcription and server_content.output_transcription.text:
                                    trans_text = server_content.output_transcription.text
                                    print(f"🤖 FRIDAY: {trans_text}", end="\r")
                                    if self.text_callback:
                                        self.text_callback(trans_text)

                                if server_content.turn_complete:
                                    if self.status_callback:
                                        self.status_callback("LISTENING", "LISTENING...")

                    await asyncio.gather(send_mic(), receive_stream())

        except Exception as e:
            print(f"[Live Session Error]: {e}")
        finally:
            self._is_running = False

# Global instance
live_streamer = GeminiLiveStreamer()

def start_live_mode(status_callback=None, text_callback=None):
    """Starts live bidirectional streaming session."""
    if status_callback:
        live_streamer.status_callback = status_callback
    if text_callback:
        live_streamer.text_callback = text_callback
    live_streamer.start()
    return "Gemini Live mode activated, Boss. We are now in full duplex live voice streaming. Speak freely."

def stop_live_mode():
    """Stops live bidirectional streaming session."""
    live_streamer.stop()
    return "Gemini Live mode deactivated, Boss. Returning to standard standby."

if __name__ == "__main__":
    def on_stat(s, t): print(f"[{s}] {t}")
    start_live_mode(status_callback=on_stat)
    time.sleep(15)
    stop_live_mode()
