import re
import webbrowser
import urllib.parse
import requests
import wikipedia

def search_web(query: str) -> str:
    """Searches Google for a user's query in the default browser."""
    clean_query = query.strip()
    encoded_query = urllib.parse.quote(clean_query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return f"Searching Google for '{clean_query}', Boss."

def play_youtube(query: str) -> str:
    """Searches and opens a video or music query on YouTube."""
    clean_query = query.strip()
    encoded_query = urllib.parse.quote(clean_query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)
    return f"Playing '{clean_query}' on YouTube, Boss."

def get_wikipedia_summary(topic: str) -> str:
    """Retrieves a concise summary of any concept, person, historical event, or science topic from Wikipedia."""
    clean_topic = topic.strip()
    try:
        summary = wikipedia.summary(clean_topic, sentences=2, auto_suggest=True)
        return summary
    except wikipedia.DisambiguationError as e:
        try:
            return wikipedia.summary(e.options[0], sentences=2)
        except Exception:
            return f"Topic '{clean_topic}' has multiple meanings. Could you be more specific, Boss?"
    except wikipedia.PageError:
        return f"I couldn't find an exact encyclopedia article for '{clean_topic}', Boss."
    except Exception as e:
        return f"Encyclopedia lookup error: {str(e)}"

def get_weather(location: str = "") -> str:
    """Fetches real-time weather conditions, temperature, and wind for any city or current location."""
    clean_loc = location.strip()
    try:
        url_target = f"https://wttr.in/{urllib.parse.quote(clean_loc)}?format=Condition:+%C,+Temperature:+%t,+Wind:+%w"
        resp = requests.get(url_target, timeout=6)
        if resp.status_code == 200:
            raw_text = resp.text.strip()
            # Clean unicode wind arrows (\u2190-\u2199) and plus signs
            clean_text = re.sub(r'[\u2190-\u2199]', '', raw_text).replace('+', '').strip()
            loc_label = f"in {clean_loc.title()}" if clean_loc else "locally"
            return f"Current weather {loc_label}: {clean_text}."
        else:
            return "Unable to retrieve weather data at this moment, Boss."
    except Exception as e:
        return f"Weather service unavailable: {str(e)}"

if __name__ == "__main__":
    print(get_weather("London"))
    print(get_wikipedia_summary("Albert Einstein"))
