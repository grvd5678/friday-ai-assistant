"""
Interactive Microphone Diagnostic & Level Tester for FRIDAY.
"""
import sys
import os
import time

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import speech_recognition as sr
import pyaudio
import numpy as np

def test_device(device_index, device_name):
    print("\n" + "="*60)
    dev_label = f"Device {device_index}: {device_name}" if device_index is not None else f"Default Mic ({device_name})"
    print(f"🎙️  TESTING: {dev_label}")
    print("="*60)
    print("👉 Speak into this microphone NOW for 3 seconds...")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 60
    recognizer.dynamic_energy_threshold = False

    try:
        mic = sr.Microphone(device_index=device_index)
        with mic as source:
            audio = recognizer.record(source, duration=3.0)

        raw = audio.get_raw_data()
        data = np.frombuffer(raw, dtype=np.int16)
        peak = int(np.max(np.abs(data)))
        rms = int(np.sqrt(np.mean(data.astype(np.float64)**2)))

        bars = min(30, int(peak / 200))
        meter = "█" * bars + "░" * (30 - bars)
        print(f"📊 Volume Peak: {peak:5d}  |  RMS: {rms:4d}  [{meter}]")

        if peak > 200:
            print("⚡ Transcribing recorded audio via Google...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"✅ Transcribed Successfully: \"{text}\"")
                print(f"🎯 RECOMMENDATION: Use MIC_INDEX={device_index if device_index is not None else ''} in .env!")
                return True
            except sr.UnknownValueError:
                print("⚠️  Audio detected, but speech was unclear. Try speaking closer to mic.")
            except Exception as e:
                print(f"⚠️  Transcription error: {e}")
        else:
            print("❌ Low signal. This microphone is either muted, very quiet, or not active.")

    except Exception as e:
        print(f"❌ Could not open device: {e}")

    return False

def main():
    print("\n🔍 F.R.I.D.A.Y. Microphone Diagnostic Utility")
    print("Scanning valid input recording devices...\n")

    p = pyaudio.PyAudio()
    valid_devices = []
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                valid_devices.append((i, info.get("name", f"Device {i}")))
        except Exception:
            pass
    p.terminate()

    # Test Default Mic first
    test_device(None, "System Default")

    # Test valid input devices
    seen = set()
    for idx, name in valid_devices:
        clean_name = name.split("(")[0].strip()
        if clean_name not in seen:
            seen.add(clean_name)
            time.sleep(0.5)
            test_device(idx, name)

    print("\n" + "="*60)
    print("💡 To lock in the working microphone:")
    print("   Add 'MIC_INDEX=<number>' in your .env file.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
