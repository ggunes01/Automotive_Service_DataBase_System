import tkinter as tk
from tkinter import ttk, messagebox
from core.db import DBHelper
from datetime import datetime

class InsurancePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#ecf0f1")
        self.pack(fill="both", expand=True)

        self.db = DBHelper()
        

        self.vehicle_map = {}   
        self.company_map = {}   
        self.policy_map = {}   
        self.assessment_map = {} 

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_policies = tk.Frame(self.notebook, bg="#ecf0f1")
        self.tab_claims = tk.Frame(self.notebook, bg="#ecf0f1")

        self.notebook.add(self.tab_policies, text="   Policies (Poliçeler)   ")
        self.notebook.add(self.tab_claims, text="   Claims (Hasar Dosyaları)   ")

        self.setup_policy_tab()
        self.setup_claim_tab()

        self.load_common_data()
        self.load_policies()
        self.load_assessments_for_combo()
        self.load_claims()

    # ================= POLICIES =================
    def setup_policy_tab(self):
        form_frame = tk.LabelFrame(self.tab_policies, text="Add New Policy", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=10, pady=10)

        # Vehicle
        tk.Label(form_frame, text="Vehicle:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_p_vehicle = ttk.Combobox(form_frame, state="readonly", width=20)
        self.combo_p_vehicle.grid(row=0, column=1, padx=5, pady=5)

        # Company
        tk.Label(form_frame, text="Ins. Company:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_p_company = ttk.Combobox(form_frame, state="readonly", width=20)
        self.combo_p_company.grid(row=0, column=3, padx=5, pady=5)

        # Policy No
        tk.Label(form_frame, text="Policy No:", bg="#ecf0f1").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_p_no = tk.Entry(form_frame, width=20)
        self.entry_p_no.grid(row=0, column=5, padx=5, pady=5)

        # Dates
        tk.Label(form_frame, text="Start Date:", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_p_start = tk.Entry(form_frame, width=20)
        self.entry_p_start.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_p_start.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="End Date:", bg="#ecf0f1").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_p_end = tk.Entry(form_frame, width=20)
        self.entry_p_end.grid(row=1, column=3, padx=5, pady=5)

        btn_add = tk.Button(form_frame, text="Save Policy", bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                            command=self.add_policy)
        btn_add.grid(row=1, column=4, columnspan=2, pady=10, sticky="ew")

        # Table
        table_frame = tk.Frame(self.tab_policies, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ID", "PolicyNo", "Vehicle", "Company", "Start", "End")
        disp_cols = ("PolicyNo", "Vehicle", "Company", "Start", "End")
        self.tree_policy = ttk.Treeview(table_frame, columns=cols,displaycolumns= disp_cols, show="headings", height=10)
        self.tree_policy.heading("PolicyNo", text="PolicyNo")
        self.tree_policy.heading("Vehicle", text="Vehicle")
        self.tree_policy.heading("Company", text="Company")
        self.tree_policy.heading("Start", text="Start")
        self.tree_policy.heading("End", text="End")

        self.tree_policy.column("PolicyNo", width=100, anchor="center")
        self.tree_policy.column("Vehicle", width=120, anchor="w")
        self.tree_policy.column("Company", width=120, anchor="w")
        self.tree_policy.column("Start", width=90, anchor="center")
        self.tree_policy.column("End", width=90, anchor="center")

        self.tree_policy.pack(side="left", fill="both", expand=True)
        
        btn_del = tk.Button(self.tab_policies, text="Delete Selected Policy", bg="#c0392b", fg="white",
                            command=self.delete_policy)
        btn_del.pack(side="bottom", anchor="e", padx=10, pady=5)

    # ================= CLAIMS =================
    def setup_claim_tab(self):
        form_frame = tk.LabelFrame(self.tab_claims, text="New Claim (Hasar Dosyası)", bg="#ecf0f1", font=("Arial", 10, "bold"))
        form_frame.pack(fill="x", padx=10, pady=10)

        # 1. Select Policy
        tk.Label(form_frame, text="Select Policy:", bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_c_policy = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_c_policy.grid(row=0, column=1, padx=5, pady=5)

        # 2. Select Assessment
        tk.Label(form_frame, text="Select Assessment:", bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_c_assessment = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_c_assessment.grid(row=0, column=3, padx=5, pady=5)

        # 3. Amount & Status
        tk.Label(form_frame, text="Amount ($):", bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_c_amount = tk.Entry(form_frame, width=15)
        self.entry_c_amount.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Status:", bg="#ecf0f1").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.combo_c_status = ttk.Combobox(form_frame, state="readonly", width=18, 
                                           values=["Pending", "Approved", "Rejected", "Paid"])
        self.combo_c_status.current(0)
        self.combo_c_status.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # 4. Date
        tk.Label(form_frame, text="Claim Date:", bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_c_date = tk.Entry(form_frame, width=20)
        self.entry_c_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_c_date.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        btn_frame = tk.Frame(form_frame, bg="#ecf0f1")
        btn_frame.grid(row=2, column=3, sticky="e", padx=20, pady=5)

        btn_add = tk.Button(btn_frame, text="Create Claim", bg="#27ae60", fg="white", font=("Arial", 9, "bold"),
                            command=self.add_claim)
        btn_add.pack(side="left", padx=5)

        btn_update = tk.Button(btn_frame, text="Update Claim", bg="#2980b9", fg="white", font=("Arial", 9, "bold"),
                               command=self.update_claim)
        btn_update.pack(side="left", padx=5)

        # Table
        table_frame = tk.Frame(self.tab_claims, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("ClaimID", "Policy", "Assessment", "Date", "Status", "Amount")
        disp_cols = ("Policy", "Assessment", "Date", "Status", "Amount")
        self.tree_claim = ttk.Treeview(table_frame, columns=cols, displaycolumns=disp_cols, show="headings", height=10)
        
        
        self.tree_claim.heading("Policy", text="Policy")
        self.tree_claim.heading("Assessment", text="Assessment")
        self.tree_claim.heading("Date", text="Date")
        self.tree_claim.heading("Status", text="Status")
        self.tree_claim.heading("Amount", text="Amount")

        self.tree_claim.column("Policy", width=150)
        self.tree_claim.column("Assessment", width=150)
        self.tree_claim.column("Date", width=90, anchor="center")
        self.tree_claim.column("Status", width=90, anchor="center")
        self.tree_claim.column("Amount", width=90, anchor="e")

        self.tree_claim.pack(side="left", fill="both", expand=True)
        
        self.tree_claim.bind("<<TreeviewSelect>>", self.on_claim_select)

        btn_del = tk.Button(self.tab_claims, text="Delete Selected Claim", bg="#c0392b", fg="white",
                            command=self.delete_claim)
        btn_del.pack(side="bottom", anchor="e", padx=10, pady=5)

    # ================= DB =================
    
    def load_common_data(self):
        self.vehicle_map.clear()
        self.company_map.clear()
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT VehicleID, LicensePlate FROM Vehicle")
                for vid, plate in cur.fetchall():
                    self.vehicle_map[plate] = vid
                self.combo_p_vehicle['values'] = list(self.vehicle_map.keys())

                cur.execute("SELECT CompanyID, Name FROM InsuranceCompany")
                for cid, name in cur.fetchall():
                    self.company_map[name] = cid
                self.combo_p_company['values'] = list(self.company_map.keys())
            finally:
                conn.close()

    def load_policies(self):
        for row in self.tree_policy.get_children():
            self.tree_policy.delete(row)
        self.policy_map.clear() 

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT P.PolicyID, P.PolicyNo, V.LicensePlate, C.Name, P.StartDate, P.EndDate
                    FROM InsurancePolicy P
                    JOIN Vehicle V ON P.VehicleID = V.VehicleID
                    JOIN InsuranceCompany C ON P.CompanyID = C.CompanyID
                """
                cur.execute(query)
                for row in cur.fetchall():
                    clean_row = [str(item) for item in row]
                    self.tree_policy.insert("", tk.END, values=clean_row)
                    
                    display = f"{clean_row[1]} - {clean_row[2]}"
                    self.policy_map[display] = row[0]

                self.combo_c_policy['values'] = list(self.policy_map.keys())
            finally:
                conn.close()

    def load_assessments_for_combo(self):
        self.assessment_map.clear()
        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT DA.AssessmentID, V.LicensePlate, DA.AssessmentDate 
                    FROM DamageAssessment DA
                    JOIN AccidentRecord AR ON DA.AccidentID = AR.AccidentID
                    JOIN Vehicle V ON AR.VehicleID = V.VehicleID
                """
                cur.execute(query)
                for aid, plate, date in cur.fetchall():
                    display = f"#{aid} - {plate} ({date})"
                    self.assessment_map[display] = aid
                
                self.combo_c_assessment['values'] = list(self.assessment_map.keys())
            finally:
                conn.close()

    def load_claims(self):
        for row in self.tree_claim.get_children():
            self.tree_claim.delete(row)

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    SELECT C.ClaimID, P.PolicyNo, 
                           ('Assessment #' + CAST(C.AssessmentID AS VARCHAR)), 
                           C.ClaimDate, C.ApprovalStatus, C.ClaimedAmount
                    FROM InsuranceClaim C
                    JOIN InsurancePolicy P ON C.PolicyID = P.PolicyID
                """
                cur.execute(query)
                for row in cur.fetchall():
                    self.tree_claim.insert("", tk.END, values=[str(x) for x in row])
            finally:
                conn.close()

    def on_claim_select(self, event):
        selected = self.tree_claim.selection()
        if not selected: return
        
        values = self.tree_claim.item(selected[0])['values']
        
        self.entry_c_date.delete(0, tk.END)
        self.entry_c_date.insert(0, values[3])
        
        self.combo_c_status.set(values[4])
        
        self.entry_c_amount.delete(0, tk.END)
        self.entry_c_amount.insert(0, values[5])

        pol_no_from_table = str(values[1])
        for key in self.policy_map.keys():
            if key.startswith(pol_no_from_table):
                self.combo_c_policy.set(key)
                break
        
        ass_text_from_table = str(values[2]) 
        try:
            ass_id_str = ass_text_from_table.split('#')[1] 
            ass_id = int(ass_id_str)
            for key, val in self.assessment_map.items():
                if val == ass_id:
                    self.combo_c_assessment.set(key)
                    break
        except:
            pass 

    def update_claim(self):
        """Seçili kaydı günceller (Status değiştirmek için ideal)"""
        selected = self.tree_claim.selection()
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen güncellenecek kaydı tablodan seçin.")
            return
        
        claim_id = self.tree_claim.item(selected[0])['values'][0]
        
        pol_text = self.combo_c_policy.get()
        ass_text = self.combo_c_assessment.get()
        date = self.entry_c_date.get()
        status = self.combo_c_status.get()
        amount = self.entry_c_amount.get()

        if not pol_text or not ass_text:
            messagebox.showwarning("Eksik", "Poliçe ve Hasar Raporu zorunludur.")
            return

        pid = self.policy_map.get(pol_text)
        aid = self.assessment_map.get(ass_text)

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    UPDATE InsuranceClaim 
                    SET ClaimDate=?, ApprovalStatus=?, ClaimedAmount=?, PolicyID=?, AssessmentID=?
                    WHERE ClaimID=?
                """
                cur.execute(query, (date, status, amount, pid, aid, claim_id))
                conn.commit()
                messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
                self.load_claims()
            except Exception as e:
                messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")
            finally:
                conn.close()

    def add_policy(self):
        veh_name = self.combo_p_vehicle.get()
        comp_name = self.combo_p_company.get()
        pol_no = self.entry_p_no.get()
        start = self.entry_p_start.get()
        end = self.entry_p_end.get()

        if not veh_name or not comp_name or not pol_no:
            messagebox.showwarning("Eksik", "Zorunlu alanları doldurun.")
            return

        vid = self.vehicle_map[veh_name]
        cid = self.company_map[comp_name]

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM InsurancePolicy WHERE PolicyNo = ?", (pol_no,))
                if cur.fetchone()[0] > 0:
                    messagebox.showwarning("Hata", "Bu Poliçe No zaten kayıtlı!")
                    return

                cur.execute("INSERT INTO InsurancePolicy (PolicyNo, StartDate, EndDate, CompanyID, VehicleID) VALUES (?, ?, ?, ?, ?)",
                            (pol_no, start, end, cid, vid))
                conn.commit()
                messagebox.showinfo("Başarılı", "Poliçe eklendi.")
                self.load_policies()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
            finally:
                conn.close()

    def add_claim(self):
        pol_text = self.combo_c_policy.get()
        ass_text = self.combo_c_assessment.get()
        date = self.entry_c_date.get()
        status = self.combo_c_status.get()
        amount = self.entry_c_amount.get()

        if not pol_text or not ass_text:
            messagebox.showwarning("Eksik", "Lütfen Poliçe ve Hasar Raporu (Assessment) seçiniz.")
            return
        
        pid = self.policy_map[pol_text]
        aid = self.assessment_map[ass_text]

        conn = self.db.connect()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                    INSERT INTO InsuranceClaim 
                    (ClaimDate, ApprovalStatus, ClaimedAmount, PolicyID, AssessmentID) 
                    VALUES (?, ?, ?, ?, ?)
                """
                cur.execute(query, (date, status, amount, pid, aid))
                conn.commit()
                messagebox.showinfo("Başarılı", "Hasar dosyası oluşturuldu.")
                self.load_claims()
            except Exception as e:
                messagebox.showerror("Hata", f"Veritabanı Hatası: {e}")
            finally:
                conn.close()

    def delete_policy(self):
        self._delete_helper(self.tree_policy, "InsurancePolicy", "PolicyID", self.load_policies)

    def delete_claim(self):
        self._delete_helper(self.tree_claim, "InsuranceClaim", "ClaimID", self.load_claims)

    def _delete_helper(self, tree, table, col, callback):
        sel = tree.selection()
        if not sel: return
        id_val = tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Sil", "Kayıt silinsin mi?"):
            conn = self.db.connect()
            try:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (id_val,))
                conn.commit()
                callback()
            except Exception as e:
                messagebox.showerror("Hata", str(e))
            finally:
                conn.close()