import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import config
from app.audio.speaker import clean_speech_text
from app.brain.memory import memory, remember_fact, recall_memories, forget_memory
from app.tools.system_control import open_app, close_app
from app.tools.document_tool import extract_text_from_plain, analyze_document

class TestFridayCore(unittest.TestCase):

    def test_config_loaded(self):
        """Verify essential configuration defaults."""
        self.assertEqual(config.BOT_NAME, "FRIDAY")
        self.assertTrue(bool(config.VOICE_NAME))
        self.assertIn("Emily", config.VOICE_NAME)

    def test_clean_speech_text(self):
        """Verify markdown syntax is stripped for natural TTS pronunciation."""
        raw = "Hello **Boss**! Check this `code` and [link](http://test.com)."
        cleaned = clean_speech_text(raw)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("`", cleaned)
        self.assertNotIn("[link]", cleaned)
        self.assertIn("Hello Boss! Check this code and link.", cleaned)

    def test_system_control_security_guard(self):
        """Verify command injection attempts are safely rejected."""
        # Attempt command injection in close_app
        bad_proc = "notepad.exe; calc.exe"
        res = close_app(bad_proc)
        self.assertIn("rejected", res.lower())

        # Attempt protected system process termination
        res_sys = close_app("csrss.exe")
        self.assertIn("protected", res_sys.lower())

        # Attempt command injection in open_app
        bad_app = "notepad & dir"
        res_open = open_app(bad_app)
        self.assertIn("rejected", res_open.lower())

    def test_memory_engine(self):
        """Verify fact retention, retrieval, and forgetting."""
        test_fact = "Test fact: Stark Tower energy level is 100%"
        rem_res = remember_fact(test_fact)
        self.assertTrue("stored" in rem_res.lower() or "remember" in rem_res.lower())

        recall_res = recall_memories("Stark Tower")
        self.assertIn("Stark Tower", recall_res)

        forget_res = forget_memory("Stark Tower")
        self.assertIn("removed", forget_res.lower())

    def test_document_tool_safety(self):
        """Verify document analyzer handles non-existent files gracefully."""
        res = analyze_document("non_existent_file_12345.pdf", "What is this?")
        self.assertIn("cannot find the file", res.lower())

    def test_capability_fast_path(self):
        """Verify capabilities question returns immediate concise tactical overview."""
        from app.brain.llm import ask_friday
        res = ask_friday("what tasks can you do")
        self.assertIn("tactical AI assistant", res)
        self.assertIn("Boss", res)

if __name__ == "__main__":
    unittest.main()
