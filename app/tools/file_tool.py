import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def _resolve_standard_path(folder_name: str) -> Path:
    """Resolves standard Windows user folders (Downloads, Documents, Desktop, Pictures, Projects)."""
    user_home = Path.home()
    f_lower = folder_name.lower().strip()

    if "download" in f_lower:
        return user_home / "Downloads"
    elif "document" in f_lower:
        # Check OneDrive Documents vs standard Documents
        onedrive_docs = user_home / "OneDrive" / "Documents"
        return onedrive_docs if onedrive_docs.exists() else user_home / "Documents"
    elif "desktop" in f_lower:
        onedrive_desk = user_home / "OneDrive" / "Desktop"
        return onedrive_desk if onedrive_desk.exists() else user_home / "Desktop"
    elif "picture" in f_lower or "photo" in f_lower:
        return user_home / "Pictures"
    elif "project" in f_lower or "workspace" in f_lower or "python" in f_lower:
        p_path = Path("D:/Python")
        return p_path if p_path.exists() else user_home
    
    # Check if direct valid directory path
    p = Path(folder_name)
    if p.exists() and p.is_dir():
        return p
    return user_home / "Downloads"

def find_files(query: str = "", extension: str = "", folder: str = "Downloads", days: int = 7) -> str:
    """
    Searches for files in Downloads, Documents, Desktop, or Projects by name, extension, and date.
    Args:
        query: text or keyword in file name (e.g. 'invoice', 'report')
        extension: file extension without dot (e.g. 'pdf', 'png', 'docx')
        folder: 'Downloads', 'Documents', 'Desktop', or 'Projects'
        days: filter files modified in last N days (default 7)
    """
    target_dir = _resolve_standard_path(folder)
    if not target_dir.exists():
        return f"Directory {target_dir} not found, Boss."

    clean_ext = extension.lower().strip().replace(".", "")
    clean_query = query.lower().strip()
    cutoff_time = time.time() - (days * 86400) if days > 0 else 0

    matches = []
    try:
        for entry in target_dir.iterdir():
            if entry.is_file():
                # Extension filter
                if clean_ext and entry.suffix.lower().replace(".", "") != clean_ext:
                    continue
                # Query filter
                if clean_query and clean_query not in entry.name.lower():
                    continue
                # Time filter
                stat = entry.stat()
                if stat.st_mtime >= cutoff_time:
                    size_mb = stat.st_size / (1024 * 1024)
                    size_str = f"{size_mb:.1f} MB" if size_mb >= 1.0 else f"{int(stat.st_size / 1024)} KB"
                    mtime_str = time.strftime("%b %d", time.localtime(stat.st_mtime))
                    matches.append((entry.name, size_str, mtime_str))

        if not matches:
            filters = []
            if clean_ext: filters.append(f".{clean_ext} extension")
            if clean_query: filters.append(f"keyword '{clean_query}'")
            filter_str = " with " + " and ".join(filters) if filters else ""
            return f"No files matching{filter_str} were found in {target_dir.name} from the last {days} days, Boss."

        # Format top 6 results
        matches.sort(key=lambda x: x[0])
        summary_lines = [f"{i+1}) {name} ({size}, {mtime})" for i, (name, size, mtime) in enumerate(matches[:6])]
        extra = f" (and {len(matches)-6} more)" if len(matches) > 6 else ""
        return f"Found {len(matches)} files in {target_dir.name}:\n" + "\n".join(summary_lines) + extra
    except Exception as e:
        return f"File search encountered an error: {str(e)}"

def organize_folder(folder_name: str = "Downloads") -> str:
    """
    Cleans up and categorizes loose files in Downloads or Desktop into organized folders:
    Documents, Images, Installers, Media, and Archives.
    """
    target_dir = _resolve_standard_path(folder_name)
    if not target_dir.exists():
        return f"Target folder {target_dir} does not exist, Boss."

    category_map = {
        "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".epub"},
        "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"},
        "Installers": {".exe", ".msi", ".iso"},
        "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
        "Media": {".mp4", ".mp3", ".wav", ".mkv", ".mov", ".flac"}
    }

    counts = {cat: 0 for cat in category_map}
    moved_total = 0

    try:
        for item in target_dir.iterdir():
            # Only process loose files, do not touch existing subfolders
            if item.is_file():
                ext = item.suffix.lower()
                dest_category = None
                for cat, extensions in category_map.items():
                    if ext in extensions:
                        dest_category = cat
                        break

                if dest_category:
                    cat_dir = target_dir / dest_category
                    cat_dir.mkdir(exist_ok=True)
                    target_file = cat_dir / item.name

                    # Avoid overwrite if file exists
                    if target_file.exists():
                        base = item.stem
                        suffix = item.suffix
                        target_file = cat_dir / f"{base}_{int(time.time()) % 10000}{suffix}"

                    shutil.move(str(item), str(target_file))
                    counts[dest_category] += 1
                    moved_total += 1

        if moved_total == 0:
            return f"{target_dir.name} is already clean and organized, Boss. No loose files needed sorting."

        breakdown = [f"{c} {cat.lower()}" for cat, c in counts.items() if c > 0]
        return f"Organized {target_dir.name}, Boss. Successfully categorized {moved_total} files: {', '.join(breakdown)}."
    except Exception as e:
        return f"Failed to organize {target_dir.name}: {str(e)}"

def open_folder(folder_name: str = "Downloads") -> str:
    """Opens a folder in Windows File Explorer (e.g. 'Downloads', 'Documents', 'Desktop', 'Projects')."""
    target_dir = _resolve_standard_path(folder_name)
    try:
        subprocess.Popen(["explorer.exe", str(target_dir)])
        return f"Opening {target_dir.name} in Windows File Explorer, Boss."
    except Exception as e:
        return f"Could not open folder {folder_name}: {str(e)}"

if __name__ == "__main__":
    print(find_files(extension="pdf", folder="Downloads", days=14))
