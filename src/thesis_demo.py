"""Desktop batch-inference demo for the binary Random Forest model."""

import os
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

import joblib
import pandas as pd

from feature_schema import FEATURE_NAMES, validate_feature_columns

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "rf_model.joblib")
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "sample_output.csv")
LOG_PATH = os.path.join(PROJECT_ROOT, "alerts_log.txt")


class DetectionDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Anomaly Detection")
        self.root.geometry("820x560")
        self.model = None
        self.csv_path = DEFAULT_CSV_PATH

        tk.Label(root, text="Network Anomaly Detection", font=("Arial", 22, "bold")).pack(pady=18)
        tk.Label(root, text="Random Forest binary anomaly detection demo").pack()

        self.status = tk.Label(root, text="Status: Ready", font=("Arial", 13, "bold"))
        self.status.pack(pady=18)

        self.summary = tk.Label(root, text="Records: 0 | Anomalies: 0", font=("Arial", 16))
        self.summary.pack(pady=12)

        self.file_label = tk.Label(root, text=f"Input: {os.path.relpath(self.csv_path, PROJECT_ROOT)}")
        self.file_label.pack(pady=8)

        buttons = tk.Frame(root)
        buttons.pack(pady=12)
        tk.Button(buttons, text="Select CSV", width=18, command=self.select_csv).grid(row=0, column=0, padx=8)
        tk.Button(buttons, text="Start Analysis", width=18, command=self.run_detection).grid(row=0, column=1, padx=8)
        tk.Button(buttons, text="View Log", width=18, command=self.view_log).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(buttons, text="Reset", width=18, command=self.reset_demo).grid(row=1, column=1, padx=8, pady=8)

        tk.Label(
            root,
            text="Binary anomaly output is not an attack-family classifier.",
            font=("Arial", 10),
        ).pack(side="bottom", pady=14)

    def select_csv(self):
        selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if selected:
            self.csv_path = selected
            self.file_label.config(text=f"Input: {selected}")

    def load_model(self):
        if self.model is None:
            self.model = joblib.load(MODEL_PATH)

    def run_detection(self):
        started = time.time()
        try:
            self.status.config(text="Status: Analysing...")
            self.root.update()
            self.load_model()

            dataframe = pd.read_csv(self.csv_path)
            dataframe.columns = dataframe.columns.str.strip()
            validate_feature_columns(dataframe.columns)
            features = dataframe.loc[:, FEATURE_NAMES]

            predictions = self.model.predict(features)
            total = len(predictions)
            anomalies = sum(int(value) == 1 for value in predictions)

            self.summary.config(text=f"Records: {total} | Anomalies: {anomalies}")
            self.status.config(
                text="Status: Analyst review recommended" if anomalies else "Status: No anomaly detected"
            )

            elapsed_ms = round((time.time() - started) * 1000, 2)
            with open(LOG_PATH, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"{datetime.now().isoformat()} | records={total} | "
                    f"anomalies={anomalies} | latency_ms={elapsed_ms}\n"
                )
        except Exception as error:
            self.status.config(text="Status: Error")
            messagebox.showerror("Analysis error", str(error))

    def view_log(self):
        if not os.path.exists(LOG_PATH):
            messagebox.showinfo("Log", "No log file found.")
            return
        log_window = tk.Toplevel(self.root)
        log_window.title("Detection Log")
        text = tk.Text(log_window, width=110, height=25)
        text.pack(padx=10, pady=10)
        with open(LOG_PATH, "r", encoding="utf-8") as log_file:
            text.insert(tk.END, log_file.read())

    def reset_demo(self):
        self.summary.config(text="Records: 0 | Anomalies: 0")
        self.status.config(text="Status: Ready")


if __name__ == "__main__":
    root = tk.Tk()
    DetectionDemoApp(root)
    root.mainloop()
