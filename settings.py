import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from utils import handle_error, validate_email, validate_password
import logging

class SettingsApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent, padding="20")
        self.db = Database(
            host="localhost",
            user="root",
            password="",
            database="churn_db"
        )
        self.create_widgets()

    def create_widgets(self):
        """Create settings widgets"""
        # User Settings LabelFrame
        user_frame = ttk.LabelFrame(self.frame, text="User Settings")
        user_frame.pack(fill='x', pady=10)

        # Email field
        email_row = ttk.Frame(user_frame)
        email_row.pack(fill='x', padx=5, pady=2)
        ttk.Label(email_row, text="Email:").pack(side='left')
        self.email_entry = ttk.Entry(email_row, width=30)
        self.email_entry.pack(side='left', padx=5)

        # Password field
        password_row = ttk.Frame(user_frame)
        password_row.pack(fill='x', padx=5, pady=2)
        ttk.Label(password_row, text="Password:").pack(side='left')
        self.password_entry = ttk.Entry(password_row, show="*", width=30)
        self.password_entry.pack(side='left', padx=5)

        # Save changes button for user settings
        save_user_btn = ttk.Button(user_frame, text="Save User Settings", command=self.save_settings)
        save_user_btn.pack(pady=10)

        # Application Settings LabelFrame
        app_frame = ttk.LabelFrame(self.frame, text="Application Settings")
        app_frame.pack(fill='x', pady=10)

        # Theme selection (radio buttons only)
        theme_row = ttk.Frame(app_frame)
        theme_row.pack(fill='x', padx=5, pady=2)
        ttk.Label(theme_row, text="Theme:").pack(side='left')
        self.theme_var = tk.StringVar(value="light")
        ttk.Radiobutton(theme_row, text="Light", variable=self.theme_var, value="light").pack(side='left', padx=5)
        ttk.Radiobutton(theme_row, text="Dark", variable=self.theme_var, value="dark").pack(side='left', padx=5)

        # Save button for application settings
        save_app_btn = ttk.Button(app_frame, text="Save Application Settings", command=self.save_app_settings)
        save_app_btn.pack(pady=10)

    def save_settings(self):
        """Save user settings (email & password) in the database"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate inputs
        if not validate_email(email):
            messagebox.showwarning("Input Error", "Please enter a valid email")
            return

        valid, pass_error = validate_password(password)
        if not valid:
            messagebox.showwarning("Input Error", pass_error)
            return

        try:
            if not self.db.connect():
                messagebox.showerror("Error", "Database connection failed")
                return
            query = """
                UPDATE User 
                SET email = %s, password = %s
                WHERE user_id = %s
            """
            # TODO: Replace with the actual user_id from session data
            user_id = 1
            self.db.execute_query(query, (email, password, user_id))
            messagebox.showinfo("Success", "User settings saved successfully")
        except Exception as e:
            handle_error(e, "Failed to save user settings")
        finally:
            self.db.disconnect()
    
    def save_app_settings(self):
        """Save application settings including theme"""
        theme = self.theme_var.get()
        try:
            # Update the application style based on the selected theme
            self.apply_theme(theme)
            msg = f"Theme changed to: {theme}"
            messagebox.showinfo("Success", msg)
        except Exception as e:
            handle_error(e, "Failed to save application settings")
    
    def apply_theme(self, theme):
        """Apply the selected theme by updating ttk styles dynamically"""
        style = ttk.Style()
        if theme == "light":
            style.theme_use("clam")
            # Light theme styles
            style.configure("TFrame", background="#f0f2f5")
            style.configure("TLabel", background="#f0f2f5", foreground="#333333")
            style.configure("TButton", background="#e4e6e9", foreground="#333333")
        elif theme == "dark":
            style.theme_use("clam")
            # Dark theme styles. Adjust colors as needed.
            style.configure("TFrame", background="#333333")
            style.configure("TLabel", background="#333333", foreground="#f0f2f5")
            style.configure("TButton", background="#555555", foreground="#f0f2f5")
        # Force a refresh by updating the parent – this is a basic refresh approach.
        for widget in self.parent.winfo_children():
            widget.configure(style=widget.winfo_class())

    def show(self):
        """Show settings module"""
        self.frame.pack(fill='both', expand=True)
        
    def hide(self):
        """Hide settings module"""
        self.frame.pack_forget()
