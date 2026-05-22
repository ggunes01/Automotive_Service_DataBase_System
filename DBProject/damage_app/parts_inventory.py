import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper

class PartsInventoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#ecf0f1")
        self.pack(fill="both", expand=True)

        self.db = DBHelper()
        
        self.part_map = {}       
        self.workorder_map = {}  

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_inventory = tk.Frame(self.notebook, bg="#ecf0f1")
        self.tab_usage = tk.Frame(self.notebook, bg="#ecf0f1")

        self.notebook.add(self.tab_inventory, text="   Inventory Management   ")
        self.notebook.add(self.tab_usage, text="   Assign Parts to Repair   ")

        self.setup_inventory_tab()
        self.setup_usage_tab()

        self.load_inventory()
        self.load_combos()
        self.load_usage_history()

 
    # INVENTORY

    def setup_inventory_tab(self):
        form_frame = tk.LabelFrame(self.tab_inventory, text="Add New Part", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=10, pady=10)

        # Part Name
        tk.Label(form_frame, text="Part Name:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_part_name = tk.Entry(form_frame, width=25)
        self.entry_part_name.grid(row=0, column=1, padx=5, pady=5)

        # Code
        tk.Label(form_frame, text="Manufacturer Code:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_part_no = tk.Entry(form_frame, width=20)
        self.entry_part_no.grid(row=0, column=3, padx=5, pady=5)

        # Qty & Cost
        tk.Label(form_frame, text="Current Qty:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_stock = tk.Entry(form_frame, width=10)
        self.entry_stock.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Unit Cost ($):", bg="#ecf0f1").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_price = tk.Entry(form_frame, width=10)
        self.entry_price.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        btn_add = tk.Button(form_frame, text="Add to Inventory", bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                            command=self.add_inventory_item)
        btn_add.grid(row=1, column=4, padx=20, pady=5)

        table_frame = tk.Frame(self.tab_inventory, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ID", "PartName", "Code", "Stock", "Cost")
        disp_cols = ("PartName", "Code", "Stock", "Cost")
        self.tree_inv = ttk.Treeview(table_frame, columns=cols,displaycolumns=disp_cols, show="headings", height=12)
        
        self.tree_inv.heading("PartName", text="Part Name")
        self.tree_inv.heading("Code", text="Manuf. Code")
        self.tree_inv.heading("Stock", text="Current Qty")
        self.tree_inv.heading("Cost", text="Unit Cost")

        self.tree_inv.column("PartName", width=150)
        self.tree_inv.column("Stock", width=80, anchor="center")
        
        self.tree_inv.pack(side="left", fill="both", expand=True)

        scrolly = tk.Scrollbar(table_frame, command=self.tree_inv.yview)
        scrolly.pack(side="right", fill="y")
        self.tree_inv.configure(yscrollcommand=scrolly.set)

        btn_del = tk.Button(self.tab_inventory, text="Delete Selected Part", bg="#c0392b", fg="white", 
                            command=self.delete_part)
        btn_del.pack(side="bottom", anchor="e", padx=10, pady=5)

    # PART USAGE

    def setup_usage_tab(self):
        # --- Form ---
        form_frame = tk.LabelFrame(self.tab_usage, text="Use Part for Repair", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=10, pady=10)

        # Work Order 
        tk.Label(form_frame, text="Select Work Order:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_workorder = ttk.Combobox(form_frame, state="readonly", width=35)
        self.combo_workorder.grid(row=0, column=1, padx=5, pady=5)

        # Part
        tk.Label(form_frame, text="Select Part:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_part = ttk.Combobox(form_frame, state="readonly", width=25)
        self.combo_part.grid(row=0, column=3, padx=5, pady=5)

        # Quantity
        tk.Label(form_frame, text="Quantity to Use:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_use_qty = tk.Entry(form_frame, width=10)
        self.entry_use_qty.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        btn_use = tk.Button(form_frame, text="Assign & Deduct Stock", bg="#e67e22", fg="white", font=("Arial", 9, "bold"),
                            command=self.assign_part)
        btn_use.grid(row=1, column=2, columnspan=2, pady=10)

        table_frame = tk.Frame(self.tab_usage, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tk.Label(table_frame, text="Recently Used Parts", bg="white", font=("Arial", 9, "italic")).pack(anchor="w")

        cols = ("UsedID", "WO", "Plate", "PartName", "QtyUsed")
        disp_cols = ("Plate", "PartName", "QtyUsed")
        self.tree_usage = ttk.Treeview(table_frame, columns=cols,displaycolumns= disp_cols, show="headings", height=10)
        
        self.tree_usage.heading("Plate", text="Vehicle Plate")
        self.tree_usage.heading("PartName", text="Part Name")
        self.tree_usage.heading("QtyUsed", text="Qty Used")
        
        self.tree_usage.pack(fill="both", expand=True)


    # DATABASE OPERATIONS
 

    def load_inventory(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        
        self.part_map.clear()
        
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = "SELECT PartID, PartName, ManufacturerCode, CurrentQuantity, UnitCost FROM Inventory"
                cur.execute(query)
                rows = cur.fetchall()
                
                for row in rows:
                    clean_row = [str(item) if item is not None else "" for item in row]
                    self.tree_inv.insert("", tk.END, values=clean_row)
                    
                    display = f"{row[1]} (Qty: {row[3]})"
                    self.part_map[display] = row[0] 

                self.combo_part['values'] = list(self.part_map.keys())
            except Exception as e:
                print(f"Inventory Load Error: {e}")
            finally:
                conn.close()

    def load_combos(self):
        """Loads Work Orders (Not Assessments) to avoid FK errors."""
        self.workorder_map.clear()
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT WO.WorkOrderID, V.LicensePlate, WO.StartDate 
                    FROM RepairWorkOrder WO
                    JOIN ServiceEntry SE ON WO.EntryID = SE.EntryID
                    JOIN Vehicle V ON SE.VehicleID = V.VehicleID
                    ORDER BY WO.StartDate DESC
                """
                cur.execute(query)
                for woid, plate, date in cur.fetchall():
                    display = f"WO#{woid} - {plate} ({date})"
                    self.workorder_map[display] = woid
                
                self.combo_workorder['values'] = list(self.workorder_map.keys())
            except Exception as e:
                print(f"Combo Load Error: {e}")
            finally:
                conn.close()

    def load_usage_history(self):
        for row in self.tree_usage.get_children():
            self.tree_usage.delete(row)
            
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT UP.UsedPartID, UP.WorkOrderID, V.LicensePlate, I.PartName, UP.Quantity
                    FROM UsedPart UP
                    JOIN Inventory I ON UP.PartID = I.PartID
                    JOIN RepairWorkOrder WO ON UP.WorkOrderID = WO.WorkOrderID
                    JOIN ServiceEntry SE ON WO.EntryID = SE.EntryID
                    JOIN Vehicle V ON SE.VehicleID = V.VehicleID
                    ORDER BY UP.UsedPartID DESC
                """
                cur.execute(query)
                for row in cur.fetchall():
                    self.tree_usage.insert("", tk.END, values=[str(x) for x in row])
            except Exception as e:
                print(f"Usage History Error: {e}")
            finally:
                conn.close()

    def add_inventory_item(self):
        name = self.entry_part_name.get()
        code = self.entry_part_no.get()
        qty = self.entry_stock.get()
        price = self.entry_price.get()

        if not name or not qty:
            messagebox.showwarning("Missing Info", "Part Name and Quantity are required.")
            return

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    INSERT INTO Inventory (PartName, ManufacturerCode, CurrentQuantity, UnitCost) 
                    VALUES (?, ?, ?, ?)
                """
                price_val = float(price) if price else 0.0
                qty_val = int(qty)
                
                cur.execute(query, (name, code, qty_val, price_val))
                conn.commit()
                messagebox.showinfo("Success", "Part added to inventory.")
                
                self.load_inventory()
                # Clear form
                self.entry_part_name.delete(0, tk.END)
                self.entry_part_no.delete(0, tk.END)
                self.entry_stock.delete(0, tk.END)
                self.entry_price.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add part: {e}")
            finally:
                conn.close()

    def assign_part(self):
        wo_text = self.combo_workorder.get()
        part_text = self.combo_part.get()
        qty_str = self.entry_use_qty.get()

        if not wo_text or not part_text or not qty_str:
            messagebox.showwarning("Missing Info", "Please select Work Order, Part and Quantity.")
            return

        try:
            qty_to_use = int(qty_str)
        except:
            messagebox.showerror("Error", "Quantity must be a number.")
            return

        wo_id = self.workorder_map[wo_text]
        part_id = self.part_map[part_text]

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT CurrentQuantity, UnitCost FROM Inventory WHERE PartID = ?", (part_id,))
                row = cur.fetchone()
                if not row:
                    messagebox.showerror("Error", "Part not found in DB.")
                    return
                
                current_stock = row[0]
                unit_cost = row[1] if row[1] else 0.0
                
                if current_stock < qty_to_use:
                    messagebox.showerror("Stock Low", f"Only {current_stock} items left in stock!")
                    return

                insert_query = """
                    INSERT INTO UsedPart (PartID, WorkOrderID, Quantity, UnitPrice) 
                    VALUES (?, ?, ?, ?)
                """
                cur.execute(insert_query, (part_id, wo_id, qty_to_use, unit_cost))

                update_query = "UPDATE Inventory SET CurrentQuantity = CurrentQuantity - ? WHERE PartID = ?"
                cur.execute(update_query, (qty_to_use, part_id))

                conn.commit()
                messagebox.showinfo("Success", "Part assigned and stock deducted.")
                
                self.load_inventory()
                self.load_usage_history()

            except Exception as e:
                messagebox.showerror("Database Error", f"Operation failed:\n{e}")
            finally:
                conn.close()

    def delete_part(self):
        selected = self.tree_inv.selection()
        if not selected: return
        pid = self.tree_inv.item(selected[0])['values'][0]

        if messagebox.askyesno("Delete", "Delete this part from inventory?"):
            conn = self.db.connect()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM Inventory WHERE PartID = ?", (pid,))
                conn.commit()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot delete part:\n{e}")
            finally:
                conn.close()