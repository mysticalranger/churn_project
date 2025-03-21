import tkinter as tk
from tkinter import ttk, messagebox
import tensorflow as tf
import pandas as pd
import numpy as np
import joblib
import os

# Load and preprocess the dataset to define the feature columns
data = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')
data = data.drop('customerID', axis=1)

# Define features (same as training)
features = [
    'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 'PhoneService',
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'Contract', 'PaperlessBilling', 'PaymentMethod', 'MonthlyCharges', 'TotalCharges'
]
df = data[features + ['Churn']]

# Preprocess categorical variables (match training script)
binary_cols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
for col in binary_cols:
    df[col] = df[col].map({'Yes': 1, 'No': 0})
df['gender'] = df['gender'].map({'Male': 1, 'Female': 0})
df['Contract'] = df['Contract'].map({'Month-to-month': 1, 'One year': 2, 'Two year': 3})
df['SeniorCitizen'] = df['SeniorCitizen'].astype(int)
categorical_cols = [
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'PaymentMethod'
]
df = pd.get_dummies(df, columns=categorical_cols)
numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()

class ChurnApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        self.model = None
        self.scaler = None
        self.create_widgets()
        self.load_model_and_scaler()

    def create_widgets(self):
        """Create simplified churn prediction widgets based on SHAP"""
        input_frame = ttk.LabelFrame(self.frame, text="Customer Details")
        input_frame.pack(fill='x', pady=10)

        self.entries = {}
        fields = [
            ("Tenure (months):", "tenure", ttk.Entry, {}),
            ("Contract Type:", "contract", ttk.Combobox, {"values": ["Month-to-month", "One year", "Two year"]}),
            ("Partner:", "partner", ttk.Combobox, {"values": ["Yes", "No"]}),
            ("Internet Service:", "internet_service", ttk.Combobox, {"values": ["DSL", "Fiber optic", "No"]}),
            ("Total Charges ($):", "total_charges", ttk.Entry, {}),
        ]

        for label, field, widget_type, options in fields:
            row = ttk.Frame(input_frame)
            row.pack(fill='x', padx=5, pady=2)
            ttk.Label(row, text=label).pack(side='left')
            self.entries[field] = widget_type(row, width=30, **options)
            self.entries[field].pack(side='left', padx=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(pady=10)
        predict_btn = ttk.Button(btn_frame, text="Predict Churn", command=self.predict_churn)
        predict_btn.pack(side='left', padx=5)
        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_fields)
        reset_btn.pack(side='left', padx=5)

        result_frame = ttk.LabelFrame(self.frame, text="Prediction Result")
        result_frame.pack(fill='x', pady=10)
        self.result_label = ttk.Label(result_frame, text="Enter details and click 'Predict'", font=("Helvetica", 12))
        self.result_label.pack(pady=20)

    def load_model_and_scaler(self):
        """Load TensorFlow model and scaler"""
        try:
            if os.path.exists("churn_model.h5"):
                self.model = tf.keras.models.load_model("churn_model.h5")
                print("Model loaded successfully")
            else:
                messagebox.showwarning("Warning", "Churn model file not found.")
                self.model = None

            if os.path.exists("scaler.pkl"):
                self.scaler = joblib.load("scaler.pkl")
                print("Scaler loaded successfully")
            else:
                messagebox.showwarning("Warning", "Scaler file not found.")
                self.scaler = None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model or scaler: {str(e)}")
            self.model = None
            self.scaler = None

    def predict_churn(self):
        """Make churn prediction with SHAP-based inputs"""
        try:
            # Collect and validate input
            input_data = {}
            for field in self.entries:
                value = self.entries[field].get()
                if not value:
                    messagebox.showwarning("Input Error", f"{field.replace('_', ' ').title()} is required")
                    return
                input_data[field] = value

            # Preprocess input data
            df_input = pd.DataFrame([input_data])
            le = {"Yes": 1, "No": 0}
            df_input["partner"] = df_input["partner"].map(le)
            df_input["contract"] = df_input["contract"].map({"Month-to-month": 1, "One year": 2, "Two year": 3})
            df_input = pd.get_dummies(df_input, columns=["internet_service"])

            # Convert numeric columns
            for col in ["tenure", "total_charges"]:
                if not df_input[col].str.match(r'^\d*\.?\d+$').all():
                    messagebox.showwarning("Input Error", f"{col.replace('_', ' ').title()} must be a number")
                    return
                df_input[col] = df_input[col].astype(float)

            # Add missing columns from training data
            original_cols = df.drop('Churn', axis=1).columns  # Now df is defined globally
            missing_cols = set(original_cols) - set(df_input.columns)
            for col in missing_cols:
                df_input[col] = 0
            df_input = df_input[original_cols]  # Reorder to match training

            # Scale the data
            if self.scaler:
                X_input = self.scaler.transform(df_input)
            else:
                messagebox.showerror("Error", "Scaler not loaded")
                return

            # Predict
            if self.model:
                prediction = self.model.predict(X_input, verbose=0)[0][0]
                churn = "Churn" if prediction > 0.5 else "No Churn"
                color = "red" if prediction > 0.5 else "green"
                self.result_label.config(
                    text=f"Prediction: {churn}\nProbability: {prediction:.2%}",
                    foreground=color
                )
            else:
                messagebox.showerror("Error", "Model not loaded")

        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")

    def reset_fields(self):
        """Reset all input fields"""
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set("")
            else:
                entry.delete(0, tk.END)
        self.result_label.config(text="Enter details and click 'Predict'", foreground="black")

    def show(self):
        self.frame.grid(row=0, column=0, sticky='nsew')

    def hide(self):
        self.frame.grid_forget()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Churn Prediction App")
    app = ChurnApp(root)
    app.show()
    root.mainloop()