"""
data_store.py
In-memory data layer for the Community Data System.
No SQL / external DB — everything lives in Python data structures
for the lifetime of the running process.
"""

import itertools
from datetime import date


def _id_gen(start=1):
    return itertools.count(start)


class DataStore:
    """Central in-memory store for all entities + simple auth."""

    def __init__(self):
        # ---------- Users / Auth ----------
        # role: "Admin" | "Staff" | "Resident"
        self.users = {
            "admin": {"password": "admin123", "role": "Admin", "full_name": "System Administrator"},
            "staff": {"password": "staff123", "role": "Staff", "full_name": "Barangay Staff"},
            "resident": {"password": "resident123", "role": "Resident", "full_name": "Juan Dela Cruz",
                         "resident_id": 1},
        }

        # ---------- ID counters ----------
        self._resident_ids = _id_gen(1)
        self._household_ids = _id_gen(1)
        self._complaint_ids = _id_gen(1)
        self._event_ids = _id_gen(1)
        self._announcement_ids = _id_gen(1)
        self._payment_ids = _id_gen(1)

        # ---------- Entities ----------
        self.residents = {}        # id -> dict
        self.households = {}       # id -> dict
        self.complaints = {}       # id -> dict
        self.events = {}           # id -> dict
        self.announcements = {}    # id -> dict
        self.payments = {}         # id -> dict

        self._seed_demo_data()

    # ------------------------------------------------------------------
    # Seed data so the app isn't empty on first run
    # ------------------------------------------------------------------
    def _seed_demo_data(self):
        r1 = self.add_resident("Juan Dela Cruz", 34, "Male", "0917-111-2222", "123 Mabini St.")
        r2 = self.add_resident("Maria Santos", 29, "Female", "0917-333-4444", "45 Rizal Ave.")
        r3 = self.add_resident("Pedro Reyes", 52, "Male", "0917-555-6666", "78 Bonifacio Rd.")

        h1 = self.add_household("Dela Cruz Family", "123 Mabini St.", 4)
        h2 = self.add_household("Santos Family", "45 Rizal Ave.", 3)

        self.add_complaint(r1, "Streetlight not working on Mabini St.", "Infrastructure")
        self.add_complaint(r2, "Loud noise complaint near barangay hall", "Noise")

        self.add_event("Community Clean-up Drive", str(date.today()), "Barangay Plaza",
                        "Monthly clean-up activity, all residents invited.")
        self.add_event("Health & Wellness Seminar", str(date.today()), "Barangay Hall",
                        "Free check-up and seminar on healthy living.")

        self.add_announcement("Water Service Interruption",
                               "Water service will be interrupted on Friday from 9AM-3PM for maintenance.")
        self.add_announcement("Barangay Assembly",
                               "Quarterly barangay assembly meeting this Saturday at 2PM.")

        self.add_payment(h1, "Monthly Dues", 250.00, str(date.today()), "Paid")
        self.add_payment(h2, "Monthly Dues", 250.00, str(date.today()), "Unpaid")

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user["password"] == password:
            return {"username": username, **user}
        return None

    # ------------------------------------------------------------------
    # Residents
    # ------------------------------------------------------------------
    def add_resident(self, name, age, gender, contact, address):
        rid = next(self._resident_ids)
        self.residents[rid] = {
            "id": rid, "name": name, "age": age, "gender": gender,
            "contact": contact, "address": address,
        }
        return rid

    def update_resident(self, rid, **fields):
        if rid in self.residents:
            self.residents[rid].update(fields)

    def delete_resident(self, rid):
        self.residents.pop(rid, None)

    # ------------------------------------------------------------------
    # Households
    # ------------------------------------------------------------------
    def add_household(self, head_name, address, member_count):
        hid = next(self._household_ids)
        self.households[hid] = {
            "id": hid, "head_name": head_name, "address": address,
            "member_count": member_count,
        }
        return hid

    def update_household(self, hid, **fields):
        if hid in self.households:
            self.households[hid].update(fields)

    def delete_household(self, hid):
        self.households.pop(hid, None)

    # ------------------------------------------------------------------
    # Complaints
    # ------------------------------------------------------------------
    def add_complaint(self, resident_id, description, category, status="Open"):
        cid = next(self._complaint_ids)
        self.complaints[cid] = {
            "id": cid, "resident_id": resident_id, "description": description,
            "category": category, "status": status, "date_filed": str(date.today()),
        }
        return cid

    def update_complaint_status(self, cid, status):
        if cid in self.complaints:
            self.complaints[cid]["status"] = status

    def delete_complaint(self, cid):
        self.complaints.pop(cid, None)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def add_event(self, title, event_date, location, description):
        eid = next(self._event_ids)
        self.events[eid] = {
            "id": eid, "title": title, "date": event_date,
            "location": location, "description": description,
        }
        return eid

    def delete_event(self, eid):
        self.events.pop(eid, None)

    # ------------------------------------------------------------------
    # Announcements
    # ------------------------------------------------------------------
    def add_announcement(self, title, body):
        aid = next(self._announcement_ids)
        self.announcements[aid] = {
            "id": aid, "title": title, "body": body,
            "date_posted": str(date.today()),
        }
        return aid

    def delete_announcement(self, aid):
        self.announcements.pop(aid, None)

    # ------------------------------------------------------------------
    # Payments / Dues
    # ------------------------------------------------------------------
    def add_payment(self, household_id, particulars, amount, due_date, status="Unpaid"):
        pid = next(self._payment_ids)
        self.payments[pid] = {
            "id": pid, "household_id": household_id, "particulars": particulars,
            "amount": amount, "due_date": due_date, "status": status,
        }
        return pid

    def update_payment_status(self, pid, status):
        if pid in self.payments:
            self.payments[pid]["status"] = status

    def delete_payment(self, pid):
        self.payments.pop(pid, None)

    # ------------------------------------------------------------------
    # Reports helpers
    # ------------------------------------------------------------------
    def report_summary(self):
        total_collected = sum(p["amount"] for p in self.payments.values() if p["status"] == "Paid")
        total_due = sum(p["amount"] for p in self.payments.values() if p["status"] == "Unpaid")
        complaint_counts = {"Open": 0, "In Progress": 0, "Resolved": 0}
        for c in self.complaints.values():
            complaint_counts[c["status"]] = complaint_counts.get(c["status"], 0) + 1
        return {
            "total_residents": len(self.residents),
            "total_households": len(self.households),
            "total_complaints": len(self.complaints),
            "complaint_counts": complaint_counts,
            "total_events": len(self.events),
            "total_announcements": len(self.announcements),
            "total_collected": total_collected,
            "total_due": total_due,
        }
