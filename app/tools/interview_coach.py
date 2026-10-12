# app/tools/interview_coach.py
"""
Personalized Interview Coach Engine for F.R.I.D.A.Y.
Conducts realistic technical, project-based, and behavioral mock interviews
using Gourav's resume, project READMEs, AWS study notes, and placement papers.
"""

import os
from app.config import config
from app.tools.folder_guard import check_file_access
from google import genai

_client = None

def _get_client():
    global _client
    if _client is None and config.GEMINI_API_KEY:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

# Session state for active interview practice
_interview_state = {
    "is_active": False,
    "topic": "projects",
    "current_question": "",
    "question_history": [],
    "cached_resume_text": "",
    "cached_project_context": {}
}

D_DRIVE_PROJECTS = {
    "swachh.ai": r"D:\Python\Swachh.ai\README.md",
    "rag-doc-assistant": r"D:\Python\rag-doc-assistant\README.md",
    "fake news detection": r"D:\Python\Fake News Detection\README.md",
    "finpulse-saas": r"D:\finpulse-saas\README.md",
    "btech-final-year-project": r"D:\Python\btech-final-year-project-main\README.md",
    "model complexity": r"D:\Python\ML-T2-090-Model-Complexity\README.md"
}

def load_project_readme(project_key: str) -> str:
    """Safely loads a project's README.md if authorized by FolderGuard."""
    path = D_DRIVE_PROJECTS.get(project_key.lower().strip())
    if not path or not os.path.exists(path):
        return ""
    
    allowed, msg = check_file_access(path, mode="r")
    if not allowed:
        return ""
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:5000]
    except Exception:
        return ""

def get_resume_path() -> str:
    """Locates Gourav's resume in D:\\ or standard paths."""
    candidates = [
        r"D:\Gourav_Das_Resume_.pdf",
        r"D:\Gourav_Das_RESUME.docx",
        os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Gourav_Das_Resume_.pdf"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Gourav_Das_Resume_.pdf")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return ""

def start_mock_interview(topic: str = "projects") -> str:
    """
    Initiates an interactive mock interview round.
    Supported topics: 'projects', 'aws', 'machine learning', 'placement', 'behavioral'.
    """
    global _interview_state
    _interview_state["is_active"] = True
    _interview_state["topic"] = topic.lower().strip()

    # Pre-load context
    context = ""
    t = _interview_state["topic"]

    if "project" in t:
        # Load Swachh.ai & RAG project overviews
        swachh_readme = load_project_readme("swachh.ai")
        rag_readme = load_project_readme("rag-doc-assistant")
        context = f"Candidate's Projects:\nSwachh.ai:\n{swachh_readme[:1500]}\n\nRAG Assistant:\n{rag_readme[:1500]}"
        prompt_instruction = "Ask a challenging technical interview question about one of Gourav's projects (e.g. Swachh.ai computer vision pipeline or RAG document retrieval chunking/latency)."

    elif "aws" in t or "cloud" in t:
        context = "Focus on AWS Cloud architecture: S3, EC2, Lambda, IAM, VPC, and serverless scalability."
        prompt_instruction = "Ask an AWS Cloud Engineer interview question testing real-world cloud design."

    elif "ml" in t or "machine learning" in t:
        context = "Focus on Machine Learning, Overfitting, Model Complexity, Evaluation Metrics, and LLMs."
        prompt_instruction = "Ask an AI/Machine Learning Engineer technical interview question."

    elif "placement" in t or "tcs" in t or "wipro" in t or "accenture" in t:
        context = "Focus on campus placement questions (Core CS fundamentals: OOP, DBMS, SQL, Data Structures, Operating Systems)."
        prompt_instruction = "Ask a campus placement interview question frequently asked by TCS, Wipro, or Accenture."

    else: # Behavioral / HR
        context = "Focus on behavioral questions using the STAR framework (Situation, Task, Action, Result)."
        prompt_instruction = "Ask a behavioral question about handling tight deadlines, working in teams, or debugging a complex roadblock."

    tactical_prompt = (
        f"You are F.R.I.D.A.Y., Gourav's elite AI career coach and technical interviewer with a charismatic Irish persona.\n"
        f"Context:\n{context}\n\n"
        f"Task:\n{prompt_instruction}\n"
        f"Start with a warm, motivating 1-sentence greeting addressing Boss or Mr. Gourav Das, introduce the interview round ({t.upper()}), and ask the question directly. Keep it crisp (2 to 3 sentences total)."
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[tactical_prompt]
        )
        question = response.text.strip() if response and response.text else "Let's begin, Boss. Tell me about the core architecture of your Swachh.ai project and how you handled image classification."
    except Exception:
        question = f"All systems set for your {t.upper()} interview, Boss. To kick things off: Can you explain the system architecture and key design challenges in your Swachh.ai and RAG projects?"

    _interview_state["current_question"] = question
    _interview_state["question_history"].append(question)
    return question

def evaluate_interview_answer(answer: str) -> str:
    """
    Evaluates Gourav's spoken or typed answer to the current interview question.
    Gives a constructive critique, score, and poses the next follow-up question.
    """
    global _interview_state
    if not _interview_state["current_question"]:
        return "We don't have an active question right now, Boss. Say 'Start mock interview' to begin a session."

    question = _interview_state["current_question"]
    topic = _interview_state["topic"]

    eval_prompt = (
        f"You are F.R.I.D.A.Y., Gourav's elite technical interview coach with an Irish female persona.\n"
        f"Question Asked: {question}\n"
        f"Candidate's Answer: {answer}\n\n"
        f"Please provide an authentic, encouraging, and razor-sharp interview evaluation:\n"
        f"1. Score (e.g. 8.5/10) with a quick 1-sentence praise.\n"
        f"2. Key Strengths: What was answered well.\n"
        f"3. High-Value Improvements: What technical keywords, metrics, or STAR details would turn this into a 10/10 hire.\n"
        f"4. Next Follow-up Question to push him further.\n"
        f"Format with clean markdown, keeping spoken introduction addressing Boss or Mr. Gourav Das."
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[eval_prompt]
        )
        critique = response.text.strip() if response and response.text else "Solid response, Boss! Next: How would you monitor this system in production?"
    except Exception as e:
        critique = f"Good effort, Boss. You covered the main ideas, but remember to mention specific metrics. Error reaching evaluator: {e}"

    # Extract follow-up question if any
    _interview_state["current_question"] = "What follow-up improvements would you deploy next?"
    return critique

def end_mock_interview() -> str:
    """Ends the active interview session."""
    global _interview_state
    _interview_state["is_active"] = False
    _interview_state["current_question"] = ""
    return "Mock interview session concluded, Boss. You did great work today. Standing by whenever you're ready for another round."

def is_interview_active() -> bool:
    """Returns True if user is currently in a mock interview session."""
    return _interview_state.get("is_active", False)

