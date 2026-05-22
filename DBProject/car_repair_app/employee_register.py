import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import hashlib
import re
from datetime import datetime  

class EmployeeRegister:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.positions = {}
        self.departments = {}

        # 2. Main Frane
        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Employee Management (Secure Register)", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.build_form()
        self.load_positions()
        self.load_departments()

    def build_form(self):
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(self.form_frame, text="First Name:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_fname = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_fname.grid(row=0, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Last Name:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_lname = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_lname.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Email:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_email = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_email.grid(row=2, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Phone:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_phone = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_phone.grid(row=3, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Hire Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_hiredate = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_hiredate.insert(0, datetime.now().strftime("%Y-%m-%d")) # Otomatik Bugün
        self.entry_hiredate.grid(row=0, column=3, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Position:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        self.combo_position = ttk.Combobox(self.form_frame, width=28, state="readonly", font=("Segoe UI", 10))
        self.combo_position.grid(row=1, column=3, sticky="w", padx=10, pady=5)

        tk.Label(self.form_frame, text="Department:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=2, sticky="w", padx=(40, 10), pady=5)
        self.combo_department = ttk.Combobox(self.form_frame, width=28, state="readonly", font=("Segoe UI", 10))
        self.combo_department.grid(row=2, column=3, sticky="w", padx=10, pady=5)

        tk.Label(self.form_frame, text="Password:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=3, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_password = tk.Entry(self.form_frame, width=30, show="•", font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_password.grid(row=3, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # Buttons
        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.grid(row=4, column=3, sticky="e", pady=20)
        
        tk.Button(btn_frame, text="Clear Fields", bg="#95a5a6", fg="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", 
                  command=self.clear_fields).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="+ Add Employee", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", 
                  command=self.add_employee).pack(side="left", padx=5)

    def load_positions(self):
        self.positions.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT PositionID, PositionName FROM Position")
        except:
            try: cur.execute("SELECT PositionID, Name FROM Position")
            except: pass
        
        values = []
        for pid, name in cur.fetchall():
            self.positions[name] = pid
            values.append(name)
        conn.close()
        self.combo_position["values"] = values

    def load_departments(self):
        self.departments.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("SELECT DepartmentID, DepartmentName FROM Department")
        except:
            try: cur.execute("SELECT DepartmentID, Name FROM Department")
            except: pass
        
        values = []
        for did, name in cur.fetchall():
            self.departments[name] = did
            values.append(name)
        conn.close()
        self.combo_department["values"] = values

    def add_employee(self):
        fname = self.entry_fname.get().strip()
        lname = self.entry_lname.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()
        hiredate = self.entry_hiredate.get().strip()
        pos_name = self.combo_position.get().strip()
        dep_name = self.combo_department.get().strip()
        raw_password = self.entry_password.get().strip()

        if not fname or not lname or not hiredate or not raw_password:
            messagebox.showerror("Error", "FirstName, Last Name, Date and Password must entered.")
            return
        email_pattern = r"^[\w\.-]+@gmail\.com$"
        
        if not re.match(email_pattern, email):
            messagebox.showwarning("Invalid Email\n", 
                                   "Ex: example@gmail.com")
            return

        # --- Date Check  ---
        try:
            # Check the format: YYYY-MM-DD
            datetime.strptime(hiredate, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Date Error", 
                                   "Invalid Date Format!\n"
                                   "Please enter in this format YYYY-AA-GG \n"
                                   "Ex: 2025-01-15")
            return

        hashed_password = hashlib.sha256(raw_password.encode('utf-8')).hexdigest()

        position_id = self.positions.get(pos_name) if pos_name else None
        department_id = self.departments.get(dep_name) if dep_name else None

        conn = None
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Personnel
                (FirstName, LastName, Email, Phone, HireDate,
                 PositionID, DepartmentID, Password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (fname, lname, email, phone, hiredate,
                  position_id, department_id, hashed_password))
            conn.commit()
            messagebox.showinfo("Succesfull", "Personel added.")
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Database Error", str(e))
            return
        finally:
            if conn: conn.close()

        self.clear_fields()

    def clear_fields(self):
        self.entry_fname.delete(0, tk.END)
        self.entry_lname.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_phone.delete(0, tk.END)
        self.entry_hiredate.delete(0, tk.END)
        self.entry_hiredate.insert(0, datetime.now().strftime("%Y-%m-%d")) 
        self.entry_password.delete(0, tk.END)
        self.combo_position.set("")
        self.combo_department.set("")
