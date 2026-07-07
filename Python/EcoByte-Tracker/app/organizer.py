import os
import shutil

FILE_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Archives": [".zip", ".rar", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg"],
    "Music": [".m4a", ".ogg"],
    "Games": [".rom", ".sav", ".pak"],
    "Code": [".js", ".json", ".html", ".css", ".py", ".sh", ".gitignore", ".md"]
}

def organize_folder(user_dir):
    """Organizes files in the target directory into neat categories."""
    # Handle paths smoothly
    if not os.path.isabs(user_dir) and not user_dir.startswith("~"):
        user_dir = os.path.join("~", user_dir)
    target_dir = os.path.expanduser(user_dir)

    if not os.path.exists(target_dir):
        print(f"\n[Error] The directory {target_dir} does not exist.")
        return 0
    
    print(f"\n[Smart Desk] Scanning {target_dir} for clutter...\n")
    moved_count = 0

    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        
        if os.path.isdir(item_path):
            continue

        _, file_ext = os.path.splitext(item)
        file_ext = file_ext.lower()

        moved = False
        for category, extension in FILE_CATEGORIES.items():
            if file_ext in extension:
                category_path = os.path.join(target_dir, category)
                os.makedirs(category_path, exist_ok=True)

                destination = os.path.join(category_path, item)
                shutil.move(item_path, destination)
                print(f" ➔ [Sorted] {item} moved to {category}")
                moved_count += 1
                moved = True
                break

        if not moved and file_ext != "":
            others_path = os.path.join(target_dir, "Others")
            os.makedirs(others_path, exist_ok=True)
            shutil.move(item_path, os.path.join(others_path, item))
            print(f" ➔ [Sorted] {item} moved to Others")
            moved_count += 1

    print(f"\n✨ Cleanup complete! Total items organized: {moved_count}")
    return moved_count