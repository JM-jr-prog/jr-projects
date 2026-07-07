import os
import shutil
from pathlib import Path

def isolate_clutter_to_trash(clutter_list, base_target_path):
    trash_dir= Path(base_target_path)/".EcoTrash"
    trash_dir.mkdir(exist_ok=True)

    bytes_optimized= 0
    moved_count= 0

    for item in clutter_list:
        source_path= Path(item["path"])
        if source_path.exists():
            try:
                file_size= source_path.stat().st_size
                destination= trash_dir/ f"{source_path.stem}_{int(os.path.getmtime(source_path))}{source_path.suffix}"

                shutil.move((str(source_path)), (str(destination)))
                bytes_optimized += file_size
                moved_count += 1
            except (PermissionError, FileNotFoundError):
                continue
    mb_saved= bytes_optimized/(1024*1024)
    co2_saved= mb_saved*0.0012

    return moved_count, mb_saved, co2_saved

def restore_clutter_from_trash(target_folder):
    """Moves all files inside .EcoTrash back into the main target folder."""
    target_dir = os.path.expanduser(target_folder)
    trash_dir = os.path.join(target_dir, ".EcoTrash")
    
    if not os.path.exists(trash_dir):
        return 0, "No trash archive folder found to restore."
        
    restored_count = 0
    files_to_restore = os.listdir(trash_dir)
    
    if not files_to_restore:
        return 0, "The trash archive folder is already empty!"
        
    for item in files_to_restore:
        source_path = os.path.join(trash_dir, item)
        destination_path = os.path.join(target_dir, item)
        
        # Skip directories just in case
        if os.path.isdir(source_path):
            continue
            
        try:
            shutil.move(source_path, destination_path)
            restored_count += 1
        except Exception as e:
            print(f"Error restoring {item}: {e}")
            
    # Clean up the empty trash directory afterward
    try:
        os.rmdir(trash_dir)
    except OSError:
        pass # Folder wasn't entirely empty or already gone
        
    return restored_count, f"Successfully restored {restored_count} files back to {target_folder}!"