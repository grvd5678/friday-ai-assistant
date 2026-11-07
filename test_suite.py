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

    def test_prepare_spoken_summary(self):
        """Verify that long resume or markdown text is distilled into a crisp 1-2 sentence spoken summary."""
        from app.audio.speaker import prepare_spoken_summary
        long_resume = (
            "Top of the morning to you, Boss. I have your resume locked in and scanned–looks like "
            "you've been putting together quite a tidy profile in AI and Cloud Engineering. "
            "Here is the breakdown: ### **CANDIDATE OVERVIEW** * **NAME:** Gourav Das * **ROLE:** AI Engineer "
            "--- ### **PROJECTS** 1. RAG Assistant. 2. Fake News Detection. 3. Blockchain."
        )
        summary = prepare_spoken_summary(long_resume)
        self.assertLess(len(summary.split()), 45)
        self.assertIn("Tactical Feed", summary)
        self.assertNotIn("###", summary)
    def test_today_fast_path(self):
        """Verify 'ok can you tell me today' returns current date and accurate telemetry without hallucinations."""
        from app.brain.llm import ask_friday
        import time
        res = ask_friday("ok can you tell me today")
        current_year = str(time.localtime().tm_year)
        self.assertIn("Boss", res)
        self.assertIn(current_year, res)
        self.assertNotIn("2023", res)

    def test_weather_fast_path(self):
        """Verify weather queries return compact live telemetry without roleplay asterisks."""
        from app.brain.llm import ask_friday
        res = ask_friday("today's weather")
        self.assertNotIn("*gets weather update*", res)
        self.assertNotIn("*", res)
        self.assertTrue(len(res) > 0)

    def test_document_session_flow(self):
        """Verify document session lifecycle: setting, querying active doc, and clearing."""
        from app.tools.document_tool import set_active_document, get_active_document, clear_active_document
        
        # Test file
        test_file = os.path.abspath(__file__)
        set_active_document(test_file)
        
        active = get_active_document()
        self.assertEqual(active["path"], test_file)
        self.assertEqual(active["name"], os.path.basename(test_file))
        self.assertIsNotNone(active["text"])
        
        clear_active_document()
        cleared = get_active_document()
        self.assertIsNone(cleared["path"])

    def test_dynamic_greetings(self):
        """Verify dynamic greetings, time-of-day awareness, and grounded salutations."""
        from app.brain.greetings import get_time_period, get_startup_greeting, get_wake_acknowledgment
        period = get_time_period()
        self.assertIn(period, ["morning", "afternoon", "evening", "night"])

        greeting = get_startup_greeting()
        self.assertTrue(isinstance(greeting, str) and len(greeting) > 10)

        ack = get_wake_acknowledgment()
        self.assertTrue(isinstance(ack, str) and len(ack) > 3)

    def test_app_launcher_robustness(self):
        """Verify app launcher handles URI protocols, URLs, and commands without shell crashes."""
        from app.tools.system_control import open_app
        # Safe command injection rejection
        bad = open_app("notepad & calc")
        self.assertIn("rejected", bad.lower())

        # Protocol launcher check
        res_spot = open_app("spotify")
        self.assertTrue("opening spotify" in res_spot.lower() or "launch" in res_spot.lower())

    def test_folder_guard_security(self):
        """Verify Gourav's 3-Tier security model: system files blocked, .env protected, project README-only."""
        from app.tools.folder_guard import check_file_access
        
        # 1. Tier 3: System files blocked
        allowed_sys, _ = check_file_access(r"C:\Windows\System32\cmd.exe")
        self.assertFalse(allowed_sys)

        # 2. Tier 3: Environment file protected
        allowed_env, _ = check_file_access(r"D:\Python\friday-ai-assistant\.env")
        self.assertFalse(allowed_env)

        # 3. Project folder: source code blocked (README-only rule)
        allowed_code, msg_code = check_file_access(r"D:\Python\Swachh.ai\model.py")
        self.assertFalse(allowed_code)
        self.assertIn("readme.md only", msg_code.lower())

        # 4. Project folder: README.md authorized
        allowed_readme, _ = check_file_access(r"D:\Python\Swachh.ai\README.md")
        self.assertTrue(allowed_readme)

        # 5. D-Drive study material: authorized
        allowed_study, _ = check_file_access(r"D:\Amazon Web Services\Cloud_Practitioner_Notes.pdf")
        self.assertTrue(allowed_study)

    def test_interview_coach_lifecycle(self):
        """Verify interview coach initialization, active tracking, and conclusion."""
        from app.tools.interview_coach import (
            start_mock_interview,
            is_interview_active,
            end_mock_interview
        )
        q = start_mock_interview("projects")
        self.assertTrue(is_interview_active())
        self.assertTrue(len(q) > 0)

        end_msg = end_mock_interview()
        self.assertFalse(is_interview_active())
        self.assertIn("concluded", end_msg.lower())

if __name__ == "__main__":
    unittest.main()

