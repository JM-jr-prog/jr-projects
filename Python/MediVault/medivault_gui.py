import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import datetime

# ─────────────────────────────────────────────
# Stub core so the GUI can run standalone
# Replace with: from medivault_core import MedivaultCore
# ─────────────────────────────────────────────
class MedivaultCore:
    def __init__(self):
        self.current_patient = "John Doe"
        self.current_meds = [
            {"name": "Aspirin",     "dosage": "100",  "frequency": "Once daily"},
            {"name": "Metformin",   "dosage": "500",  "frequency": "Twice daily"},
            {"name": "Lisinopril",  "dosage": "10",   "frequency": "Once daily"},
        ]
        self._patients = [
            {"name": "John Doe",   "age": 45},
            {"name": "Jane Smith", "age": 32},
        ]
        self._user_name = "Admin"
        self._user_age  = 30

    # ── status ──────────────────────────────
    def get_status(self):
        return {
            "current_patient": self.current_patient,
            "meds_count":      len(self.current_meds),
            "user_name":       self._user_name,
            "user_age":        self._user_age,
        }

    # ── medications ─────────────────────────
    def add_medication(self, name, dosage, frequency):
        if not name or not dosage or not frequency:
            return False, "❌ All fields are required."
        self.current_meds.append({"name": name, "dosage": dosage, "frequency": frequency})
        return True, f"✅ '{name}' added successfully."

    def remove_medication(self, index):
        try:
            idx = int(index) - 1
            if 0 <= idx < len(self.current_meds):
                removed = self.current_meds.pop(idx)
                return True, f"✅ '{removed['name']}' removed."
            return False, "❌ Invalid medication number."
        except ValueError:
            return False, "❌ Please enter a valid number."

    def get_current_meds(self):
        if not self.current_meds:
            return "No medications on record."
        lines = [f"{i+1}. {m['name']}  |  {m['dosage']}mg  |  {m['frequency']}"
                 for i, m in enumerate(self.current_meds)]
        return "\n".join(lines)

    # ── patients ────────────────────────────
    def get_patients(self):
        return self._patients

    def add_patient(self, name, age):
        if not name:
            return False, "❌ Name is required."
        self._patients.append({"name": name, "age": age})
        return True, f"✅ Patient '{name}' added."

    def switch_patient(self, index):
        try:
            idx = int(index) - 1
            if 0 <= idx < len(self._patients):
                self.current_patient = self._patients[idx]["name"]
                self.current_meds = []           # fresh slate per patient
                return True, f"✅ Switched to '{self.current_patient}'."
            return False, "❌ Invalid patient number."
        except ValueError:
            return False, "❌ Please enter a valid number."

    def remove_patient(self, index):
        try:
            idx = int(index) - 1
            if 0 <= idx < len(self._patients):
                removed = self._patients.pop(idx)
                if self.current_patient == removed["name"]:
                    self.current_patient = self._patients[0]["name"] if self._patients else None
                return True, f"✅ Patient '{removed['name']}' removed."
            return False, "❌ Invalid patient number."
        except ValueError:
            return False, "❌ Please enter a valid number."

    def edit_patient(self, name, age):
        for p in self._patients:
            if p["name"] == self.current_patient:
                old_name = p["name"]
                p["name"] = name or p["name"]
                p["age"]  = age  or p["age"]
                self.current_patient = p["name"]
                return True, f"✅ Updated '{old_name}' → '{p['name']}'."
        return False, "❌ Patient not found."


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER MIXIN – shared button / entry factory
# ═══════════════════════════════════════════════════════════════════════════════
class _WidgetFactory:
    """Reusable factory methods for dialogs."""

    def _make_button(self, parent, text, command, color, padx=30, pady=12):
        btn = tk.Button(
            parent, text=text, font=('Segoe UI', 11, 'bold'),
            bg=color, fg='white', command=command,
            relief=tk.FLAT, bd=0, padx=padx, pady=pady,
            activebackground=color, activeforeground='white',
            cursor='hand2'
        )
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._lighten(color)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=color))
        return btn

    @staticmethod
    def _lighten(hex_color):
        """Lighten a hex color by ~20 %."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = (min(255, int(c * 1.25)) for c in (r, g, b))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _make_entry(self, parent, colors, placeholder=''):
        entry = tk.Entry(
            parent, font=('Segoe UI', 11),
            bg=colors['bg_secondary'], fg=colors['text_primary'],
            insertbackground='white', relief=tk.FLAT, bd=0,
            highlightthickness=2,
            highlightbackground=colors['accent_primary'],
            highlightcolor=colors['accent_secondary']
        )
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=colors['text_muted'])
            entry.bind('<FocusIn>',  lambda e, en=entry, ph=placeholder, c=colors: self._ph_clear(en, ph, c))
            entry.bind('<FocusOut>', lambda e, en=entry, ph=placeholder, c=colors: self._ph_restore(en, ph, c))
        return entry

    @staticmethod
    def _ph_clear(entry, placeholder, colors):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=colors['text_primary'])

    @staticmethod
    def _ph_restore(entry, placeholder, colors):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=colors['text_muted'])

    def _labeled_entry(self, parent, label_text, key, colors, placeholder=''):
        tk.Label(parent, text=label_text, font=('Segoe UI', 11),
                 fg=colors['text_secondary'], bg=colors['bg_card']).pack(anchor='w', padx=40, pady=(8, 2))
        entry = self._make_entry(parent, colors, placeholder)
        entry.pack(padx=40, fill=tk.X, pady=(0, 4))
        return entry


# ═══════════════════════════════════════════════════════════════════════════════
#  ADD MEDICATION DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class ModernAddMedDialog(_WidgetFactory):
    def __init__(self, parent, core, colors):
        self.colors = colors
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Add Medication")
        self.top.geometry("460x420")
        self.top.resizable(False, False)
        self.top.configure(bg=colors['bg_primary'])
        self.top.transient(parent)
        self.top.grab_set()
        self._build()

    def _build(self):
        c = self.colors
        frame = tk.Frame(self.top, bg=c['bg_card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.92, relheight=0.92)

        tk.Label(frame, text="➕ Add New Medication", font=('Segoe UI', 18, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).pack(pady=(28, 18))

        self.e_name  = self._labeled_entry(frame, "Medication Name",  'name',      c, "e.g. Aspirin")
        self.e_dose  = self._labeled_entry(frame, "Dosage (mg)",      'dosage',    c, "e.g. 100")
        self.e_freq  = self._labeled_entry(frame, "Frequency",        'frequency', c, "e.g. Once daily")

        btn_frame = tk.Frame(frame, bg=c['bg_card'])
        btn_frame.pack(pady=28)

        add_btn = self._make_button(btn_frame, "Add Medication", self._ok, c['accent_success'])
        add_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                               bg=c['bg_secondary'], fg='white',
                               command=self.top.destroy, relief=tk.FLAT, bd=0,
                               padx=30, pady=12, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _ok(self):
        name  = self.e_name.get().strip()
        dosage = self.e_dose.get().strip()
        freq  = self.e_freq.get().strip()

        # strip placeholders
        if name  == "e.g. Aspirin":    name  = ""
        if dosage == "e.g. 100":       dosage = ""
        if freq   == "e.g. Once daily": freq   = ""

        if not name or not dosage or not freq:
            _flash_label(self.top, "All fields are required!", self.colors)
            return
        self.result = (name, dosage, freq)
        self.top.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  REMOVE MEDICATION DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class ModernRemoveMedDialog(_WidgetFactory):
    def __init__(self, parent, med_count, colors):
        self.colors = colors
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Remove Medication")
        self.top.geometry("420x300")
        self.top.resizable(False, False)
        self.top.configure(bg=colors['bg_primary'])
        self.top.transient(parent)
        self.top.grab_set()
        self._build(med_count)

    def _build(self, med_count):
        c = self.colors
        frame = tk.Frame(self.top, bg=c['bg_card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.92, relheight=0.90)

        tk.Label(frame, text="🗑️ Remove Medication", font=('Segoe UI', 18, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).pack(pady=(28, 6))
        tk.Label(frame, text=f"Enter number (1 – {med_count})", font=('Segoe UI', 11),
                 fg=c['text_secondary'], bg=c['bg_card']).pack(pady=(0, 16))

        self.e_num = self._make_entry(frame, c, f"1 – {med_count}")
        self.e_num.pack(padx=40, fill=tk.X, pady=(0, 8))

        btn_frame = tk.Frame(frame, bg=c['bg_card'])
        btn_frame.pack(pady=22)

        rm_btn = self._make_button(btn_frame, "Remove", self._ok, c['accent_danger'])
        rm_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                               bg=c['bg_secondary'], fg='white',
                               command=self.top.destroy, relief=tk.FLAT, bd=0,
                               padx=30, pady=12, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _ok(self):
        val = self.e_num.get().strip()
        if not val or not val.isdigit():
            _flash_label(self.top, "Please enter a valid number!", self.colors)
            return
        self.result = val
        self.top.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  PATIENT MANAGEMENT DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class ModernPatientManagementDialog(_WidgetFactory):
    def __init__(self, parent, core, colors):
        self.core   = core
        self.colors = colors
        self.top = tk.Toplevel(parent)
        self.top.title("Patient Management")
        self.top.geometry("560x560")
        self.top.resizable(False, False)
        self.top.configure(bg=colors['bg_primary'])
        self.top.transient(parent)
        self.top.grab_set()
        self._build()

    def _build(self):
        c = self.colors
        frame = tk.Frame(self.top, bg=c['bg_card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.94, relheight=0.94)

        tk.Label(frame, text="👥 Patient Management", font=('Segoe UI', 18, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).pack(pady=(24, 12))

        # ── Patient list ────────────────────
        list_frame = tk.Frame(frame, bg=c['bg_secondary'], bd=0)
        list_frame.pack(padx=20, fill=tk.BOTH, expand=True)

        self.lb = tk.Listbox(
            list_frame, font=('Segoe UI', 12),
            bg=c['bg_card'], fg=c['text_primary'],  # Fixed: bg_card for better contrast
            selectbackground=c['accent_primary'], selectforeground='white',
            relief=tk.FLAT, bd=0, highlightthickness=0,
            activestyle='none'
        )
        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.lb.yview)
        self.lb.configure(yscrollcommand=sb.set)
        self.lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._refresh_list()

        # ── Add new patient row ─────────────
        add_frame = tk.Frame(frame, bg=c['bg_card'])
        add_frame.pack(fill=tk.X, padx=20, pady=(12, 6))

        tk.Label(add_frame, text="New patient:", font=('Segoe UI', 11),
                 fg=c['text_secondary'], bg=c['bg_card']).pack(side=tk.LEFT, padx=(0, 8))

        self.e_new_name = self._make_entry(add_frame, c, "Full name")
        self.e_new_name.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        self.e_new_age = self._make_entry(add_frame, c, "Age")
        self.e_new_age.config(width=6)
        self.e_new_age.pack(side=tk.LEFT, padx=(0, 6))

        add_btn = self._make_button(add_frame, "Add", self._add_patient,
                                    c['accent_success'], padx=14, pady=8)
        add_btn.pack(side=tk.LEFT)

        # ── Action buttons ──────────────────
        btn_frame = tk.Frame(frame, bg=c['bg_card'])
        btn_frame.pack(pady=16)

        actions = [
            ("🔄 Switch",  self._switch,  c['accent_primary']),
            ("🗑 Remove",  self._remove,  c['accent_danger']),
            ("✖ Close",   self.top.destroy, c['bg_secondary']),
        ]
        for text, cmd, color in actions:
            btn = self._make_button(btn_frame, text, cmd, color, padx=18, pady=10)
            btn.pack(side=tk.LEFT, padx=8)

        self.msg_label = tk.Label(frame, text="", font=('Segoe UI', 10),
                                  fg=c['accent_success'], bg=c['bg_card'])
        self.msg_label.pack(pady=(0, 8))

    def _refresh_list(self):
        self.lb.delete(0, tk.END)
        for i, p in enumerate(self.core.get_patients(), 1):
            marker = " ◀ current" if p['name'] == self.core.current_patient else ""
            self.lb.insert(tk.END, f"  {i}.  {p['name']}  (age {p['age']}){marker}")

    def _selected_index(self):
        sel = self.lb.curselection()
        return str(sel[0] + 1) if sel else None

    def _switch(self):
        idx = self._selected_index()
        if not idx:
            self._flash("Select a patient first.")
            return
        ok, msg = self.core.switch_patient(idx)
        self._flash(msg, ok)
        self._refresh_list()

    def _remove(self):
        idx = self._selected_index()
        if not idx:
            self._flash("Select a patient first.")
            return
        ok, msg = self.core.remove_patient(idx)
        self._flash(msg, ok)
        self._refresh_list()

    def _add_patient(self):
        name = self.e_new_name.get().strip()
        age  = self.e_new_age.get().strip()
        if name == "Full name": name = ""
        if age  == "Age":       age  = ""
        ok, msg = self.core.add_patient(name, age)
        self._flash(msg, ok)
        if ok:
            self.e_new_name.delete(0, tk.END)
            self.e_new_age.delete(0, tk.END)
        self._refresh_list()

    def _flash(self, msg, success=True):
        color = self.colors['accent_success'] if success else self.colors['accent_danger']
        self.msg_label.config(text=msg, fg=color)
        self.top.after(3000, lambda: self.msg_label.config(text=""))


# ═══════════════════════════════════════════════════════════════════════════════
#  EDIT PATIENT DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class ModernEditPatientDialog(_WidgetFactory):
    def __init__(self, parent, core, colors):
        self.core   = core
        self.colors = colors
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Patient")
        self.top.geometry("440x340")
        self.top.resizable(False, False)
        self.top.configure(bg=colors['bg_primary'])
        self.top.transient(parent)
        self.top.grab_set()
        self._build()

    def _build(self):
        c = self.colors
        # find current patient data
        current = next(
            (p for p in self.core.get_patients() if p['name'] == self.core.current_patient),
            {"name": self.core.current_patient, "age": ""}
        )

        frame = tk.Frame(self.top, bg=c['bg_card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.92, relheight=0.92)

        tk.Label(frame, text="✏️ Edit Patient", font=('Segoe UI', 18, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).pack(pady=(28, 8))
        tk.Label(frame, text=f"Editing: {current['name']}", font=('Segoe UI', 11),
                 fg=c['text_secondary'], bg=c['bg_card']).pack(pady=(0, 18))

        self.e_name = self._labeled_entry(frame, "New Name", 'name', c, current['name'])
        self.e_name.delete(0, tk.END)
        self.e_name.insert(0, current['name'])
        self.e_name.config(fg=c['text_primary'])

        self.e_age = self._labeled_entry(frame, "New Age", 'age', c, str(current.get('age', '')))
        self.e_age.delete(0, tk.END)
        self.e_age.insert(0, str(current.get('age', '')))
        self.e_age.config(fg=c['text_primary'])

        btn_frame = tk.Frame(frame, bg=c['bg_card'])
        btn_frame.pack(pady=28)

        save_btn = self._make_button(btn_frame, "Save Changes", self._ok, c['accent_primary'])
        save_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=('Segoe UI', 11),
                               bg=c['bg_secondary'], fg='white',
                               command=self.top.destroy, relief=tk.FLAT, bd=0,
                               padx=30, pady=12, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _ok(self):
        name = self.e_name.get().strip()
        age  = self.e_age.get().strip()
        if not name:
            _flash_label(self.top, "Name cannot be empty!", self.colors)
            return
        self.result = (name, age)
        self.top.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY – floating flash message
# ═══════════════════════════════════════════════════════════════════════════════
def _flash_label(parent, text, colors, duration=2500):
    lbl = tk.Label(parent, text=f"⚠  {text}", font=('Segoe UI', 10, 'bold'),
                   bg=colors['accent_danger'], fg='white', padx=14, pady=8)
    lbl.place(relx=0.5, rely=0.94, anchor='center')
    parent.after(duration, lbl.destroy)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN GUI
# ═══════════════════════════════════════════════════════════════════════════════
class ModernMedivaultGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MediVault – Medication Intelligence")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg='#0a0e17')

        # FIXED COLORS - Better contrast
        self.colors = {
            'bg_primary':      '#0a0e17',
            'bg_secondary':    '#1a1f2e',
            'bg_card':         '#252b3a',
            'bg_hover':        '#3a4155',
            'accent_primary':  '#4f46e5',
            'accent_secondary':'#06b6d4',
            'accent_success':  '#10b981',
            'accent_danger':   '#ef4444',
            'text_primary':    '#ffffff',      # FIXED: Pure white
            'text_secondary':  '#cbd5e1',      # FIXED: Lighter gray
            'text_muted':      '#94a3b8',
        }

        self.core = MedivaultCore()
        self._setup_styles()
        self.setup_ui()
        self.update_status_display()

    # ── ttk style ───────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        c = self.colors
        style.configure('Treeview',
                        background=c['bg_card'],
                        foreground=c['text_primary'],
                        fieldbackground=c['bg_card'],
                        rowheight=32,
                        font=('Segoe UI', 11))
        style.configure('Treeview.Heading',
                        background=c['bg_secondary'],
                        foreground=c['text_secondary'],
                        font=('Segoe UI', 11, 'bold'),
                        relief=tk.FLAT)
        style.map('Treeview',
                  background=[('selected', c['accent_primary'])],
                  foreground=[('selected', 'white')])
        style.configure('Vertical.TScrollbar',   troughcolor=c['bg_secondary'],
                        background=c['bg_card'],   borderwidth=0)
        style.configure('Horizontal.TScrollbar', troughcolor=c['bg_secondary'],
                        background=c['bg_card'],   borderwidth=0)

    # ── root layout ─────────────────────────────────────────────────────────
    def setup_ui(self):
        self._create_gradient_bg()

        main = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.95, relheight=0.95)

        self._create_header(main)
        self._create_action_buttons(main)  # FIXED: Proper positioning
        self._create_content_area(main)

    # ── animated gradient canvas ─────────────────────────────────────────
    def _create_gradient_bg(self):
        canvas = tk.Canvas(self.root, highlightthickness=0, bg='#0a0e17')
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_canvas = canvas
        self._bg_time   = 0.0

        def _animate():
            self._bg_canvas.delete("grad")
            t = self._bg_time
            bands = [
                ('#0a0e17', 0),
                ('#111827', 300 + math.sin(t) * 60),
                ('#1a1f2e', 600 + math.cos(t * 0.7) * 80),
                ('#252b3a', 900 + math.sin(t * 1.3) * 40),
            ]
            w = self._bg_canvas.winfo_width()  or 1200
            h = self._bg_canvas.winfo_height() or 800
            for color, x_off in reversed(bands):
                self._bg_canvas.create_polygon(
                    x_off, 0, w, 0, w, h, x_off - 150, h,
                    fill=color, outline='', tags="grad"
                )
            self._bg_time += 0.018
            self.root.after(50, _animate)

        _animate()

    # ── header ──────────────────────────────────────────────────────────────
    def _create_header(self, parent):
        c = self.colors
        header = tk.Frame(parent, bg=c['bg_card'], bd=0, height=110)
        header.place(relx=0, rely=0, relwidth=1, relheight=0.14)
        header.pack_propagate(False)

        # logo pill
        logo_c = tk.Canvas(header, width=56, height=56, bg=c['bg_card'], highlightthickness=0)
        logo_c.place(x=24, y=27)
        logo_c.create_oval(4, 4, 52, 52, fill=c['accent_primary'], outline=c['accent_secondary'], width=2)
        logo_c.create_text(28, 28, text='💊', font=('Segoe UI Emoji', 22))

        # title
        tk.Label(header, text="MediVault", font=('Segoe UI', 28, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).place(x=92, y=18)
        tk.Label(header, text="Medication Intelligence System",
                 font=('Segoe UI', 11), fg=c['text_secondary'], bg=c['bg_card']).place(x=94, y=60)

        # status bar
        status_bar = tk.Frame(header, bg=c['bg_secondary'], height=28)
        status_bar.place(relx=0, rely=1.0, anchor='sw', relwidth=1)

        self.status_label = tk.Label(status_bar, font=('Segoe UI', 10, 'bold'),
                                     fg=c['text_primary'], bg=c['bg_secondary'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=4)

        # pill row (patient / med count / patient count)
        self.pills_frame = tk.Frame(header, bg=c['bg_card'])
        self.pills_frame.place(relx=0.98, rely=0.42, anchor='e')

    def _make_pill(self, parent, text, bg, fg='white'):
        pill = tk.Label(parent, text=text, font=('Segoe UI', 10, 'bold'),
                        bg=bg, fg=fg, padx=14, pady=5,
                        relief=tk.FLAT)
        pill.pack(side=tk.LEFT, padx=6)
        return pill

    # ── action buttons ──────────────────────────────────────────────────────
    def _create_action_buttons(self, parent):
        c = self.colors
        # FIXED: Proper positioning - below header with padding
        btn_frame = tk.Frame(parent, bg=c['bg_primary'])
        btn_frame.place(relx=0.5, rely=0.16, anchor='n', relwidth=0.95)  # FIXED: Centered below header
        
        btn_frame.pack_propagate(False)
        btn_frame.configure(height=80)

        buttons = [
            ("➕  Add Medication", self.add_med_dialog,    c['accent_primary']),
            ("📋  View All",       self.view_meds,         c['accent_secondary']),
            ("🗑️  Remove",         self.remove_med_dialog,  c['accent_danger']),
            ("👥  Patients",       self.patient_management, c['accent_primary']),
            ("✏️  Edit Patient",   self.edit_patient_dialog,c['accent_secondary']),
        ]

        for i, (text, cmd, color) in enumerate(buttons):
            btn = self._create_glass_button(btn_frame, text, cmd, color)
            btn.place(relx=i*0.2, rely=0.5, anchor='center')

    def _create_glass_button(self, parent, text, command, color):
        c = self.colors
        frame = tk.Frame(parent, bg=c['bg_card'], bd=0)

        canvas = tk.Canvas(frame, bg=c['bg_card'], highlightthickness=1,
                           highlightbackground=color, relief=tk.FLAT,
                           width=175, height=52, cursor='hand2')
        canvas.pack(pady=2)

        icon  = text[:2].strip()
        label = text[2:].strip()

        icon_id  = canvas.create_text(18, 26, text=icon,  font=('Segoe UI Emoji', 17), anchor='w', fill='white')
        label_id = canvas.create_text(46, 26, text=label, font=('Segoe UI', 11, 'bold'), anchor='w', fill='white')
        
        def on_enter(e):
            canvas.configure(bg=color+'44', highlightbackground=color)  # FIXED: Better hover
        def on_leave(e):
            canvas.configure(bg=c['bg_card'], highlightbackground=color)
        def on_click(e):
            command()

        canvas.bind('<Enter>',    on_enter)
        canvas.bind('<Leave>',    on_leave)
        canvas.bind('<Button-1>', on_click)
        return frame

    # ── content area ────────────────────────────────────────────────────────
    def _create_content_area(self, parent):
        c = self.colors
        content = tk.Frame(parent, bg=c['bg_card'], bd=0)
        content.place(relx=0.5, rely=0.52, relwidth=0.99, relheight=0.70, anchor='center')  # FIXED: Lower position

        # ── Medications panel (left 62 %) ──
        meds_panel = tk.Frame(content, bg=c['bg_primary'])
        meds_panel.place(relx=0, rely=0, relwidth=0.62, relheight=1)

        tk.Label(meds_panel, text="📋  Current Medications", font=('Segoe UI', 16, 'bold'),
                 fg=c['text_primary'], bg=c['bg_primary']).place(x=24, y=18)

        tree_outer = tk.Frame(meds_panel, bg=c['bg_secondary'])
        tree_outer.place(x=18, rely=0.12, relwidth=0.96, relheight=0.85)
        tree_outer.grid_rowconfigure(0, weight=1)
        tree_outer.grid_columnconfigure(0, weight=1)

        cols = ('ID', 'Medication', 'Dosage', 'Frequency', 'Status')
        self.meds_tree = ttk.Treeview(tree_outer, columns=cols, show='headings', height=16)
        widths = {'ID': 50, 'Medication': 200, 'Dosage': 120, 'Frequency': 180, 'Status': 110}
        for col in cols:
            self.meds_tree.heading(col, text=col)
            self.meds_tree.column(col, width=widths[col], anchor='center' if col in ('ID','Status','Dosage') else 'w')

        vbar = ttk.Scrollbar(tree_outer, orient=tk.VERTICAL,   command=self.meds_tree.yview)
        hbar = ttk.Scrollbar(tree_outer, orient=tk.HORIZONTAL, command=self.meds_tree.xview)
        self.meds_tree.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

        self.meds_tree.grid(row=0, column=0, sticky='nsew')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='ew')

        # double-click = select row
        self.meds_tree.bind('<Double-1>', self._on_tree_double_click)

        # ── Log panel (right 36 %) ──
        log_panel = tk.Frame(content, bg=c['bg_primary'])
        log_panel.place(relx=0.63, rely=0, relwidth=0.36, relheight=1)

        tk.Label(log_panel, text="📊  Activity Log", font=('Segoe UI', 16, 'bold'),
                 fg=c['text_primary'], bg=c['bg_primary']).place(x=24, y=18)

        log_outer = tk.Frame(log_panel, bg=c['bg_secondary'])
        log_outer.place(x=14, rely=0.12, relwidth=0.96, relheight=0.85)

        # clear button
        clear_btn = tk.Button(log_outer, text="Clear", font=('Segoe UI', 9),
                              bg=c['accent_danger'], fg='white',  # FIXED: Better contrast
                              command=self._clear_log, relief=tk.FLAT, bd=0,
                              cursor='hand2', padx=8, pady=3)
        clear_btn.pack(anchor='ne', padx=8, pady=6)

        self.log_text = scrolledtext.ScrolledText(
            log_outer, wrap=tk.WORD,
            bg=c['bg_card'], fg=c['text_primary'],
            font=('Consolas', 10), insertbackground='white',
            selectbackground=c['accent_primary'],
            relief=tk.FLAT, bd=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    # ── tree interactions ────────────────────────────────────────────────────
    def _on_tree_double_click(self, event):
        item = self.meds_tree.focus()
        if item:
            vals = self.meds_tree.item(item, 'values')
            self.log_message(f"Selected → {vals[1]}  {vals[2]}  |  {vals[3]}")

    # ── logging ─────────────────────────────────────────────────────────────
    def log_message(self, message):
        c = self.colors
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if "✅" in message:
            icon, color = "✅", c['accent_success']
        elif "❌" in message:
            icon, color = "❌", c['accent_danger']
        elif "⚠" in message:
            icon, color = "⚠", '#f59e0b'
        else:
            icon, color = "›", c['accent_secondary']

        entry = f"[{ts}] {icon}  {message}\n"
        self.log_text.insert(tk.END, entry)

        start = self.log_text.index(f"end - {len(entry)+1}c")
        end   = self.log_text.index("end - 1c")
        tag   = f"clr_{ts.replace(':','')}"
        self.log_text.tag_add(tag, start, end)
        self.log_text.tag_config(tag, foreground=color)
        self.log_text.see(tk.END)

    def _clear_log(self):
        self.log_text.delete('1.0', tk.END)

    # ── status / refresh ─────────────────────────────────────────────────────
    def update_status_display(self):
        status = self.core.get_status()
        c = self.colors

        # pills
        for w in self.pills_frame.winfo_children():
            w.destroy()

        patient_name = status['current_patient'] or 'No Patient'
        self._make_pill(self.pills_frame, f"👤  {patient_name}", c['bg_secondary'], c['text_primary'])
        self._make_pill(self.pills_frame, f"💊  {status['meds_count']} meds", c['bg_secondary'], c['text_primary'])
        self._make_pill(self.pills_frame, f"👥  {len(self.core.get_patients())} patients", c['bg_secondary'], c['text_primary'])

        self.status_label.config(
            text=f"Welcome, {status['user_name']}  ·  Age: {status['user_age']}")

        self.refresh_meds_display()

    def refresh_meds_display(self):
        for item in self.meds_tree.get_children():
            self.meds_tree.delete(item)

        for i, med in enumerate(self.core.current_meds, 1):
            status_text = "✅ Active" if i % 3 != 0 else "⏳ Pending"
            values = (i, med['name'], f"{med['dosage']} mg", med['frequency'], status_text)
            tag = 'even' if i % 2 == 0 else 'odd'
            self.meds_tree.insert('', tk.END, values=values, tags=(tag,))

        self.meds_tree.tag_configure('even', background=self.colors['bg_secondary'])
        self.meds_tree.tag_configure('odd',  background=self.colors['bg_card'])

    # ── dialog launchers ─────────────────────────────────────────────────────
    def add_med_dialog(self):
        dlg = ModernAddMedDialog(self.root, self.core, self.colors)
        self.root.wait_window(dlg.top)
        if dlg.result:
            ok, msg = self.core.add_medication(*dlg.result)
            self.log_message(msg)
            self.update_status_display()

    def remove_med_dialog(self):
        if not self.core.current_meds:
            self._modern_message("No medications to remove.", "Info")
            return
        dlg = ModernRemoveMedDialog(self.root, len(self.core.current_meds), self.colors)
        self.root.wait_window(dlg.top)
        if dlg.result:
            ok, msg = self.core.remove_medication(dlg.result)
            self.log_message(msg)
            self.update_status_display()

    def view_meds(self):
        text = self.core.get_current_meds()
        self._modern_message(text, "Current Medications")

    def patient_management(self):
        dlg = ModernPatientManagementDialog(self.root, self.core, self.colors)
        self.root.wait_window(dlg.top)
        self.update_status_display()

    def edit_patient_dialog(self):
        if not self.core.current_patient:
            self._modern_message("No patient selected.", "Warning")
            return
        dlg = ModernEditPatientDialog(self.root, self.core, self.colors)
        self.root.wait_window(dlg.top)
        if dlg.result:
            ok, msg = self.core.edit_patient(*dlg.result)
            self.log_message(msg)
            self.update_status_display()

    # ── generic message popup ────────────────────────────────────────────────
    def _modern_message(self, message, title="MediVault"):
        c = self.colors
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("480x320")
        dlg.resizable(False, False)
        dlg.configure(bg=c['bg_primary'])
        dlg.transient(self.root)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg=c['bg_card'], bd=0)
        frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.90, relheight=0.85)

        tk.Label(frame, text=title, font=('Segoe UI', 16, 'bold'),
                 fg=c['text_primary'], bg=c['bg_card']).pack(pady=(24, 12))

        tk.Label(frame, text=message, font=('Segoe UI', 11),
                 fg=c['text_primary'], bg=c['bg_card'],  # FIXED: Better contrast
                 justify=tk.LEFT, wraplength=400).pack(pady=12, padx=28)

        ok_btn = tk.Button(frame, text="OK", font=('Segoe UI', 11, 'bold'),
                           bg=c['accent_primary'], fg='white',
                           command=dlg.destroy,
                           relief=tk.FLAT, bd=0, padx=36, pady=10, cursor='hand2')
        ok_btn.pack(pady=20)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = ModernMedivaultGUI(root)
    root.mainloop()