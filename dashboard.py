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
        self.controller = controller  # Store the controller
        self.frame = None
        self.content_frame = None
        self.create_widgets()
        # Ensure the dashboard is hidden at creation
        self.hide()
        
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def interpolate_color(self, start_rgb, end_rgb, factor):
        return tuple(int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * factor) for i in range(3))

    def animate_hover_in(self, btn, start_color, end_color, steps=10, delay=20, current=0):
        if current > steps:
            return
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        factor = current / steps
        current_rgb = self.interpolate_color(start_rgb, end_rgb, factor)
        btn.configure(background=self.rgb_to_hex(current_rgb))
        btn.after(delay, lambda: self.animate_hover_in(btn, start_color, end_color, steps, delay, current+1))

    def animate_hover_out(self, btn, start_color, end_color, steps=10, delay=20, current=0):
        if current > steps:
            return
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        factor = current / steps
        current_rgb = self.interpolate_color(start_rgb, end_rgb, factor)
        btn.configure(background=self.rgb_to_hex(current_rgb))
        btn.after(delay, lambda: self.animate_hover_out(btn, start_color, end_color, steps, delay, current+1))

    def on_hover_enter(self, event):
        btn = event.widget
        # Animate from normal color to a darker shade
        self.animate_hover_in(btn, "#e4e6e9", "#96a6b5")  # adjust colors as desired

    def on_hover_leave(self, event):
        btn = event.widget
        # Animate back from darkened color to normal color
        self.animate_hover_out(btn, "#96a6b5", "#e4e6e9")

    def create_widgets(self):
        """Create an updated, modern dashboard layout with improved styling."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#333333", background="#f0f2f5")
        style.configure("Nav.TFrame", background="#e4e6e9")
        style.configure("Content.TFrame", background="#ffffff")
        
        # Main container frame using grid
        self.frame = ttk.Frame(self.root, style="TFrame", padding="20")
        self.frame.grid(sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header frame spanning two columns
        header = ttk.Frame(self.frame, style="TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Churn Prediction Dashboard", style="Header.TLabel")
        title.grid(row=0, column=0, sticky="w")

        logout_btn = ttk.Button(header, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1, sticky="e")

        # Navigation panel on the left with its own style
        nav_frame = ttk.Frame(self.frame, style="Nav.TFrame", padding="10")
        nav_frame.grid(row=1, column=0, sticky="ns", padx=(0,10))

        buttons = [
            ("Analytics", self.show_analytics),
            ("Customer Details", self.show_customer_details),
            ("Settings", self.show_settings),
            ("Churn Prediction", self.show_churn_prediction)
        ]

        # Create the content area BEFORE initializing modules
        self.content_frame = ttk.Frame(self.frame, style="Content.TFrame", padding="20")
        self.content_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        # Fix: configure grid on self.frame, not DashboardApp (self)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        for i, (text, command) in enumerate(buttons):
            # Using tk.Button for animation flexibility
            btn = tk.Button(nav_frame, text=text, width=20, command=command, bg="#e4e6e9", relief="raised", borderwidth=1, font=("Helvetica", 10))
            btn.grid(row=i, column=1, pady=8, sticky="w")
            btn.bind("<Enter>", self.on_hover_enter)
            btn.bind("<Leave>", self.on_hover_leave)

        print("DashboardApp: create_widgets called")
        
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
        """Handle logout"""
        try:
            for attr in ['churn_app', 'analytics_app', 'customer_details_app', 'setting_app']:
                component = getattr(self, attr, None)
                if component and hasattr(component, 'hide'):
                    # Only hide if the frame still exists.
                    if component.frame and component.frame.winfo_exists():
                        component.hide()
            # Call the logout routine from controller or on_logout
            if self.controller:
                self.controller.logout()
            elif hasattr(self, 'on_logout'):
                self.on_logout()
        except Exception as e:
            handle_error(e, "Logout failed")
            
    def show_analytics(self):
        """Show analytics module"""
        print("DashboardApp: show_analytics called")
        self.clear_content()

        try:
            import matplotlib
            matplotlib.use('TkAgg')

            # Ensure content_frame is visible
            self.content_frame.grid(sticky="nsew")

            # Create and show AnalyticsApp
            self.analytics_app = AnalyticsApp(self.content_frame)
            self.analytics_app.show()

            # Ensure AnalyticsApp fills content_frame properly
            self.analytics_app.frame.grid(row=0, column=1, sticky="nsew")
            # Ensure frame expansion
            self.content_frame.grid_rowconfigure(0, weight=1)
            self.content_frame.grid_columnconfigure(1, weight=1)

            # Update UI
            self.content_frame.update_idletasks()

            print("DashboardApp: AnalyticsApp show() completed")
        except Exception as e:
            print(f"DashboardApp: Exception in show_analytics: {e}")
            import traceback
            traceback.print_exc()

        
    def show_customer_details(self):
        """Show customer details module"""
        self.clear_content()
        self.customer_details_app = CustomerDetailsApp(self.content_frame)
        self.customer_details_app.show()
        self.customer_details_app.frame.grid(row=0, column=0, sticky="nsew")
        # Ensure frame expansion
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()

        
    def show_settings(self):
        """Show settings module"""
        self.clear_content()
        self.setting_app = SettingsApp(self.content_frame)
        self.setting_app.show()
        self.setting_app.frame.grid(row=0, column=0, sticky="nsew")
        # Ensure frame expansion
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()

        
    def show_churn_prediction(self):
        """Show churn prediction module"""
        self.clear_content()
        self.churn_app = ChurnApp(self.content_frame)
        self.churn_app.show()
        self.churn_app.frame.grid(row=0, column=0, sticky="nsew")
        # Ensure frame expansion
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()

        
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reconfigure the content_frame with a minimum size
        self.content_frame.config(width=800, height=500)
        self.content_frame.grid_propagate(False)  # Prevent grid from changing the size
        
        # Ensure row/column configuration allows expansion
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
            
    def hide_widget(self, widget):
        if widget and widget.winfo_exists():
            widget.grid_forget()
        else:
            print("Widget does not exist or has already been destroyed.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dashboard")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    def dummy_logout():
        print("Logged out")
    
    app = DashboardApp(root, dummy_logout)
    app.show()
    root.mainloop()
