import tkinter as tk
import re
from tkinter import ttk, messagebox
from core.db import DBHelper

class VehiclePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#ecf0f1")
        self.pack(fill="both", expand=True)

        self.db = DBHelper()

        self.customer_map = {}  
        self.model_map = {}     

        self.create_widgets()
        
        self.load_combobox_data()
        self.load_vehicles()

    def create_widgets(self):
        form_frame = tk.LabelFrame(self, text="Add New Vehicle", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(form_frame, text="License Plate:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_plate = tk.Entry(form_frame, width=18)
        self.entry_plate.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Chassis No:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_chassis = tk.Entry(form_frame, width=18)
        self.entry_chassis.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Engine No:", bg="#ecf0f1").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_engine = tk.Entry(form_frame, width=18)
        self.entry_engine.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="Mileage:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_mileage = tk.Entry(form_frame, width=18)
        self.entry_mileage.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Prod. Year:", bg="#ecf0f1").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_year = tk.Entry(form_frame, width=18)
        self.entry_year.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Customer:", bg="#ecf0f1").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.combo_customer = ttk.Combobox(form_frame, state="readonly", width=16)
        self.combo_customer.grid(row=1, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="Vehicle Model:", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.combo_model = ttk.Combobox(form_frame, state="readonly", width=16)
        self.combo_model.grid(row=2, column=1, padx=5, pady=5)

        add_btn = tk.Button(form_frame, text="Save Vehicle", bg="#27ae60", fg="white", 
                            font=("Arial", 10, "bold"), width=15, command=self.add_vehicle)
        add_btn.grid(row=2, column=4, columnspan=2, pady=10, sticky="e")

        # ---TABLE ---
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")

        columns = ("VehicleID", "LicensePlate", "ChassisNo", "EngineNo", "Mileage", "ProductionYear", "Customer", "Model")
        display_cols = ("LicensePlate", "ChassisNo", "EngineNo", "Mileage", "ProductionYear", "Customer", "Model")
        
        self.tree = ttk.Treeview(table_frame, columns=columns,displaycolumns= display_cols, show="headings", 
                                 yscrollcommand=scroll_y.set, height=15)
        
        self.tree.heading("LicensePlate", text="Plate")
        self.tree.heading("ChassisNo", text="Chassis")
        self.tree.heading("EngineNo", text="Engine")
        self.tree.heading("Mileage", text="KM")
        self.tree.heading("ProductionYear", text="Year")
        self.tree.heading("Customer", text="Customer") 
        self.tree.heading("Model", text="Model")

        self.tree.column("LicensePlate", width=90, anchor="center")
        self.tree.column("ChassisNo", width=110, anchor="center")
        self.tree.column("EngineNo", width=100, anchor="center")
        self.tree.column("Mileage", width=70, anchor="center")
        self.tree.column("ProductionYear", width=60, anchor="center")
        self.tree.column("Customer", width=120, anchor="w")
        self.tree.column("Model", width=120, anchor="w")

        self.tree.pack(fill="both", expand=True)
        scroll_y.config(command=self.tree.yview)

    # ================= DB =================

    def load_combobox_data(self):
        self.customer_map.clear()
        self.model_map.clear()
        
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                
                cur.execute("SELECT CustomerID, FirstName, LastName FROM Customer")
                for cid, fname, lname in cur.fetchall():
                    full_name = f"{fname} {lname}"
                    self.customer_map[full_name] = cid 
                
                cur.execute("SELECT ModelID, Make, ModelName FROM VehicleModel") 
                for mid, make, mname in cur.fetchall():
                    model_display = f"{make} - {mname}"
                    self.model_map[model_display] = mid

                self.combo_customer['values'] = list(self.customer_map.keys())
                self.combo_model['values'] = list(self.model_map.keys())
                
            except Exception as e:
                print(f"Combobox Data Error: {e}")
            finally:
                conn.close()

    def load_vehicles(self):
        """Veritabanından araçları çeker. Mümkünse JOIN yaparak isimleri getirir."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT 
                        V.VehicleID, 
                        V.LicensePlate, 
                        V.ChassisNo, 
                        V.EngineNo, 
                        V.Mileage, 
                        V.ProductionYear, 
                        (C.FirstName + ' ' + C.LastName) as CustomerName,
                        (VM.Make + ' ' + VM.ModelName) as ModelName
                    FROM Vehicle V
                    LEFT JOIN Customer C ON V.CustomerID = C.CustomerID
                    LEFT JOIN VehicleModel VM ON V.ModelID = VM.ModelID
                """
                cur.execute(query)
                rows = cur.fetchall()

                for row in rows:
                    clean_row = [str(item) if item is not None else "" for item in row]
                    self.tree.insert("", tk.END, values=clean_row)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load vehicles:\n{e}")
            finally:
                conn.close()

    def add_vehicle(self):
        plate = self.entry_plate.get().strip()
        chassis = self.entry_chassis.get().strip()
        engine = self.entry_engine.get().strip()
        mileage = self.entry_mileage.get().strip()
        year = self.entry_year.get().strip()
        
        selected_customer_name = self.combo_customer.get()
        selected_model_name = self.combo_model.get()

        if not plate or not chassis:
            messagebox.showwarning("Missing Info", "License Plate and Chassis No are required!")
            return
        
        if not selected_customer_name or not selected_model_name:
            messagebox.showwarning("Missing Info", "Please select a Customer and a Model!")
            return
        
        if not re.fullmatch(r"^[A-Za-z0-9]{17}$", chassis):
            messagebox.showwarning("Invalid Input", "Chassis No must be exactly 17 alphanumeric characters.")
            return

        if not re.fullmatch(r"^[A-Za-z0-9]{9}$", engine):
            messagebox.showwarning("Invalid Input", "Engine No must be exactly 9 alphanumeric characters.")
            return

        cust_id = self.customer_map.get(selected_customer_name)
        model_id = self.model_map.get(selected_model_name)

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    INSERT INTO Vehicle (LicensePlate, ChassisNo, EngineNo, Mileage, ProductionYear, CustomerID, ModelID)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                mileage_val = int(mileage) if mileage else 0
                year_val = int(year) if year else None

                cur.execute(query, (plate, chassis, engine, mileage_val, year_val, cust_id, model_id))
                conn.commit()
                messagebox.showinfo("Success", "Vehicle added successfully.")
                
                self.load_vehicles()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not add vehicle:\n{e}")
            finally:
                conn.close()

    def delete_vehicle(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a vehicle to delete.")
            return

        item_data = self.tree.item(selected_item[0])
        vehicle_id = item_data['values'][0]

        if messagebox.askyesno("Confirm", f"Delete vehicle ID: {vehicle_id}?"):
            conn = self.db.connect()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM Vehicle WHERE VehicleID = ?", (vehicle_id,))
                    conn.commit()
                    messagebox.showinfo("Deleted", "Vehicle deleted.")
                    self.load_vehicles()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete:\n{e}")
                finally:
                    conn.close()

    def clear_form(self):
        self.entry_plate.delete(0, tk.END)
        self.entry_chassis.delete(0, tk.END)
        self.entry_engine.delete(0, tk.END)
        self.entry_mileage.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.combo_customer.set("")
        self.combo_model.set("")