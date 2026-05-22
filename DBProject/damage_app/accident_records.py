import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
from datetime import datetime
import re

class AccidentRecordPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#ecf0f1")
        self.pack(fill="both", expand=True)

        self.db = DBHelper()
    

        self.vehicles = {} 
        tk.Label(self, text="Accident Records", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", padx=20, pady=(20, 20))

        self.build_form()
        self.build_table()
        
        self.load_vehicles()
        self.load_accidents()

    # ================= FORM =================
    def build_form(self):
        form_frame = tk.LabelFrame(self, text="New Accident Record", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        form_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Vehicle Selection and Date
        tk.Label(form_frame, text="Select Vehicle:", bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_vehicle = ttk.Combobox(form_frame, width=30, state="readonly")
        self.combo_vehicle.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Accident Date (YYYY-MM-DD):", bg="white").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_date = tk.Entry(form_frame, width=20, bg="#f9f9f9")
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d")) 
        self.entry_date.grid(row=0, column=3, padx=5, pady=5)

        # Location
        tk.Label(form_frame, text="Accident Location:", bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_location = tk.Entry(form_frame, width=33, bg="#f9f9f9")
        self.entry_location.grid(row=1, column=1, padx=5, pady=5)

        # Description
        tk.Label(form_frame, text="Event Description:", bg="white").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.text_desc = tk.Text(form_frame, width=80, height=3, bg="#f9f9f9")
        self.text_desc.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)


        btn_add = tk.Button(form_frame, text="+ Add Accident Record", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"),
                            command=self.add_accident)
        btn_add.grid(row=3, column=3, sticky="e", pady=10)

    # ================= TABLE AREA =================
    def build_table(self):
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols = ("AccidentID", "Date", "LicensePlate", "Location", "Description")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        
        self.tree.heading("AccidentID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("LicensePlate", text="Vehicle Plate")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Description", text="Description")

        self.tree.column("AccidentID", width=50, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("LicensePlate", width=100, anchor="center")
        self.tree.column("Location", width=150)
        self.tree.column("Description", width=300)

        scrolly = ttk.Scrollbar(table_frame, command=self.tree.yview)
        scrolly.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrolly.set)
        
        self.tree.pack(fill="both", expand=True)


        btn_del = tk.Button(self, text="Delete Selected Record", bg="#7f8c8d", fg="white", 
                            command=self.delete_record)
        btn_del.pack(anchor="e", padx=20, pady=10)

    # ================= DB =================
    def load_vehicles(self):
        self.vehicles.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT VehicleID, LicensePlate FROM Vehicle")
        values = []
        for vid, plate in cur.fetchall():
            self.vehicles[plate] = vid
            values.append(plate)
        conn.close()
        self.combo_vehicle["values"] = values

    def load_accidents(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT AR.AccidentID, AR.AccidentDate, V.LicensePlate, AR.AccidentLocation, AR.EventDescription
            FROM AccidentRecord AR
            JOIN Vehicle V ON AR.VehicleID = V.VehicleID
            ORDER BY AR.AccidentDate DESC
        """)
        for row in cur.fetchall():
            date_str = row[1].strftime("%Y-%m-%d") if row[1] else "-"
            vals = (row[0], date_str, row[2], row[3], row[4])
            self.tree.insert("", tk.END, values=vals)
        conn.close()

    def add_accident(self):
        plate = self.combo_vehicle.get()
        date_str = self.entry_date.get().strip()
        location = self.entry_location.get().strip()
        desc = self.text_desc.get("1.0", tk.END).strip()

        if not plate or plate not in self.vehicles:
            messagebox.showerror("Error", "Please select a valid vehicle.")
            return
        
        if not date_str:
            messagebox.showerror("Error", "Date is required.")
            return

        # DATE VALIDATION
        try:
            input_date = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now()
            
            # Check for future date
            if input_date > today:
                messagebox.showwarning("Invalid Date", "Accident date cannot be in the future!")
                return
        except ValueError:
            messagebox.showerror("Format Error", "Date format must be YYYY-MM-DD.")
            return

        vehicle_id = self.vehicles[plate]

        conn = self.db.connect()
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO AccidentRecord (VehicleID, AccidentDate, AccidentLocation, EventDescription)
                VALUES (?, ?, ?, ?)
            """
            cur.execute(query, (vehicle_id, date_str, location, desc))
            conn.commit()
            messagebox.showinfo("Success", "Accident record added.")
            
            self.combo_vehicle.set("")
            self.entry_location.delete(0, tk.END)
            self.text_desc.delete("1.0", tk.END)
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            self.load_accidents()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a record to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Do you want to delete the selected accident record?"):
            return

        acc_id = self.tree.item(selected[0])["values"][0]

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM AccidentRecord WHERE AccidentID = ?", (acc_id,))
            conn.commit()
            conn.close()
            self.load_accidents()
            messagebox.showinfo("Deleted", "Record deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))