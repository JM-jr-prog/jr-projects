import flet as ft
from app.ui import build_ui_dashboard

def main(page: ft.Page):
    # Relinquish rendering execution steps straight to our UI architecture
    build_ui_dashboard(page)

if __name__ == "__main__":  
    # Launch application window tree structures natively
    ft.app(target=main)

#cd /Users/jhonmoises/coding/Python/ECOSYNC