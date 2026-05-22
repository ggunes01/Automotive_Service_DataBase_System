import tkinter as tk
from tkinter import messagebox
from core.db import DBHelper

from car_repair_app.vehicle_management import VehicleManagement
from car_repair_app.service_entry_management import ServiceEntryManagement
from car_repair_app.repair_work_order_management import RepairWorkOrderManagement
from car_repair_app.labor_records_management import LaborRecordManagement
from car_repair_app.used_parts_management import UsedPartManagement
from car_repair_app.inventory_parts_stock_management import InventoryManagement
from car_repair_app.supplier_order_management import SupplierOrderManagement
from car_repair_app.invoice_management import InvoiceManagement
from car_repair_app.employee_register import EmployeeRegister

class CarRepairMainMenu:
    def __init__(self, user_data):
        self.user = user_data
        self.window = tk.Tk()
        self.window.title("Car Repair Tracking System - Main Menu")
        self.window.geometry("1100x700")
        self.window.resizable(True, True)

        self.colors = {
            "sidebar_bg": "#2c3e50",
            "content_bg": "#ecf0f1",
            "header_bg": "#34495e",
            "active_btn": "#3498db",
            "danger": "#c0392b",
            "card_blue": "#3498db",
            "card_orange": "#e67e22",
            "card_green": "#27ae60"
        }

        self.create_header()

        main_container = tk.Frame(self.window)
        main_container.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(main_container, bg=self.colors["sidebar_bg"], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(main_container, bg=self.colors["content_bg"])
        self.content_area.pack(side="right", fill="both", expand=True)

        self.build_sidebar_menu()
        self.build_dashboard_content() 

        self.window.mainloop()

    def create_header(self):
        header_frame = tk.Frame(self.window, bg=self.colors["header_bg"], height=60)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="CAR REPAIR TRACKING SYSTEM", 
                 bg=self.colors["header_bg"], fg="white", 
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=20)

        tk.Label(header_frame, text=f"Welcome: {self.user['FullName']}", 
                 bg=self.colors["header_bg"], fg="#ffffff", 
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=20)

    # --- SAYFA DEĞİŞTİRME MEKANİZMASI ---
    def switch_content(self, page_class):

        for widget in self.content_area.winfo_children():
            widget.destroy()

        try:
            page_class(self.content_area) 
        except Exception as e:
            messagebox.showerror("Error", f"Could not load page:\n{e}")

    def logout(self):
        """Mevcut pencereyi kapatır ve ui_login.py ekranını yeniden açar."""
        self.window.destroy()
        
        try:
            from car_repair_app.ui_login import CarRepairLoginGUI 
            CarRepairLoginGUI()
        except ImportError:
            try:
                from ui_login import CarRepairLoginGUI
                CarRepairLoginGUI()
            except ImportError as e:
                messagebox.showerror("Error", f"Login ekranı 'ui_login.py' bulunamadı.\nHata: {e}")

    def build_sidebar_menu(self):
        tk.Label(self.sidebar, text="MENU", bg=self.colors["sidebar_bg"], fg="#95a5a6", 
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=20, pady=(20, 10))

        def create_menu_btn(text, command):
            btn = tk.Button(self.sidebar, text=text, bg=self.colors["sidebar_bg"], fg="white",
                            font=("Segoe UI", 10), bd=0, activebackground=self.colors["active_btn"],
                            activeforeground="white", anchor="w", padx=20, cursor="hand2",
                            command=command)
            btn.pack(fill="x", pady=2, ipady=8)

        # --- MENÜ BUTTTONS ---
        
        create_menu_btn("Dashboard", self.build_dashboard_content)
        create_menu_btn("Vehicle Management", lambda: self.switch_content(VehicleManagement))
        create_menu_btn("Service Entry", lambda: self.switch_content(ServiceEntryManagement))
        create_menu_btn("Repair Work Orders", lambda: self.switch_content(RepairWorkOrderManagement))
        create_menu_btn("Labor Records", lambda: self.switch_content(LaborRecordManagement))
        create_menu_btn("Used Parts", lambda: self.switch_content(UsedPartManagement))
        create_menu_btn("Inventory & Parts Stock", lambda: self.switch_content(InventoryManagement))
        create_menu_btn("Supplier Orders", lambda: self.switch_content(SupplierOrderManagement))
        create_menu_btn("Invoices & Payments", lambda: self.switch_content(InvoiceManagement))
        create_menu_btn("New Employee Register", lambda: self.switch_content(EmployeeRegister))

        tk.Button(self.sidebar, text="Logout", bg=self.colors["danger"], fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                  command=self.logout).pack(side="bottom", fill="x", ipady=10)

    def build_dashboard_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        tk.Label(self.content_area, text="General Status Dashboard", 
                 bg=self.colors["content_bg"], fg="#2c3e50", 
                 font=("Segoe UI", 24, "bold")).pack(pady=40)

        cards_frame = tk.Frame(self.content_area, bg=self.colors["content_bg"])
        cards_frame.pack()

        # --- DB ---
        total_veh = 0
        in_repair = 0
        completed = 0

        db = DBHelper()
        conn = db.connect()
        if conn:
            try:
                cur = conn.cursor()
                
                cur.execute("SELECT COUNT(*) FROM Vehicle")
                total_veh = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM Invoice WHERE PaymentStatus = 'Paid'")
                completed = cur.fetchone()[0]

                query_in_repair = """
                    SELECT COUNT(SE.EntryID)
                    FROM ServiceEntry SE
                    LEFT JOIN Invoice I ON SE.EntryID = I.EntryID
                    WHERE SE.ActualDeliveryDate IS NULL
                    AND (I.PaymentStatus IS NULL OR I.PaymentStatus != 'Paid')
                """
                cur.execute(query_in_repair)
                in_repair = cur.fetchone()[0]
                
            except Exception as e:
                print("Dashboard Data Error:", e)
            finally:
                conn.close()

        def create_card(title, value, color, col):
            card = tk.Frame(cards_frame, bg=color, width=250, height=150)
            card.pack_propagate(False)
            tk.Label(card, text=str(value), bg=color, fg="white", font=("Segoe UI", 48, "bold")).pack(expand=True)
            tk.Label(card, text=title, bg=color, fg="white", font=("Segoe UI", 12)).pack(side="bottom", pady=15)
            card.grid(row=0, column=col, padx=20)

        create_card("Total Vehicles", total_veh, self.colors["card_blue"], 0)
        create_card("In Repair", in_repair, self.colors["card_orange"], 1)
        create_card("Completed (Paid)", completed, self.colors["card_green"], 2)

def open_car_repair_main_menu(user_data):
    CarRepairMainMenu(user_data)