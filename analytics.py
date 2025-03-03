import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import os

matplotlib.use("TkAgg")

def handle_error(e, message="Error occurred"):
    print(f"{message}: {str(e)}")

class AnalyticsApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent, bg="#f0f4f8", relief="flat")
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.create_widgets()
        self.load_data()
        self.show_default_pie_chart()
    
    def create_widgets(self):
        # Header Frame
        self.header_frame = tk.Frame(self.frame, bg="#ffffff", bd=1, relief="solid", highlightbackground="#d9e1e8", highlightthickness=1)
        self.header_frame.pack(fill='x', pady=(0, 10), padx=10)
        ttk.Label(self.header_frame, text="Customer Churn Analytics", font=("Helvetica", 14, "bold"), background="#ffffff").pack(pady=5)
        self.status_label = ttk.Label(self.header_frame, text="Select a field and click 'Update Chart' to explore churn data", font=("Helvetica", 10), foreground="#555555", background="#ffffff")
        self.status_label.pack(pady=5)

        # Menu Frame
        self.menu_frame = tk.Frame(self.frame, bg="#ffffff", bd=1, relief="solid", highlightbackground="#d9e1e8", highlightthickness=1)
        self.menu_frame.pack(fill='x', pady=10, padx=10)

        ttk.Label(self.menu_frame, text="Choose a Field:", font=("Helvetica", 12, "bold"), background="#ffffff").pack(side='left', padx=10, pady=10)
        
        # Combobox
        self.selected_field = tk.StringVar()
        style = ttk.Style()
        style.configure("TCombobox", font=("Helvetica", 11), padding=5)
        self.field_menu = ttk.Combobox(self.menu_frame, textvariable=self.selected_field, state="readonly", style="TCombobox")
        self.field_menu.pack(side='left', padx=10, pady=10)
        self.field_menu.insert(0, "Select a field...")
        self.field_menu.set("Select a field...")
        self.field_menu.bind("<<ComboboxSelected>>", self.on_field_select)
        
        # Filter Widgets
        self.min_label = ttk.Label(self.menu_frame, text="Min:", font=("Helvetica", 11), background="#ffffff")
        self.min_entry = ttk.Entry(self.menu_frame, width=8, font=("Helvetica", 11))
        self.max_label = ttk.Label(self.menu_frame, text="Max:", font=("Helvetica", 11), background="#ffffff")
        self.max_entry = ttk.Entry(self.menu_frame, width=8, font=("Helvetica", 11))
        
        # Button
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=6, background="#4a90e2", foreground="white")
        style.map("TButton", background=[("active", "#357abd")], foreground=[("active", "white")])
        self.plot_button = ttk.Button(self.menu_frame, text="Update Chart", command=self.update_charts, style="TButton")
        self.plot_button.pack(side='left', padx=10, pady=10)
        
        # Chart Frame
        self.chart_frame = tk.Frame(self.frame, bg="#ffffff", bd=1, relief="solid", highlightbackground="#d9e1e8", highlightthickness=1)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
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
        numerical_fields = self.df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        numerical_fields.remove("Churn")
        categorical_fields = self.df.select_dtypes(exclude=['float64', 'int64']).columns.tolist()
        all_fields = numerical_fields + categorical_fields
        self.field_menu['values'] = all_fields
    
    def on_field_select(self, event=None):
        selected_field = self.selected_field.get()
        if selected_field == "Select a field...":
            self.clear_filters()
            self.status_label.config(text="Select a field and click 'Update Chart' to explore churn data")
            return
        
        self.status_label.config(text=f"Selected {selected_field}. Click 'Update Chart' to view.")
        self.clear_filters()
        
        if selected_field in ["tenure", "MonthlyCharges", "TotalCharges"]:
            self.min_label.pack(side='left', padx=10, pady=10)
            self.min_entry.pack(side='left', padx=5, pady=10)
            self.max_label.pack(side='left', padx=10, pady=10)
            self.max_entry.pack(side='left', padx=5, pady=10)
            min_value = self.df[selected_field].min()
            max_value = self.df[selected_field].max()
            if hasattr(self, "range_label"):
                self.range_label.pack_forget()
            self.range_label = ttk.Label(self.menu_frame, text=f"Range: {min_value:.2f} to {max_value:.2f}", 
                                         font=("Helvetica", 10), foreground="#357abd", background="#ffffff")
            self.range_label.pack(side='left', padx=10, pady=10)
    
    def clear_filters(self):
        self.min_label.pack_forget()
        self.min_entry.pack_forget()
        self.max_label.pack_forget()
        self.max_entry.pack_forget()
        if hasattr(self, "range_label"):
            self.range_label.pack_forget()
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)
    
    def update_charts(self, show_feedback=True):
        selected_field = self.selected_field.get()
        if selected_field == "Select a field..." or not selected_field:
            messagebox.showwarning("Warning", "Please select a field to explore!")
            self.status_label.config(text="Select a field and click 'Update Chart' to explore churn data")
            return
        
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if self.df.empty:
            self.status_label.config(text="Error: No data available!")
            return
        
        df_filtered = self.df.copy()
        filter_applied = False
        
        if selected_field in ["tenure", "MonthlyCharges", "TotalCharges"]:
            min_val = self.min_entry.get()
            max_val = self.max_entry.get()
            try:
                min_value = float(self.df[selected_field].min())
                max_value = float(self.df[selected_field].max())
                
                if min_val:
                    min_val = float(min_val)
                    if min_val < min_value or min_val > max_value:
                        messagebox.showerror("Error", f"Min value out of range! Must be between {min_value} and {max_value}")
                        return
                    df_filtered = df_filtered[df_filtered[selected_field] >= min_val]
                    filter_applied = True
                
                if max_val:
                    max_val = float(max_val)
                    if max_val < min_value or max_val > max_value:
                        messagebox.showerror("Error", f"Max value out of range! Must be between {min_value} and {max_value}")
                        return
                    df_filtered = df_filtered[df_filtered[selected_field] <= max_val]
                    filter_applied = True
            except ValueError:
                messagebox.showerror("Error", "Invalid filter values! Please enter numbers.")
                return
        
        sns.set_style("whitegrid")
        fig, ax = plt.subplots(figsize=(12, 7), facecolor="#f0f4f8")
        fig.patch.set_facecolor("#f0f4f8")
        
        if selected_field in self.df.select_dtypes(include=['float64', 'int64']).columns.tolist():
            sns.histplot(df_filtered[df_filtered["Churn"] == 0][selected_field], bins=30, kde=True, ax=ax, color="#2ecc71", label="No Churn", alpha=0.6)
            sns.histplot(df_filtered[df_filtered["Churn"] == 1][selected_field], bins=30, kde=True, ax=ax, color="#e74c3c", label="Churn", alpha=0.6)
            ax.legend(fontsize=12, frameon=True, facecolor="#ffffff", edgecolor="#d9e1e8")
            ax.set_title(f"{selected_field} vs Churn", fontsize=16, pad=15, color="#333333")
            ax.set_xlabel(selected_field, fontsize=12, color="#333333")
            ax.set_ylabel("Frequency", fontsize=12, color="#333333")
            ax.tick_params(axis='both', labelsize=10, colors="#555555")
        else:
            sns.countplot(x=selected_field, hue="ChurnStatus", data=df_filtered, ax=ax, palette={"No": "#2ecc71", "Yes": "#e74c3c"})
            ax.set_title(f"Churn by {selected_field}", fontsize=16, pad=15, color="#333333")
            ax.set_xlabel(selected_field, fontsize=12, color="#333333")
            ax.set_ylabel("Count", fontsize=12, color="#333333")
            ax.tick_params(axis='both', labelsize=10, colors="#555555")
            # Removed rotation for horizontal labels
            ax.legend(title="Churn", fontsize=12, title_fontsize=13, frameon=True, facecolor="#ffffff", edgecolor="#d9e1e8")
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.status_label.config(text=f"Showing {selected_field}{' (filtered)' if filter_applied else ''}")
    
    def show_default_pie_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        fig, ax = plt.subplots(figsize=(6, 6), facecolor="#f0f4f8")
        fig.patch.set_facecolor("#f0f4f8")
        churn_counts = self.df['ChurnStatus'].value_counts()
        ax.pie(churn_counts, labels=churn_counts.index, autopct='%1.1f%%', colors=["#2ecc71", "#e74c3c"], startangle=90,
               textprops={'fontsize': 12, 'color': "#333333"}, wedgeprops={'edgecolor': "#ffffff", 'linewidth': 1.5})
        ax.set_title("Overall Churn Distribution", fontsize=16, pad=15, color="#333333")
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.status_label.config(text="Showing overall churn distribution")
    
    def show(self):
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.config(bg="#f0f4f8")
        self.frame.update_idletasks()
        self.show_default_pie_chart()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Analytics Dashboard")
    root.geometry("1400x800")
    root.configure(bg="#f0f4f8")
    app = AnalyticsApp(root)
    root.mainloop()