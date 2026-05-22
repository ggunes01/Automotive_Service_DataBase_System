import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper

class LaborRecordManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.workorders = {}   
        self.personnel = {}    
        self.rates = {}        
        self.operations = {}   

        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Labor Records (İşçilik Kayıtları)", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.build_form()
        
        # Load Datas
        self.load_workorders()
        self.load_personnel()
        self.load_rates_smart()       
        self.load_service_operations() 
        self.load_labor_records()

    # ================= FORM =================
    def build_form(self):
        form_frame = tk.LabelFrame(self.main_frame, text="Add New Labor Record", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 20))

        # --- Work Order & Personnel ---
        tk.Label(form_frame, text="Work Order:", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_wo = ttk.Combobox(form_frame, state="readonly", width=40) # Genişletildi
        self.combo_wo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Technician:", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_personnel = ttk.Combobox(form_frame, state="readonly", width=25)
        self.combo_personnel.grid(row=0, column=3, padx=5, pady=5)

        # --- Service Operation ---
        tk.Label(form_frame, text="Standard Op (Optional):", bg="white", fg="#2980b9", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_operation = ttk.Combobox(form_frame, state="readonly", width=40)
        self.combo_operation.grid(row=1, column=1, padx=5, pady=5)
        self.combo_operation.bind("<<ComboboxSelected>>", self.on_operation_select)

        tk.Label(form_frame, text="Rate Class:", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.combo_rate = ttk.Combobox(form_frame, state="readonly", width=25)
        self.combo_rate.grid(row=1, column=3, padx=5, pady=5)
        self.combo_rate.bind("<<ComboboxSelected>>", self.on_rate_select)

        # --- Description & Hours & Rate ---
        tk.Label(form_frame, text="Description:", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_desc = tk.Entry(form_frame, width=42)
        self.entry_desc.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Hours Spent:", bg="white").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.entry_hours = tk.Entry(form_frame, width=10)
        self.entry_hours.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Hourly Rate ($):", bg="white").grid(row=2, column=3, padx=5, pady=5, sticky="e")
        self.entry_hourly_rate = tk.Entry(form_frame, width=10)
        self.entry_hourly_rate.grid(row=2, column=4, padx=5, pady=5)

        btn_add = tk.Button(form_frame, text="+ Add Record", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"),
                            command=self.add_record)
        btn_add.grid(row=3, column=4, pady=10, sticky="e")

        cols = ("ID", "WO", "Tech", "Desc", "Hours", "Rate", "Total")
        display_cols = ("WO", "Tech", "Desc", "Hours", "Rate", "Total")
        self.tree = ttk.Treeview(self.main_frame, columns=cols, displaycolumns=display_cols, show="headings", height=10)
        
        headers = ["Work Order", "Technician", "Description", "Hours", "Hourly Rate", "Total Cost"]
        widths = [140, 100, 200, 60, 80, 80] 

        for col, h, w in zip(display_cols, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center" if w < 100 else "w")

        self.tree.pack(fill="both", expand=True)

        btn_del = tk.Button(self.main_frame, text="Delete Selected", bg="#c0392b", fg="white", 
                            command=self.delete_record)
        btn_del.pack(anchor="e", pady=10)

    # ================= DB =================

    def load_workorders(self):
        self.workorders.clear()
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            query = """
                SELECT WO.WorkOrderID, V.LicensePlate, C.FirstName, C.LastName 
                FROM RepairWorkOrder WO
                JOIN ServiceEntry SE ON WO.EntryID = SE.EntryID
                JOIN Vehicle V ON SE.VehicleID = V.VehicleID
                JOIN Customer C ON V.CustomerID = C.CustomerID
                ORDER BY WO.WorkOrderID DESC
            """
            cur.execute(query)
            for wid, plate, fn, ln in cur.fetchall():
                display = f"WO#{wid} - {plate} - {fn} {ln}"
                self.workorders[display] = wid
            self.combo_wo['values'] = list(self.workorders.keys())
        except Exception as e:
            print(f"WorkOrder Load Error: {e}")
        finally:
            conn.close()

    def load_personnel(self):
        self.personnel.clear()
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT PersonnelID, FirstName, LastName FROM Personnel")
            for pid, fn, ln in cur.fetchall():
                self.personnel[f"{fn} {ln}"] = pid
            self.combo_personnel['values'] = list(self.personnel.keys())
        finally:
            conn.close()

    def load_rates_smart(self):
        self.rates.clear()
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM LaborRate")
            rows = cur.fetchall()
            
            col_names = [column[0] for column in cur.description]

            if not rows: return    
            id_idx = 0
            name_idx = 1 
            rate_idx = 2

            if len(col_names) >= 3:
                for idx, col in enumerate(col_names):
                    c = col.lower()
                    if "rate" in c and ("hour" in c or "amount" in c or "cost" in c or "price" in c):
                        rate_idx = idx
                    elif "name" in c or "desc" in c or "type" in c or "class" in c:
                        name_idx = idx
            
            for row in rows:
                rid = row[id_idx]
                rname = str(row[name_idx])
                
                try:
                    ramount = float(row[rate_idx])
                except:
                    ramount = 0.0

                display = f"{rname} (${ramount:.2f})"
                self.rates[display] = {'id': rid, 'amount': ramount}
            
            self.combo_rate['values'] = list(self.rates.keys())

        except Exception as e:
            print("LaborRate Smart Load Error:", e)
        finally:
            conn.close()

    def load_service_operations(self):
        self.operations.clear()
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT OperationName, Description, StandardDuration, RateID FROM ServiceOperation")
            for row in cur.fetchall():
                op_name, desc, duration, rate_id = row
                final_desc = desc if desc else op_name
                
                self.operations[op_name] = {
                    'desc': final_desc,
                    'duration': float(duration) if duration else 0.0,
                    'rate_id': rate_id
                }
            self.combo_operation['values'] = list(self.operations.keys())
        except Exception as e:
            print("ServiceOperation Load Error:", e)
        finally:
            conn.close()

    def on_operation_select(self, event):
        selected_op = self.combo_operation.get()
        if selected_op in self.operations:
            data = self.operations[selected_op]
            
            self.entry_desc.delete(0, tk.END)
            self.entry_desc.insert(0, data['desc'])

            self.entry_hours.delete(0, tk.END)
            self.entry_hours.insert(0, str(data['duration']))

            if data['rate_id']:
                for disp, rdata in self.rates.items():
                    if rdata['id'] == data['rate_id']:
                        self.combo_rate.set(disp)
                        self.on_rate_select(None)
                        break

    def on_rate_select(self, event):
        selected = self.combo_rate.get()
        if selected in self.rates:
            amount = self.rates[selected]['amount']
            self.entry_hourly_rate.delete(0, tk.END)
            self.entry_hourly_rate.insert(0, f"{amount:.2f}")

    def load_labor_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            query = """
                SELECT 
                    L.LaborRecordID, 
                    ('WO#' + CAST(L.WorkOrderID AS VARCHAR) + ' - ' + V.LicensePlate),
                    (P.FirstName + ' ' + P.LastName),
                    L.Description, L.HoursSpent, L.HourlyRate,
                    (L.HoursSpent * L.HourlyRate)
                FROM LaborRecord L
                JOIN Personnel P ON L.PersonnelID = P.PersonnelID
                JOIN RepairWorkOrder WO ON L.WorkOrderID = WO.WorkOrderID
                JOIN ServiceEntry SE ON WO.EntryID = SE.EntryID
                JOIN Vehicle V ON SE.VehicleID = V.VehicleID
                ORDER BY L.LaborRecordID DESC
            """
            cur.execute(query)
            for row in cur.fetchall():
                vals = list(row)
                vals[4] = f"{float(vals[4]):.2f}" 
                vals[5] = f"{float(vals[5]):.2f}" 
                vals[6] = f"{float(vals[6]):.2f}" 
                self.tree.insert("", tk.END, values=vals)
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıtlar yüklenemedi:\n{e}")
        finally:
            conn.close()

    def add_record(self):
        wo_text = self.combo_wo.get()
        pers_text = self.combo_personnel.get()
        desc = self.entry_desc.get().strip()
        hours_str = self.entry_hours.get().strip()
        rate_str = self.entry_hourly_rate.get().strip()
        
        rate_class_text = self.combo_rate.get()
        rate_id = self.rates[rate_class_text]['id'] if rate_class_text in self.rates else None

        if not wo_text or not pers_text or not hours_str or not rate_str:
            messagebox.showwarning("Missing Info", "Work Order, Technician, Hours, and Rate are required.")
            return

        try:
            wo_id = self.workorders[wo_text]
            pers_id = self.personnel[pers_text]
            hours = float(hours_str)
            hourly_rate = float(rate_str)
            
            conn = self.db.connect()
            cur = conn.cursor()
            
            query = """
                INSERT INTO LaborRecord (WorkOrderID, PersonnelID, Description, HoursSpent, HourlyRate, RateID)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cur.execute(query, (wo_id, pers_id, desc, hours, hourly_rate, rate_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Labor Record added.")
            self.load_labor_records()
            
            self.entry_desc.delete(0, tk.END)
            self.entry_hours.delete(0, tk.END)
            self.combo_operation.set('')

        except ValueError:
            messagebox.showerror("Error", "Hours and Rate must be valid numbers.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_record(self):
        sel = self.tree.selection()
        if not sel: return
        rec_id = self.tree.item(sel[0])['values'][0]

        if messagebox.askyesno("Confirm", "Delete this record?"):
            conn = self.db.connect()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM LaborRecord WHERE LaborRecordID = ?", (rec_id,))
                conn.commit()
                self.load_labor_records()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()