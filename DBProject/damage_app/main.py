import tkinter as tk
from core.db import DBHelper
from tkinter import messagebox
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from damage_app.customer_management import CustomerManagement # EKLENDİ
from damage_app.vehicle_management import VehiclePage
from damage_app.damage_assessment_management import DamageAssessmentPage
from damage_app.insurance_claims import InsurancePage
from damage_app.parts_inventory import PartsInventoryPage
from damage_app.accident_records import AccidentRecordPage

def open_damage_main_menu(user_data):

    app = MainDashboard(user_data)
    app.run()

class MainDashboard:
    def __init__(self, user_data):
        self.user_data = user_data
        
        # Get user name safely
        if isinstance(user_data, dict):
            self.user_name = user_data.get("FullName", "User")
        else:
            self.user_name = user_data[1] if user_data and len(user_data) > 1 else "User"

        self.window = tk.Tk()
        self.window.title("Damage Tracking System - Main Menu")
        self.window.geometry("1000x600")
        
        try:
            self.window.state('zoomed') 
        except:
            pass


        self.bg_color = "#ecf0f1"      
        self.sidebar_color = "#2c3e50" 
        self.header_color = "#34495e"  
        self.text_color = "#ffffff"    
        self.active_color = "#1abc9c"  

        self.setup_ui()

    def setup_ui(self):
        header_frame = tk.Frame(self.window, bg=self.header_color, height=60)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        lbl_title = tk.Label(header_frame, text="DAMAGE TRACKING SYSTEM", 
                             bg=self.header_color, fg="white", font=("Arial", 14, "bold"))
        lbl_title.pack(side="left", padx=20)

        lbl_user = tk.Label(header_frame, text=f"Welcome: {self.user_name}", 
                            bg=self.header_color, fg="#ffffff", font=("Arial", 10, "bold"))
        lbl_user.pack(side="right", padx=20)

        main_container = tk.Frame(self.window, bg=self.bg_color)
        main_container.pack(side="bottom", fill="both", expand=True)

        sidebar_frame = tk.Frame(main_container, bg=self.sidebar_color, width=220)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)


        tk.Label(sidebar_frame, text="MENU", bg=self.sidebar_color, fg="#95a5a6", 
                 font=("Arial", 10, "bold")).pack(pady=(20, 10), anchor="w", padx=20)

        self.create_sidebar_btn(sidebar_frame, "Dashboard", self.show_dashboard)
        self.create_sidebar_btn(sidebar_frame, "Customer Management", self.show_customer_page) # EKLENDİ
        self.create_sidebar_btn(sidebar_frame, "Vehicle Management", self.show_vehicle_page)
        self.create_sidebar_btn(sidebar_frame, "Accident Records", self.show_accident_page)
        self.create_sidebar_btn(sidebar_frame, "Damage Assessment", self.show_damage_page)
        self.create_sidebar_btn(sidebar_frame, "Insurance & Claims", self.show_insurance_page)
        self.create_sidebar_btn(sidebar_frame, "Parts & Inventory", self.show_parts_page)
        
        logout_btn = tk.Button(sidebar_frame, text="Logout", bg="#c0392b", fg="white", 
                               font=("Arial", 10, "bold"), bd=0, command=self.logout)
        logout_btn.pack(side="bottom", fill="x", pady=20, padx=10)

        self.content_frame = tk.Frame(main_container, bg=self.bg_color)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.show_dashboard()

    def create_sidebar_btn(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=self.sidebar_color, fg=self.text_color, 
                        font=("Arial", 11), bd=0, activebackground=self.active_color, 
                        activeforeground="white", cursor="hand2", command=command, anchor="w", padx=20, pady=10)
        btn.pack(fill="x", pady=1)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.content_frame, text="General Status Dashboard", bg=self.bg_color, 
                 font=("Arial", 22, "bold"), fg="#2c3e50").pack(pady=30)
        
        stats_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        stats_frame.pack(pady=20)

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
        self.create_stat_card(stats_frame, "Total Vehicles", str(total_veh), "#3498db")
        self.create_stat_card(stats_frame, "In Repair", str(in_repair), "#e67e22")
        self.create_stat_card(stats_frame, "Completed (Paid)", str(completed), "#27ae60")
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, width=250, height=150)
        card.pack(side="left", padx=20)
        card.pack_propagate(False)
        
        tk.Label(card, text=value, bg=color, fg="white", font=("Arial", 48, "bold")).pack(expand=True)
        tk.Label(card, text=title, bg=color, fg="white", font=("Arial", 12)).pack(side="bottom", pady=15)
    # --- MENÜ ---
    
    def show_customer_page(self):
        self.clear_content()
        CustomerManagement(self.content_frame)

    def show_vehicle_page(self):
        self.clear_content()
        VehiclePage(self.content_frame)

    def show_damage_page(self):
        self.clear_content()
        DamageAssessmentPage(self.content_frame)

    def show_insurance_page(self):
        self.clear_content()
        InsurancePage(self.content_frame)

    def show_parts_page(self):
        self.clear_content()
        PartsInventoryPage(self.content_frame)

    def show_accident_page(self):
        self.clear_content()
        AccidentRecordPage(self.content_frame)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    test_user = {"FullName": "Test Admin", "status": True}
    open_damage_main_menu(test_user)