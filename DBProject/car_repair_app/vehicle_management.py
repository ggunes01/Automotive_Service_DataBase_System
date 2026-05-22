import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import re 

class VehicleManagement:
    def __init__(self, parent):
        """
        parent: Ana menüdeki content_area frame'i
        """
        self.db = DBHelper()
        self.parent = parent
        
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.customers = {}  
        self.models = {}      

       
        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)


        tk.Label(self.main_frame, text="Vehicle Management", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))


        self.build_form()
        self.load_customers()
        self.load_models()
        self.load_vehicles()

    # ===================== FORM =====================
    def build_form(self):
        # Beyaz Kart Arka Planı
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        inputs = [
            ("License Plate:", 0), ("Chassis No:", 1), 
            ("Engine No:", 2),     ("Mileage:", 3), 
            ("Production Year:", 4)
        ]

        self.entries = {} 

        for text, row in inputs:
            tk.Label(self.form_frame, text=text, font=("Segoe UI", 10, "bold"), 
                     bg="white", fg="#555").grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            entry = tk.Entry(self.form_frame, font=("Segoe UI", 10), width=25,
                             bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
            entry.grid(row=row, column=1, sticky="w", padx=10, pady=5, ipady=4)
            
            if text == "License Plate:": self.entry_plate = entry
            elif text == "Chassis No:": self.entry_chassis = entry
            elif text == "Engine No:": self.entry_engine = entry
            elif text == "Mileage:": self.entry_mileage = entry
            elif text == "Production Year:": self.entry_year = entry

        # Customer
        tk.Label(self.form_frame, text="Customer:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        
        self.combo_customer = ttk.Combobox(self.form_frame, width=28, state="readonly", font=("Segoe UI", 10))
        self.combo_customer.grid(row=0, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # Model
        tk.Label(self.form_frame, text="Vehicle Model:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        
        self.combo_model = ttk.Combobox(self.form_frame, width=28, state="readonly", font=("Segoe UI", 10))
        self.combo_model.grid(row=1, column=3, sticky="w", padx=10, pady=5, ipady=4)

        add_btn = tk.Button(self.form_frame, text="+ Add Vehicle", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_vehicle)
        add_btn.grid(row=4, column=3, sticky="e", pady=10, padx=10, ipadx=20, ipady=5)


        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("VehicleID", "LicensePlate", "ChassisNo", "EngineNo", "Mileage", "ProductionYear", "Customer", "Model")
        display_cols = ("LicensePlate", "ChassisNo", "EngineNo", "Mileage", "ProductionYear", "Customer", "Model")
        
        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, show="headings", height=10, 
                                 yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "LicensePlate": 100, "ChassisNo": 120, "EngineNo": 120,
            "Mileage": 80, "ProductionYear": 80, "Customer": 150, "Model": 150
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        delete_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        delete_frame.pack(fill="x", pady=10)
        
        delete_btn = tk.Button(delete_frame, text="Delete Selected Vehicle", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_vehicle)
        delete_btn.pack(side="right", ipadx=10, ipady=5)


    # ===================== DB =====================
    
    def load_customers(self):
        self.customers.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT CustomerID, FirstName, LastName FROM Customer")

        names = []
        for cid, fn, ln in cur.fetchall():
            name = f"{fn} {ln}"
            self.customers[name] = cid
            names.append(name)

        conn.close()
        self.combo_customer["values"] = names

    def load_models(self):
        self.models.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT ModelID, Make, ModelName FROM VehicleModel")

        models = []
        for mid, make, modelname in cur.fetchall():
            display = f"{make} {modelname}"
            self.models[display] = mid
            models.append(display)

        conn.close()
        self.combo_model["values"] = models

    def load_vehicles(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    V.VehicleID, V.LicensePlate, V.ChassisNo, V.EngineNo,
                    V.Mileage, V.ProductionYear,
                    (C.FirstName + ' ' + C.LastName) AS CustomerName,
                    (M.Make + ' ' + M.ModelName)   AS ModelName
                FROM Vehicle V
                JOIN Customer C     ON V.CustomerID = C.CustomerID
                JOIN VehicleModel M ON V.ModelID = M.ModelID
            """)

            for row in cur.fetchall():
                self.tree.insert("", tk.END, values=list(row))

        except Exception as e:
            messagebox.showerror("Hata", f"Araçlar yüklenemedi: {e}")
        finally:
            conn.close()

    def add_vehicle(self):
        plate   = self.entry_plate.get().strip()
        chassis = self.entry_chassis.get().strip()
        engine  = self.entry_engine.get().strip()
        mileage = self.entry_mileage.get().strip()
        year    = self.entry_year.get().strip()

        customer_name = self.combo_customer.get().strip()
        model_name    = self.combo_model.get().strip()

        if not plate or not chassis:
            messagebox.showerror("Error", "License plate and chassis no are required.")
            return

        if customer_name not in self.customers:
            messagebox.showerror("Error", "Select a customer.")
            return

        if model_name not in self.models:
            messagebox.showerror("Error", "Select a model.")
            return
        if not re.fullmatch(r"^[A-Za-z0-9]{17}$", chassis):
            messagebox.showwarning("Invalid Chassis No", "Chassis number needsto exactly 17 Character and must include only number or letters .")
            return

        if not re.fullmatch(r"^[A-Za-z0-9]{9}$", engine):
            messagebox.showwarning("Invalid Engine No", "Engine number needsto exactly 17 Character and must include only number or letters .")
            return

        customer_id = self.customers[customer_name]
        model_id    = self.models[model_name]

        try:
            conn = self.db.connect()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM Vehicle WHERE LicensePlate = ?", (plate,))
            count = cur.fetchone()[0]

            if count > 0:

                messagebox.showwarning("Error", f"Bu plaka ({plate}) zaten sistemde kayıtlı!")
                conn.close()
                return
            
            cur.execute("SELECT COUNT(*) FROM Vehicle WHERE ChassisNo = ?", (chassis,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Error", "This Chassis Number already registered!")
                conn.close()
                return

            cur.execute("""
                INSERT INTO Vehicle
                (LicensePlate, ChassisNo, EngineNo, Mileage, ProductionYear, CustomerID, ModelID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (plate, chassis, engine, mileage, year, customer_id, model_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Vehicle added successfully.")
            self.load_vehicles()
            
            # Temizleme
            self.entry_plate.delete(0, tk.END)
            self.entry_chassis.delete(0, tk.END)
            self.entry_engine.delete(0, tk.END)
            self.entry_mileage.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
            self.combo_customer.set("")
            self.combo_model.set("")
            
        except Exception as e:
             messagebox.showerror("Database Error", str(e))

    def delete_vehicle(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a vehicle to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected vehicle?"):
            return

        raw_id = self.tree.item(selected[0])["values"][0]

        if isinstance(raw_id, int):
            vehicle_id = raw_id
        else:
            import re
            m = re.search(r"\d+", str(raw_id))
            if not m:
                messagebox.showerror("Error", f"Invalid VehicleID: {raw_id}")
                return
            vehicle_id = int(m.group())

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM Vehicle WHERE VehicleID = ?", (vehicle_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", f"Vehicle {vehicle_id} deleted.")
            self.load_vehicles()
            
        except Exception as e:
            error_msg = str(e)

            if "REFERENCE constraint" in error_msg:
                messagebox.showerror("Silme Hatası", 
                    "Bu aracı silemezsiniz çünkü bu araca ait 'Service Entry' (Servis Giriş) kayıtları mevcut.\n\n"
                    "Önce bu araca ait servis geçmişini silmeniz gerekmektedir.")
            else:
                messagebox.showerror("Database Error", error_msg)
