"""
Check available Gemini models in your Google API.
"""
import sys
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("🔍 Checking available Gemini models...\n")
try:
    models = client.models.list()
    
    print("✅ Available Models:")
    model_names = []
    for model in models:
        model_names.append(model.name)
        print(f"  - {model.name}")
    
    print("\n💡 Recommended for FRIDAY:")
    if "models/gemini-2.5-flash" in model_names:
        print("  ✅ gemini-2.5-flash")
    if "models/gemini-3.5-flash-lite" in model_names:
        print("  ✅ gemini-3.5-flash-lite (Active)")
    if "models/gemini-3.5-flash" in model_names:
        print("  ✅ gemini-3.5-flash")
        
except Exception as e:
    print(f"❌ Error: {e}")
