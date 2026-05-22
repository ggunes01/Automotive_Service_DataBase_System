import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import re

class UsedPartManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

       
        for widget in self.parent.winfo_children():
            widget.destroy()


        self.workorders = {}   
        self.parts = {}        
        self.part_costs = {}   


        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Used Parts Management", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))


        self.build_form()
        

        self.load_workorders()
        self.load_parts()
        self.load_used_parts()

    def format_number(self, val):
        """Format decimal/numeric values to plain string with 2 decimals."""
        if val is None: return ""
        try: return f"{float(val):.2f}"
        except: return str(val)

    # ================= FORM =================
    def build_form(self):
        # White Card
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        # Work Order
        tk.Label(self.form_frame, text="Work Order:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.combo_workorder = ttk.Combobox(self.form_frame, width=40, state="readonly", font=("Segoe UI", 10))
        self.combo_workorder.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Part
        tk.Label(self.form_frame, text="Part:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        self.combo_part = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_part.grid(row=0, column=3, columnspan=3, sticky="w", padx=10, pady=5)
        self.combo_part.bind("<<ComboboxSelected>>", self.on_part_selected)

        # Quantity
        tk.Label(self.form_frame, text="Quantity:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_qty = tk.Entry(self.form_frame, width=10, font=("Segoe UI", 10),
                                  bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_qty.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=4)

        # Unit Price 
        tk.Label(self.form_frame, text="Unit Price (Auto):", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_unit_price = tk.Entry(self.form_frame, width=10, font=("Segoe UI", 10),
                                         bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_unit_price.grid(row=1, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # Discount
        tk.Label(self.form_frame, text="Discount (%):", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=4, sticky="w", padx=(20, 10), pady=5)
        self.entry_discount = tk.Entry(self.form_frame, width=10, font=("Segoe UI", 10),
                                       bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_discount.grid(row=1, column=5, sticky="w", padx=10, pady=5, ipady=4)

        add_btn = tk.Button(self.form_frame, text="+ Add Used Part", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_used_part)
        add_btn.grid(row=2, column=5, sticky="e", pady=15, padx=10, ipadx=10, ipady=5)


        # ================= TABLE =================
        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("UsedPartID", "WorkOrderID", "PartName", "Quantity", "UnitPrice", "DiscountRate", "Total", "Technician")
        display_cols = ("PartName", "Quantity", "UnitPrice", "DiscountRate", "Total", "Technician")
        
        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, show="headings", height=10,
                                 yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "PartName": 150,  "Quantity": 70, "UnitPrice": 80,
            "DiscountRate": 80, "Total": 90, "Technician": 120
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center" if col != "PartName" and col != "Technician" else "w")

        self.tree.pack(side="left", fill="both", expand=True)

        delete_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        delete_frame.pack(fill="x", pady=10)
        
        delete_btn = tk.Button(delete_frame, text="Delete Selected Part", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_used_part)
        delete_btn.pack(side="right", ipadx=10, ipady=5)


    # ================= DB =================
    
    def on_part_selected(self, event):
        selected_text = self.combo_part.get()
        if not selected_text: return

        part_id = self.parts.get(selected_text)
        if part_id:
            cost = self.part_costs.get(part_id, 0.0)
            
            # Entry'yi temizle ve fiyatı yaz
            self.entry_unit_price.delete(0, tk.END)
            self.entry_unit_price.insert(0, f"{cost:.2f}")

    def load_workorders(self):
        self.workorders.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT W.WorkOrderID, SE.EntryID, V.LicensePlate, C.FirstName, C.LastName
            FROM RepairWorkOrder W
            JOIN ServiceEntry SE ON W.EntryID = SE.EntryID
            JOIN Vehicle     V  ON SE.VehicleID = V.VehicleID
            JOIN Customer    C  ON V.CustomerID = C.CustomerID
        """)
        values = []
        for wid, entry_id, plate, fn, ln in cur.fetchall():
            display = f"{wid} - {plate} - {fn} {ln}"
            self.workorders[display] = wid
            values.append(display)
        conn.close()
        self.combo_workorder["values"] = values

    def load_parts(self):
        self.parts.clear()
        self.part_costs.clear()
        
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT PartID, PartName, ManufacturerCode, UnitCost FROM Inventory")
        values = []
        for pid, pname, manu, cost in cur.fetchall():
            display = f"{pname} ({manu})"
            self.parts[display] = pid
            
            self.part_costs[pid] = float(cost) if cost is not None else 0.0
            
            values.append(display)
        conn.close()
        self.combo_part["values"] = values

    def load_used_parts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                UP.UsedPartID, UP.WorkOrderID, I.PartName, UP.Quantity,
                UP.UnitPrice, UP.DiscountRate, (P.FirstName + ' ' + P.LastName) AS Technician
            FROM UsedPart UP
            JOIN Inventory       I ON UP.PartID = I.PartID
            JOIN RepairWorkOrder W ON UP.WorkOrderID = W.WorkOrderID
            JOIN Personnel       P ON W.AssignedTechnicianID = P.PersonnelID
            ORDER BY UP.UsedPartID
        """)
        for row in cur.fetchall():
            usedpart_id, workorder_id, part_name, qty, unit_price, discount, technician = row
            
            q = float(qty) if qty else 0.0
            p = float(unit_price) if unit_price else 0.0
            d = float(discount) if discount else 0.0
            
            total_val = q * p * (1 - (d / 100))

            formatted = (
                usedpart_id, workorder_id, part_name, self.format_number(qty),
                self.format_number(unit_price), self.format_number(discount), 
                self.format_number(total_val), # Calculated Total
                technician
            )
            self.tree.insert("", tk.END, values=formatted)
        conn.close()

    def add_used_part(self):
        workorder_disp = self.combo_workorder.get().strip()
        part_disp      = self.combo_part.get().strip()
        qty_str        = self.entry_qty.get().strip()
        unit_str       = self.entry_unit_price.get().strip()
        disc_str       = self.entry_discount.get().strip()

        if not workorder_disp or workorder_disp not in self.workorders:
            messagebox.showerror("Error", "Select a work order.")
            return
        if not part_disp or part_disp not in self.parts:
            messagebox.showerror("Error", "Select a part.")
            return
        if not qty_str:
            messagebox.showerror("Error", "Quantity is required.")
            return
        if not unit_str:
            messagebox.showerror("Error", "Unit price is required.")
            return

        try: qty_val = int(qty_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer.")
            return

        try: unit_val = float(unit_str)
        except ValueError:
            messagebox.showerror("Error", "Unit price must be a number.")
            return

        discount_val = 0.0
        if disc_str:
            try: discount_val = float(disc_str)
            except ValueError:
                messagebox.showerror("Error", "Discount must be a number.")
                return

        workorder_id = self.workorders[workorder_disp]
        part_id      = self.parts[part_disp]

        conn = None
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO UsedPart
                (WorkOrderID, PartID, Quantity, UnitPrice, DiscountRate)
                VALUES (?, ?, ?, ?, ?)
            """, (workorder_id, part_id, qty_val, unit_val, discount_val))
            conn.commit()
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("DB Error", str(e))
            return
        finally:
            if conn: conn.close()

        self.load_used_parts()
        self.combo_workorder.set("")
        self.combo_part.set("")
        self.entry_qty.delete(0, tk.END)
        self.entry_unit_price.delete(0, tk.END)
        self.entry_discount.delete(0, tk.END)
        messagebox.showinfo("Success", "Used part added.")

    def delete_used_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a used part to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected part?"):
            return

        raw_id = self.tree.item(selected[0])["values"][0]
        if isinstance(raw_id, int):
            usedpart_id = raw_id
        else:
            m = re.search(r"\d+", str(raw_id))
            if not m:
                messagebox.showerror("Error", f"Invalid UsedPartID: {raw_id}")
                return
            usedpart_id = int(m.group())

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM UsedPart WHERE UsedPartID = ?", (usedpart_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Used part {usedpart_id} deleted.")
            self.load_used_parts()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
