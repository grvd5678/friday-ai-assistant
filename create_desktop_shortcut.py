import os
import sys
import subprocess

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def create_shortcut():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    pythonw_path = os.path.join(project_dir, "venv", "Scripts", "pythonw.exe")
    main_script = os.path.join(project_dir, "main.py")
    ico_path = os.path.join(project_dir, "friday.ico")

    # In modern Windows 11, VBScript is disabled.
    # pythonw.exe is a native GUI executable, so pointing the shortcut directly to pythonw.exe
    # launches FRIDAY completely silently with ZERO black console window and ZERO VBScript dependencies!
    ps_cmd = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $DesktopPath = [Environment]::GetFolderPath('Desktop')
    $ShortcutPath = Join-Path $DesktopPath "F.R.I.D.A.Y..lnk"

    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = '{pythonw_path}'
    $Shortcut.Arguments = '"{main_script}"'
    $Shortcut.WorkingDirectory = '{project_dir}'
    $Shortcut.IconLocation = '{ico_path}'
    $Shortcut.Description = "F.R.I.D.A.Y. Tactical AI Assistant"
    $Shortcut.Hotkey = "Ctrl+Alt+F"
    $Shortcut.Save()

    # Also Start Menu
    $StartMenuPath = [Environment]::GetFolderPath('Programs')
    if (Test-Path $StartMenuPath) {{
        $StartShortcut = $WshShell.CreateShortcut((Join-Path $StartMenuPath "F.R.I.D.A.Y..lnk"))
        $StartShortcut.TargetPath = '{pythonw_path}'
        $StartShortcut.Arguments = '"{main_script}"'
        $StartShortcut.WorkingDirectory = '{project_dir}'
        $StartShortcut.IconLocation = '{ico_path}'
        $StartShortcut.Description = "F.R.I.D.A.Y. Tactical AI Assistant"
        $StartShortcut.Save()
    }}
    Write-Output "SUCCESS: $ShortcutPath"
    """

    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    if "SUCCESS" in result.stdout:
        print(f"✅ Desktop Shortcut updated to native pythonw.exe!")
        print(f"🎯 No more VBScript dependency — 100% compatible with Windows 11!")
        print(f"🚀 Double-click F.R.I.D.A.Y. on your Desktop now — it will open directly!")
    else:
        print(f"[ERROR] Could not create shortcut: {result.stderr} (stdout: {result.stdout})")

if __name__ == "__main__":
    create_shortcut()
