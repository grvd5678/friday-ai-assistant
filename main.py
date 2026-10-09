import sys
import os

# Ensure Windows terminal handles UTF-8 emojis without charmap encoding crashes
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from app.config import config
from app.brain.llm import ask_friday
from app.audio.speaker import speak
from app.audio.listener import listen
from app.audio.wakeword import wake_listener
from app.brain.greetings import get_startup_greeting, get_wake_acknowledgment

def run_cli():
    """Runs FRIDAY in interactive terminal mode."""
    print("\n" + "="*58)
    print(f"🤖 {config.BOT_NAME} 3.0 SYSTEM ONLINE & OPERATIONAL (CLI MODE)")
    print("="*58 + "\n")
    
    greeting = get_startup_greeting()
    speak(greeting)

    # Start wake word listener in background
    def on_wake(phrase):
        print(f"\n✨ Wake phrase detected: '{phrase}'. Activating microphone...")
        clean = phrase.lower().strip()
        pure_greetings = {"hello", "hey", "hi", "friday", "hey friday", "hi friday", "hello friday", "ok friday", "wake up", "are you there"}
        if clean not in pure_greetings and len(clean.split()) > 2:
            print(f"⚡ Processing: '{phrase}'...")
            reply = ask_friday(phrase)
            speak(reply)
        else:
            ack = get_wake_acknowledgment()
            speak(ack)
            voice_query = listen()
            if voice_query:
                print(f"⚡ Processing: '{voice_query}'...")
                reply = ask_friday(voice_query)
                speak(reply)

    wake_listener.start(on_wake)

    while True:
        try:
            print(f"\nOptions: Press [ENTER] to use Mic, or type your query below. (Or say 'Hey {config.BOT_NAME}')")
            user_input = input(f"👤 You (Type or press Enter for Mic): ").strip()

            # If user pressed Enter without typing, try microphone
            if not user_input:
                user_input = listen()

            # Exit commands
            if user_input and user_input.lower() in ["exit", "quit", "goodbye", "bye", "shutdown"]:
                speak("Goodbye, Boss. Powering down systems.")
                wake_listener.stop()
                break

            if not user_input:
                continue

            print(f"⚡ Processing: '{user_input}'...")
            response = ask_friday(user_input)
            speak(response)

        except KeyboardInterrupt:
            print(f"\nShutting down {config.BOT_NAME}...")
            wake_listener.stop()
            speak("Goodbye, Boss.")
            break
        except Exception as e:
            print(f"System Error: {e}")

def main():
    # If user passes --cli or --console, launch terminal mode
    if "--cli" in sys.argv or "--console" in sys.argv:
        run_cli()
    else:
        # Default: Launch the Futuristic Sci-Fi Holographic HUD
        try:
            from app.ui.hud_app import launch_hud
            launch_hud()
        except Exception as e:
            print(f"GUI launch encountered: {e}. Falling back to CLI mode...")
            run_cli()

if __name__ == "__main__":
    main()