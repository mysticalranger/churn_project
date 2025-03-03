import tkinter as tk
from tkinter import ttk
from utils import handle_error
from churn1 import ChurnApp
from analytics import AnalyticsApp
import logging
from settings import SettingsApp
from customer_details import CustomerDetailsApp

class DashboardApp:
    def __init__(self, root, controller=None, **kwargs):
        self.root = root
        self.controller = controller
        self.frame = None
        self.content_frame = None
        self.create_widgets()
        self.hide()
        
        # Create a style for hover effects
        style = ttk.Style()
        style.configure("TButton", background="#e4e6e9")  # Default background
        self.hover_style = "Hover.TButton"
        style.configure(self.hover_style, background="#96a6b5")  # Hover background
        
    def on_hover_enter(self, event):
        btn = event.widget
        # Apply the hover style
        btn.configure(style=self.hover_style)

    def on_hover_leave(self, event):
        btn = event.widget
        # Revert to the default style
        btn.configure(style="TButton")

    def create_widgets(self):
        """Create an updated, modern dashboard layout with improved styling."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#333333", background="#f0f2f5")
        style.configure("Nav.TFrame", background="#e4e6e9")
        style.configure("Content.TFrame", background="#ffffff")
        style.configure("TButton", background="#e4e6e9")  # Default button background
        style.configure("Hover.TButton", background="#96a6b5")  # Hover button background
        
        # Main container frame using grid
        self.frame = ttk.Frame(self.root, style="TFrame", padding="20")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header frame spanning both columns
        header = ttk.Frame(self.frame, style="TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Churn Prediction Dashboard", style="Header.TLabel")
        title.grid(row=0, column=0, sticky="w", padx=10)

        logout_btn = ttk.Button(header, text="Logout", command=self.logout, style="TButton")
        logout_btn.grid(row=0, column=1, sticky="e", padx=10)

        # Navigation panel on the left (fixed width)
        nav_frame = ttk.Frame(self.frame, style="Nav.TFrame", padding="10")
        nav_frame.grid(row=1, column=0, sticky="ns", padx=(0, 10))
        nav_frame.grid_columnconfigure(0, weight=0)  # Prevent resizing
        nav_frame.config(width=200)  # Set a fixed width for the navigation panel

        # Content area on the right
        self.content_frame = ttk.Frame(self.frame, style="Content.TFrame", padding="20")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=10)

        # Add navigation buttons
        buttons = [
            ("Analytics", self.show_analytics),
            ("Customer Details", self.show_customer_details),
            ("Settings", self.show_settings),
            ("Churn Prediction", self.show_churn_prediction)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, command=command, style="TButton")
            btn.pack(fill="x", pady=5, padx=5)
            # Bind hover effects
            btn.bind("<Enter>", self.on_hover_enter)
            btn.bind("<Leave>", self.on_hover_leave)

        # Configure weights for responsiveness
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)  # Let content area expand
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        print("DashboardApp: create_widgets called")
        
        # Debug statements
        self.root.after(100, self.print_debug_info)
        
    def show(self):
        """Show dashboard"""
        print("DashboardApp: show called")
        self.frame.tkraise()
        self.frame.grid(sticky="nsew")
        
    def hide(self):
        """Hide dashboard"""
        print("Hiding dashboard")
        if self.frame and self.frame.winfo_exists():
            self.frame.grid_forget()
            
        # Hide any sub-components that might be visible
        for attr in ['churn_app', 'analytics_app', 'customer_details_app', 'setting_app']:
            if hasattr(self, attr) and getattr(self, attr) is not None:
                component = getattr(self, attr)
                if hasattr(component, 'hide'):
                    component.hide()
        
        # Also hide the content frame if it exists
        if hasattr(self, 'content_frame') and self.content_frame:
            self.content_frame.grid_forget()
        
    def logout(self):
        """Handler for logout"""
        print("Logout - showing login screen")
        if self.controller:
            self.controller.logout()
        else:
            print("Controller not available to handle logout")
            
    def show_analytics(self):
        """Show analytics module"""
        print("DashboardApp: show_analytics called")
        self.clear_content()

        try:
            import matplotlib
            matplotlib.use('TkAgg')

            # Ensure content_frame is visible and positioned in column 1
            self.content_frame.grid(row=1, column=1, sticky="nsew")  # Explicitly set row and column

            # Create and show AnalyticsApp
            self.analytics_app = AnalyticsApp(self.content_frame)
            self.analytics_app.show()

            # Ensure AnalyticsApp fills content_frame properly in column 0 of content_frame
            self.analytics_app.frame.grid(row=0, column=0, sticky="nsew")
            # Ensure frame expansion in content_frame
            self.content_frame.grid_rowconfigure(0, weight=1)
            self.content_frame.grid_columnconfigure(0, weight=1)

            # Update UI
            self.content_frame.update_idletasks()

            print("DashboardApp: AnalyticsApp show() completed")
            self.print_debug_info()
        except Exception as e:
            print(f"DashboardApp: Exception in show_analytics: {e}")
            import traceback
            traceback.print_exc()

    def show_customer_details(self):
        """Show customer details module"""
        self.clear_content()
        self.customer_details_app = CustomerDetailsApp(self.content_frame)
        self.customer_details_app.show()
        self.customer_details_app.frame.grid(row=0, column=0, sticky="nsew")  # Place in column 0 of content_frame
        self.content_frame.grid(row=1, column=1, sticky="nsew")  # Ensure content_frame stays in column 1
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()
        self.print_debug_info()

    def show_settings(self):
        """Show settings module"""
        self.clear_content()
        self.setting_app = SettingsApp(self.content_frame)
        self.setting_app.show()
        self.setting_app.frame.grid(row=0, column=0, sticky="nsew")  # Place in column 0 of content_frame
        self.content_frame.grid(row=1, column=1, sticky="nsew")  # Ensure content_frame stays in column 1
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()
        self.print_debug_info()

    def show_churn_prediction(self):
        """Show churn prediction module"""
        self.clear_content()
        self.churn_app = ChurnApp(self.content_frame)
        self.churn_app.show()
        self.churn_app.frame.grid(row=0, column=0, sticky="nsew")  # Place in column 0 of content_frame
        self.content_frame.grid(row=1, column=1, sticky="nsew")  # Ensure content_frame stays in column 1
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()
        self.print_debug_info()

    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Ensure content_frame is ready to receive new content in column 0 of its grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        print("DashboardApp: clear_content executed, content_frame children:", self.content_frame.winfo_children())
        
    def analytics_debug(self):
        """Helper function to debug analytics display issues"""
        try:
            print("\n--- DISPLAY DEBUG INFO ---")
            print(f"Content frame exists: {hasattr(self, 'content_frame')}")
            if hasattr(self, 'content_frame'):
                print(f"Content frame widget: {self.content_frame}")
                print(f"Content frame winfo_exists: {self.content_frame.winfo_exists()}")
                print(f"Content frame winfo_viewable: {self.content_frame.winfo_viewable()}")
                print(f"Content frame winfo_width: {self.content_frame.winfo_width()}")
                print(f"Content frame winfo_height: {self.content_frame.winfo_height()}")
                print(f"Content frame winfo_children: {len(self.content_frame.winfo_children())}")
                
            # Try to create a basic visible element
            test_label = tk.Label(self.content_frame, text="TEST VISIBILITY", bg="yellow")
            test_label.grid(row=2, column=0)
            
            # Try to create a colorful chart as a test
            test_frame = tk.Frame(self.content_frame, bg="red", width=400, height=300)
            test_frame.grid(row=3, column=0)
            test_frame.grid_propagate(False)  # Don't let it shrink
            
            for i in range(5):
                color = ["yellow", "green", "blue", "purple", "orange"][i]
                test_label = tk.Label(test_frame, text=f"TEST BAR {i}", bg=color, 
                                      width=20, height=2)
                test_label.pack(fill='x', expand=True)
            
            # Check if matplotlib is working properly
            import matplotlib
            print(f"Matplotlib backend: {matplotlib.get_backend()}")
            
            # Force update
            self.content_frame.update()
            print("--- DEBUG COMPLETE ---\n")
        except Exception as e:
            print(f"Debug error: {e}")
            
    def safe_hide_widget(self, widget):
        if widget and widget.winfo_exists():
            widget.grid_forget()  # Use grid_forget for consistency
        else:
            print("Widget does not exist or has already been destroyed.")

    def print_debug_info(self):
        print(f"Nav Frame - Width: {self.frame.winfo_width()}, Height: {self.frame.winfo_height()}")
        print(f"Content Frame - Width: {self.content_frame.winfo_width()}, Height: {self.content_frame.winfo_height()}")
        print(f"Root - Width: {self.root.winfo_width()}, Height: {self.root.winfo_height()}")

# Keep your main() function as is for testing
def main():
    # login_success = check_login()  # Original login check
    login_success = True  # Temporarily bypass login for testing

    if login_success:
        # Initialize and show the dashboard
        app = DashboardApp(root)

        app.show()
    else:
        print("Login failed. Please try again.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dashboard")
    root.geometry("1200x600")
    
    def dummy_logout():
        print("Logged out")
    
    app = DashboardApp(root, dummy_logout)
    app.show()
    root.mainloop()
