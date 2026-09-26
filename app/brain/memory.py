import os
import json
import time
from typing import List, Dict, Any, Optional
from app.config import config

class MemoryManager:
    """Manages short-term conversation context and persistent long-term memories for FRIDAY."""

    def __init__(self, memory_file: Optional[str] = None):
        self.memory_file = memory_file or config.MEMORY_FILE or "friday_memory.json"
        self.short_term_history: List[Dict[str, str]] = []
        self.max_short_term = 12
        self.long_term_data: Dict[str, Any] = {
            "user_profile": {
                "name": "Boss",
                "preferences": {}
            },
            "facts": [],
            "notes": []
        }
        self.load_memory()

    def load_memory(self):
        """Loads persistent memory from disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.long_term_data = json.load(f)
            except Exception as e:
                print(f"[Memory] Warning: Could not read memory file ({e}). Starting fresh.")

    def save_memory(self):
        """Persists memory data to disk safely."""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.long_term_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory] Error saving memory: {e}")

    # --- Short-term History ---
    def add_message(self, role: str, content: str):
        """Adds a message to the active conversational buffer."""
        self.short_term_history.append({"role": role, "content": content})
        if len(self.short_term_history) > self.max_short_term:
            self.short_term_history = self.short_term_history[-self.max_short_term:]

    def get_history(self) -> List[Dict[str, str]]:
        return self.short_term_history

    def clear_history(self):
        self.short_term_history = []

    # --- Long-term Persistent Memory ---
    def remember_fact(self, fact: str, category: str = "facts") -> str:
        """Stores a new fact or note into long-term memory."""
        clean_fact = fact.strip()
        if not clean_fact:
            return "No fact provided."

        entry = {
            "content": clean_fact,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if category not in self.long_term_data:
            self.long_term_data[category] = []

        # Avoid exact duplicates
        existing = [item["content"].lower() for item in self.long_term_data[category] if isinstance(item, dict) and "content" in item]
        if clean_fact.lower() in existing:
            return f"I already remember that: '{clean_fact}'"

        self.long_term_data[category].append(entry)
        self.save_memory()
        return f"I have stored that in my long-term memory: '{clean_fact}'"

    def recall_facts(self, query: str = "") -> List[str]:
        """Recalls all facts or filters facts relevant to a search query."""
        all_facts = []
        for cat in ["facts", "notes"]:
            items = self.long_term_data.get(cat, [])
            for item in items:
                text = item.get("content", "") if isinstance(item, dict) else str(item)
                if not query or query.lower() in text.lower():
                    all_facts.append(text)
        return all_facts

    def forget_fact(self, query: str) -> str:
        """Removes stored facts matching the query from long-term memory."""
        clean_query = query.lower().strip()
        if not clean_query:
            return "No query specified to forget."

        removed_count = 0
        for cat in ["facts", "notes"]:
            items = self.long_term_data.get(cat, [])
            new_items = []
            for item in items:
                text = item.get("content", "") if isinstance(item, dict) else str(item)
                if clean_query in text.lower():
                    removed_count += 1
                else:
                    new_items.append(item)
            self.long_term_data[cat] = new_items

        if removed_count > 0:
            self.save_memory()
            return f"I have removed {removed_count} memory entry matching '{query}', Boss."
        else:
            return f"No memories found matching '{query}', Boss."

    def set_user_pref(self, key: str, value: Any) -> str:
        """Sets a user preference in the profile."""
        if "user_profile" not in self.long_term_data:
            self.long_term_data["user_profile"] = {"name": "Boss", "preferences": {}}
        self.long_term_data["user_profile"]["preferences"][key] = value
        self.save_memory()
        return f"Preference '{key}' saved as '{value}'."

    def get_memory_context_prompt(self) -> str:
        """Formats remembered facts into a concise prompt prefix for the LLM."""
        facts = self.recall_facts()
        user_name = self.long_term_data.get("user_profile", {}).get("name", "Boss")
        prefs = self.long_term_data.get("user_profile", {}).get("preferences", {})

        parts = [f"USER CONTEXT:\n- Addressing user as: {user_name}"]
        if prefs:
            parts.append(f"- User preferences: {json.dumps(prefs)}")
        if facts:
            parts.append("- Long-term memories/facts you know about the user:")
            for f in facts[-10:]:  # Keep most recent 10 facts
                parts.append(f"  * {f}")
        return "\n".join(parts)

# Singleton memory manager instance
memory = MemoryManager()

def remember_fact(fact: str) -> str:
    """Stores a personal detail, preference, schedule item, or note into FRIDAY's long-term memory."""
    return memory.remember_fact(fact)

def recall_memories(query: str = "") -> str:
    """Searches and retrieves facts or notes stored in FRIDAY's long-term memory."""
    facts = memory.recall_facts(query)
    if not facts:
        return "I do not have any saved memories matching that request, Boss."
    return "Here is what I have on record:\n" + "\n".join(f"- {f}" for f in facts)

def forget_memory(query: str) -> str:
    """Removes a fact or note from FRIDAY's long-term memory."""
    return memory.forget_fact(query)
