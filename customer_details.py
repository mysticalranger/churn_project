import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from utils import handle_error, format_currency
import logging

class CustomerDetailsApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        # Add a border for debugging so the frame is visible
        self.frame.config(borderwidth=2, relief="solid")
        
        self.db = Database(
            host="localhost",
            user="root",
            password="riyranagi007*",
            database="churn_db"
        )
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Top section unified style (for Search + Customer Information)
        style.configure("Top.TFrame", background="#F0F8FF")  # Light pastel (AliceBlue)
        style.configure("Top.TLabel", background="#F0F8FF", font=("TkDefaultFont", 10))
        style.configure("Top.TLabelframe", background="#F0F8FF", borderwidth=2)
        style.configure("Top.TLabelframe.Label", background="#F0F8FF", font=("TkDefaultFont", 10, "bold"))
        
        # Bottom section style (remains white)
        style.configure("Details.TFrame", background="#FFFFFF")
        style.configure("Details.TLabelframe", background="#FFFFFF")
        
        # Custom style for Entry widgets
        style.configure("Custom.TEntry", padding=3)
    
    def create_widgets(self):
        """Create customer details widgets with separate sections."""
        # Place the main frame in the parent using grid
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Container for scrollable content (includes both top and bottom sections)
        details_container = ttk.Frame(self.frame, style="Details.TFrame")
        details_container.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        scroll_frame = ttk.Frame(details_container)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        details_container.rowconfigure(0, weight=1)
        details_container.columnconfigure(0, weight=1)
        scroll_frame.rowconfigure(0, weight=1)
        scroll_frame.columnconfigure(0, weight=1)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(scroll_frame, background="#FFFFFF")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscroll = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.canvas.yview)
        vscroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=vscroll.set)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))
        
        # Internal frame inside canvas
        self.details_frame = ttk.Frame(self.canvas, style="Details.TFrame")
        self.details_window = self.canvas.create_window((0, 0), window=self.details_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.details_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # -------------------------------
        # TOP SECTION: Search + Customer Information (Unified Look)
        self.top_section = ttk.Frame(self.details_frame, style="Top.TFrame")
        self.top_section.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Search Frame
        search_frame = ttk.Frame(self.top_section, padding="10", style="Top.TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(search_frame, text="Search Customer (by ID):", style="Top.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=30, style="Custom.TEntry")
        self.search_entry.grid(row=0, column=1, padx=(0, 5))
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_customer)
        search_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Customer Information Panel
        info_frame = ttk.Labelframe(self.top_section, text="Customer Information", padding="10", style="Top.TLabelframe")
        info_frame.grid(row=1, column=0, sticky="ew")
        self.entries = {}
        # Define a list of tuples: (database_field_key, display_label)
        fields = [
            ("customerID", "Customer ID"),
            ("gender", "Gender"),
            ("tenure", "Tenure"),
            ("MonthlyCharges", "Monthly Charges")
        ]
        for idx, (key, label_text) in enumerate(fields):
            r, c = divmod(idx, 2)
            ttk.Label(info_frame, text=f"{label_text}:", style="Top.TLabel").grid(row=r, column=c*2, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(info_frame, width=20, style="Custom.TEntry")
            entry.grid(row=r, column=c*2+1, sticky="w", padx=5, pady=5)
            self.entries[key] = entry
        
        # -------------------------------
        # BOTTOM SECTION: Vertically Stacked Panels
        bottom_section = ttk.Frame(self.details_frame, style="Details.TFrame")
        bottom_section.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        bottom_section.columnconfigure(0, weight=1)
        
        # Service Churn Summary Frame with Load Button
        service_frame = ttk.Labelframe(bottom_section, text="Service Churn Summary", padding=10, style="Details.TLabelframe")
        service_frame.grid(row=0, column=0, sticky="ew", pady=5)
        btn_load_service = ttk.Button(service_frame, text="Load Service Churn Summary", command=self.load_service_churn)
        btn_load_service.pack(side="top", fill="x", pady=(0, 5))
        self.service_tree = ttk.Treeview(service_frame, columns=("Internet Service", "Churn Count"), show="headings")
        self.service_tree.heading("Internet Service", text="Internet Service")
        self.service_tree.heading("Churn Count", text="Churn Count")
        self.service_tree.column("Internet Service", anchor="w", width=150)
        self.service_tree.column("Churn Count", anchor="center", width=80)
        self.service_tree.pack(fill="both", expand=True)
        
        # Top 10 Churned Customers Frame with Load Button
        top_customers_frame = ttk.Labelframe(bottom_section, text="Top 10 Churned Customers", padding=10, style="Details.TLabelframe")
        top_customers_frame.grid(row=1, column=0, sticky="ew", pady=5)
        btn_load_top = ttk.Button(top_customers_frame, text="Load Top 10 Churned Customers", command=self.load_top_churn_customers)
        btn_load_top.pack(side="top", fill="x", pady=(0, 5))
        self.top_tree = ttk.Treeview(top_customers_frame, columns=("Customer ID", "Total Charges"), show="headings")
        self.top_tree.heading("Customer ID", text="Customer ID")
        self.top_tree.heading("Total Charges", text="Total Charges")
        self.top_tree.column("Customer ID", anchor="w", width=150)
        self.top_tree.column("Total Charges", anchor="e", width=120)
        self.top_tree.pack(fill="both", expand=True)
        
        # Transactions Frame (Commented Out)
        # trans_frame = ttk.Labelframe(bottom_section, text="Transactions", padding=10, style="Details.TLabelframe")
        # trans_frame.grid(row=2, column=0, sticky="ew", pady=5)
        # self.trans_tree = ttk.Treeview(trans_frame, columns=("Amount",), show="headings")
        # self.trans_tree.heading("Amount", text="Amount")
        # self.trans_tree.column("Amount", anchor="e", width=120)
        # self.trans_tree.pack(fill="both", expand=True)
        
        # Churn Prediction Frame (Commented Out)
        # prediction_frame = ttk.Labelframe(bottom_section, text="Churn Prediction", padding=10, style="Details.TLabelframe")
        # prediction_frame.grid(row=3, column=0, sticky="ew", pady=5)
        # self.churn_label = ttk.Label(prediction_frame, text="No prediction available", anchor="center")
        # self.churn_label.pack(fill="both", expand=True)
    
    def on_canvas_configure(self, event):
        """
        Adjust the details_frame inside the canvas:
         - If the details_frame needs less width than available, center it.
         - Otherwise, make it fit the canvas width.
        """
        canvas_width = event.width
        max_width = 800  # Adjust this value as needed.
        self.details_frame.update_idletasks()
        req_width = self.details_frame.winfo_reqwidth()
        
        if req_width < canvas_width:
            desired_width = req_width if req_width <= max_width else max_width
        else:
            desired_width = canvas_width

        self.canvas.itemconfig(self.details_window, width=desired_width)
        x_offset = (canvas_width - desired_width) // 2
        self.canvas.coords(self.details_window, x_offset, 0)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    
    def search_customer(self):
        """Search for customer details and update panels"""
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a customer ID")
            return
        try:
            if not self.db.connect():
                messagebox.showerror("Error", "Database connection failed")
                return
            query = """
                SELECT * FROM Customer 
                WHERE customerID LIKE %s
            """
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute(query, (f"%{search_term}%",))
            customer = cursor.fetchone()
            cursor.close()
            if customer:
                self.display_customer(customer)
                # self.load_transactions(customer['customerID'])  # Commented Out
                # self.load_churn_prediction(customer['customerID'])  # Commented Out
            else:
                messagebox.showinfo("Not Found", "No matching customer found")
        except Exception as e:
            handle_error(e, "Search failed")
        finally:
            self.db.disconnect()
    
    def display_customer(self, customer):
        """Display selected customer details (only key fields)"""
        for field, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(customer.get(field, "")))
    
    # def load_transactions(self, customerID):  # Commented Out
    #     """Load customer transactions (only amount)"""
    #     try:
    #         query = """
    #             SELECT amount 
    #             FROM Transaction 
    #             WHERE customerID = %s
    #         """
    #         cursor = self.db.connection.cursor()
    #         cursor.execute(query, (customerID,))
    #         transactions = cursor.fetchall()
    #         cursor.close()
    #         self.trans_tree.delete(*self.trans_tree.get_children())
    #         for trans in transactions:
    #             self.trans_tree.insert("", "end", values=(format_currency(trans[0]),))
    #     except Exception as e:
    #         handle_error(e, "Failed to load transactions")
            
    # def load_churn_prediction(self, customerID):  # Commented Out
    #     """Load churn prediction for a specific customer"""
    #     try:
    #         query = """
    #             SELECT prediction, probability 
    #             FROM ChurnPrediction 
    #             WHERE customerID = %s
    #             LIMIT 1
    #         """
    #         cursor = self.db.connection.cursor()
    #         cursor.execute(query, (customerID,))
    #         prediction = cursor.fetchone()
    #         cursor.close()
    #         if prediction:
    #             self.churn_label.config(
    #                 text=f"Prediction: {prediction[0]} | Probability: {prediction[1]:.2%}"
    #             )
    #         else:
    #             self.churn_label.config(text="No prediction available")
    #     except Exception as e:
    #         handle_error(e, "Failed to load churn prediction")
            
    def load_service_churn(self):
        """Load and display service churn summary by InternetService for churned customers"""
        try:
            if not self.db.connect():
                messagebox.showerror("Error", "Database connection failed")
                return
            query = """
                SELECT InternetService, COUNT(*) AS churn_count
                FROM Customer 
                WHERE Churn = 'Yes'
                GROUP BY InternetService
                ORDER BY churn_count DESC
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            self.service_tree.delete(*self.service_tree.get_children())
            for row in results:
                self.service_tree.insert("", "end", values=(row[0], row[1]))
        except Exception as e:
            handle_error(e, "Failed to load service churn summary")
        finally:
            self.db.disconnect()
            
    def load_top_churn_customers(self):
        """Load and display top 10 customers (by Total Charges) among those who churned"""
        try:
            if not self.db.connect():
                messagebox.showerror("Error", "Database connection failed")
                return

            query = """
                SELECT customerID, TotalCharges 
                FROM Customer 
                WHERE Churn = 'Yes'
                ORDER BY TotalCharges DESC
                LIMIT 10
            """
            cursor = self.db.connection.cursor()
            cursor.execute(query)
            top_customers = cursor.fetchall()
            cursor.close()

            # Debug: output the query result
            print("Top customers query result (before insertion):", top_customers)

            # Clear existing items
            children_before = self.top_tree.get_children()
            print("Existing children before clearing:", children_before)
            self.top_tree.delete(*children_before)

            # Insert each customer row into the treeview.
            for cust in top_customers:
                try:
                    total_charges = float(cust[1])
                except (TypeError, ValueError):
                    total_charges = 0.0
                formatted_charges = format_currency(total_charges)
                self.top_tree.insert("", "end", values=(cust[0], formatted_charges))
                print("Inserted row:", (cust[0], formatted_charges))

            # Debug: print the children now inserted
            new_children = self.top_tree.get_children()
            print("Treeview children after insertion:", new_children)

            # Reconfigure display columns
            self.top_tree["displaycolumns"] = ("Customer ID", "Total Charges")
            self.top_tree.column("Customer ID", width=150, anchor="w")
            self.top_tree.column("Total Charges", width=120, anchor="e")

            # Force refresh: update and scroll to the top
            self.top_tree.update_idletasks()
            self.top_tree.yview_moveto(0)
            if new_children:
                self.top_tree.see(new_children[0])
            else:
                print("Warning: No items were inserted into the treeview.")

        except Exception as e:
            handle_error(e, "Failed to load top churn customers")
        finally:
            self.db.disconnect()
            
    def show(self):
        """Show customer details module by ensuring the frame fills the parent's assigned space."""
        self.frame.grid(row=0, column=0, sticky="nsew")
        
    def hide(self):
        """Hide customer details module"""
        self.frame.grid_forget()
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Customer Details")
    root.geometry("1000x600")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    app = CustomerDetailsApp(root)
    app.show()
    root.mainloop()
