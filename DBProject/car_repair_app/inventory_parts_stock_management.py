import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import re

class InventoryManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.suppliers = {}

        # Main Frame
        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Inventory & Parts Stock", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.build_form()
        
        # Load Data
        self.load_suppliers()
        self.load_inventory()

    def format_number(self, val):
        if val is None: return ""
        try: return f"{float(val):.2f}"
        except: return str(val)

    # ================= FORM =================
    def build_form(self):
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(self.form_frame, text="Part Name:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_name = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_name.grid(row=0, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Manufacturer Code:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_manu = tk.Entry(self.form_frame, width=30, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_manu.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=4)

        tk.Label(self.form_frame, text="Supplier:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.combo_supplier = ttk.Combobox(self.form_frame, width=28, state="readonly", font=("Segoe UI", 10))
        self.combo_supplier.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # --- Price and Stock Infos ---
        # Current Quantity
        tk.Label(self.form_frame, text="Current Quantity:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_quantity = tk.Entry(self.form_frame, width=15, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_quantity.grid(row=0, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # Unit Price
        tk.Label(self.form_frame, text="Unit Price:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_price = tk.Entry(self.form_frame, width=15, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_price.grid(row=1, column=3, sticky="w", padx=10, pady=5, ipady=4)

        # Min Stock
        tk.Label(self.form_frame, text="Min Stock Level:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").grid(row=2, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_min_stock = tk.Entry(self.form_frame, width=15, font=("Segoe UI", 10), bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_min_stock.grid(row=2, column=3, sticky="w", padx=10, pady=5, ipady=4)

        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=(20, 10), sticky="ew")

        tk.Button(btn_frame, text="Add Part", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", command=self.add_part).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Selected", bg="#f39c12", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", command=self.update_part).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear Fields", bg="#95a5a6", fg="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat", command=self.clear_fields).pack(side="left", padx=5)

        # --- STOK Changing ---
        adjust_frame = tk.Frame(self.form_frame, bg="#f0f2f5", padx=10, pady=10, relief="solid", bd=0)
        adjust_frame.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20) 

        tk.Label(adjust_frame, text="Quick Adjust (+/-):", bg="#f0f2f5", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.entry_adjust = tk.Entry(adjust_frame, width=8, font=("Segoe UI", 9))
        self.entry_adjust.pack(side="left", padx=5)
        tk.Button(adjust_frame, text="Apply", bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", command=self.adjust_quantity).pack(side="left")


        # ================= TABLE =================
        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("PartID", "PartName", "ManufacturerCode", "CurrentQuantity", "UnitCost", "MinStockLevel", "SupplierName")
        display_cols = ("PartName", "ManufacturerCode", "CurrentQuantity", "UnitCost", "MinStockLevel", "SupplierName")
        self.tree = ttk.Treeview(table_container, columns=columns,displaycolumns=display_cols, show="headings", height=10, yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "PartName": 150, "ManufacturerCode": 120, "CurrentQuantity": 100,
             "UnitCost": 80, "MinStockLevel": 100, "SupplierName": 150
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # --- Delete  ---
        delete_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        delete_frame.pack(fill="x", pady=10)
        
        delete_btn = tk.Button(delete_frame, text="Delete Selected Part", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_part)
        delete_btn.pack(side="right", ipadx=10, ipady=5)


    # ================= Database =================
    
    def load_suppliers(self):
        self.suppliers = {}
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT SupplierID, Name FROM Supplier")
        values = []
        for sid, sname in cur.fetchall():
            self.suppliers[sname] = sid
            values.append(sname)
        conn.close()
        self.combo_supplier["values"] = values

    def load_inventory(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT I.PartID, I.PartName, I.ManufacturerCode,
                   I.CurrentQuantity, I.UnitCost, I.MinStockLevel,
                   S.Name AS SupplierName
            FROM Inventory I
            LEFT JOIN Supplier S ON I.SupplierID = S.SupplierID
            ORDER BY I.PartID
        """)
        for row in cur.fetchall():
            part_id, name, manu, qty, unit_cost, minstock, supplier = row
            formatted = (
                part_id, name, manu,
                int(qty) if qty is not None else "",
                self.format_number(unit_cost),
                int(minstock) if minstock is not None else "",
                supplier if supplier is not None else "",
            )
            self.tree.insert("", tk.END, values=formatted)
        conn.close()

    def clear_fields(self):
        self.entry_name.delete(0, tk.END)
        self.entry_manu.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_min_stock.delete(0, tk.END)
        self.combo_supplier.set("")
        self.entry_adjust.delete(0, tk.END)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0])["values"]
        
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])

        self.entry_manu.delete(0, tk.END)
        self.entry_manu.insert(0, values[2])

        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, values[3])

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, values[4])

        self.entry_min_stock.delete(0, tk.END)
        self.entry_min_stock.insert(0, values[5])

        self.combo_supplier.set(values[6])

    def add_part(self):
        name = self.entry_name.get().strip()
        manu = self.entry_manu.get().strip()
        qty = self.entry_quantity.get().strip()
        price = self.entry_price.get().strip()
        min_stock = self.entry_min_stock.get().strip()
        supplier = self.combo_supplier.get().strip()

        if supplier not in self.suppliers:
            messagebox.showerror("Error", "Invalid supplier.")
            return

        supplier_id = self.suppliers[supplier]

        try: qty_val = int(qty)
        except:
            messagebox.showerror("Error", "Current quantity must be integer.")
            return

        try: price_val = float(price)
        except:
            messagebox.showerror("Error", "Unit cost must be number.")
            return

        min_stock_val = None
        if min_stock:
            try: min_stock_val = int(min_stock)
            except:
                messagebox.showerror("Error", "MinStockLevel must be integer.")
                return

        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO Inventory
                (PartName, ManufacturerCode, CurrentQuantity, UnitCost, MinStockLevel, SupplierID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, manu, qty_val, price_val, min_stock_val, supplier_id))
            conn.commit()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

        self.load_inventory()
        self.clear_fields()

    def update_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a part to update.")
            return

        raw_id = self.tree.item(selected[0])["values"][0]
        if isinstance(raw_id, int): part_id = raw_id
        else:
            m = re.search(r"\d+", str(raw_id))
            if not m: return
            part_id = int(m.group())

        name = self.entry_name.get().strip()
        manu = self.entry_manu.get().strip()
        qty = self.entry_quantity.get().strip()
        price = self.entry_price.get().strip()
        min_stock = self.entry_min_stock.get().strip()
        supplier = self.combo_supplier.get().strip()

        if supplier not in self.suppliers:
            messagebox.showerror("Error", "Invalid supplier.")
            return
        supplier_id = self.suppliers[supplier]

        try:
            qty_val = int(qty)
            price_val = float(price)
        except:
            messagebox.showerror("Error", "Check numeric fields.")
            return

        min_stock_val = None
        if min_stock: min_stock_val = int(min_stock)

        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE Inventory
                SET PartName=?, ManufacturerCode=?, CurrentQuantity=?,
                    UnitCost=?, MinStockLevel=?, SupplierID=?
                WHERE PartID=?
            """, (name, manu, qty_val, price_val, min_stock_val, supplier_id, part_id))
            conn.commit()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()
        self.load_inventory()

    def adjust_quantity(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a part.")
            return

        vals = self.tree.item(selected[0])["values"]
        raw_part_id, qty = vals[0], vals[3]
        adjust_val = self.entry_adjust.get()

        try: adjust_val = int(adjust_val)
        except:
            messagebox.showerror("Error", "Adjustment must be integer.")
            return

        try: current_qty = int(qty)
        except:
            messagebox.showerror("Error", "Row quantity is invalid.")
            return

        if isinstance(raw_part_id, int): part_id = raw_part_id
        else:
            m = re.search(r"\d+", str(raw_part_id))
            if not m: return
            part_id = int(m.group())

        new_qty = current_qty + adjust_val
        if new_qty < 0:
            messagebox.showerror("Error", "Quantity cannot be negative.")
            return

        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE Inventory SET CurrentQuantity=? WHERE PartID=?", (new_qty, part_id))
            conn.commit()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

        self.load_inventory()
        self.entry_adjust.delete(0, tk.END)

    def delete_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a part to delete.")
            return

        raw_id = self.tree.item(selected[0])["values"][0]
        if isinstance(raw_id, int): part_id = raw_id
        else:
            m = re.search(r"\d+", str(raw_id))
            if not m: return
            part_id = int(m.group())
        
        if not messagebox.askyesno("Confirm", f"Delete Part ID {part_id}?"):
            return

        conn = self.db.connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM Inventory WHERE PartID=?", (part_id,))
            conn.commit()
            messagebox.showinfo("Deleted", f"Part {part_id} deleted.")
        except Exception as e:
            if "REFERENCE constraint" in str(e):
                messagebox.showerror("Error", "Cannot delete this part because it is used in 'Used Parts'.")
            else:
                messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()
        self.load_inventory()
