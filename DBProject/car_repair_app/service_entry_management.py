import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import re
from datetime import datetime

class ServiceEntryManagement:
    def __init__(self, parent):
        """
        parent: Ana menüdeki content_area frame'i
        """
        self.db = DBHelper()
        self.parent = parent
        

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.vehicles = {}   
        self.personnel = {}  


        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)


        tk.Label(self.main_frame, text="Service Entry (Vehicle Check-In)", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.build_form()
        
        self.load_vehicles()
        self.load_personnel()
        self.load_entries()

    def format_date(self, value):
        """Render datetime/date columns as YYYY-MM-DD strings."""
        if value is None:
            return ""
        try:
            return value.strftime("%Y-%m-%d")
        except Exception:
            return str(value)

    # =============== FORM ===============
    def build_form(self):
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        # Vehicle
        tk.Label(self.form_frame, text="Select Vehicle:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.combo_vehicle = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_vehicle.grid(row=0, column=1, sticky="w", padx=10, pady=5, ipady=4)

        # Personnel
        tk.Label(self.form_frame, text="Accepting Personnel:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        
        self.combo_personnel = ttk.Combobox(self.form_frame, width=30, state="readonly", font=("Segoe UI", 10))
        self.combo_personnel.grid(row=0, column=3, sticky="w", padx=10, pady=5, ipady=4)


        # Entry Date
        tk.Label(self.form_frame, text="Entry Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.entry_date = tk.Entry(self.form_frame, font=("Segoe UI", 10), width=20,
                                   bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_date.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=4)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Estimated Date
        tk.Label(self.form_frame, text="Est. Delivery (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        
        self.entry_est_date = tk.Entry(self.form_frame, font=("Segoe UI", 10), width=20,
                                       bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_est_date.grid(row=1, column=3, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Notes / Issues:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=2, column=0, sticky="nw", padx=10, pady=(15, 5))
        
        self.text_notes = tk.Text(self.form_frame, width=80, height=3, font=("Segoe UI", 10),
                                  bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.text_notes.grid(row=2, column=1, columnspan=3, sticky="we", padx=10, pady=(15, 5))

 
        add_btn = tk.Button(self.form_frame, text="+ Create Service Entry", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_service_entry)
        add_btn.grid(row=3, column=3, sticky="e", pady=15, padx=10, ipadx=10, ipady=5)


        # =============== TABLE =================
        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("EntryID", "EntryDate", "EstimatedDelivery", "VehiclePlate", "CustomerName", "AcceptingPersonnel", "Notes")
        display_cols = ("EntryDate", "EstimatedDelivery", "VehiclePlate", "CustomerName", "AcceptingPersonnel", "Notes")
        
        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, show="headings", height=10,
                                 yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "EntryDate": 90, "EstimatedDelivery": 110,
            "VehiclePlate": 100, "CustomerName": 120, "AcceptingPersonnel": 120, "Notes": 200
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        delete_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        delete_frame.pack(fill="x", pady=10)
        
        delete_btn = tk.Button(delete_frame, text="Delete Selected Entry", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_service_entry)
        delete_btn.pack(side="right", ipadx=10, ipady=5)

    def load_vehicles(self):
        self.vehicles.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                V.VehicleID, V.LicensePlate, C.FirstName, C.LastName
            FROM Vehicle V
            JOIN Customer C ON V.CustomerID = C.CustomerID
        """)
        values = []
        for vid, plate, fn, ln in cur.fetchall():
            display = f"{plate} - {fn} {ln}"
            self.vehicles[display] = vid
            values.append(display)
        conn.close()
        self.combo_vehicle["values"] = values

    def load_personnel(self):
        self.personnel.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT PersonnelID, FirstName, LastName
            FROM Personnel
        """)
        values = []
        for pid, fn, ln in cur.fetchall():
            name = f"{fn} {ln}"
            self.personnel[name] = pid
            values.append(name)
        conn.close()
        self.combo_personnel["values"] = values

    def load_entries(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                SE.EntryID, SE.EntryDate, SE.EstimatedDeliveryDate,
                V.LicensePlate,
                (C.FirstName + ' ' + C.LastName) AS CustomerName,
                (P.FirstName + ' ' + P.LastName) AS PersonnelName,
                SE.Notes
            FROM ServiceEntry SE
            JOIN Vehicle   V ON SE.VehicleID = V.VehicleID
            JOIN Customer  C ON V.CustomerID = C.CustomerID
            JOIN Personnel P ON SE.AcceptedByPersonnelID = P.PersonnelID
        """)

        for row in cur.fetchall():
            entry_id, entry_date, est_date, plate, customer, personnel, notes = row
            formatted = (
                entry_id,
                self.format_date(entry_date),
                self.format_date(est_date),
                plate,
                customer,
                personnel,
                notes if notes is not None else ""
            )
            self.tree.insert("", tk.END, values=formatted)

        conn.close()


    def add_service_entry(self):
        vehicle_display = self.combo_vehicle.get().strip()
        personnel_display = self.combo_personnel.get().strip()
        entry_date_str = self.entry_date.get().strip()
        est_date_str = self.entry_est_date.get().strip()
        notes = self.text_notes.get("1.0", tk.END).strip()

        if not vehicle_display or vehicle_display not in self.vehicles:
            messagebox.showerror("Hata", "Lütfen bir araç seçin.")
            return

        if not personnel_display or personnel_display not in self.personnel:
            messagebox.showerror("Hata", "Lütfen teslim alan personeli seçin.")
            return

        if not entry_date_str:
            messagebox.showerror("Hata", "Giriş tarihi zorunludur.")
            return

        try:
            d_entry = datetime.strptime(entry_date_str, "%Y-%m-%d")
            
            if est_date_str: 
                d_est = datetime.strptime(est_date_str, "%Y-%m-%d")
                
                if d_est < d_entry:
                    messagebox.showwarning("Tarih Hatası", 
                        "Tahmini teslim tarihi, giriş tarihinden eski olamaz!\n"
                        "Lütfen tarihleri kontrol ediniz.")
                    return
        except ValueError:
            messagebox.showerror("Format Hatası", "Tarih formatı hatalı! (YYYY-MM-DD olmalı)\nÖrn: 2025-12-14")
            return

        vehicle_id = self.vehicles[vehicle_display]
        personnel_id = self.personnel[personnel_display]

        conn = None
        try:
            conn = self.db.connect()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO ServiceEntry
                (VehicleID, EntryDate, EstimatedDeliveryDate, Notes, AcceptedByPersonnelID)
                VALUES (?, ?, ?, ?, ?)
            """, (vehicle_id, entry_date_str, est_date_str, notes, personnel_id))

            conn.commit()
            
            messagebox.showinfo("Başarılı", "Servis girişi oluşturuldu.")
            self.load_entries()

            self.combo_vehicle.set("")
            self.combo_personnel.set("")
            self.entry_date.delete(0, tk.END)
            self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.entry_est_date.delete(0, tk.END)
            self.text_notes.delete("1.0", tk.END)

        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Veritabanı Hatası", str(e))
        finally:
            if conn: conn.close()


    def delete_service_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a service entry to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected service entry?"):
            return

        raw_id = self.tree.item(selected[0])["values"][0]

        if isinstance(raw_id, int):
            entry_id = raw_id
        else:
            m = re.search(r"\d+", str(raw_id))
            if not m:
                messagebox.showerror("Error", f"Invalid EntryID: {raw_id}")
                return
            entry_id = int(m.group())

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM ServiceEntry WHERE EntryID = ?", (entry_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", f"Service entry {entry_id} deleted.")
            self.load_entries()
        except Exception as e:
             messagebox.showerror("Error", str(e))