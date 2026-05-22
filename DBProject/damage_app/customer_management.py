import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper

class CustomerManagement:
    def __init__(self, parent):
        self.db = DBHelper()
        self.parent = parent
        
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(self.main_frame, text="Customer Management", 
                 font=("Segoe UI", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(anchor="w", pady=(0, 20))

        self.form_frame = tk.Frame(self.main_frame, bg="white", padx=20, pady=20)
        self.form_frame.pack(fill="x", pady=(0, 20))

        self.entries = {}
        labels_info = [
            ("First Name:", 0, 0), ("Last Name:", 0, 1), 
            ("Phone:", 1, 0),      ("Email:", 1, 1), 
            ("Address:", 2, 0),    ("National ID:", 2, 1)
        ]

        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.columnconfigure(3, weight=1)

        for text, row, col in labels_info:
            tk.Label(self.form_frame, text=text, font=("Segoe UI", 10, "bold"), 
                     bg="white", fg="#555").grid(row=row, column=col*2, sticky="w", padx=(0, 10), pady=10)
            
            entry = tk.Entry(self.form_frame, font=("Segoe UI", 10), 
                             bg="#f9f9f9", relief="flat", highlightthickness=1, highlightbackground="#ddd")
            entry.grid(row=row, column=col*2+1, sticky="ew", padx=(0, 20), pady=10, ipady=5)
            
            self.entries[text] = entry

        add_btn = tk.Button(self.form_frame, text="+ Add Customer", bg="#27ae60", fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=self.add_customer)
        add_btn.grid(row=3, column=3, sticky="e", pady=(10, 0), ipady=5, ipadx=15)

        table_container = tk.Frame(self.main_frame, bg="white")
        table_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "FirstName", "LastName", "Phone", "Email", "Address", "NationalID")
        display_cols = ("FirstName", "LastName", "Phone", "Email", "Address", "NationalID")
        
        self.tree = ttk.Treeview(table_container, columns=columns, displaycolumns=display_cols, 
                                 show="headings", height=12, yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        headers = {
            "FirstName": 100, "LastName": 100, 
            "Phone": 100, "Email": 150, "Address": 200, "NationalID": 100
        }
        
        for col, width in headers.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        self.load_customers()

    # ================== DB ==================

    def load_customers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT CustomerID, FirstName, LastName, Phone, Email, Address, NationalID FROM Customer")
            for row in cur.fetchall():
                clean_row = [str(i).replace("'", "") if i is not None else "" for i in row]
                self.tree.insert("", tk.END, values=clean_row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    def add_customer(self):
        fname = self.entries["First Name:"].get().strip()
        lname = self.entries["Last Name:"].get().strip()
        phone = self.entries["Phone:"].get().strip()
        email = self.entries["Email:"].get().strip()
        address = self.entries["Address:"].get().strip()
        nationalid = self.entries["National ID:"].get().strip()

        if not fname or not lname:
            messagebox.showwarning("Validation", "First and Last Name are required.")
            return

        try:
            conn = self.db.connect()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Customer (FirstName, LastName, Phone, Email, Address, NationalID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (fname, lname, phone, email, address, nationalid))
            conn.commit()
            
            messagebox.showinfo("Success", "Customer added successfully.")
            
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                
            self.load_customers()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not add customer: {e}")
        finally:
            if 'conn' in locals(): conn.close()