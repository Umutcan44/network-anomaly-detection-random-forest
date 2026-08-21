import tkinter as tk
from tkinter import messagebox
import pandas as pd
import joblib
from datetime import datetime
import os
import time

MODEL_PATH = "rf_model.joblib"
CSV_PATH = "out_demo.csv"
LOG_PATH = "alerts_log.txt"

class ThesisDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Anomaly Detection System")
        self.root.geometry("880x620")
        self.root.configure(bg="#111827")

        self.model = None

        tk.Label(root, text="Network Anomaly Detection System",
                 font=("Arial", 24, "bold"),
                 fg="white", bg="#111827").pack(pady=(25, 5))

        tk.Label(root, text="Machine Learning-Based IDS using Random Forest",
                 font=("Arial", 13),
                 fg="#9ca3af", bg="#111827").pack(pady=5)

        tk.Label(root, text="Bachelor Thesis Demonstration",
                 font=("Arial", 11),
                 fg="#60a5fa", bg="#111827").pack(pady=(0, 18))

        panel = tk.Frame(root, bg="#1f2937", padx=35, pady=25)
        panel.pack(pady=10)

        self.status = tk.Label(panel, text="🟢 Status: Ready",
                               font=("Arial", 14, "bold"),
                               fg="#22c55e", bg="#1f2937")
        self.status.grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(panel, text="Packets / Records Analysed",
                 font=("Arial", 12),
                 fg="#d1d5db", bg="#1f2937").grid(row=1, column=0, padx=35, pady=(20, 5))

        self.records_value = tk.Label(panel, text="0",
                                      font=("Arial", 25, "bold"),
                                      fg="white", bg="#1f2937")
        self.records_value.grid(row=2, column=0, padx=35, pady=5)

        tk.Label(panel, text="Detected Anomalies",
                 font=("Arial", 12),
                 fg="#d1d5db", bg="#1f2937").grid(row=1, column=1, padx=35, pady=(20, 5))

        self.attacks_value = tk.Label(panel, text="0",
                                      font=("Arial", 25, "bold"),
                                      fg="white", bg="#1f2937")
        self.attacks_value.grid(row=2, column=1, padx=35, pady=5)

        tk.Label(panel, text="Attack Type",
                 font=("Arial", 12),
                 fg="#d1d5db", bg="#1f2937").grid(row=3, column=0, padx=35, pady=(20, 5))

        self.attack_type_value = tk.Label(panel, text="-",
                                          font=("Arial", 16, "bold"),
                                          fg="white", bg="#1f2937")
        self.attack_type_value.grid(row=4, column=0, padx=35, pady=5)

        tk.Label(panel, text="Risk Level",
                 font=("Arial", 12),
                 fg="#d1d5db", bg="#1f2937").grid(row=3, column=1, padx=35, pady=(20, 5))

        self.risk_value = tk.Label(panel, text="-",
                                   font=("Arial", 18, "bold"),
                                   fg="white", bg="#1f2937")
        self.risk_value.grid(row=4, column=1, padx=35, pady=5)

        self.result = tk.Label(root, text="Result: Waiting for analysis",
                               font=("Arial", 17, "bold"),
                               fg="#facc15", bg="#111827")
        self.result.pack(pady=20)

        btn_frame = tk.Frame(root, bg="#111827")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="▶ Start Analysis",
                  font=("Arial", 12, "bold"),
                  width=20, command=self.run_detection).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="📄 View Detection Log",
                  font=("Arial", 12, "bold"),
                  width=20, command=self.view_log).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="↺ Reset Demo",
                  font=("Arial", 12, "bold"),
                  width=20, command=self.reset_demo).grid(row=1, column=0, padx=10, pady=15)

        tk.Button(btn_frame, text="Exit",
                  font=("Arial", 12, "bold"),
                  width=20, command=root.quit).grid(row=1, column=1, padx=10, pady=15)

        tk.Label(root,
                 text="Developed by Umutcan Kargın | Supervisor: PhD Eng Leszek Grocholski",
                 font=("Arial", 10),
                 fg="#9ca3af", bg="#111827").pack(side="bottom", pady=12)

    def load_model(self):
        if self.model is None:
            self.model = joblib.load(MODEL_PATH)

    def run_detection(self):
        start_time = time.time()

        try:
            self.status.config(text="🟡 Status: Analysing traffic...", fg="#facc15")
            self.result.config(text="Result: Analysis in progress", fg="#facc15")
            self.root.update()

            self.load_model()

            df = pd.read_csv(CSV_PATH)
            df.columns = df.columns.str.strip()

            for col in ["Label", "label", "Attack", "attack"]:
                if col in df.columns:
                    df = df.drop(columns=[col])

            predictions = self.model.predict(df)
            total = len(predictions)
            detected = int(sum(predictions))

            self.records_value.config(text=str(total))
            self.attacks_value.config(text=str(detected))

            if detected > 0:
                attack_type = "UDP Flood / DDoS-like Traffic"
                risk = "HIGH"
                self.status.config(text="🔴 Status: Threat Detected", fg="#ef4444")
                self.result.config(text="Result: Attack Detected", fg="#ef4444")
                self.attack_type_value.config(text=attack_type, fg="#ef4444")
                self.risk_value.config(text=risk, fg="#ef4444")
            else:
                attack_type = "Benign Traffic"
                risk = "LOW"
                self.status.config(text="🟢 Status: Normal Traffic", fg="#22c55e")
                self.result.config(text="Result: Normal Traffic", fg="#22c55e")
                self.attack_type_value.config(text=attack_type, fg="#22c55e")
                self.risk_value.config(text=risk, fg="#22c55e")

            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            with open(LOG_PATH, "a") as log:
                log.write(
                    f"{datetime.now()} | Records Analysed: {total} | "
                    f"Detected Anomalies: {detected} | "
                    f"Attack Type: {attack_type} | Risk Level: {risk} | "
                    f"Detection Time: {elapsed_ms} ms\n"
                )

        except Exception as e:
            self.status.config(text="🔴 Status: Error", fg="#ef4444")
            self.result.config(text="Result: Error", fg="#ef4444")
            messagebox.showerror("Error", str(e))

    def view_log(self):
        if not os.path.exists(LOG_PATH):
            messagebox.showinfo("Log", "No log file found.")
            return

        log_window = tk.Toplevel(self.root)
        log_window.title("Real-Time Detection Log")
        log_window.geometry("950x480")
        log_window.configure(bg="#111827")

        text = tk.Text(log_window, bg="#0f172a", fg="#e5e7eb",
                       font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        with open(LOG_PATH, "r") as f:
            text.insert(tk.END, f.read())

    def reset_demo(self):
        self.records_value.config(text="0")
        self.attacks_value.config(text="0")
        self.attack_type_value.config(text="-", fg="white")
        self.risk_value.config(text="-", fg="white")
        self.status.config(text="🟢 Status: Ready", fg="#22c55e")
        self.result.config(text="Result: Waiting for analysis", fg="#facc15")

        try:
            open(LOG_PATH, "w").close()
        except Exception:
            pass

root = tk.Tk()
app = ThesisDemoApp(root)
root.mainloop()
