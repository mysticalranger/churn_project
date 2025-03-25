import tkinter as tk
from tkinter import ttk, messagebox
from utils import validate_email, handle_error
# Remove direct generate_token import – token will be generated on the server.
from email_utils import send_email  # if needed elsewhere
from dotenv import load_dotenv
import os
import requests  # New import

load_dotenv()
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:5000")

class ForgotPasswordApp:
    def __init__(self, root, on_back_to_login):
        self.root = root
        self.on_back_to_login = on_back_to_login
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(
            self.root,
            bg="white",
            bd=2,
            relief="groove",
            highlightthickness=2,
            highlightbackground="grey"
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        font_family = "Helvetica"

        title = tk.Label(
            self.frame,
            text="Reset Password",
            font=(font_family, 20, "bold"),
            fg="black",
            bg="white"
        )
        title.grid(row=0, column=0, columnspan=2, pady=(10, 15))

        email_label = tk.Label(
            self.frame,
            text="Enter your email:",
            font=(font_family, 12),
            fg="black",
            bg="white"
        )
        email_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0))
        self.email_entry = ttk.Entry(self.frame, width=40, font=(font_family, 12))
        self.email_entry.grid(row=2, column=0, columnspan=2, sticky="w", padx=40, pady=(0, 10))

        self.reset_btn = tk.Button(
            self.frame,
            text="Reset Password",
            command=self.request_password_reset,
            font=(font_family, 12, "bold"),
            bg="black",
            fg="white",
            bd=0,
            padx=10,
            pady=2,
            activebackground="grey",
            activeforeground="white"
        )
        self.reset_btn.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        self.back_btn = tk.Button(
            self.frame,
            text="Back to Login",
            command=self.destroy_and_back,
            font=(font_family, 10, "underline"),
            fg="blue",
            bg="white",
            bd=0,
            cursor="hand2"
        )
        self.back_btn.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        self.message_label = tk.Label(
            self.frame,
            text="",
            font=(font_family, 10, "italic"),
            fg="red",
            bg="white"
        )
        self.message_label.grid(row=5, column=0, columnspan=2, pady=(2, 5))

    def request_password_reset(self):
        email = self.email_entry.get().strip()
        if not validate_email(email):
            self.show_message("Please enter a valid email address")
            return

        try:
            # Make a POST request to the server's /request_reset endpoint.
            # Updated to use a configurable URL and better error handling
            url = f"{PUBLIC_URL}/request_reset"
            print(f"Sending reset request to: {url}")  # Debug line
            
            response = requests.post(url, data={"email": email}, timeout=10)  # Added timeout
            response.raise_for_status()  # Raise an exception for non-200 responses
            
            if response.status_code == 200:
                # For testing, we display the token; in production, the server would send the email.
                result = response.text
                messagebox.showinfo("Reset Password", f"Password reset instructions have been sent to {email}\n{result}")
                self.frame.destroy()
                self.on_back_to_login()
            else:
                self.show_message(f"Failed to request password reset: {response.text}")
        except requests.RequestException as e:
            self.show_message(f"Connection failed: {str(e)}")
            handle_error(e)
        except Exception as e:
            self.show_message(f"Failed to request reset: {str(e)}")
            handle_error(e)

    def destroy_and_back(self):
        self.frame.destroy()
        self.on_back_to_login()

    def show_message(self, message):
        self.message_label.config(text=message)
        self.message_label.after(3000, lambda: self.message_label.config(text=""))

if __name__ == "__main__":
    def go_to_login():
        print("Back to login page.")
    root = tk.Tk()
    root.title("Forgot Password - Churn Project")
    root.geometry("400x400")
    app = ForgotPasswordApp(root, on_back_to_login=go_to_login)
    root.mainloop()