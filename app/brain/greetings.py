# app/brain/greetings.py
"""
Dynamic, grounded greetings and salutations for F.R.I.D.A.Y.
Calm, warm, capable, and attentive to real-world time.
Avoids repetitive or dramatic honorifics.
"""

import time
import random

TITLES = ["Gourav", "Boss", "Sir", ""]

def get_random_title(prefer_formal: bool = False) -> str:
    """Returns a natural title or empty string for calm, steady addressing."""
    if prefer_formal:
        return "Gourav"
    return random.choices(TITLES, weights=[0.4, 0.2, 0.1, 0.3], k=1)[0]

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

def get_startup_greeting() -> str:
    """
    Generates a calm, warm, and attentive greeting upon system launch.
    Reflects the steady presence of a thoughtful personal assistant.
    """
    period = get_time_period()

    if period == "morning":
        options = [
            "Good morning. All systems are initialized and running smoothly. What are we working on today?",
            "Morning, Gourav. Neural core is active and ready when you are.",
            "Good morning. Diagnostics look clean across the board. Standing by for instructions.",
            "Top of the morning to you. Systems are green and ready for whatever's on the agenda today.",
        ]
    elif period == "afternoon":
        options = [
            "Good afternoon. Systems are running smoothly. What can I help you tackle?",
            "Afternoon, Gourav. Everything is in order and standing by.",
            "Good afternoon. Tactical feed is active and systems are ready when you are.",
            "Afternoon. Keeping tabs on system diagnostics. Let me know what you need.",
        ]
    elif period == "evening":
        options = [
            "Good evening. All diagnostics are nominal. Shall we review your tasks or dive into something new?",
            "Evening, Gourav. Systems are running quietly in the background. Ready for your command.",
            "Good evening. All quiet on the system front. How can I assist you tonight?",
            "Evening. HUD is active and responsive. What's on your mind?",
        ]
    else:  # night
        options = [
            "Working late tonight? Systems are quiet and steady. I'm right here if you need anything.",
            "Late night session, Gourav. Diagnostics are clean. Let me know how I can help.",
            "Burning the midnight oil? All systems operational and standing by.",
            "Good evening. It's late, but everything is green and ready when you need me.",
        ]

    return random.choice(options)

def get_wake_acknowledgment() -> str:
    """Returns a short, calm, attentive response when awakened."""
    options = [
        "Right here.",
        "I'm listening, Gourav.",
        "Yes, go ahead.",
        "Ready when you are.",
        "Standing by.",
        "How can I help?",
        "Listening.",
    ]
    return random.choice(options)

def get_arrival_greeting() -> str:
    """Returns a gentle, respectful arrival salutation when user arrives at workstation."""
    options = [
        "Welcome back to your workstation. Systems are ready.",
        "Good to have you back, Gourav. All diagnostics are green.",
        "Workstation active and standing by.",
        "Visual contact confirmed. Ready whenever you are.",
    ]
    return random.choice(options)

