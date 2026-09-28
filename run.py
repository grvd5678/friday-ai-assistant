"""Entrypoint alias for F.R.I.D.A.Y. AI Assistant with automatic virtual environment forwarding."""
import os
import sys
import subprocess

def _ensure_venv():
    """If executed with global Python instead of project venv, re-launch inside venv seamlessly."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        try:
            if os.path.samefile(sys.executable, venv_python):
                return
        except Exception:
            if os.path.abspath(sys.executable).lower() == os.path.abspath(venv_python).lower():
                return
        # Relaunch under venv
        result = subprocess.run([venv_python, os.path.join(project_dir, "main.py")] + sys.argv[1:])
        sys.exit(result.returncode)

if __name__ == "__main__":
    _ensure_venv()
    import main
    main.main()
