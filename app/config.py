import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_NAME = os.getenv("BOT_NAME", "FRIDAY")
    VOICE_NAME = os.getenv("FRIDAY_VOICE", "en-IE-EmilyNeural")  # Authentic Irish female neural AI voice
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    MEMORY_FILE = os.getenv("MEMORY_FILE", "friday_memory.json")
    MIC_INDEX = int(os.getenv("MIC_INDEX")) if os.getenv("MIC_INDEX", "").strip().isdigit() else None
    MIC_THRESHOLD = int(os.getenv("MIC_THRESHOLD")) if os.getenv("MIC_THRESHOLD", "").strip().isdigit() else 35

config = Config()