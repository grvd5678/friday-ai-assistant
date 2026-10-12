# app/brain/greetings.py

import time
import random

TITLES = ["Boss", "Sir", "Mr. Gourav Das"]

def get_time_period() -> str:
    hour = time.localtime().tm_hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def get_random_title(prefer_formal: bool = False) -> str:
    if prefer_formal:
        return "Mr. Gourav Das"
    return random.choices(TITLES, weights=[0.5, 0.3, 0.2], k=1)[0]

def get_startup_greeting() -> str:
    period = get_time_period()
    t = get_random_title()

    if period == "morning":
        options = [
            f"Good morning, {t}. All systems are green and I'm fully operational. What are we building today?",
            f"Top of the morning to you, {t}. Diagnostics are clean, neural core is hot, and I'm standing by.",
            f"Morning, {t}. Coffee optional, but I'd recommend it — we've got work to do.",
            f"Good morning, {t}. Arc reactor's humming, tactical feed is live. Ready when you are.",
        ]
    elif period == "afternoon":
        options = [
            f"Good afternoon, {t}. Systems are running at peak efficiency. What's on the agenda?",
            f"Afternoon, {t}. I've been keeping an eye on things. All quiet on the tactical front.",
            f"Good afternoon, {t}. Ready to get back into it — just say the word.",
            f"Afternoon, {t}. HUD is primed, AI core is active. What do you need?",
        ]
    elif period == "evening":
        options = [
            f"Good evening, {t}. Systems nominal. Shall we review the day or dive into something new?",
            f"Evening, {t}. Still at it, I see. All diagnostics are green — I'm right here with you.",
            f"Good evening, {t}. The tactical feed is live and I'm fully operational. What are we working on tonight?",
            f"Evening, {t}. I've got the HUD warmed up and ready. What's the mission?",
        ]
    else:
        options = [
            f"Burning the midnight oil again, {t}? Systems are quiet and I'm right here.",
            f"Late night session, {t}? All diagnostics are clean. I'll keep the lights on.",
            f"Still going, {t}? Respect. I'm fully operational — what do you need?",
            f"Good evening, {t}. It's late, but I'm not going anywhere. What are we tackling?",
        ]

    return random.choice(options)

def get_wake_acknowledgment() -> str:
    t = get_random_title()
    options = [
        f"Right here, {t}.",
        f"Yes, {t}. Go ahead.",
        f"At your service, {t}. What do you need?",
        f"I'm listening, {t}.",
        f"Standing by, {t}.",
        f"On it — what's the command, {t}?",
        f"You've got my full attention, {t}.",
    ]
    return random.choice(options)

def get_arrival_greeting() -> str:
    t = get_random_title()
    options = [
        f"Welcome back to your workstation, {t}. Systems standing by.",
        f"Visual contact confirmed. Good to have you back, {t}.",
        f"There you are, {t}. I've kept everything warm for you.",
        f"Optical sensors confirm your presence, {t}. Ready when you are.",
        f"Back at the helm, {t}? All systems are green.",
    ]
    return random.choice(options)
