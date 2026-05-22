import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
from datetime import datetime
import re

class InvoiceManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent

        for widget in self.parent.winfo_children():
            widget.destroy()


        self.entries = {}   
        self.customers = {} 
        self.invoices_map = {} # 

        self.invoice_details_cache = {} 

        # Main Frame
        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab_invoices = tk.Frame(self.notebook, bg="#ecf0f1")
        self.tab_payments = tk.Frame(self.notebook, bg="#ecf0f1")

        self.notebook.add(self.tab_invoices, text="   Invoices (Faturalar)   ")
        self.notebook.add(self.tab_payments, text="   Payments (Ödemeler)   ")

        self.setup_invoice_tab()
        self.setup_payment_tab()
        
        self.load_entries()
        self.load_customers()
        self.load_invoices()
        self.load_payments()

    def format_date(self, val):
        if val is None: return ""
        try: return val.strftime("%Y-%m-%d")
        except: return str(val)

    def format_number(self, val):
        if val is None: return ""
        try: return f"{float(val):.2f}"
        except: return str(val)

    # ================= TAB 1: INVOICES =================
    def setup_invoice_tab(self):
        form_frame = tk.LabelFrame(self.tab_invoices, text="New Invoice", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Entry & Customer
        tk.Label(form_frame, text="Service Entry:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_entry = ttk.Combobox(form_frame, width=35, state="readonly")
        self.combo_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_entry.bind("<<ComboboxSelected>>", self.calculate_service_cost)

        tk.Label(form_frame, text="Customer:", bg="white").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.combo_customer = ttk.Combobox(form_frame, width=30, state="readonly")
        self.combo_customer.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Date & Status
        tk.Label(form_frame, text="Invoice Date:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_date = tk.Entry(form_frame, width=20, bg="#f9f9f9")
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form_frame, text="Status:", bg="white").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.combo_status = ttk.Combobox(form_frame, width=20, state="readonly", values=["Pending", "Paid", "Cancelled"])
        self.combo_status.set("Pending")
        self.combo_status.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Total & VAT
        tk.Label(form_frame, text="Total Amount (Auto):", bg="white", fg="#e67e22").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_total = tk.Entry(form_frame, width=15, bg="#f9f9f9") # Otomatik dolacak
        self.entry_total.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form_frame, text="VAT Rate (%):", bg="white").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_vat = tk.Entry(form_frame, width=10, bg="#f9f9f9")
        self.entry_vat.insert(0, "20") # Varsayılan %20 KDV
        self.entry_vat.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Calculate
        btn_calc = tk.Button(form_frame, text="Calculate Cost", bg="#3498db", fg="white", 
                             font=("Segoe UI", 8), command=lambda: self.calculate_service_cost(None))
        btn_calc.grid(row=2, column=4, padx=5)

        btn_add = tk.Button(form_frame, text="+ Create Invoice", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 9, "bold"), command=self.add_invoice)
        btn_add.grid(row=3, column=3, sticky="e", pady=10)

        # Table
        table_frame = tk.Frame(self.tab_invoices, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("InvoiceID", "Date", "Total", "VAT", "Status", "Customer")
        disp_cols = ("Date", "Total", "VAT", "Status", "Customer")
        self.tree_inv = ttk.Treeview(table_frame, columns=cols,displaycolumns=disp_cols, show="headings", height=10)
        
        headers = {"Date": 90, "Total": 90, "VAT": 60, "Status": 90, "Customer": 150}
        for c, w in headers.items():
            self.tree_inv.heading(c, text=c)
            self.tree_inv.column(c, width=w, anchor="center")
        
        self.tree_inv.pack(side="left", fill="both", expand=True)
        
        btn_del = tk.Button(self.tab_invoices, text="Delete Invoice", bg="#c0392b", fg="white", command=self.delete_invoice)
        btn_del.pack(anchor="e", padx=10, pady=5)

    # ================= TAB 2: PAYMENTS =================
    def setup_payment_tab(self):
        pay_form = tk.LabelFrame(self.tab_payments, text="Add Payment", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        pay_form.pack(fill="x", padx=10, pady=10)

        # Invoice Select
        tk.Label(pay_form, text="Select Invoice:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_pay_invoice = ttk.Combobox(pay_form, width=35, state="readonly")
        self.combo_pay_invoice.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_pay_invoice.bind("<<ComboboxSelected>>", self.calculate_payment_amount)

        # Amount
        tk.Label(pay_form, text="Amount (Total+VAT):", bg="white", fg="#e67e22").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_pay_amount = tk.Entry(pay_form, width=15, bg="#f9f9f9") # Otomatik dolacak
        self.entry_pay_amount.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Date & Method
        tk.Label(pay_form, text="Date:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_pay_date = tk.Entry(pay_form, width=20, bg="#f9f9f9")
        self.entry_pay_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_pay_date.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(pay_form, text="Method:", bg="white").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.combo_pay_method = ttk.Combobox(pay_form, width=15, state="readonly", values=["Cash", "Credit Card", "Bank Transfer"])
        self.combo_pay_method.current(0)
        self.combo_pay_method.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        btn_pay = tk.Button(pay_form, text="+ Add Payment", bg="#2980b9", fg="white", 
                            font=("Segoe UI", 9, "bold"), command=self.add_payment)
        btn_pay.grid(row=1, column=4, padx=20)

        # Table
        pay_table_frame = tk.Frame(self.tab_payments, bg="white")
        pay_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        p_cols = ("PaymentID", "InvoiceID", "Date", "Amount", "Method")
        p_disp_cols = ("Date", "Amount", "Method")
        self.tree_pay = ttk.Treeview(pay_table_frame, columns=p_cols, displaycolumns= p_disp_cols, show="headings", height=10)
        
        for c in p_disp_cols:
            self.tree_pay.heading(c, text=c)
            self.tree_pay.column(c, width=100, anchor="center")
        
        self.tree_pay.pack(side="left", fill="both", expand=True)

        btn_del_pay = tk.Button(self.tab_payments, text="Delete Payment", bg="#c0392b", fg="white", command=self.delete_payment)
        btn_del_pay.pack(anchor="e", padx=10, pady=5)

    # ================= Auto Calc =================
    
    def calculate_service_cost(self, event=None):

        selection = self.combo_entry.get()
        if not selection:

            if event is None: messagebox.showwarning("Warning", "Please Select Service Entry")
            return

        entry_id = self.entries.get(selection)
        if not entry_id: return

        conn = self.db.connect()
        try:
            cur = conn.cursor()
        
            # I.UnitCost 
            query_parts = """
                SELECT SUM(Quantity * UnitPrice * (1 - (COALESCE(DiscountRate, 0) / 100.0)))
                FROM UsedPart
                WHERE WorkOrderID IN (SELECT WorkOrderID FROM RepairWorkOrder WHERE EntryID = ?)
            """
            cur.execute(query_parts, (entry_id,))
            parts_result = cur.fetchone()[0]
            parts_cost = float(parts_result) if parts_result is not None else 0.0

            # --- 2. İşçilik ---
            query_labor = """
                SELECT SUM(HoursSpent * HourlyRate)
                FROM LaborRecord
                WHERE WorkOrderID IN (SELECT WorkOrderID FROM RepairWorkOrder WHERE EntryID = ?)
            """
            cur.execute(query_labor, (entry_id,))
            labor_result = cur.fetchone()[0]
            labor_cost = float(labor_result) if labor_result is not None else 0.0

            total_cost = parts_cost + labor_cost

            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, f"{total_cost:.2f}")

        except Exception as e:
            messagebox.showerror("Hesaplama Hatası", str(e))
        finally:
            conn.close()

    def calculate_payment_amount(self, event):
        selection = self.combo_pay_invoice.get()
        if not selection: return

        inv_id = self.invoices_map.get(selection)
        if not inv_id: return

        details = self.invoice_details_cache.get(inv_id)
        if details:
            total = details['total']
            vat = details['vat']
            final_amount = total + (total * vat / 100.0)
            
            self.entry_pay_amount.delete(0, tk.END)
            self.entry_pay_amount.insert(0, f"{final_amount:.2f}")

    # ================= Load Data =================
    
    def load_entries(self):
        self.entries.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT SE.EntryID, V.LicensePlate, C.FirstName, C.LastName
            FROM ServiceEntry SE
            JOIN Vehicle V ON SE.VehicleID = V.VehicleID
            JOIN Customer C ON V.CustomerID = C.CustomerID
        """)
        values = []
        for eid, plate, fn, ln in cur.fetchall():
            disp = f"{eid} - {fn} {ln} - {plate}"
            self.entries[disp] = eid
            values.append(disp)
        conn.close()
        self.combo_entry["values"] = values

    def load_customers(self):
        self.customers.clear()
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT CustomerID, FirstName, LastName FROM Customer")
        values = []
        for cid, fn, ln in cur.fetchall():
            name = f"{fn} {ln}"
            self.customers[name] = cid
            values.append(name)
        conn.close()
        self.combo_customer["values"] = values

    def load_invoices(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        self.invoices_map.clear()
        self.invoice_details_cache.clear()

        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT I.InvoiceID, I.InvoiceDate, I.TotalAmount, I.VATRate,
                   I.PaymentStatus, I.EntryID, C.FirstName, C.LastName
            FROM Invoice I
            JOIN Customer C ON I.CustomerID = C.CustomerID
            ORDER BY I.InvoiceID DESC
        """)
        for row in cur.fetchall():
            inv_id, date, total, vat, status, entry, fn, ln = row
            cust_name = f"{fn} {ln}"
            
            self.tree_inv.insert("", tk.END, values=(
                inv_id, self.format_date(date), self.format_number(total), 
                self.format_number(vat), status, cust_name
            ))

            disp_inv = f"Invoice #{inv_id} - {cust_name}"
            self.invoices_map[disp_inv] = inv_id
            
            t_val = float(total) if total else 0.0
            v_val = float(vat) if vat else 0.0
            self.invoice_details_cache[inv_id] = {'total': t_val, 'vat': v_val}
        
        conn.close()
        self.combo_pay_invoice['values'] = list(self.invoices_map.keys())

    def load_payments(self):
        for row in self.tree_pay.get_children():
            self.tree_pay.delete(row)
        
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT PaymentID, InvoiceID, PaymentDate, PaymentAmount, PaymentMethod
                FROM Payment
                ORDER BY PaymentDate DESC
            """)
            for row in cur.fetchall():
                clean_row = [str(x) if x is not None else "" for x in row]
                if row[2]: clean_row[2] = self.format_date(row[2])
                self.tree_pay.insert("", tk.END, values=clean_row)
        except Exception as e:
            print("Payment Load Error:", e)
        finally:
            conn.close()

    def add_invoice(self):
        disp_entry = self.combo_entry.get()
        disp_cust = self.combo_customer.get()
        date = self.entry_date.get().strip()
        total = self.entry_total.get().strip()
        vat = self.entry_vat.get().strip()
        status = self.combo_status.get().strip()

        if not disp_entry or not disp_cust or not total:
            messagebox.showwarning("Eksik", "Lütfen tüm alanları doldurun.")
            return

        entry_id = self.entries[disp_entry]
        customer_id = self.customers[disp_cust]

        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Invoice
                (InvoiceDate, TotalAmount, VATRate, PaymentStatus, EntryID, CustomerID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, total, vat, status, entry_id, customer_id))
            conn.commit()
            messagebox.showinfo("Başarılı", "Fatura oluşturuldu.")
            self.load_invoices()
            
            self.entry_total.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            conn.close()

    def add_payment(self):
        inv_text = self.combo_pay_invoice.get()
        amount = self.entry_pay_amount.get().strip()
        date = self.entry_pay_date.get().strip()
        method = self.combo_pay_method.get()

        if not inv_text or not amount:
            messagebox.showwarning("Eksik", "Fatura ve Tutar seçilmelidir.")
            return

        inv_id = self.invoices_map[inv_text]

        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Payment (InvoiceID, PaymentDate, PaymentAmount, PaymentMethod)
                VALUES (?, ?, ?, ?)
            """, (inv_id, date, amount, method))
            
            cur.execute("UPDATE Invoice SET PaymentStatus = 'Paid' WHERE InvoiceID = ?", (inv_id,))
            
            conn.commit()

            messagebox.showinfo("Payment Succesful", "Payment Added, Invoice status changed to 'Paid' ")
            self.load_payments()
            self.load_invoices() 
            self.entry_pay_amount.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            conn.close()

    def delete_invoice(self):
        self._delete_helper(self.tree_inv, "Invoice", "InvoiceID", self.load_invoices)

    def delete_payment(self):
        self._delete_helper(self.tree_pay, "Payment", "PaymentID", self.load_payments)

    def _delete_helper(self, tree, table, col, callback):
        sel = tree.selection()
        if not sel: return
        id_val = tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Delete", "Do you want to delete this record"):
            conn = self.db.connect()
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (id_val,))
                conn.commit()
                callback()
                if table == "Invoice": self.load_payments() 
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't Delete:\n{e}")
            finally:
                conn.close()