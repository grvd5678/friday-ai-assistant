# app/tools/folder_guard.py
"""
Folder Access Guard for F.R.I.D.A.Y.
Enforces Gourav's 3-Tier Security Architecture:
- Tier 3: Strictly Forbidden (C:\\Windows, Program Files, .ssh, .env, credentials)
- Tier 2: Read-Only Study Materials & Project README.md Only
- Tier 1: Write allowed only to F.R.I.D.A.Y.'s own screenshots, memories, and exports
"""

import os
from typing import Tuple

# Tier 3: Forbidden directory fragments
FORBIDDEN_PATHS = [
    r"c:\windows",
    r"c:\program files",
    r"c:\program files (x86)",
    r"\.ssh",
    r"\.aws",
    r"\credentials",
    r"system32"
]

# Project folders where ONLY README.md / .md overview access is permitted
README_ONLY_PROJECTS = [
    "btech-final-year-project-main",
    "fake news detection",
    "friday-ai-assistant",
    "ml-t2-090-model-complexity",
    "myproject-1.0-main",
    "rag-doc-assistant",
    "swachh.ai",
    "finpulse-saas"
]

# D-Drive Study & Preparation Folders (Full Read & Analysis)
STUDY_FOLDERS = [
    "amazon web services",
    "aws re_start",
    "aws_restart",
    "full stack and machine learning",
    "placement  paper (tcs , wipro , accenture etc) lets code",
    "placement paper",
    "recordings",
    "it notes for interview"
]

def check_file_access(file_path: str, mode: str = "r") -> Tuple[bool, str]:
    """
    Evaluates whether F.R.I.D.A.Y. is authorized to access a given file path.
    Returns (is_allowed: bool, reason_or_message: str).
    """
    if not file_path:
        return False, "Invalid empty file path."

    norm_path = os.path.normpath(file_path).lower()
    base_name = os.path.basename(norm_path)

    # 1. Block any hidden environment / credential files
    if base_name == ".env" or base_name.startswith(".env."):
        return False, "Access denied: Environment configuration (.env) files are strictly protected, Boss."

    # 2. Block Tier 3 forbidden system directories
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in norm_path:
            return False, f"Access denied: '{forbidden}' is a protected system directory, Boss."

    # 3. Block unauthorized write operations outside Tier 1
    if mode in ["w", "a", "x", "w+"]:
        # Only allow writing inside friday-ai-assistant (screenshots, memories) or Friday_Exports
        if "friday-ai-assistant" in norm_path or "friday_exports" in norm_path or "pictures\\webcam" in norm_path:
            return True, "Authorized write path."
        return False, "Write access rejected: F.R.I.D.A.Y. operates in Read-Only mode outside her workspace, Boss."

    # 4. Check project folders (Strictly README.md only)
    for proj in README_ONLY_PROJECTS:
        if proj in norm_path:
            # Only allow markdown documentation (.md)
            if base_name == "readme.md" or norm_path.endswith(".md"):
                return True, "Authorized: Project README documentation access granted."
            else:
                return False, f"Access restricted: For project '{proj}', I am strictly authorized to read README.md only, Boss."

    # 5. Study Folders (Full read access)
    for study in STUDY_FOLDERS:
        if study in norm_path:
            return True, "Authorized: Study & interview preparation material access granted."

    # 6. Default allow read for standard user documents (resumes, pdfs, txt, docx)
    allowed_exts = [".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".png", ".jpg", ".jpeg"]
    ext = os.path.splitext(norm_path)[1]
    if ext in allowed_exts:
        return True, "Authorized: User document read access granted."

    return True, "Authorized access."

