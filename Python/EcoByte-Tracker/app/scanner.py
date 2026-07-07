import os
import time
import hashlib
from pathlib import Path
from datetime import datetime

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx",  # Documents
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",            # Images
    ".mp3", ".wav", ".aac", ".flac", ".m4a",            # Audio
    ".mp4", ".mkv", ".mov", ".avi",                     # Videos
    ".zip", ".rar", ".tar", ".gz",                      # Archives
    ".exe", ".msi", ".dmg"                              # Installers
}

def calculate_sha256(file_path):
    hasher=hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError):
        return None
    
def scan_directory_metadata(target_path, age_threshold_days=30):
    base_dir = Path(target_path)
    if not base_dir.exists() or not base_dir.is_dir():
        return [],[]
    
    neglected_clutter= []
    duplicated_clutter= []
    tracked_hashes= {}
    current_time= time.time()
    seconds_threshold= age_threshold_days * 86400

    for root, dirs, files in os.walk(base_dir):
        # Safety Guardrails: Skip trash folders and hidden system folders completely
        if ".EcoTrash" in root or any(part.startswith('.') for part in Path(root).parts):
            continue
        
        for file_name in files:
            full_path = Path(root) / file_name
            
            # Skip hidden files (like system .DS_Store files)
            if file_name.startswith('.'):
                continue
                
            # --- THE PROTECTION CHECK ---
            # If the file extension isn't in our safe list, skip it instantly!
            if full_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            try:
                if not full_path.exists():
                    continue

                file_stat = full_path.stat()
                file_size_bytes = file_stat.st_size
                last_modified_timestamp = file_stat.st_mtime
                size_in_mb = file_size_bytes / (1024 * 1024)

                file_age_seconds = current_time - last_modified_timestamp
                file_age_days = int(file_age_seconds / 86400)
                readable_date = datetime.fromtimestamp(last_modified_timestamp).strftime('%Y-%m-%d')

                file_record = {
                    "path": str(full_path),
                    "name": file_name,
                    "size_mb": size_in_mb,
                    "age_days": file_age_days,
                    "last_modified": readable_date
                }

                file_hash = calculate_sha256(full_path)
                if file_hash:
                    if file_hash in tracked_hashes:
                        file_record["original reference"] = tracked_hashes[file_hash]
                        duplicated_clutter.append(file_record)
                    else:
                        tracked_hashes[file_hash] = str(full_path)
                        if file_age_seconds > seconds_threshold:
                            neglected_clutter.append(file_record)
            except PermissionError:
                continue
                
    return neglected_clutter, duplicated_clutter