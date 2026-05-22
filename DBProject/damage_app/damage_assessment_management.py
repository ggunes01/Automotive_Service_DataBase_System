import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
from datetime import datetime

class DamageAssessmentPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#ecf0f1")
        self.pack(fill="both", expand=True)

        self.db = DBHelper()
        self.accident_map = {} 

        self.create_widgets()
        self.load_combobox_data()
        self.load_assessments()

    def create_widgets(self):
        form_frame = tk.LabelFrame(self, text="New Damage Assessment", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(form_frame, text="Select Accident:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_accident = ttk.Combobox(form_frame, state="readonly", width=35)
        self.combo_accident.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Date:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_date = tk.Entry(form_frame, width=15)
        self.entry_date.grid(row=0, column=3, padx=5, pady=5)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="Level:", bg="#ecf0f1").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.combo_level = ttk.Combobox(form_frame, state="readonly", width=15, 
                                        values=["Minor", "Moderate", "Severe", "Total Loss"])
        self.combo_level.current(0)
        self.combo_level.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="Report No:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_report_no = tk.Entry(form_frame, width=35)
        self.entry_report_no.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        add_btn = tk.Button(form_frame, text="Create Assessment", bg="#e67e22", fg="white", 
                            font=("Arial", 9, "bold"), width=18, command=self.add_assessment)
        add_btn.grid(row=1, column=4, padx=5, pady=10)

        detail_btn = tk.Button(form_frame, text="Manage Details (Parts)", bg="#3498db", fg="white",
                               font=("Arial", 9, "bold"), width=20, command=self.open_details_window)
        detail_btn.grid(row=1, column=5, padx=5, pady=10)

        # --- 2. TABLE AREA ---
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")

        columns = ("AssessmentID", "Plate", "Date", "ReportNo", "DamageLevel")
        display_cols = ("Plate", "Date", "ReportNo", "DamageLevel")

        self.tree = ttk.Treeview(table_frame, columns=columns, displaycolumns=display_cols,
                                 show="headings", yscrollcommand=scroll_y.set, height=12)
        
        self.tree.heading("Plate", text="Vehicle Plate")
        self.tree.heading("Date", text="Assessment Date")
        self.tree.heading("ReportNo", text="Expertise Report No")
        self.tree.heading("DamageLevel", text="Damage Level")

        self.tree.column("Plate", width=120, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("ReportNo", width=150, anchor="w")
        self.tree.column("DamageLevel", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)
        scroll_y.config(command=self.tree.yview)


    # ================= DB =================

    def load_combobox_data(self):
        self.accident_map.clear()
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT A.AccidentID, V.LicensePlate, A.AccidentDate 
                    FROM AccidentRecord A
                    JOIN Vehicle V ON A.VehicleID = V.VehicleID
                """
                cur.execute(query)
                rows = cur.fetchall()
                for aid, plate, acc_date in rows:
                    display_text = f"{plate} - {acc_date}"
                    self.accident_map[display_text] = aid
                self.combo_accident['values'] = list(self.accident_map.keys())
            finally:
                conn.close()

    def load_assessments(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT DA.AssessmentID, V.LicensePlate, DA.AssessmentDate, 
                           DA.ExpertiseReportNo, DA.DamageLevel
                    FROM DamageAssessment DA
                    JOIN AccidentRecord AR ON DA.AccidentID = AR.AccidentID
                    JOIN Vehicle V ON AR.VehicleID = V.VehicleID
                    ORDER BY DA.AssessmentDate DESC
                """
                cur.execute(query)
                for row in cur.fetchall():
                    self.tree.insert("", tk.END, values=[str(x) for x in row])
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def add_assessment(self):
        selection = self.combo_accident.get()
        date_val = self.entry_date.get().strip()
        report_no = self.entry_report_no.get().strip()
        level = self.combo_level.get()

        if not selection or not date_val or not report_no:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        acc_id = self.accident_map.get(selection)
        
        current_user_id = getattr(self.master, "current_user_id", 1) 

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                
                cur.execute("SELECT COUNT(*) FROM DamageAssessment WHERE ExpertiseReportNo = ?", (report_no,))
                if cur.fetchone()[0] > 0:
                    messagebox.showwarning("Duplicate", "Report No already exists!")
                    return

                query = """
                    INSERT INTO DamageAssessment 
                    (AccidentID, AssessmentDate, ExpertiseReportNo, DamageLevel, AssessedByPersonnelID)
                    VALUES (?, ?, ?, ?, ?)
                """
                cur.execute(query, (acc_id, date_val, report_no, level, current_user_id))
                conn.commit()
                
                messagebox.showinfo("Success", "Assessment Created.")
                self.load_assessments()
                self.entry_report_no.delete(0, tk.END)
                
            except Exception as e:
                messagebox.showerror("Error", f"Database Error:\n{e}")
            finally:
                conn.close()

    def open_details_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an Assessment first to add details.")
            return
        
        item_vals = self.tree.item(selected[0])['values']
        assessment_id = item_vals[0]
        plate = item_vals[1]

        detail_win = tk.Toplevel(self)
        detail_win.title(f"Damage Details for Assessment #{assessment_id} ({plate})")
        detail_win.geometry("650x450")

        f_top = tk.Frame(detail_win, pady=10)
        f_top.pack(fill="x")

        tk.Label(f_top, text="Damaged Area:").pack(side="left", padx=5)
        entry_area = tk.Entry(f_top, width=20)
        entry_area.pack(side="left", padx=5)

        tk.Label(f_top, text="Repair Type:").pack(side="left", padx=5)
        combo_type = ttk.Combobox(f_top, width=15, values=["Repair", "Replace", "Paint", "Check"])
        combo_type.pack(side="left", padx=5)

        cols = ("ID", "Area", "Type")
        disp_cols = ("Area", "Type")

        tree_det = ttk.Treeview(detail_win, columns=cols, displaycolumns=disp_cols, show="headings")
        tree_det.heading("Area", text="Damaged Area")
        tree_det.heading("Type", text="Repair Type")
        
        tree_det.column("Area", width=300, anchor="w")
        tree_det.column("Type", width=150, anchor="center")
        
        tree_det.pack(fill="both", expand=True, padx=10, pady=5)

        def load_details():
            for row in tree_det.get_children():
                tree_det.delete(row)
            conn = self.db.connect()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT DamageDetailID, DamagedArea, RepairType FROM DamageDetail WHERE AssessmentID = ?", (assessment_id,))
                    for r in cur.fetchall():
                        tree_det.insert("", tk.END, values=list(r))
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                finally:
                    conn.close()

        def add_detail():
            area = entry_area.get()
            rtype = combo_type.get()
            if not area or not rtype:
                messagebox.showwarning("Warning", "Area and Type are required!")
                return
            conn = self.db.connect()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO DamageDetail (DamagedArea, RepairType, AssessmentID) VALUES (?, ?, ?)", (area, rtype, assessment_id))
                    conn.commit()
                    load_details()
                    entry_area.delete(0, tk.END)
                finally:
                    conn.close()

        def delete_detail():
            sel = tree_det.selection()
            if not sel: 
                messagebox.showwarning("Warning", "Select an item to remove.")
                return
            did = tree_det.item(sel[0])['values'][0]
            
            conn = self.db.connect()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM DamageDetail WHERE DamageDetailID = ?", (did,))
                    conn.commit()
                    load_details()
                finally:
                    conn.close()

        btn_add = tk.Button(f_top, text="+ Add", bg="#27ae60", fg="white", command=add_detail)
        btn_add.pack(side="left", padx=10)
        btn_del = tk.Button(detail_win, text="Remove Selected Item", bg="#c0392b", fg="white", command=delete_detail)
        btn_del.pack(pady=5)

        load_details()