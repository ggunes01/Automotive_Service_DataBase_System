import tkinter as tk
from tkinter import messagebox
from core.auth import car_repair_login

class CarRepairLoginGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Car Repair Tracking - Login")
        self.window.geometry("400x500") 
        self.window.resizable(False, False)

        bg_color = "#f0f2f5"
        self.window.configure(bg=bg_color)

        card_frame = tk.Frame(self.window, bg="white", padx=30, pady=30)
        card_frame.place(relx=0.5, rely=0.5, anchor="center", width=340, height=420)

        tk.Label(card_frame, text="Welcome Back", font=("Segoe UI", 18, "bold"), 
                 bg="white", fg="#333").pack(pady=(0, 5))
        
        tk.Label(card_frame, text="Login to your account", font=("Segoe UI", 10), 
                 bg="white", fg="#777").pack(pady=(0, 30))

        tk.Label(card_frame, text="Email Address", font=("Segoe UI", 9, "bold"), 
                 bg="white", fg="#555").pack(anchor="w", pady=(0, 5))
        
        self.email_entry = tk.Entry(card_frame, font=("Segoe UI", 11), width=30, 
                                    bg="#f7f9fc", relief="flat", highlightthickness=1, 
                                    highlightbackground="#e1e4e8")
        self.email_entry.pack(fill="x", ipady=8, pady=(0, 15))

        tk.Label(card_frame, text="Password", font=("Segoe UI", 9, "bold"), 
                 bg="white", fg="#555").pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(card_frame, font=("Segoe UI", 11), width=30, show="*",
                                       bg="#f7f9fc", relief="flat", highlightthickness=1, 
                                       highlightbackground="#e1e4e8")
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 25))

        login_btn = tk.Button(card_frame, text="LOGIN", font=("Segoe UI", 10, "bold"), 
                              bg="#2563eb", fg="white", # Mavi Buton
                              activebackground="#1d4ed8", activeforeground="white",
                              relief="flat", cursor="hand2",
                              command=self.login)
        login_btn.pack(fill="x", ipady=10)

        tk.Label(card_frame, text="Car Repair Tracking System v1.0", font=("Segoe UI", 8), 
                 bg="white", fg="#aaa").pack(side="bottom", pady=(20, 0))

        self.window.mainloop()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password.")
            return

        result = car_repair_login(email, password)

        if not result["status"]:
            messagebox.showerror("Login Failed", result["message"])
            return

        messagebox.showinfo("Success", f"Welcome {result['FullName']}")

        from car_repair_app.main import open_car_repair_main_menu
        self.window.destroy()
        open_car_repair_main_menu(result)

    def open_main_menu(self, user_data):
        self.window.destroy()

        main_window = tk.Tk()
        main_window.title("Car Repair Main Menu")
        main_window.geometry("400x300")

        tk.Label(
            main_window,
            text=f"Logged in as: {user_data['FullName']}",
            font=("Arial", 12)
        ).pack(pady=20)

        tk.Label(
            main_window,
            text="(Car Repair Dashboard placeholder)",
            font=("Arial", 11),
            fg="gray"
        ).pack()

        main_window.mainloop()
