import json
import os
import time
import threading
from pathlib import Path
import flet as ft
from app.scanner import scan_directory_metadata
from app.actions import isolate_clutter_to_trash, restore_clutter_from_trash
from app.organizer import organize_folder  


CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def build_ui_dashboard(page: ft.Page):
    page.title = "EcoSync - Automated Storage Janitor"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 750
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.START

    config = load_config()

    # --- UI Components ---
    title_text = ft.Text("EcoSync Automation Hub", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT)
    subtitle = ft.Text("Optimize storage and eliminate silent carbon emissions.", size=14, color=ft.Colors.GREY_400)
    
    path_input = ft.TextField(label="Target Folder Path", value=config["target_folder"], width=450)
    age_input = ft.TextField(label="Age Threshold (Days)", value=str(config["age_threshold_days"]), width=150)
    
    status_text = ft.Text("System Status: Idle", size=16, weight=ft.FontWeight.W_500)
    progress_bar = ft.ProgressBar(width=650, value=0, visible=False)
    
    log_box = ft.ListView(expand=True, spacing=5, padding=10, height=150, auto_scroll=True)
    
    # --- Structural Scheduler Functions ---
    scheduler_thread = None
    stop_scheduler_event = threading.Event()

    def run_automation_pipeline():
        current_config = load_config()
        target = current_config["target_folder"]
        threshold = int(current_config["age_threshold_days"])
        
        target = os.path.expanduser(target)

        old, duplicates = scan_directory_metadata(target, threshold)
        all_clutter = old + duplicates
        
        if all_clutter:
            moved, mb, co2 = isolate_clutter_to_trash(all_clutter, target)
            return f"Optimization Complete! Shifted {moved} files. Freed {mb:.2f} MB (~{co2:.4f}g CO2 offset)."
        return "Scan complete. No matching digital clutter found."

    def background_schedule_loop(stop_event):
        while not stop_event.is_set():
            current_config = load_config()
            if not current_config["scheduler_active"]:
                break
                
            current_time = time.strftime("%H:%M")
            if current_time == current_config["schedule_time"]:
                status_text.value = "Status: Executing Scheduled Clean..."
                page.update()
                result = run_automation_pipeline()
                log_box.controls.append(ft.Text(f"[{time.strftime('%Y-%m-%d %H:%M')}] {result}", color=ft.Colors.GREEN_300))
                status_text.value = "Status: Automation Active (Sleeping)"
                page.update()
                time.sleep(61)
            time.sleep(10)

    # --- Button Interactive Handlers ---
    def on_manual_clean(e):
        progress_bar.visible = True
        status_text.value = "Status: Scanning directories..."
        page.update()
        
        config["target_folder"] = path_input.value
        config["age_threshold_days"] = int(age_input.value)
        save_config(config)
        
        result = run_automation_pipeline()
        
        status_text.value = "System Status: Clean Completed"
        progress_bar.visible = False
        log_box.controls.append(ft.Text(f"[Manual Run] {result}"))
        page.update()

    # 2. FILE ORGANIZER HANDLER
    def on_file_organize(e):
        if not path_input.value.strip():
            status_text.value = "Status: Error - Path input field empty!"
            page.update()
            return

        progress_bar.visible = True
        status_text.value = "Status: Running Smart Desk File Organizer..."
        page.update()

        # Update saved path configurations dynamically
        config["target_folder"] = path_input.value
        save_config(config)

        # Call the imported logic directly from organizer.py
        total_sorted = organize_folder(path_input.value)

        status_text.value = "System Status: Smart Desk Sorting Complete"
        progress_bar.visible = False
        log_box.controls.append(
            ft.Text(f"[Smart Desk] Sorted and categorized {total_sorted} files successfully!", color=ft.Colors.LIGHT_BLUE_200)
        )
        page.update()
    
    def on_restore_trash(e):
        if not path_input.value.strip():
            status_text.value = "Status: Error - Path input field empty!"
            page.update()
            return

        progress_bar.visible = True
        status_text.value = "Status: Restoring files from archive..."
        page.update()

        # Call the restore function
        count, message = restore_clutter_from_trash(path_input.value)

        status_text.value = "System Status: Restore Process Completed"
        progress_bar.visible = False
        
        # Log the output
        log_box.controls.append(
            ft.Text(f"[Restore] {message}", color=ft.Colors.ORANGE_300 if count > 0 else ft.Colors.GREY_400)
        )
        page.update()

    def on_toggle_scheduler(e):
        nonlocal scheduler_thread
        config["target_folder"] = path_input.value
        config["age_threshold_days"] = int(age_input.value)
        
        if schedule_switch.value:
            config["scheduler_active"] = True
            save_config(config)
            stop_scheduler_event.clear()
            scheduler_thread = threading.Thread(target=background_schedule_loop, args=(stop_scheduler_event,), daemon=True)
            scheduler_thread.start()
            status_text.value = "Status: Automation Active (Sleeping)"
            log_box.controls.append(ft.Text("[System] Background automation engine turned ON.", color=ft.Colors.BLUE_200))
        else:
            config["scheduler_active"] = False
            save_config(config)
            stop_scheduler_event.set()
            status_text.value = "System Status: Idle (Scheduler Stopped)"
            log_box.controls.append(ft.Text("[System] Background automation engine killed successfully.", color=ft.Colors.RED_200))
            
        page.update()

    schedule_switch = ft.Switch(label="Enable Automated Scheduler (Every night at 23:00)", value=config["scheduler_active"], on_change=on_toggle_scheduler)

    if config["scheduler_active"]:
        stop_scheduler_event.clear()
        scheduler_thread = threading.Thread(target=background_schedule_loop, args=(stop_scheduler_event,), daemon=True)
        scheduler_thread.start()
        status_text.value = "Status: Automation Active (Sleeping)"

    # Layout Rendering Architecture
    page.add(
        ft.Container(
            content=ft.Column([
                title_text,
                subtitle,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([path_input, age_input], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                schedule_switch,
                ft.Divider(height=20),
                # 3. ADDED THE NEW BUTTON SIDE-BY-SIDE WITH EXTENDED SPACING
                ft.Row([
                    ft.ElevatedButton("Run Manual Clean", icon="brush", on_click=on_manual_clean, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Run File Organizer", icon="folder_copy", on_click=on_file_organize, bgcolor=ft.Colors.BLUE_GREY_700, color=ft.Colors.WHITE),
                    # ➔ ADDED THIS RESTORE BUTTON
                    ft.ElevatedButton("Restore Archive", icon="settings_backup_restore", on_click=on_restore_trash, bgcolor=ft.Colors.ORANGE_700, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.START, spacing=15),
                ft.Divider(height=20),
                status_text,
                progress_bar,
                ft.Text("Execution Activity Logs:", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(content=log_box, border=ft.Border.all(1, ft.Colors.GREY_700), border_radius=5, bgcolor=ft.Colors.BLACK12)
            ]),
            padding=30
        )
    )