import tkinter as tk
from tkinter import ttk
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import handle_error
import logging
import os

class AnalyticsApp:
    def __init__(self, parent):
        self.parent = parent
        # Change the background from BLACK to something lighter (black makes content hard to see)
        self.frame = tk.Frame(self.parent, bg="white", bd=2, relief="solid")  # Add border for visibility
        print("AnalyticsApp: __init__ called, frame created")
        self.create_widgets()
    
    def create_widgets(self):
        print("AnalyticsApp: create_widgets called")
        # Create a control panel using pack (inside self.frame)
        control_frame = tk.Frame(self.frame, bg="white")
        control_frame.pack(fill='x', pady=10)
        
        ttk.Label(control_frame, text="Min Tenure:").pack(side='left', padx=(15,0))
        self.min_tenure = ttk.Entry(control_frame, width=5)
        self.min_tenure.pack(side='left', padx=2)
        ttk.Label(control_frame, text="Max Tenure:").pack(side='left', padx=(5,0))
        self.max_tenure = ttk.Entry(control_frame, width=5)
        self.max_tenure.pack(side='left', padx=2)
        
        ttk.Label(control_frame, text="Min Monthly Charges:").pack(side='left', padx=(15,0))
        self.min_mcharges = ttk.Entry(control_frame, width=5)
        self.min_mcharges.pack(side='left', padx=2)
        ttk.Label(control_frame, text="Max Monthly Charges:").pack(side='left', padx=(5,0))
        self.max_mcharges = ttk.Entry(control_frame, width=5)
        self.max_mcharges.pack(side='left', padx=2)
        
        range_info = ("Available ranges from dataset (approx.): Tenure: 0-72 months, Monthly Charges: 18-120")
        ttk.Label(self.frame, text=range_info, foreground="blue").pack(pady=5)
        
        filter_btn = ttk.Button(control_frame, text="Apply Filters", command=self.update_charts)
        filter_btn.pack(side='left', padx=10)
        
        # Create the chart display area - add a background color to make it visible during debugging
        self.chart_frame = tk.Frame(self.frame, bg="lightblue")
        self.chart_frame.pack(fill='both', expand=True, pady=10)
    
    def update_charts(self):
        print("AnalyticsApp: update_charts called")
        try:
            # Clear any previous content
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
                
            # Add a fallback label in case charts don't load
            fallback = tk.Label(self.chart_frame, text="Loading charts...", bg="lightblue")
            fallback.pack(expand=True)
            self.chart_frame.update()

            # Load dataset from CSV
            file_path = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
            print(f"Looking for CSV at: {os.path.abspath(file_path)}")
            
            df = pd.read_csv(file_path)
            print(f"AnalyticsApp: CSV loaded, shape: {df.shape}")
            
            # Data cleaning steps
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
            df.drop(columns=['customerID'], inplace=True)
            # Conditionally drop columns that exist
            for col in ['Partner', 'Dependents', 'MultipleLines']:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)
                    
            df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})
            df['ChurnStatus'] = df['Churn'].map({0: 'No', 1: 'Yes'})
            if 'Contract' in df.columns:
                contract_mapping = {"Month-to-month": 1, "One year": 2, "Two year": 3}
                df['ContractMapped'] = df['Contract'].map(contract_mapping)
            else:
                df['ContractMapped'] = None
            print("AnalyticsApp: Data cleaning complete")
            
            # Apply filters (if any)
            try:
                min_t = float(self.min_tenure.get())
                df = df[df['tenure'] >= min_t]
            except ValueError:
                pass
            try:
                max_t = float(self.max_tenure.get())
                df = df[df['tenure'] <= max_t]
            except ValueError:
                pass
            try:
                min_mc = float(self.min_mcharges.get())
                df = df[df['MonthlyCharges'] >= min_mc]
            except ValueError:
                pass
            try:
                max_mc = float(self.max_mcharges.get())
                df = df[df['MonthlyCharges'] <= max_mc]
            except ValueError:
                pass
            print(f"AnalyticsApp: Filters applied, filtered shape: {df.shape}")
            
            # Clear previous chart area contents first
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Create plots
            sns.set_style("whitegrid")
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))
            
            # Chart 1: Churn Distribution
            sns.countplot(x="ChurnStatus", data=df, ax=axs[0],
                          palette={'No': 'lightgreen', 'Yes': 'tomato'})
            axs[0].set_title("Churn Distribution")
            
            # Chart 2: Monthly Charges by Churn
            sns.boxplot(x="ChurnStatus", y="MonthlyCharges", data=df, ax=axs[1],
                        palette={'No': 'lightgreen', 'Yes': 'tomato'})
            axs[1].set_title("Monthly Charges by Churn")
            
            # Chart 3: Tenure vs. Monthly Charges
            sns.scatterplot(x="tenure", y="MonthlyCharges", hue="ChurnStatus",
                            data=df, ax=axs[2], palette={'No': 'lightgreen', 'Yes': 'tomato'})
            axs[2].set_title("Tenure vs. Monthly Charges")
            fig.tight_layout()
            print("AnalyticsApp: Charts created")
            
            # Create and pack the canvas
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            print("AnalyticsApp: Chart canvas embedded")
            
        except Exception as e:
            print("AnalyticsApp: Exception in update_charts:", e)
            handle_error(e, "Failed to update charts")
    
    def show(self):
        print("AnalyticsApp: show called")
        # Place self.frame in the parent's grid cell
        self.frame.grid(row=0, column=0, sticky="nsew")
        # For debugging, add a visible border/background to the frame
        self.frame.config(borderwidth=2, relief="solid", bg="pink")
        # Force parent (content_frame) to expand its cell
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.update_idletasks()
        # Fix: call update_idletasks on self.frame, not self
        self.frame.update_idletasks()  
        # Log the widgets inside the parent for debug
        print("AnalyticsApp: parent grid slaves:", self.parent.grid_slaves())
        # Update charts once placed
        self.update_charts()
    
    def hide(self):
        print("AnalyticsApp: hide called")
        self.frame.grid_forget()

if __name__ == "__main__":
    # For stand-alone testing
    import tkinter as tk
    root = tk.Tk()
    root.title("Analytics Module")
    root.geometry("1200x600")  # Give it a reasonable size for testing
    app = AnalyticsApp(root)
    app.show()
    root.mainloop()
