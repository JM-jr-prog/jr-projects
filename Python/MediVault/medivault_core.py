'''
Medivault is used to keep your medicine record/s, helps avoid Polypharmacy.

Objective:
To avoid harmful effects of Drug Interaction
To remove information gaps between doctors and pharmacies
To help in medecine management
'''

import json
import os

DB_FILE = "meds_vault.json"

# Case-insensitive conflict registry (all keys/values converted to lowercase internally)
CONFLICT_REGISTRY = {
    "aspirin": ["warfarin", "ibuprofen", "naproxen"],
    "warfarin": ["aspirin", "vitamin k", "ibuprofen"],
    "lisinopril": ["potassium", "spironolactone"],
    "simvastatin": ["grapefruit juice", "amiodarone"],
    "metformin": ["alcohol", "contrast dye"],
    "ibuprofen": ["aspirin", "warfarin", "lisinopril"],
    "naproxen": ["aspirin", "warfarin"],
    "vitamin k": ["warfarin"],
    "potassium": ["lisinopril"],
    "spironolactone": ["lisinopril", "potassium"],
    "grapefruit juice": ["simvastatin"],
    "amiodarone": ["simvastatin"],
    "alcohol": ["metformin"],
    "contrast dye": ["metformin"]
}

class MedivaultCore:
    def __init__(self):
        self.data = self.load_data()
        self.patients = self.data.get("patients", {})
        self.current_patient = self.data.get("current_patient", None)
        
        if self.current_patient and self.current_patient in self.patients:
            self.current_meds = self.patients[self.current_patient].get("medications", [])
            self.user_profile = self.patients[self.current_patient].get("user", {"name": "Guest", "age": 0})
        else:
            self.current_meds = []
            self.user_profile = {"name": "Guest", "age": 0}

    def load_data(self):
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            return {"patients": {}, "current_patient": None}
        except:
            return {"patients": {}, "current_patient": None}

    def save_data(self):
        data = {
            "patients": self.patients,
            "current_patient": self.current_patient
        }
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def add_medication(self, med_name, dosage, frequency):
        """Add medication with conflict checking"""
        if not med_name.strip():
            return False, "Medication name cannot be empty"
        
        try:
            dosage = float(dosage)
        except ValueError:
            return False, "Dosage must be a valid number"
        
        if not frequency.strip():
            return False, "Frequency cannot be empty"
        
        conflicts = self.check_conflicts(med_name)
        if conflicts:
            return False, f"⚠️ Conflicts detected: {', '.join(conflicts)}"
        
        new_med = {
            "name": med_name.strip(),
            "dosage": dosage,
            "frequency": frequency.strip()
        }
        self.current_meds.append(new_med)
        self.patients[self.current_patient]["medications"] = self.current_meds
        self.data["patients"] = self.patients
        self.save_data()
        return True, f"{med_name} added successfully!"

    def remove_medication(self, index):
        """Remove medication by index (1-based)"""
        if not self.current_meds:
            return False, "No medications to remove"
        
        try:
            idx = int(index) - 1
            if 0 <= idx < len(self.current_meds):
                removed = self.current_meds.pop(idx)
                self.patients[self.current_patient]["medications"] = self.current_meds
                self.data["patients"] = self.patients
                self.save_data()
                return True, f"Removed: {removed['name']}"
            else:
                return False, "Invalid selection"
        except ValueError:
            return False, "Enter a valid number"

    def check_conflicts(self, new_med_name):
        """CASE-INSENSITIVE conflict checking"""
        conflicts = []
        new_med_lower = new_med_name.lower().strip()
        
        for med in self.current_meds:
            existing_med_lower = med['name'].lower().strip()
            
            # Check both directions
            if new_med_lower in CONFLICT_REGISTRY:
                for conflict_med in CONFLICT_REGISTRY[new_med_lower]:
                    if existing_med_lower == conflict_med:
                        conflicts.append(f"{new_med_name} ↔ {med['name']}")
                        break
            
            if existing_med_lower in CONFLICT_REGISTRY:
                for conflict_med in CONFLICT_REGISTRY[existing_med_lower]:
                    if new_med_lower == conflict_med:
                        conflicts.append(f"{med['name']} ↔ {new_med_name}")
                        break
        
        return conflicts

    def get_current_meds(self):
        """Get formatted list of current medications"""
        if not self.current_meds:
            return "No medications recorded."
        
        lines = ["Name                  | Dosage  | Frequency       | ID "]
        lines.append("-" * 50)
        for i, med in enumerate(self.current_meds, 1):
            lines.append(f"{med['name']:<20} | {med['dosage']:<6}mg | {med['frequency']:<15} | {i:<2}")
        lines.append("-" * 50)
        return "\n".join(lines)

    def add_patient(self, pid, name, age):
        """Add new patient"""
        if not pid.strip():
            return False, "ID cannot be empty"
        
        if pid in self.patients:
            return False, f"Patient '{pid}' already exists"
        
        try:
            age = int(age)
            self.patients[pid] = {
                "user": {"name": name or pid, "age": age},
                "medications": []
            }
            self.data["patients"] = self.patients
            self.current_patient = pid
            self.current_meds = []
            self.user_profile = self.patients[pid]["user"]
            self.save_data()
            return True, f"Created & selected: {name or pid} ({pid})"
        except ValueError:
            return False, "Age must be a number"

    def delete_patient(self, pid):
        """Delete patient by ID"""
        if pid not in self.patients:
            return False, "Patient not found"
        
        profile = self.patients[pid]["user"]
        del self.patients[pid]
        self.data["patients"] = self.patients
        self.save_data()
        
        if self.current_patient == pid:
            self.current_patient = None
            self.current_meds = []
            self.user_profile = {"name": "Guest", "age": 0}
        
        return True, f"'{profile['name']}' DELETED PERMANENTLY!"

    def switch_patient(self, pid):
        """Switch to patient by ID"""
        if pid in self.patients:
            self.current_patient = pid
            self.current_meds = self.patients[pid]["medications"]
            self.user_profile = self.patients[pid]["user"]
            self.save_data()
            return True, f"Switched to: {self.user_profile['name']} ({pid})"
        return False, "Patient not found"

    def edit_patient(self, name=None, age=None):
        """Edit current patient"""
        if name:
            self.user_profile["name"] = name
        if age:
            try:
                self.user_profile["age"] = int(age)
            except ValueError:
                return False, "Invalid age"
        
        self.patients[self.current_patient]["user"] = self.user_profile
        self.data["patients"] = self.patients
        self.save_data()
        return True, "Patient updated!"

    def get_patients_list(self):
        """Get formatted list of all patients"""
        if not self.patients:
            return "No patients found"
        
        lines = []
        for pid, data in self.patients.items():
            profile = data["user"]
            meds_count = len(data.get("medications", []))
            lines.append(f"{profile['name']} ({pid}) - {meds_count} meds")
        return "\n".join(lines)

    def get_status(self):
        """Get current status"""
        return {
            "current_patient": self.current_patient,
            "user_name": self.user_profile["name"],
            "user_age": self.user_profile["age"],
            "meds_count": len(self.current_meds)
        }