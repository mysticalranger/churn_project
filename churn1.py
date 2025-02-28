import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from utils import handle_error, validate_number
import logging
import joblib
import pandas as pd
import os

class ChurnApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        self.db = Database(
            host="localhost",
            user="root",
            password="riyranagi007*",
            database="churn_db"
        )
        self.model = None
        self.create_widgets()
        self.load_model()
        
    def create_widgets(self):
        """Create churn prediction widgets"""
        # Input fields
        input_frame = ttk.LabelFrame(self.frame, text="Customer Details")
        input_frame.pack(fill='x', pady=10)
        
        fields = [
            ("Tenure (months):", "tenure"),
            ("Monthly Charges:", "monthly_charges"),
            ("Total Charges:", "total_charges"),
            ("Contract Type:", "contract"),
            ("Payment Method:", "payment_method")
        ]
        
        self.entries = {}
        for label, field in fields:
            row = ttk.Frame(input_frame)
            row.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(row, text=label).pack(side='left')
            if field == "contract":
                self.entries[field] = ttk.Combobox(
                    row,
                    values=["Month-to-month", "One year", "Two year"]
                )
            elif field == "payment_method":
                self.entries[field] = ttk.Combobox(
                    row,
                    values=[
                        "Electronic check",
                        "Mailed check",
                        "Bank transfer",
                        "Credit card"
                    ]
                )
            else:
                self.entries[field] = ttk.Entry(row, width=30)
            self.entries[field].pack(side='left', padx=5)
            
        # Predict button
        predict_btn = ttk.Button(
            input_frame,
            text="Predict Churn",
            command=self.predict_churn
        )
        predict_btn.pack(pady=10)
        
        # Result display
        result_frame = ttk.LabelFrame(self.frame, text="Prediction Result")
        result_frame.pack(fill='x', pady=10)
        
        self.result_label = ttk.Label(
            result_frame,
            text="Please enter customer details and click 'Predict'",
            font=("Helvetica", 12)
        )
        self.result_label.pack(pady=20)
        
    def load_model(self):
        """Load churn prediction model"""
        try:
            if os.path.exists("churn_model.pkl"):
                self.model = joblib.load("churn_model.pkl")
            else:
                self.model = None
                messagebox.showwarning("Warning", "Churn model file not found. Predictions will be disabled.")
        except Exception as e:
            handle_error(e, "Failed to load prediction model")
            messagebox.showerror(
                "Error",
                "Churn prediction model could not be loaded"
            )
            
    def predict_churn(self):
        """Make churn prediction"""
        try:
            # Validate inputs
            tenure = self.entries["tenure"].get()
            if not validate_number(tenure, min_val=0):
                messagebox.showwarning("Input Error", "Invalid tenure value")
                return
                
            monthly_charges = self.entries["monthly_charges"].get()
            if not validate_number(monthly_charges, min_val=0):
                messagebox.showwarning("Input Error", "Invalid monthly charges")
                return
                
            total_charges = self.entries["total_charges"].get()
            if not validate_number(total_charges, min_val=0):
                messagebox.showwarning("Input Error", "Invalid total charges")
                return
                
            contract = self.entries["contract"].get()
            if not contract:
                messagebox.showwarning("Input Error", "Contract type required")
                return
                
            payment_method = self.entries["payment_method"].get()
            if not payment_method:
                messagebox.showwarning("Input Error", "Payment method required")
                return
                
            # Prepare input data
            input_data = {
                "tenure": float(tenure),
                "MonthlyCharges": float(monthly_charges),
                "TotalCharges": float(total_charges),
                "Contract": contract,
                "PaymentMethod": payment_method
            }
            
            # Convert to DataFrame
            df = pd.DataFrame([input_data])
            
            # Make prediction
            if self.model:
                prediction = self.model.predict(df)[0]
                probability = self.model.predict_proba(df)[0][1]
                
                self.result_label.config(
                    text=f"Prediction: {'Churn' if prediction == 1 else 'No Churn'}\n"
                         f"Probability: {probability:.2%}"
                )
            else:
                messagebox.showerror("Error", "Prediction model not loaded")
                
        except Exception as e:
            handle_error(e, "Prediction failed")
            messagebox.showerror("Error", "Failed to make prediction")
            
    def show(self):
        """Show churn prediction module"""
        self.frame.grid(row=0, column=0, sticky='nsew') 
        
    def hide(self):
        """Hide churn prediction module"""
        self.frame.grid_forget()  # Use the same geometry manager as show()
