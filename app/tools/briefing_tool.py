import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from app.config import config
from app.brain.memory import memory
from app.tools.sys_info import get_datetime_info, get_battery_status
from app.tools.web_search import get_weather

def get_top_headlines(limit: int = 2) -> list:
    """Fetches top news headlines from Google News RSS feed."""
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    headlines = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item"):
                title = item.find("title")
                if title is not None and title.text:
                    clean_title = title.text.split(" - ")[0].strip()
                    headlines.append(clean_title)
                    if len(headlines) >= limit:
                        break
    except Exception:
        headlines = ["Global tech developments remain active today."]
    return headlines

def get_morning_briefing() -> str:
    """Generates a crisp 30-second morning tactical briefing for the user."""
    # 1. Date & Time
    dt_info = get_datetime_info()
    
    # 2. Weather
    try:
        weather_info = get_weather()
    except Exception:
        weather_info = "Weather telemetry currently unavailable."

    # 3. Battery
    bat_info = get_battery_status()

    # 4. Top Headlines
    headlines = get_top_headlines(limit=2)
    news_text = " Additionally: " + "; ".join(headlines) if headlines else ""

    # 5. Long-term memory / Reminders
    facts = memory.long_term_data.get("facts", [])
    notes = memory.long_term_data.get("notes", [])
    reminders_list = [
        f.get("fact", "").strip() for f in facts if isinstance(f, dict) and f.get("fact", "").strip()
    ] + [
        n.get("note", "").strip() for n in notes if isinstance(n, dict) and n.get("note", "").strip()
    ]
    if reminders_list:
        reminders = f" You have {len(reminders_list)} items in memory: " + "; ".join(reminders_list[:2]) + "."
    else:
        reminders = " No pending reminders stored in memory."

    briefing = (
        f"Good day, Boss. All systems are online and operational. {dt_info}. "
        f"{weather_info}. {bat_info}. "
        f"In top headlines: {news_text}. "
        f"{reminders} "
        f"Standing by for your instructions."
    )
    return briefing

if __name__ == "__main__":
    print(get_morning_briefing())
