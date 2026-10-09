# app/brain/greetings.py
"""
Dynamic Marvel-style greetings and salutations for F.R.I.D.A.Y.
Adapts time of day, varies titles ('Boss', 'Sir', 'Mr. Gourav Das'),
and provides natural conversational wake acknowledgments.
"""

import time
import random

TITLES = ["Boss", "Sir", "Mr. Gourav Das"]

def get_time_period() -> str:
    """Returns 'morning', 'afternoon', 'evening', or 'night' based on system clock."""
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
    """Selects an appropriate respectful title."""
    if prefer_formal:
        return "Mr. Gourav Das"
    # Weighted selection: Boss (50%), Sir (30%), Mr. Gourav Das (20%)
    return random.choices(TITLES, weights=[0.5, 0.3, 0.2], k=1)[0]

def get_startup_greeting(user_name: str = "Mr. Gourav Das") -> str:
    """
    Generates a charismatic, time-aware greeting upon system launch.
    Marvel F.R.I.D.A.Y. style: tactical, sharp, and aware of outside world time.
    """
    period = get_time_period()
    title = get_random_title()

    if period == "morning":
        options = [
            f"Good morning, {title}. All tactical systems are online and operational. How may I assist you today?",
            f"Top of the morning to you, {title}. Diagnostics are green and standing by. What are we tackling first?",
            f"Good morning, {user_name}. Systems initialized. Standing by for your command."
        ]
    elif period == "afternoon":
        options = [
            f"Good afternoon, {title}. All systems are active and running at peak performance. What's on the agenda?",
            f"Good afternoon, {title}. Tactical HUD is primed and standing by. How can I help you?",
            f"Good afternoon, {user_name}. Ready for today's tasks and interview preparations."
        ]
    elif period == "evening":
        options = [
            f"Good evening, {title}. All workstation diagnostics are nominal. What are we working on tonight?",
            f"Good evening, {title}. Systems standing by. Shall we review your projects or continue your study sessions?",
            f"Good evening, {user_name}. All systems operational and ready for your command."
        ]
    else: # night
        options = [
            f"Burning the midnight oil, {title}? Systems are active, quiet, and standing by.",
            f"Working late tonight, {title}? All diagnostics look clean. How may I assist you?",
            f"Good evening, {user_name}. All quiet on the tactical feed. Standing by for your instructions."
        ]

    return random.choice(options)

def get_wake_acknowledgment() -> str:
    """Returns a short, natural acknowledgment when user says 'Hey Friday' or wake word."""
    title = get_random_title()
    options = [
        f"Yes {title}, I'm listening.",
        f"Right here, {title}.",
        f"At your service, {title}.",
        f"Standing by, {title}. What do you need?",
        f"Go ahead, {title}."
    ]
    return random.choice(options)

def get_arrival_greeting() -> str:
    """Returns an arrival salutation when optical face presence detects user sitting down."""
    title = get_random_title()
    options = [
        f"Welcome back to your workstation, {title}. Systems standing by.",
        f"Visual contact verified. Good to see you, {title}.",
        f"Workstation unlocked and ready, {title}."
    ]
    return random.choice(options)

