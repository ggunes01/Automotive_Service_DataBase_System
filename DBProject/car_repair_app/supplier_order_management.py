import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
import re
from datetime import datetime

class SupplierOrderManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        for widget in self.parent.winfo_children():
            widget.destroy()

        self.suppliers = {}   
        self.parts = {}       
        self.part_costs = {}  


        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)


        tk.Label(self.main_frame, text="Supplier Orders", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))


        self.build_form()
        
        self.load_suppliers()
        self.load_parts()
        self.load_orders()

    def format_number(self, val):
        if val is None: return ""
        try: return f"{float(val):.2f}"
        except: return str(val)

    def format_date(self, val):
        if val is None: return ""
        try: 
            if isinstance(val, str): return val
            return val.strftime("%Y-%m-%d")
        except: return str(val)

    # ================= FORM  =================
    def build_form(self):
        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        # Supplier
        tk.Label(self.form_frame, text="Supplier:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.combo_supplier = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_supplier.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Part
        tk.Label(self.form_frame, text="Part:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=0, column=2, sticky="w", padx=(40, 10), pady=5)
        self.combo_part = ttk.Combobox(self.form_frame, width=35, state="readonly", font=("Segoe UI", 10))
        self.combo_part.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        self.combo_part.bind("<<ComboboxSelected>>", self.on_part_selected)

        # Order Date
        tk.Label(self.form_frame, text="Order Date (YYYY-MM-DD):", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_orderdate = tk.Entry(self.form_frame, width=20, font=("Segoe UI", 10),
                                        bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_orderdate.grid(row=1, column=1, sticky="w", padx=10, pady=5, ipady=4)
        self.entry_orderdate.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Status
        tk.Label(self.form_frame, text="Status:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=1, column=2, sticky="w", padx=(40, 10), pady=5)
        self.combo_status = ttk.Combobox(self.form_frame, width=20, state="readonly", 
                                         values=["Pending", "Ordered", "Received", "Cancelled"], font=("Segoe UI", 10))
        self.combo_status.grid(row=1, column=3, sticky="w", padx=10, pady=5)
        self.combo_status.set("Pending")

        # Quantity
        tk.Label(self.form_frame, text="Quantity:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_qty = tk.Entry(self.form_frame, width=15, font=("Segoe UI", 10),
                                  bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_qty.grid(row=2, column=1, sticky="w", padx=10, pady=5, ipady=4)

        # Unit Cost
        tk.Label(self.form_frame, text="Unit Cost:", font=("Segoe UI", 10, "bold"), 
                 bg="white", fg="#555").grid(row=2, column=2, sticky="w", padx=(40, 10), pady=5)
        self.entry_unitprice = tk.Entry(self.form_frame, width=15, font=("Segoe UI", 10),
                                        bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
        self.entry_unitprice.grid(row=2, column=3, sticky="w", padx=10, pady=5, ipady=4)

        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.grid(row=3, column=3, sticky="e", pady=15, padx=10)

        update_btn = tk.Button(btn_frame, text="Update Status/Info", bg="#f39c12", fg="white", 
                               font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                               command=self.update_order)
        update_btn.pack(side="left", padx=5)

        add_btn = tk.Button(btn_frame, text="+ Add Supplier Order", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_order)
        add_btn.pack(side="left", padx=5)


        # ================= TABLE =================
        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("OrderID", "SupplierName", "PartName", "OrderDate", 
                   "Quantity", "UnitCost", "TotalAmount", "Status")
        display_cols = ("SupplierName", "PartName", "OrderDate", 
                   "Quantity", "UnitCost", "TotalAmount", "Status")
        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, show="headings", height=10,
                                 yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "SupplierName": 120, "PartName": 120, "OrderDate": 90,
            "Quantity": 70, "UnitCost": 80, "TotalAmount": 90, "Status": 90
        }

        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        delete_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        delete_frame.pack(fill="x", pady=10)
        
        delete_btn = tk.Button(delete_frame, text="Delete Selected Order", bg="#c0392b", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                               command=self.delete_order)
        delete_btn.pack(side="right", ipadx=10, ipady=5)


    # ================= DB =================
    
    def on_part_selected(self, event):
        """Parça seçildiğinde Unit Cost'u otomatik doldurur."""
        selected_text = self.combo_part.get()
        if not selected_text: return

        part_id = self.parts.get(selected_text)
        if part_id:
            cost = self.part_costs.get(part_id, 0.0)
            
            self.entry_unitprice.delete(0, tk.END)
            self.entry_unitprice.insert(0, f"{cost:.2f}")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        vals = self.tree.item(selected[0])['values']
        if not vals: return

        self.combo_supplier.set(vals[1])
        self.combo_part.set(vals[2])
        
        self.entry_orderdate.delete(0, tk.END)
        self.entry_orderdate.insert(0, str(vals[3]))
        
        self.entry_qty.delete(0, tk.END)
        self.entry_qty.insert(0, str(vals[4]))
        
        self.entry_unitprice.delete(0, tk.END)
        self.entry_unitprice.insert(0, str(vals[5]))
        
        self.combo_status.set(vals[7])

    def load_suppliers(self):
        self.suppliers.clear()
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT SupplierID, Name FROM Supplier")
            values = []
            for sid, name in cur.fetchall():
                self.suppliers[name] = sid
                values.append(name)
            self.combo_supplier["values"] = values
        finally:
            conn.close()

    def load_parts(self):
        self.parts.clear()
        self.part_costs.clear() 
        
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT PartID, PartName, ManufacturerCode, UnitCost FROM Inventory")
            values = []
            for pid, pname, manu, cost in cur.fetchall():
                display = f"{pname} ({manu})"
                self.parts[display] = pid
                
                self.part_costs[pid] = float(cost) if cost is not None else 0.0
                
                values.append(display)
            self.combo_part["values"] = values
        finally:
            conn.close()

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT SO.OrderID, S.Name AS SupplierName, 
                       (I.PartName + ' (' + ISNULL(I.ManufacturerCode, '') + ')') AS PartDisplay, 
                       SO.OrderDate, SO.DeliveryDate, SO.Quantity, SO.UnitCost, SO.TotalAmount, SO.Status
                FROM SupplierOrder SO
                JOIN Supplier  S ON SO.SupplierID = S.SupplierID
                JOIN Inventory I ON SO.PartID     = I.PartID
                ORDER BY SO.OrderID DESC
            """)
            for row in cur.fetchall():
                order_id, supplier_name, part_name, order_date, delivery_date, qty, unit_cost, total_amount, status = row
                formatted = (
                    order_id, supplier_name, part_name, self.format_date(order_date),
                    qty if qty is not None else "",
                    self.format_number(unit_cost),
                    self.format_number(total_amount),
                    status or ""
                )
                self.tree.insert("", tk.END, values=formatted)
        finally:
            conn.close()

    def add_order(self):
        supplier_name = self.combo_supplier.get().strip()
        part_disp     = self.combo_part.get().strip()
        order_date    = self.entry_orderdate.get().strip()
        qty_str       = self.entry_qty.get().strip()
        price_str     = self.entry_unitprice.get().strip()
        status        = self.combo_status.get().strip()

        if supplier_name not in self.suppliers:
            messagebox.showerror("Error", "Select a supplier.")
            return
        if part_disp not in self.parts:
            messagebox.showerror("Error", "Select a part.")
            return
        if not order_date or not qty_str or not price_str:
            messagebox.showerror("Error", "Date, Quantity and Price are required.")
            return

        try: 
            qty_val = int(qty_str)
            price_val = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be int, Price must be number.")
            return

        supplier_id = self.suppliers[supplier_name]
        part_id     = self.parts[part_disp]
        total_amount = qty_val * price_val

        conn = None
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO SupplierOrder
                (SupplierID, PartID, OrderDate, DeliveryDate, Quantity, UnitCost, Status, TotalAmount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (supplier_id, part_id, order_date, None, qty_val, price_val, status, total_amount))
            
            if status == "Received":
                cur.execute("UPDATE Inventory SET CurrentQuantity = CurrentQuantity + ? WHERE PartID = ?", (qty_val, part_id))

            conn.commit()
            messagebox.showinfo("Success", "Supplier order added.")
            self.load_orders()
            self.clear_form()
        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("DB Error", str(e))
        finally:
            if conn: conn.close()

    def update_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen güncellemek için bir sipariş seçin.")
            return

        raw_id = self.tree.item(selected[0])['values'][0] 
        
        supplier_name = self.combo_supplier.get().strip()
        part_disp     = self.combo_part.get().strip()
        order_date    = self.entry_orderdate.get().strip()
        qty_str       = self.entry_qty.get().strip()
        price_str     = self.entry_unitprice.get().strip()
        new_status    = self.combo_status.get().strip()

        if not supplier_name or not part_disp or not qty_str:
            messagebox.showerror("Eksik", "Lütfen alanları doldurun.")
            return

        try:
            qty_val = int(qty_str)
            price_val = float(price_str)
            total_amount = qty_val * price_val
            supplier_id = self.suppliers[supplier_name]
            part_id = self.parts[part_disp]
        except:
            messagebox.showerror("Hata", "Sayısal değerler geçersiz.")
            return

        conn = self.db.connect()
        try:
            cur = conn.cursor()
            
            cur.execute("SELECT Status, PartID, Quantity FROM SupplierOrder WHERE OrderID = ?", (raw_id,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Hata", "Sipariş bulunamadı.")
                return
            
            old_status = row[0]
            
            cur.execute("""
                UPDATE SupplierOrder
                SET SupplierID=?, PartID=?, OrderDate=?, Quantity=?, UnitCost=?, Status=?, TotalAmount=?
                WHERE OrderID=?
            """, (supplier_id, part_id, order_date, qty_val, price_val, new_status, total_amount, raw_id))

            if old_status != "Received" and new_status == "Received":
                cur.execute("UPDATE Inventory SET CurrentQuantity = CurrentQuantity + ? WHERE PartID = ?", (qty_val, part_id))
                messagebox.showinfo("Bilgi", "Sipariş 'Received' oldu, stok artırıldı.")
                
            conn.commit()
            messagebox.showinfo("Başarılı", "Sipariş güncellendi.")
            self.load_orders()
            self.clear_form()

        except Exception as e:
            if conn: conn.rollback()
            messagebox.showerror("Hata", str(e))
        finally:
            conn.close()

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an order to delete.")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected order?"):
            return

        raw_id = self.tree.item(selected[0])["values"][0]
        
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM SupplierOrder WHERE OrderID = ?", (raw_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Supplier order {raw_id} deleted.")
            self.load_orders()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def clear_form(self):
        self.combo_supplier.set("")
        self.combo_part.set("")
        self.entry_orderdate.delete(0, tk.END)
        self.entry_orderdate.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_qty.delete(0, tk.END)
        self.entry_unitprice.delete(0, tk.END)
        self.combo_status.set("Pending")