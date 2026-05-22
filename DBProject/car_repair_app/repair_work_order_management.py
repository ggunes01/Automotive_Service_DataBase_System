import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
from datetime import datetime
import re

class RepairWorkOrderManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.service_entries = {}
        self.personnel = {}
        self.assessments = {}
        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Repair Work Orders", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.build_form()
        
        self.load_service_entries()
        self.load_personnel()
        self.load_assessments()
        self.load_work_orders()

    def format_date(self, value):
        if value is None: return "-"
        try: return value.strftime("%Y-%m-%d")
        except: return str(value)

    # ================= FORM =================
    def build_form(self):
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        # --- Service Entry & Assessment ---
        tk.Label(self.form_frame, text="Service Entry:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.combo_service = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_service.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.form_frame, text="Assessment:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=40, pady=5)
        self.combo_assessment = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_assessment.grid(row=0, column=3, sticky="w", padx=10, pady=5)

        # --- Teknisyen & Start Date ---
        tk.Label(self.form_frame, text="Assigned Technician:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.combo_personnel = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_personnel.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.form_frame, text="Start Date:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=40, pady=5)
        self.entry_start = tk.Entry(self.form_frame, font=("Segoe UI", 10), width=20, bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_start.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_start.grid(row=1, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # --- Priority & Status ---
        tk.Label(self.form_frame, text="Priority:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.combo_priority = ttk.Combobox(self.form_frame, width=18, state="readonly", values=["Low", "Medium", "High", "Urgent"], font=("Segoe UI", 10))
        self.combo_priority.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.combo_priority.current(1) 

        tk.Label(self.form_frame, text="Status:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=2, sticky="w", padx=40, pady=5)
        self.combo_status = ttk.Combobox(self.form_frame, width=20, state="readonly", 
                                         values=["Pending", "In Progress", "Waiting Parts", "Completed"], 
                                         font=("Segoe UI", 10))
        self.combo_status.grid(row=2, column=3, sticky="w", padx=10, pady=5)
        self.combo_status.current(1) 

        # --- BUTON ---
        add_btn = tk.Button(self.form_frame, text="+ Create Order", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_work_order)
        add_btn.grid(row=3, column=3, sticky="e", pady=15, padx=10, ipadx=10, ipady=5)


        # ================= TABLE =================
        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("WorkOrderID", "EntryID", "StartDate", "EndDate", "Status", "Priority", 
                   "VehiclePlate", "CustomerName", "AssignedTechnician", "AssessmentID")
        
        display_cols = ("StartDate", "Status", "Priority", 
                        "VehiclePlate", "CustomerName", "AssignedTechnician")

        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, 
                                 show="headings", height=10, yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "StartDate": 90, "Status": 90, "Priority": 80, 
            "VehiclePlate": 100, "CustomerName": 120, "AssignedTechnician": 120
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.fill_form_from_selection)

        btn_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        btn_frame.pack(fill="x", pady=10)
        
        update_btn = tk.Button(btn_frame, text="Update Selected Order", bg="#2980b9", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.update_work_order)
        update_btn.pack(side="left", ipadx=10, ipady=5)

        delete_btn = tk.Button(btn_frame, text="Delete Selected Order", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_work_order)
        delete_btn.pack(side="right", ipadx=10, ipady=5)


    # ================= DB =================
    
    def load_service_entries(self):
        self.service_entries.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT SE.EntryID, SE.EntryDate, V.LicensePlate, C.FirstName, C.LastName
            FROM ServiceEntry SE
            JOIN Vehicle  V ON SE.VehicleID = V.VehicleID
            JOIN Customer C ON V.CustomerID = C.CustomerID
            ORDER BY SE.EntryDate DESC
        """)
        values = []
        for entry_id, entry_date, plate, fn, ln in cur.fetchall():
            display = f"{plate} - {fn} {ln} (Giriş: {entry_date})"
            self.service_entries[display] = entry_id
            values.append(display)
        conn.close()
        self.combo_service["values"] = values

    def load_personnel(self):
        self.personnel.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT PersonnelID, FirstName, LastName FROM Personnel")
        values = []
        for pid, fn, ln in cur.fetchall():
            name = f"{fn} {ln}"
            self.personnel[name] = pid
            values.append(name)
        conn.close()
        self.combo_personnel["values"] = values

    def load_assessments(self):
        self.assessments.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT A.AssessmentID, V.LicensePlate, A.AssessmentDate
            FROM DamageAssessment A
            LEFT JOIN AccidentRecord AR ON A.AccidentID = AR.AccidentID
            LEFT JOIN Vehicle V         ON AR.VehicleID = V.VehicleID
            ORDER BY A.AssessmentDate DESC
        """)
        values = []
        for aid, plate, date in cur.fetchall():
            plate_part = plate if plate else "?"
            display = f"Assessment #{aid} - {plate_part} ({date})"
            self.assessments[display] = aid
            values.append(display)
        conn.close()
        self.combo_assessment["values"] = values

    def load_work_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                W.WorkOrderID, W.EntryID, W.StartDate, W.EndDate, W.Status, W.Priority,
                V.LicensePlate, (C.FirstName + ' ' + C.LastName) AS CustomerName,
                (P.FirstName + ' ' + P.LastName) AS TechnicianName, W.AssessmentID
            FROM RepairWorkOrder W
            JOIN ServiceEntry SE ON W.EntryID = SE.EntryID
            JOIN Vehicle      V  ON SE.VehicleID = V.VehicleID
            JOIN Customer     C  ON V.CustomerID = C.CustomerID
            LEFT JOIN Personnel P  ON W.AssignedTechnicianID = P.PersonnelID
            ORDER BY W.WorkOrderID DESC
        """)
        for row in cur.fetchall():
            formatted = (
                row[0], row[1], self.format_date(row[2]), self.format_date(row[3]),
                row[4] or "", row[5] or "", row[6], row[7], row[8] or "Not Assigned", row[9]
            )
            self.tree.insert("", tk.END, values=formatted)
        conn.close()

    def fill_form_from_selection(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])["values"]
        
        entry_id = vals[1]
        status = vals[4]
        priority = vals[5]
        tech_name = vals[8] 
        assessment_id = vals[9]
        start_date = vals[2]

        self.entry_start.delete(0, tk.END)
        self.entry_start.insert(0, start_date)

        self.combo_status.set(status)
        self.combo_priority.set(priority)

        for key, val in self.service_entries.items():
            if val == entry_id:
                self.combo_service.set(key)
                break
        
        for key, val in self.assessments.items():
            if val == assessment_id:
                self.combo_assessment.set(key)
                break
        
        if tech_name in self.personnel:
            self.combo_personnel.set(tech_name)
        elif tech_name == "Not Assigned":
            self.combo_personnel.set("")


    def add_work_order(self):
        service_disp     = self.combo_service.get().strip()
        assessment_disp  = self.combo_assessment.get().strip()
        personnel_disp   = self.combo_personnel.get().strip()
        start_date       = self.entry_start.get().strip()
        priority         = self.combo_priority.get().strip()
        status           = self.combo_status.get().strip()
        
        if not service_disp or service_disp not in self.service_entries:
            messagebox.showerror("Error", "Select a service entry.")
            return
        if not assessment_disp or assessment_disp not in self.assessments:
            messagebox.showerror("Error", "Select an assessment.")
            return
        if not personnel_disp or personnel_disp not in self.personnel:
            messagebox.showerror("Error", "Select assigned technician.")
            return
        if not start_date:
            messagebox.showerror("Error", "Start date is required.")
            return

        entry_id      = self.service_entries[service_disp]
        assessment_id = self.assessments[assessment_disp]
        technician_id = self.personnel[personnel_disp]
        
        if status == "Completed":
            end_date_db = datetime.now()
        else:
            end_date_db = None

        conn = None
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            
            query = """
                INSERT INTO RepairWorkOrder
                (EntryID, StartDate, EndDate, Status, Priority, AssignedTechnicianID, AssessmentID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(query, (entry_id, start_date, end_date_db, status, priority, technician_id, assessment_id))
            conn.commit()
            
            messagebox.showinfo("Success", "Work order created successfully.")
            self.load_work_orders()
            
            # Reset form
            self.combo_service.set("")
            self.combo_assessment.set("")
            self.combo_personnel.set("")
            self.entry_start.delete(0, tk.END)
            self.entry_start.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.combo_priority.set("Medium")
            self.combo_status.set("In Progress")

        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("DB Error", str(e))
        finally:
            if conn: conn.close()

    def update_work_order(self):
        """Seçili kaydı formdaki yeni verilerle günceller."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen güncellenecek satırı seçin.")
            return
        
        workorder_id = self.tree.item(selected[0])["values"][0]

        service_disp     = self.combo_service.get().strip()
        assessment_disp  = self.combo_assessment.get().strip()
        personnel_disp   = self.combo_personnel.get().strip()
        start_date       = self.entry_start.get().strip()
        priority         = self.combo_priority.get().strip()
        status           = self.combo_status.get().strip()

        if not service_disp or service_disp not in self.service_entries:
            messagebox.showerror("Hata", "Geçersiz Service Entry.")
            return
        if not personnel_disp or personnel_disp not in self.personnel:
            messagebox.showerror("Hata", "Geçersiz Teknisyen.")
            return

        entry_id      = self.service_entries[service_disp]
        assessment_id = self.assessments.get(assessment_disp, None) 
        technician_id = self.personnel[personnel_disp]
        
        if status == "Completed":
            end_date_db = datetime.now()
        else:
            end_date_db = None

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            
            if assessment_id:
                query = """
                    UPDATE RepairWorkOrder
                    SET EntryID=?, StartDate=?, EndDate=?, Status=?, Priority=?, AssignedTechnicianID=?, AssessmentID=?
                    WHERE WorkOrderID=?
                """
                params = (entry_id, start_date, end_date_db, status, priority, technician_id, assessment_id, workorder_id)
            else:
                 pass

            cur.execute(query, params)
            conn.commit()
            
            messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
            self.load_work_orders()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")
        finally:
            conn.close()

    def delete_work_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a work order to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected Work Order?"):
            return

        raw_id = self.tree.item(selected[0])["values"][0]
        if isinstance(raw_id, int):
            workorder_id = raw_id
        else:
            m = re.search(r"\d+", str(raw_id))
            if not m: return
            workorder_id = int(m.group())

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM RepairWorkOrder WHERE WorkOrderID = ?", (workorder_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Work order deleted.")
            self.load_work_orders()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))