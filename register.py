import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from utils import validate_email, validate_password, handle_error
from email_utils import generate_token, send_email
import threading
from datetime import datetime, timedelta
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:5000")

class RegisterApp:
    def __init__(self, root, controller=None, **kwargs):
        self.root = root
        self.controller = controller  # Store the controller
        self.db = Database(
            host="localhost",      # Change to your DB host if different
            user="root",           # Change to your DB user
            password="riyranagi007*",  # Replace with your DB password
            database="churn_db"    # Replace with your DB name
        )
        self.frame = None
        self.create_widgets()

    def create_widgets(self):
        print("Debug: create_widgets called")
        self.frame = tk.Frame(
            self.root, 
            bg="white", 
            bd=2, 
            relief="groove", 
            highlightthickness=2, 
            highlightbackground="grey"
        )
        # Don't place the frame yet - let the show() method handle placement

        font_family = "Helvetica"
        label_fg = "black"

        # Title Label
        title = tk.Label(
            self.frame,
            text="Register",
            font=(font_family, 20, "bold"),
            fg=label_fg,
            bg="white"
        )
        title.grid(row=0, column=0, columnspan=2, pady=(10, 15))

        # Email
        email_label = tk.Label(
            self.frame,
            text="Email:",
            fg=label_fg,
            bg="white",
            font=(font_family, 12)
        )
        email_label.grid(row=1, column=0, sticky="w", padx=40, pady=(5,0))
        self.email_entry = ttk.Entry(self.frame, width=40, font=(font_family, 12))
        self.email_entry.grid(row=1, column=1, sticky="w", padx=40, pady=(5,0))

        # Password
        password_label = tk.Label(
            self.frame,
            text="Password:",
            fg=label_fg,
            bg="white",
            font=(font_family, 12)
        )
        password_label.grid(row=2, column=0, sticky="w", padx=40, pady=(5,0))
        self.password_entry = ttk.Entry(self.frame, show="*", width=40, font=(font_family, 12))
        self.password_entry.grid(row=2, column=1, sticky="w", padx=40, pady=(5,0))

        # Confirm Password
        confirm_label = tk.Label(
            self.frame,
            text="Confirm Password:",
            fg=label_fg,
            bg="white",
            font=(font_family, 12)
        )
        confirm_label.grid(row=3, column=0, sticky="w", padx=40, pady=(5,0))
        self.confirm_entry = ttk.Entry(self.frame, show="*", width=40, font=(font_family, 12))
        self.confirm_entry.grid(row=3, column=1, sticky="w", padx=40, pady=(5,0))

        # Show Password Checkbutton
        self.show_password_var = tk.BooleanVar(value=False)
        show_password_chk = tk.Checkbutton(
            self.frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            fg=label_fg,
            bg="white",
            bd=0,
            highlightthickness=0,
            font=(font_family, 10),
            selectcolor="white"
        )
        show_password_chk.grid(row=4, column=0, columnspan=2, sticky="w", padx=40, pady=(5,0))

        # Register Button
        self.register_btn = tk.Button(
            self.frame,
            text="Register",
            command=self.register,
            font=(font_family, 12, "bold"),
            bg="black",
            fg="white",
            bd=0,
            padx=10,
            pady=2,
            activebackground="grey",
            activeforeground="white"
        )
        self.register_btn.grid(row=5, column=0, columnspan=2, pady=(10,2))
        self.register_btn.bind("<Enter>", lambda e: self.register_btn.config(bg="grey"))
        self.register_btn.bind("<Leave>", lambda e: self.register_btn.config(bg="black"))
        
        # Go to Login Button
        self.login_link = tk.Button(
            self.frame,
            text="Already have an account? Login",
            command=self.destroy_and_back,  # Changed to use the new method
            font=(font_family, 10, "underline"),
            fg="blue",
            bg="white",
            bd=0,
            cursor="hand2"
        )
        self.login_link.grid(row=6, column=1, sticky="e", padx=10, pady=10)

        # Error Message Label
        self.error_label = tk.Label(
            self.frame,
            text="",
            fg="red",
            font=(font_family, 10, "italic"),
            bg="white"
        )
        self.error_label.grid(row=7, column=0, columnspan=2, pady=(2,5))

    def toggle_password_visibility(self):
        show = "" if self.show_password_var.get() else "*"
        self.password_entry.config(show=show)
        self.confirm_entry.config(show=show)

    def register(self):
        print("Debug: register button clicked")  # Debug statement
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_entry.get().strip()

        if not validate_email(email):
            self.show_error("Please enter a valid email address")
            return

        valid_pass, msg = validate_password(password)
        if not valid_pass:
            self.show_error(msg or "Please enter a valid password")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match")
            return

        # Start registration in a separate thread to prevent UI blocking.
        threading.Thread(target=self._do_register, args=(email, password), daemon=True).start()

    def _do_register(self, email, password):
        try:
            # Attempt to connect to the database
            if not self.db.connect():
                self.root.after(0, lambda: self.show_error("Database connection failed."))
                return

            # Check if the email is already registered
            check_query = "SELECT * FROM User WHERE email = %s"
            user_exists = self.db.fetch_one(check_query, (email,))
            if user_exists:
                self.root.after(0, lambda: self.show_error("A user with that email already exists."))
                return

            # Generate a verification token and expiration time
            token = generate_token()
            expiration_time = datetime.utcnow() + timedelta(hours=24)

            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Insert new user (unverified) along with verification token and expiration time
            insert_query = (
                "INSERT INTO User (email, password, role, verified, verification_token, token_expiration) "
                "VALUES (%s, %s, 'user', FALSE, %s, %s)"
            )
            self.db.execute_query(insert_query, (email, hashed_password, token, expiration_time))

            # Send verification email
            try:
                verification_link = f"{os.environ.get('PUBLIC_URL')}/verify?token={token}"
                print(f"Constructing verification link with URL: {os.environ.get('PUBLIC_URL')}")
                email_subject = "Please verify your email address"
                email_body = f"Click the following link to verify your email:\n{verification_link}"
                send_email(email, email_subject, email_body)
            except Exception as e:
                self.root.after(0, lambda: self.show_error("Failed to send verification email. Please try again later."))
                handle_error(e)
                return  # Stop further processing if email sending fails

            # Schedule post-registration steps on the main thread
            self.root.after(0, lambda: self._post_registration(email))

        except Exception as e:
            print("Debug: Exception in _do_register:", e)
            self.root.after(0, lambda: self.show_error("Registration failed. Please try again."))
            handle_error(e)
        finally:
            self.db.disconnect()
            print("Debug: DB disconnected")

    def _post_registration(self, email):
        print("Debug: _post_registration called")
        messagebox.showinfo(
            "Registration Successful",
            f"Your account has been created.\nA verification email has been sent to {email}.\nPlease check your email to verify your account."
        )
        print("Debug: messagebox closed, calling destroy_and_back")
        self.destroy_and_back()

    def destroy_and_back(self):
        if self.controller:
            self.controller.go_to_login()
        else:
            # Fallback for standalone testing
            if self.frame and self.frame.winfo_exists():
                self.frame.destroy()
            self.frame = None
            if hasattr(self, 'on_back_to_login'):
                self.on_back_to_login()

    def show(self):
        """Show the register view"""
        if not self.frame:
            self.create_widgets()
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

    def hide(self):
        """Hide the register view"""
        if self.frame and self.frame.winfo_exists():
            self.frame.place_forget()

    def show_error(self, message):
        self.error_label.config(text=message)
        self.error_label.after(3000, lambda: self.error_label.config(text=""))

if __name__ == "__main__":
    print("Debug: Running register.py as __main__")  # Debug statement

    

    def go_to_login():
         print("Debug: go_to_login called")
        

    root = tk.Tk()
    root.title("Register - Churn Project")
    root.geometry("400x400")
    app = RegisterApp(root,on_back_to_login=go_to_login)
    print("Debug: RegisterApp instance created")  # Debug statement
    root.mainloop()