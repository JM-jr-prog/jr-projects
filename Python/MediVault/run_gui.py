#!/usr/bin/env python3.11
import tkinter as tk
from medivault_gui import ModernMedivaultGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMedivaultGUI(root)
    root.mainloop()