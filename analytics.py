import tkinter as tk
from tkinter import ttk
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import os

# Ensure Matplotlib uses the correct backend
matplotlib.use("TkAgg")

def handle_error(e, message="Error occurred"):
    print(f"{message}: {str(e)}")

class AnalyticsApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, bg="white", bd=2, relief="solid")
        self.frame.pack(fill='both', expand=True)
        self.create_widgets()
        self.update_charts()  # Display default Churn count graph
    
    def create_widgets(self):
        self.menu_frame = tk.Frame(self.frame, bg="white")
        self.menu_frame.pack(fill='x', pady=10)
        
        ttk.Label(self.menu_frame, text="Select Field Against Churn:").pack(side='left', padx=5)
        self.selected_field = tk.StringVar()
        self.field_menu = ttk.Combobox(self.menu_frame, textvariable=self.selected_field)
        self.field_menu.pack(side='left', padx=5)
        self.field_menu.bind("<<ComboboxSelected>>", self.update_filters)
        
        self.filter_frame = tk.Frame(self.menu_frame, bg="white")
        self.filter_frame.pack(side='left', padx=10)
        
        self.plot_button = ttk.Button(self.menu_frame, text="Plot Graph", command=self.update_charts)
        self.plot_button.pack(side='left', padx=10)
        
        self.chart_frame = tk.Frame(self.frame, bg="lightblue")
        self.chart_frame.pack(fill='both', expand=True, pady=10)
        
        self.load_data()
    
    def load_data(self):
        try:
            file_path = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
            if not os.path.exists(file_path):
                raise FileNotFoundError("Dataset file not found!")
            
            self.df = pd.read_csv(file_path)
            self.df['TotalCharges'] = pd.to_numeric(self.df['TotalCharges'], errors='coerce')
            self.df.drop(columns=['customerID'], inplace=True)
            self.df['Churn'] = self.df['Churn'].map({'No': 0, 'Yes': 1})
            self.df['ChurnStatus'] = self.df['Churn'].map({0: 'No', 1: 'Yes'})
            self.df['SeniorCitizen'] = self.df['SeniorCitizen'].map({0: 'Non-Senior', 1: 'Senior'})
            self.df = self.df.dropna(subset=['TotalCharges'])
            self.populate_menu()
        except Exception as e:
            handle_error(e, "Failed to load data")
    
    def populate_menu(self):
        numerical_fields = self.df.select_dtypes(include=['number']).columns.tolist()
        numerical_fields.remove("Churn")  # Remove Churn from menu
        self.field_menu['values'] = numerical_fields + ["SeniorCitizen"]
    
    def update_filters(self, event=None):
        for widget in self.filter_frame.winfo_children():
            widget.destroy()
        
        self.min_val = None
        self.max_val = None
        
        selected_field = self.selected_field.get()
        if selected_field in ["tenure", "MonthlyCharges"]:
            ttk.Label(self.filter_frame, text="Min Value:").pack(side='left', padx=(15,0))
            self.min_val = ttk.Entry(self.filter_frame, width=8)
            self.min_val.pack(side='left', padx=2)
            
            ttk.Label(self.filter_frame, text="Max Value:").pack(side='left', padx=(5,0))
            self.max_val = ttk.Entry(self.filter_frame, width=8)
            self.max_val.pack(side='left', padx=2)
            
            if selected_field == "tenure":
                ttk.Label(self.filter_frame, text="(Available range: 0-72 months)", foreground="blue").pack(side='left', padx=5)
            elif selected_field == "MonthlyCharges":
                ttk.Label(self.filter_frame, text="(Available range: 18-120)", foreground="blue").pack(side='left', padx=5)
    
    def update_charts(self, event=None):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        selected_field = self.selected_field.get() or "Churn"
        
        if self.df.empty:
            print("Dataframe is empty! Check data loading.")
            return
        
        df_filtered = self.df.copy()
        
        if selected_field in ["tenure", "MonthlyCharges"]:
            try:
                min_val = float(self.min_val.get()) if self.min_val and self.min_val.get() else df_filtered[selected_field].min()
                max_val = float(self.max_val.get()) if self.max_val and self.max_val.get() else df_filtered[selected_field].max()
                df_filtered = df_filtered[(df_filtered[selected_field] >= min_val) & (df_filtered[selected_field] <= max_val)]
            except ValueError:
                print("Invalid filter values. Using full range.")
        
        sns.set_style("whitegrid")
        fig, ax = plt.subplots(figsize=(16, 9))
        
        if selected_field == "SeniorCitizen":
            sns.countplot(x="SeniorCitizen", hue="ChurnStatus", data=df_filtered, ax=ax, palette={"No": "lightgreen", "Yes": "tomato"})
            ax.set_title("Churn Distribution by Senior Citizen Status")
            ax.set_xlabel("Senior Citizen Status")
            ax.set_ylabel("Count")
        elif selected_field == "Churn":
            sns.countplot(x="ChurnStatus", data=df_filtered, ax=ax, palette={"No": "lightgreen", "Yes": "tomato"})
            ax.set_title("Churn Count")
            ax.set_xlabel("Churn Status")
            ax.set_ylabel("Count")
        else:
            sns.barplot(x=df_filtered["ChurnStatus"], y=df_filtered[selected_field], ax=ax, 
                        palette={'No': 'lightgreen', 'Yes': 'tomato'})
            ax.set_title(f"{selected_field} by Churn")
            ax.set_xlabel("Churn Status")
            ax.set_ylabel(selected_field)
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.chart_frame.update_idletasks()
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
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Analytics Module")
    root.geometry("1400x800")
    app = AnalyticsApp(root)
    root.mainloop()
