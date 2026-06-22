"""
main.py
Community Data System — Tkinter GUI (no SQL database, in-memory store)

Run:
    python main.py

Demo accounts:
    admin    / admin123     (Admin)
    staff    / staff123     (Staff)
    resident / resident123  (Resident)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from data_store import DataStore

# ----------------------------------------------------------------------
# Visual constants
# ----------------------------------------------------------------------
BG = "#f4f6f8"
SIDEBAR_BG = "#1f2d3d"
SIDEBAR_BTN_BG = "#27384a"
SIDEBAR_BTN_ACTIVE = "#3a4f66"
ACCENT = "#2e86de"
DANGER = "#e74c3c"
SUCCESS = "#27ae60"
WARNING = "#f39c12"
TEXT_DARK = "#1f2d3d"
CARD_BG = "#ffffff"
FONT_FAMILY = "Segoe UI"


def style_treeview(style: ttk.Style):
    style.configure("Treeview", rowheight=26, font=(FONT_FAMILY, 10), background="white",
                     fieldbackground="white")
    style.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"), background="#dde4ea")
    style.map("Treeview", background=[("selected", ACCENT)])


# ========================================================================
# LOGIN WINDOW
# ========================================================================
class LoginWindow(tk.Tk):
    def __init__(self, store: DataStore):
        super().__init__()
        self.store = store
        self.title("Community Data System — Login")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.eval('tk::PlaceWindow . center')

        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self, bg=CARD_BG, padx=36, pady=32)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="🏘", font=(FONT_FAMILY, 36), bg=CARD_BG).pack(pady=(0, 6))
        tk.Label(card, text="Community Data System", font=(FONT_FAMILY, 16, "bold"),
                 bg=CARD_BG, fg=TEXT_DARK).pack()
        tk.Label(card, text="Sign in to continue", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#7f8c8d").pack(pady=(0, 20))

        tk.Label(card, text="Username", font=(FONT_FAMILY, 9, "bold"), bg=CARD_BG,
                 fg=TEXT_DARK, anchor="w").pack(fill="x")
        self.username_var = tk.StringVar()
        un_entry = tk.Entry(card, textvariable=self.username_var, font=(FONT_FAMILY, 11),
                             relief="solid", bd=1, width=28)
        un_entry.pack(pady=(2, 14), ipady=4)
        un_entry.focus_set()

        tk.Label(card, text="Password", font=(FONT_FAMILY, 9, "bold"), bg=CARD_BG,
                 fg=TEXT_DARK, anchor="w").pack(fill="x")
        self.password_var = tk.StringVar()
        pw_entry = tk.Entry(card, textvariable=self.password_var, font=(FONT_FAMILY, 11),
                             relief="solid", bd=1, width=28, show="•")
        pw_entry.pack(pady=(2, 6), ipady=4)

        self.error_label = tk.Label(card, text="", font=(FONT_FAMILY, 9), bg=CARD_BG, fg=DANGER)
        self.error_label.pack(pady=(0, 6))

        login_btn = tk.Button(card, text="Log In", font=(FONT_FAMILY, 11, "bold"), bg=ACCENT,
                               fg="white", activebackground="#256bb0", relief="flat",
                               cursor="hand2", command=self._attempt_login)
        login_btn.pack(fill="x", ipady=6, pady=(8, 14))

        hint = tk.Label(card,
                         text="Demo accounts:\nadmin/admin123 · staff/staff123 · resident/resident123",
                         font=(FONT_FAMILY, 8), bg=CARD_BG, fg="#95a5a6", justify="center")
        hint.pack()

        self.bind("<Return>", lambda e: self._attempt_login())

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            self.error_label.config(text="Please enter both username and password.")
            return

        user = self.store.authenticate(username, password)
        if user:
            self.destroy()
            app = MainApp(self.store, user)
            app.mainloop()
        else:
            self.error_label.config(text="Invalid username or password.")
            self.password_var.set("")


# ========================================================================
# MAIN APPLICATION (post-login)
# ========================================================================
class MainApp(tk.Tk):
    SECTIONS = [
        ("Residents Directory", "👤"),
        ("Households", "🏠"),
        ("Complaints & Requests", "📋"),
        ("Community Events", "📅"),
        ("Announcements", "📢"),
        ("Dues & Payments", "💰"),
        ("Reports & Analytics", "📊"),
    ]

    # Which roles can see which section
    ROLE_ACCESS = {
        "Admin": {"Residents Directory", "Households", "Complaints & Requests",
                  "Community Events", "Announcements", "Dues & Payments",
                  "Reports & Analytics", "User Management"},
        "Staff": {"Residents Directory", "Households", "Complaints & Requests",
                  "Community Events", "Announcements", "Dues & Payments",
                  "Reports & Analytics"},
        "Resident": {"Complaints & Requests", "Community Events", "Announcements",
                     "Dues & Payments", "Reports & Analytics"},
    }

    def __init__(self, store: DataStore, user: dict):
        super().__init__()
        self.store = store
        self.user = user
        self.role = user["role"]

        self.title("Community Data System")
        self.geometry("1180x700")
        self.minsize(1000, 620)
        self.configure(bg=BG)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style_treeview(style)

        self._build_layout()
        self.show_section(self._first_allowed_section())

    # ------------------------------------------------------------------
    def _allowed_sections(self):
        allowed = self.ROLE_ACCESS.get(self.role, set())
        return [(name, icon) for name, icon in self.SECTIONS if name in allowed]

    def _first_allowed_section(self):
        sections = self._allowed_sections()
        return sections[0][0] if sections else "Reports & Analytics"

    # ------------------------------------------------------------------
    def _build_layout(self):
        # ----- Sidebar -----
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=230)
        self.sidebar.pack(side="left", fill="y")

        header = tk.Frame(self.sidebar, bg=SIDEBAR_BG, pady=18, padx=16)
        header.pack(fill="x")
        tk.Label(header, text="🏘 Community", font=(FONT_FAMILY, 14, "bold"),
                 bg=SIDEBAR_BG, fg="white").pack(anchor="w")
        tk.Label(header, text="Data System", font=(FONT_FAMILY, 10),
                 bg=SIDEBAR_BG, fg="#9fb3c8").pack(anchor="w")

        user_box = tk.Frame(self.sidebar, bg=SIDEBAR_BTN_BG, padx=14, pady=10)
        user_box.pack(fill="x", padx=12, pady=(4, 14))
        tk.Label(user_box, text=self.user.get("full_name", self.user["username"]),
                 font=(FONT_FAMILY, 10, "bold"), bg=SIDEBAR_BTN_BG, fg="white",
                 anchor="w").pack(fill="x")
        tk.Label(user_box, text=f"Role: {self.role}", font=(FONT_FAMILY, 8),
                 bg=SIDEBAR_BTN_BG, fg="#9fb3c8", anchor="w").pack(fill="x")

        self.nav_buttons = {}
        for name, icon in self._allowed_sections():
            btn = tk.Button(self.sidebar, text=f"  {icon}  {name}", font=(FONT_FAMILY, 10),
                             bg=SIDEBAR_BG, fg="white", activebackground=SIDEBAR_BTN_ACTIVE,
                             activeforeground="white", bd=0, relief="flat", anchor="w",
                             cursor="hand2", padx=12, pady=10,
                             command=lambda n=name: self.show_section(n))
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_buttons[name] = btn

        if self.role == "Admin":
            btn = tk.Button(self.sidebar, text="  ⚙  User Management", font=(FONT_FAMILY, 10),
                             bg=SIDEBAR_BG, fg="white", activebackground=SIDEBAR_BTN_ACTIVE,
                             activeforeground="white", bd=0, relief="flat", anchor="w",
                             cursor="hand2", padx=12, pady=10,
                             command=lambda: self.show_section("User Management"))
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_buttons["User Management"] = btn

        spacer = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        spacer.pack(fill="both", expand=True)

        logout_btn = tk.Button(self.sidebar, text="  ⎋  Log Out", font=(FONT_FAMILY, 10, "bold"),
                                bg=DANGER, fg="white", activebackground="#c0392b", bd=0,
                                relief="flat", anchor="w", cursor="hand2", padx=12, pady=10,
                                command=self._logout)
        logout_btn.pack(fill="x", padx=8, pady=12, side="bottom")

        # ----- Main content area -----
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.topbar = tk.Frame(self.content, bg="white", height=50)
        self.topbar.pack(fill="x")
        self.section_title = tk.Label(self.topbar, text="", font=(FONT_FAMILY, 14, "bold"),
                                       bg="white", fg=TEXT_DARK)
        self.section_title.pack(side="left", padx=20, pady=10)
        tk.Label(self.topbar, text=str(date.today().strftime("%B %d, %Y")),
                 font=(FONT_FAMILY, 9), bg="white", fg="#95a5a6").pack(side="right", padx=20)

        self.body = tk.Frame(self.content, bg=BG)
        self.body.pack(fill="both", expand=True, padx=18, pady=14)

    def _logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.destroy()
            login = LoginWindow(self.store)
            login.mainloop()

    # ------------------------------------------------------------------
    def show_section(self, name):
        for n, btn in self.nav_buttons.items():
            btn.config(bg=SIDEBAR_BTN_ACTIVE if n == name else SIDEBAR_BG)

        self.section_title.config(text=name)
        for widget in self.body.winfo_children():
            widget.destroy()

        builder = {
            "Residents Directory": self._build_residents,
            "Households": self._build_households,
            "Complaints & Requests": self._build_complaints,
            "Community Events": self._build_events,
            "Announcements": self._build_announcements,
            "Dues & Payments": self._build_payments,
            "Reports & Analytics": self._build_reports,
            "User Management": self._build_user_management,
        }.get(name)

        if builder:
            builder()

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def _can_edit(self):
        return self.role in ("Admin", "Staff")

    def _toolbar(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(0, 10))
        return bar

    def _make_tree(self, parent, columns, headings, widths):
        frame = tk.Frame(parent, bg=CARD_BG)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for col, head, w in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return tree

    def _styled_button(self, parent, text, command, color=ACCENT, side="left"):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         font=(FONT_FAMILY, 9, "bold"), relief="flat", cursor="hand2",
                         padx=12, pady=6, activebackground=color)
        btn.pack(side=side, padx=(0, 8))
        return btn

    def _search_box(self, parent, on_change):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(side="right")
        tk.Label(frame, text="🔍", bg=BG, font=(FONT_FAMILY, 10)).pack(side="left")
        var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=var, font=(FONT_FAMILY, 10), width=24,
                          relief="solid", bd=1)
        entry.pack(side="left", padx=4, ipady=3)
        var.trace_add("write", lambda *a: on_change(var.get()))
        return var

    # ==================================================================
    # 1. RESIDENTS DIRECTORY
    # ==================================================================
    def _build_residents(self):
        editable = self._can_edit()
        bar = self._toolbar(self.body)
        if editable:
            self._styled_button(bar, "+ Add Resident", self._add_resident_dialog)
            self._styled_button(bar, "✎ Edit", self._edit_resident_dialog, color=WARNING)
            self._styled_button(bar, "🗑 Delete", self._delete_resident, color=DANGER)
        search_var = self._search_box(bar, lambda q: self._refresh_residents(q))

        self.residents_tree = self._make_tree(
            self.body,
            columns=("id", "name", "age", "gender", "contact", "address"),
            headings=("ID", "Name", "Age", "Gender", "Contact", "Address"),
            widths=(40, 160, 50, 70, 120, 220),
        )
        self._refresh_residents()

    def _refresh_residents(self, query=""):
        tree = self.residents_tree
        tree.delete(*tree.get_children())
        q = query.lower().strip()
        for r in sorted(self.store.residents.values(), key=lambda x: x["id"]):
            if q and q not in r["name"].lower() and q not in r["address"].lower():
                continue
            tree.insert("", "end", iid=r["id"],
                        values=(r["id"], r["name"], r["age"], r["gender"], r["contact"], r["address"]))

    def _add_resident_dialog(self):
        self._resident_form("Add Resident")

    def _edit_resident_dialog(self):
        sel = self.residents_tree.selection()
        if not sel:
            messagebox.showinfo("Select Resident", "Please select a resident to edit.")
            return
        rid = int(sel[0])
        self._resident_form("Edit Resident", self.store.residents[rid])

    def _resident_form(self, title, existing=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("360x380")
        win.configure(bg=CARD_BG)
        win.grab_set()

        fields = {}
        labels = ["Name", "Age", "Gender", "Contact", "Address"]
        keys = ["name", "age", "gender", "contact", "address"]
        for label, key in zip(labels, keys):
            tk.Label(win, text=label, bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(12, 0))
            var = tk.StringVar(value=str(existing[key]) if existing else "")
            tk.Entry(win, textvariable=var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1).pack(fill="x", padx=20, ipady=4)
            fields[key] = var

        def save():
            try:
                name = fields["name"].get().strip()
                age = int(fields["age"].get().strip())
                gender = fields["gender"].get().strip()
                contact = fields["contact"].get().strip()
                address = fields["address"].get().strip()
                if not name or not address:
                    raise ValueError("Name and Address are required.")
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e) if str(e) else "Age must be a number.")
                return

            if existing:
                self.store.update_resident(existing["id"], name=name, age=age, gender=gender,
                                            contact=contact, address=address)
            else:
                self.store.add_resident(name, age, gender, contact, address)
            win.destroy()
            self._refresh_residents()

        self._styled_button(win, "Save", save, color=SUCCESS).pack(pady=18)

    def _delete_resident(self):
        sel = self.residents_tree.selection()
        if not sel:
            messagebox.showinfo("Select Resident", "Please select a resident to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this resident record?"):
            self.store.delete_resident(int(sel[0]))
            self._refresh_residents()

    # ==================================================================
    # 2. HOUSEHOLDS
    # ==================================================================
    def _build_households(self):
        editable = self._can_edit()
        bar = self._toolbar(self.body)
        if editable:
            self._styled_button(bar, "+ Add Household", self._add_household_dialog)
            self._styled_button(bar, "✎ Edit", self._edit_household_dialog, color=WARNING)
            self._styled_button(bar, "🗑 Delete", self._delete_household, color=DANGER)

        self.households_tree = self._make_tree(
            self.body,
            columns=("id", "head_name", "address", "member_count"),
            headings=("ID", "Head of Household", "Address", "Members"),
            widths=(40, 200, 260, 80),
        )
        self._refresh_households()

    def _refresh_households(self):
        tree = self.households_tree
        tree.delete(*tree.get_children())
        for h in sorted(self.store.households.values(), key=lambda x: x["id"]):
            tree.insert("", "end", iid=h["id"],
                        values=(h["id"], h["head_name"], h["address"], h["member_count"]))

    def _add_household_dialog(self):
        self._household_form("Add Household")

    def _edit_household_dialog(self):
        sel = self.households_tree.selection()
        if not sel:
            messagebox.showinfo("Select Household", "Please select a household to edit.")
            return
        hid = int(sel[0])
        self._household_form("Edit Household", self.store.households[hid])

    def _household_form(self, title, existing=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("360x320")
        win.configure(bg=CARD_BG)
        win.grab_set()

        fields = {}
        labels = ["Head of Household", "Address", "Member Count"]
        keys = ["head_name", "address", "member_count"]
        for label, key in zip(labels, keys):
            tk.Label(win, text=label, bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(12, 0))
            var = tk.StringVar(value=str(existing[key]) if existing else "")
            tk.Entry(win, textvariable=var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1).pack(fill="x", padx=20, ipady=4)
            fields[key] = var

        def save():
            try:
                head_name = fields["head_name"].get().strip()
                address = fields["address"].get().strip()
                member_count = int(fields["member_count"].get().strip())
                if not head_name or not address:
                    raise ValueError("Head of Household and Address are required.")
            except ValueError as e:
                messagebox.showerror("Invalid Input",
                                      str(e) if "required" in str(e) else "Member count must be a number.")
                return

            if existing:
                self.store.update_household(existing["id"], head_name=head_name, address=address,
                                              member_count=member_count)
            else:
                self.store.add_household(head_name, address, member_count)
            win.destroy()
            self._refresh_households()

        self._styled_button(win, "Save", save, color=SUCCESS).pack(pady=18)

    def _delete_household(self):
        sel = self.households_tree.selection()
        if not sel:
            messagebox.showinfo("Select Household", "Please select a household to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this household record?"):
            self.store.delete_household(int(sel[0]))
            self._refresh_households()

    # ==================================================================
    # 3. COMPLAINTS & REQUESTS
    # ==================================================================
    def _build_complaints(self):
        bar = self._toolbar(self.body)
        self._styled_button(bar, "+ File Complaint", self._add_complaint_dialog)
        if self._can_edit():
            self._styled_button(bar, "Update Status", self._update_complaint_status, color=WARNING)
            self._styled_button(bar, "🗑 Delete", self._delete_complaint, color=DANGER)

        self.complaints_tree = self._make_tree(
            self.body,
            columns=("id", "resident", "category", "description", "status", "date"),
            headings=("ID", "Resident", "Category", "Description", "Status", "Date Filed"),
            widths=(40, 140, 110, 280, 100, 100),
        )
        self._refresh_complaints()

    def _refresh_complaints(self):
        tree = self.complaints_tree
        tree.delete(*tree.get_children())
        is_resident = self.role == "Resident"
        my_id = self.user.get("resident_id")
        for c in sorted(self.store.complaints.values(), key=lambda x: x["id"]):
            if is_resident and c["resident_id"] != my_id:
                continue
            resident = self.store.residents.get(c["resident_id"])
            rname = resident["name"] if resident else "Unknown"
            tree.insert("", "end", iid=c["id"],
                        values=(c["id"], rname, c["category"], c["description"], c["status"], c["date_filed"]))

    def _add_complaint_dialog(self):
        win = tk.Toplevel(self)
        win.title("File a Complaint / Request")
        win.geometry("400x380")
        win.configure(bg=CARD_BG)
        win.grab_set()

        is_resident = self.role == "Resident"
        resident_var = tk.StringVar()

        tk.Label(win, text="Resident", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(16, 0))
        if is_resident:
            me = self.store.residents.get(self.user.get("resident_id"))
            resident_var.set(me["name"] if me else self.user["full_name"])
            tk.Entry(win, textvariable=resident_var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1, state="readonly").pack(fill="x", padx=20, ipady=4)
            resident_id_map = {resident_var.get(): self.user.get("resident_id")}
        else:
            names = [r["name"] for r in self.store.residents.values()]
            resident_id_map = {r["name"]: r["id"] for r in self.store.residents.values()}
            combo = ttk.Combobox(win, textvariable=resident_var, values=names, state="readonly")
            combo.pack(fill="x", padx=20, ipady=2)
            if names:
                combo.current(0)

        tk.Label(win, text="Category", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(14, 0))
        category_var = tk.StringVar(value="Infrastructure")
        ttk.Combobox(win, textvariable=category_var,
                     values=["Infrastructure", "Noise", "Sanitation", "Safety/Peace & Order", "Other"],
                     state="readonly").pack(fill="x", padx=20, ipady=2)

        tk.Label(win, text="Description", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(14, 0))
        desc_text = tk.Text(win, height=6, font=(FONT_FAMILY, 10), relief="solid", bd=1)
        desc_text.pack(fill="x", padx=20)

        def save():
            description = desc_text.get("1.0", "end").strip()
            rname = resident_var.get()
            if not description or rname not in resident_id_map:
                messagebox.showerror("Invalid Input", "Please select a resident and enter a description.")
                return
            self.store.add_complaint(resident_id_map[rname], description, category_var.get())
            win.destroy()
            self._refresh_complaints()

        self._styled_button(win, "Submit", save, color=SUCCESS).pack(pady=16)

    def _update_complaint_status(self):
        sel = self.complaints_tree.selection()
        if not sel:
            messagebox.showinfo("Select Complaint", "Please select a complaint to update.")
            return
        cid = int(sel[0])

        win = tk.Toplevel(self)
        win.title("Update Status")
        win.geometry("300x180")
        win.configure(bg=CARD_BG)
        win.grab_set()

        tk.Label(win, text="New Status", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold")).pack(pady=(20, 4))
        status_var = tk.StringVar(value=self.store.complaints[cid]["status"])
        ttk.Combobox(win, textvariable=status_var, values=["Open", "In Progress", "Resolved"],
                     state="readonly").pack(padx=20, fill="x")

        def save():
            self.store.update_complaint_status(cid, status_var.get())
            win.destroy()
            self._refresh_complaints()

        self._styled_button(win, "Update", save, color=SUCCESS).pack(pady=18)

    def _delete_complaint(self):
        sel = self.complaints_tree.selection()
        if not sel:
            messagebox.showinfo("Select Complaint", "Please select a complaint to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this complaint record?"):
            self.store.delete_complaint(int(sel[0]))
            self._refresh_complaints()

    # ==================================================================
    # 4. COMMUNITY EVENTS
    # ==================================================================
    def _build_events(self):
        bar = self._toolbar(self.body)
        if self._can_edit():
            self._styled_button(bar, "+ Add Event", self._add_event_dialog)
            self._styled_button(bar, "🗑 Delete", self._delete_event, color=DANGER)

        self.events_tree = self._make_tree(
            self.body,
            columns=("id", "title", "date", "location", "description"),
            headings=("ID", "Title", "Date", "Location", "Description"),
            widths=(40, 200, 100, 150, 320),
        )
        self._refresh_events()

    def _refresh_events(self):
        tree = self.events_tree
        tree.delete(*tree.get_children())
        for e in sorted(self.store.events.values(), key=lambda x: x["id"]):
            tree.insert("", "end", iid=e["id"],
                        values=(e["id"], e["title"], e["date"], e["location"], e["description"]))

    def _add_event_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add Community Event")
        win.geometry("400x420")
        win.configure(bg=CARD_BG)
        win.grab_set()

        labels_keys = [("Title", "title"), ("Date (YYYY-MM-DD)", "date"), ("Location", "location")]
        fields = {}
        for label, key in labels_keys:
            tk.Label(win, text=label, bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 0))
            default = str(date.today()) if key == "date" else ""
            var = tk.StringVar(value=default)
            tk.Entry(win, textvariable=var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1).pack(fill="x", padx=20, ipady=4)
            fields[key] = var

        tk.Label(win, text="Description", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(14, 0))
        desc_text = tk.Text(win, height=5, font=(FONT_FAMILY, 10), relief="solid", bd=1)
        desc_text.pack(fill="x", padx=20)

        def save():
            title = fields["title"].get().strip()
            edate = fields["date"].get().strip()
            location = fields["location"].get().strip()
            description = desc_text.get("1.0", "end").strip()
            if not title or not edate:
                messagebox.showerror("Invalid Input", "Title and Date are required.")
                return
            self.store.add_event(title, edate, location, description)
            win.destroy()
            self._refresh_events()

        self._styled_button(win, "Save Event", save, color=SUCCESS).pack(pady=16)

    def _delete_event(self):
        sel = self.events_tree.selection()
        if not sel:
            messagebox.showinfo("Select Event", "Please select an event to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this event?"):
            self.store.delete_event(int(sel[0]))
            self._refresh_events()

    # ==================================================================
    # 5. ANNOUNCEMENTS
    # ==================================================================
    def _build_announcements(self):
        bar = self._toolbar(self.body)
        if self._can_edit():
            self._styled_button(bar, "+ Post Announcement", self._add_announcement_dialog)
            self._styled_button(bar, "🗑 Delete", self._delete_announcement, color=DANGER)

        canvas_frame = tk.Frame(self.body, bg=BG)
        canvas_frame.pack(fill="both", expand=True)
        canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.announcement_list_frame = tk.Frame(canvas, bg=BG)

        self.announcement_list_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.announcement_list_frame, anchor="nw", width=1000)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._refresh_announcements()

    def _refresh_announcements(self):
        for widget in self.announcement_list_frame.winfo_children():
            widget.destroy()

        for a in sorted(self.store.announcements.values(), key=lambda x: -x["id"]):
            card = tk.Frame(self.announcement_list_frame, bg=CARD_BG, padx=18, pady=14)
            card.pack(fill="x", pady=6, padx=4)
            top = tk.Frame(card, bg=CARD_BG)
            top.pack(fill="x")
            tk.Label(top, text=a["title"], font=(FONT_FAMILY, 12, "bold"), bg=CARD_BG,
                     fg=TEXT_DARK, anchor="w").pack(side="left")
            tk.Label(top, text=a["date_posted"], font=(FONT_FAMILY, 8), bg=CARD_BG,
                     fg="#95a5a6").pack(side="right")
            tk.Label(card, text=a["body"], font=(FONT_FAMILY, 10), bg=CARD_BG, fg="#34495e",
                     anchor="w", justify="left", wraplength=900).pack(fill="x", pady=(6, 8))
            if self._can_edit():
                tk.Button(card, text="🗑 Delete", bg=DANGER, fg="white", relief="flat",
                          font=(FONT_FAMILY, 8, "bold"), cursor="hand2", padx=8, pady=3,
                          command=lambda aid=a["id"]: self._delete_announcement_by_id(aid)
                          ).pack(anchor="e")

    def _add_announcement_dialog(self):
        win = tk.Toplevel(self)
        win.title("Post Announcement")
        win.geometry("420x360")
        win.configure(bg=CARD_BG)
        win.grab_set()

        tk.Label(win, text="Title", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(16, 0))
        title_var = tk.StringVar()
        tk.Entry(win, textvariable=title_var, font=(FONT_FAMILY, 10), relief="solid",
                  bd=1).pack(fill="x", padx=20, ipady=4)

        tk.Label(win, text="Message", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(14, 0))
        body_text = tk.Text(win, height=8, font=(FONT_FAMILY, 10), relief="solid", bd=1)
        body_text.pack(fill="x", padx=20)

        def save():
            title = title_var.get().strip()
            body = body_text.get("1.0", "end").strip()
            if not title or not body:
                messagebox.showerror("Invalid Input", "Title and message are required.")
                return
            self.store.add_announcement(title, body)
            win.destroy()
            self._refresh_announcements()

        self._styled_button(win, "Post", save, color=SUCCESS).pack(pady=16)

    def _delete_announcement(self):
        messagebox.showinfo("Delete Announcement", "Use the Delete button on the announcement card.")

    def _delete_announcement_by_id(self, aid):
        if messagebox.askyesno("Confirm Delete", "Delete this announcement?"):
            self.store.delete_announcement(aid)
            self._refresh_announcements()

    # ==================================================================
    # 6. DUES & PAYMENTS
    # ==================================================================
    def _build_payments(self):
        bar = self._toolbar(self.body)
        if self._can_edit():
            self._styled_button(bar, "+ Add Payment Record", self._add_payment_dialog)
            self._styled_button(bar, "Mark Paid", self._mark_paid, color=SUCCESS)
            self._styled_button(bar, "🗑 Delete", self._delete_payment, color=DANGER)

        self.payments_tree = self._make_tree(
            self.body,
            columns=("id", "household", "particulars", "amount", "due_date", "status"),
            headings=("ID", "Household", "Particulars", "Amount (₱)", "Due Date", "Status"),
            widths=(40, 180, 160, 100, 100, 100),
        )
        self._refresh_payments()

    def _refresh_payments(self):
        tree = self.payments_tree
        tree.delete(*tree.get_children())
        is_resident = self.role == "Resident"
        my_household_id = None
        if is_resident:
            me = self.store.residents.get(self.user.get("resident_id"))
            if me:
                for h in self.store.households.values():
                    if h["address"] == me["address"]:
                        my_household_id = h["id"]
                        break

        for p in sorted(self.store.payments.values(), key=lambda x: x["id"]):
            if is_resident and p["household_id"] != my_household_id:
                continue
            household = self.store.households.get(p["household_id"])
            hname = household["head_name"] if household else "Unknown"
            tree.insert("", "end", iid=p["id"],
                        values=(p["id"], hname, p["particulars"], f"{p['amount']:.2f}",
                                p["due_date"], p["status"]))

    def _add_payment_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add Payment Record")
        win.geometry("380x420")
        win.configure(bg=CARD_BG)
        win.grab_set()

        tk.Label(win, text="Household", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(16, 0))
        household_map = {h["head_name"]: h["id"] for h in self.store.households.values()}
        household_var = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=household_var, values=list(household_map.keys()),
                              state="readonly")
        combo.pack(fill="x", padx=20, ipady=2)
        if household_map:
            combo.current(0)

        labels_keys = [("Particulars", "particulars"), ("Amount", "amount"), ("Due Date", "due_date")]
        fields = {}
        for label, key in labels_keys:
            tk.Label(win, text=label, bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 0))
            default = str(date.today()) if key == "due_date" else ""
            var = tk.StringVar(value=default)
            tk.Entry(win, textvariable=var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1).pack(fill="x", padx=20, ipady=4)
            fields[key] = var

        def save():
            hname = household_var.get()
            if hname not in household_map:
                messagebox.showerror("Invalid Input", "Please select a household.")
                return
            try:
                amount = float(fields["amount"].get().strip())
            except ValueError:
                messagebox.showerror("Invalid Input", "Amount must be a number.")
                return
            particulars = fields["particulars"].get().strip()
            due_date = fields["due_date"].get().strip()
            if not particulars or not due_date:
                messagebox.showerror("Invalid Input", "Particulars and Due Date are required.")
                return
            self.store.add_payment(household_map[hname], particulars, amount, due_date)
            win.destroy()
            self._refresh_payments()

        self._styled_button(win, "Save", save, color=SUCCESS).pack(pady=16)

    def _mark_paid(self):
        sel = self.payments_tree.selection()
        if not sel:
            messagebox.showinfo("Select Payment", "Please select a payment record.")
            return
        self.store.update_payment_status(int(sel[0]), "Paid")
        self._refresh_payments()

    def _delete_payment(self):
        sel = self.payments_tree.selection()
        if not sel:
            messagebox.showinfo("Select Payment", "Please select a payment record to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete this payment record?"):
            self.store.delete_payment(int(sel[0]))
            self._refresh_payments()

    # ==================================================================
    # 7. REPORTS & ANALYTICS
    # ==================================================================
    def _build_reports(self):
        summary = self.store.report_summary()

        cards_frame = tk.Frame(self.body, bg=BG)
        cards_frame.pack(fill="x", pady=(0, 16))

        stat_cards = [
            ("Total Residents", summary["total_residents"], ACCENT),
            ("Total Households", summary["total_households"], "#8e44ad"),
            ("Total Complaints", summary["total_complaints"], WARNING),
            ("Upcoming Events", summary["total_events"], SUCCESS),
            ("Collected Dues", f"₱{summary['total_collected']:.2f}", SUCCESS),
            ("Outstanding Dues", f"₱{summary['total_due']:.2f}", DANGER),
        ]

        for i, (label, value, color) in enumerate(stat_cards):
            card = tk.Frame(cards_frame, bg=CARD_BG, padx=16, pady=14)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            cards_frame.grid_columnconfigure(i % 3, weight=1)
            tk.Label(card, text=str(value), font=(FONT_FAMILY, 20, "bold"), bg=CARD_BG,
                     fg=color).pack(anchor="w")
            tk.Label(card, text=label, font=(FONT_FAMILY, 9), bg=CARD_BG,
                     fg="#7f8c8d").pack(anchor="w")

        # Complaint status breakdown (simple bar chart using Canvas)
        chart_frame = tk.Frame(self.body, bg=CARD_BG, padx=20, pady=16)
        chart_frame.pack(fill="both", expand=True)
        tk.Label(chart_frame, text="Complaint Status Breakdown", font=(FONT_FAMILY, 11, "bold"),
                 bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w", pady=(0, 10))

        counts = summary["complaint_counts"]
        max_val = max(counts.values()) if counts.values() and max(counts.values()) > 0 else 1
        colors = {"Open": DANGER, "In Progress": WARNING, "Resolved": SUCCESS}

        for status, count in counts.items():
            row = tk.Frame(chart_frame, bg=CARD_BG)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=status, font=(FONT_FAMILY, 9), bg=CARD_BG, width=14,
                     anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg="#ecf0f1", height=20)
            bar_bg.pack(side="left", fill="x", expand=True)
            bar_width_ratio = count / max_val
            bar = tk.Frame(bar_bg, bg=colors.get(status, ACCENT), height=20)
            bar.place(relx=0, rely=0, relwidth=max(bar_width_ratio, 0.02), relheight=1)
            tk.Label(row, text=str(count), font=(FONT_FAMILY, 9, "bold"), bg=CARD_BG,
                     width=4).pack(side="left")

        tk.Label(chart_frame, text=f"Total Announcements Posted: {summary['total_announcements']}",
                 font=(FONT_FAMILY, 9), bg=CARD_BG, fg="#7f8c8d").pack(anchor="w", pady=(16, 0))

    # ==================================================================
    # USER MANAGEMENT (Admin only)
    # ==================================================================
    def _build_user_management(self):
        bar = self._toolbar(self.body)
        self._styled_button(bar, "+ Add User", self._add_user_dialog)
        self._styled_button(bar, "🗑 Delete", self._delete_user, color=DANGER)

        self.users_tree = self._make_tree(
            self.body,
            columns=("username", "full_name", "role"),
            headings=("Username", "Full Name", "Role"),
            widths=(160, 220, 120),
        )
        self._refresh_users()

    def _refresh_users(self):
        tree = self.users_tree
        tree.delete(*tree.get_children())
        for username, info in self.store.users.items():
            tree.insert("", "end", iid=username,
                        values=(username, info.get("full_name", ""), info["role"]))

    def _add_user_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add User")
        win.geometry("360x340")
        win.configure(bg=CARD_BG)
        win.grab_set()

        labels_keys = [("Username", "username"), ("Password", "password"), ("Full Name", "full_name")]
        fields = {}
        for label, key in labels_keys:
            tk.Label(win, text=label, bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                     anchor="w").pack(fill="x", padx=20, pady=(14, 0))
            var = tk.StringVar()
            tk.Entry(win, textvariable=var, font=(FONT_FAMILY, 10), relief="solid",
                      bd=1).pack(fill="x", padx=20, ipady=4)
            fields[key] = var

        tk.Label(win, text="Role", bg=CARD_BG, font=(FONT_FAMILY, 9, "bold"),
                 anchor="w").pack(fill="x", padx=20, pady=(14, 0))
        role_var = tk.StringVar(value="Staff")
        ttk.Combobox(win, textvariable=role_var, values=["Admin", "Staff", "Resident"],
                     state="readonly").pack(fill="x", padx=20, ipady=2)

        def save():
            username = fields["username"].get().strip()
            password = fields["password"].get().strip()
            full_name = fields["full_name"].get().strip()
            if not username or not password or not full_name:
                messagebox.showerror("Invalid Input", "All fields are required.")
                return
            if username in self.store.users:
                messagebox.showerror("Duplicate User", "That username already exists.")
                return
            self.store.users[username] = {"password": password, "role": role_var.get(),
                                           "full_name": full_name}
            win.destroy()
            self._refresh_users()

        self._styled_button(win, "Create User", save, color=SUCCESS).pack(pady=16)

    def _delete_user(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showinfo("Select User", "Please select a user to delete.")
            return
        username = sel[0]
        if username == self.user["username"]:
            messagebox.showerror("Not Allowed", "You cannot delete your own currently logged-in account.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?"):
            self.store.users.pop(username, None)
            self._refresh_users()


# ========================================================================
def main():
    store = DataStore()
    login = LoginWindow(store)
    login.mainloop()


if __name__ == "__main__":
    main()
