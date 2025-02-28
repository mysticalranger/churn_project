import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import bcrypt

from db import Database
from utils import validate_email, validate_password, handle_error
from dashboard import DashboardApp
from captcha.image import ImageCaptcha
import random
import string
from io import BytesIO

class LoginApp:
    def __init__(self, root, controller=None, on_login_success=None, on_register=None, **kwargs):
        self.root = root
        self.controller = controller  # Store the controller
        
        # Keep old callbacks for backward compatibility
        self.on_login_success_callback = on_login_success
        self.on_register_callback = on_register
        
        self.db = Database(
            host="localhost", user="root", password="riyranagi007*", database="churn_db"
        )

        self.video_source = "background1.mp4"
        self.vid = cv2.VideoCapture(self.video_source)
        self.delay = 15

        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.frame = None
        self.create_widgets()
        self.update_video()

     

    def on_login_success(self):
        """Handle successful login with controller or callback"""
        if self.controller:
            self.controller.login_success()
        elif self.on_login_success_callback:
            self.on_login_success_callback()

    def on_register(self):
        """Navigate to register page using controller or callback"""
        if self.controller:
            self.controller.go_to_register()
        elif self.on_register_callback:
            self.on_register_callback()

    def on_forgot_password(self):
        """Navigate to forgot password page"""
        self.hide()
        # If using controller, this should be handled by controller
        # For now, keep the original implementation for backward compatibility
        from forgot_password import ForgotPasswordApp
        self.forgot_password_page = ForgotPasswordApp(self.root, self.show)

    def create_widgets(self):
        # Create a white background frame with a grey border using grid layout for precise alignment
        if self.frame is None:
            self.frame = tk.Frame(
                self.root, 
                bg="white", 
                bd=2, 
                relief="groove", 
                highlightthickness=2, 
                highlightbackground="grey"
            )

        font_family = "Helvetica"
        label_fg = "black"  # Text color for labels

        # Title Label
        title = tk.Label(
            self.frame,
            text="Churn Prediction System",
            font=(font_family, 20, "bold"),
            fg=label_fg,
            bg="white"
        )
        title.grid(row=0, column=0, columnspan=2, pady=(10, 15))

        # Email Label above entry
        email_label = tk.Label(
            self.frame,
            text="Email:",
            fg=label_fg,
            bg="white",
            font=(font_family, 12)
        )
        email_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=40, pady=(5,0))

        self.email_entry = ttk.Entry(
            self.frame, 
            width=40, 
            font=(font_family, 12)
        )
        self.email_entry.grid(row=2, column=0, columnspan=2, sticky="w", padx=40, pady=(0,5))

        # Password Label above entry
        password_label = tk.Label(
            self.frame,
            text="Password:",
            fg=label_fg,
            bg="white",
            font=(font_family, 12)
        )
        password_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=40, pady=(5,0))

        self.password_entry = ttk.Entry(
            self.frame, 
            show="*", 
            width=40, 
            font=(font_family, 12)
        )
        self.password_entry.grid(row=4, column=0, columnspan=2, sticky="w", padx=40, pady=(0,5))

        # Show Password Checkbutton on its own row (left-aligned)
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
        show_password_chk.grid(row=5, column=0, columnspan=2, sticky="w", padx=40, pady=(0,5))

        # Login Button with minimal bottom spacing
        self.login_btn = tk.Button(
            self.frame,
            text="Login",
            command=self.authenticate,
            font=(font_family, 12, "bold"),
            bg="black",
            fg="white",
            bd=0,
            padx=10,
            pady=2,
            activebackground="grey",
            activeforeground="white"
        )
        self.login_btn.grid(row=6, column=0, columnspan=2, pady=(5,2))
        self.login_btn.bind("<Enter>", self.on_enter)
        self.login_btn.bind("<Leave>", self.on_leave)

        # Error Message Label with minimal bottom spacing
        self.error_label = tk.Label(
            self.frame,
            text="",
            fg="red",
            font=(font_family, 10, "italic"),
            bg="white"
        )
        self.error_label.grid(row=7, column=0, columnspan=2, pady=(2,5))

        # Register Link Button – place at the bottom-right corner
        self.register_link = tk.Button(
            self.frame,
            text="Don't have an account? Register",
            command=self.on_register,  # Do not add parentheses here!
            font=(font_family, 10, "underline"),
            fg="blue",
            bg="white",
            bd=0,
            cursor="hand2"
        )
        self.register_link.grid(row=8, column=0, columnspan=2, pady=(0,10))

        # Forgot Password link – place at the bottom-left corner
        self.forgot_password_link = tk.Button(
            self.frame,
            text="Forgot Password?",
            command=self.on_forgot_password,
            font=(font_family, 10, "underline"),
            fg="blue",
            bg="white",
            bd=0,
            cursor="hand2"
        )
        self.forgot_password_link.grid(row=5, column=1,sticky="e", padx=40, pady=(0,5))

               
        

    def update_video(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image)
            self.bg_label.imgtk = imgtk
            self.bg_label.configure(image=imgtk)
        else:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.root.after(self.delay, self.update_video)

    def toggle_password_visibility(self):
        self.password_entry.config(
            show="" if self.show_password_var.get() else "*"
        )

    def authenticate(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not validate_email(email):
            self.show_error("Please enter a valid email address")
            return
        if not validate_password(password)[0]:
            self.show_error("Please enter a valid password")
            return

        try:
            if not self.db.connect():
                self.show_error("Database connection failed")
                return

            # In the authenticate method:
            query = "SELECT * FROM User WHERE email = %s"
            result = self.db.fetch_one(query, (email,))
            if result and bcrypt.checkpw(password.encode('utf-8'), result['password'].encode('utf-8')):
                if result['verified']:
                    print("Authentication successful, showing CAPTCHA")  # Debug statement
                    if self.controller:
                        self.controller.show_view("captcha")
                    else:
                        self.on_login_success()
                else:
                    self.show_error("Please verify your email before logging in")
            else:
                self.show_error("Invalid email or password")

        except Exception as e:
            self.show_error("Login failed")
            handle_error(e)
        finally:
            self.db.disconnect()

    def show_error(self, message):
        self.error_label.config(text=message)
        self.error_label.after(
            3000, lambda: self.error_label.config(text="")
        )  # Clear after 3 seconds

    def show(self):
        """Show the login view"""
        print("LoginApp: show called")
        if not self.frame:
            self.create_widgets()
        
        # Hide any lingering auxiliary widgets
        if hasattr(self, 'forgot_password_page'):
            if self.forgot_password_page and hasattr(self.forgot_password_page, 'hide'):
                self.forgot_password_page.hide()
        
        # Re-open the video if needed
        if not self.vid.isOpened():
            self.vid = cv2.VideoCapture(self.video_source)
        
        # Place the main login frame and bring to front
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        self.frame.tkraise()
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Optional: Move focus to the login frame so that no button gets auto-activated
        self.frame.focus_set()
        
        # Clear any pre-existing form data
        if hasattr(self, 'email_entry') and self.email_entry:
            self.email_entry.delete(0, 'end')
        if hasattr(self, 'password_entry') and self.password_entry:
            self.password_entry.delete(0, 'end')
        
        # Force update the UI
        self.root.update()

    def hide(self):
        """Hide the login view"""
        print(f"LoginApp: hide called")
        if self.frame and self.frame.winfo_exists():
            self.frame.place_forget()
        
        # Hide any other components
        if hasattr(self, 'forgot_password_page') and self.forgot_password_page:
            if hasattr(self.forgot_password_page, 'hide'):
                self.forgot_password_page.hide()

    def on_enter(self, event):
        self.login_btn.config(bg="grey", fg="white")

    def on_leave(self, event):
        self.login_btn.config(bg="black", fg="#FFFFFF")


if __name__ == "__main__":
    # For standalone testing
    def on_login_success():
        print("Logged in successfully!")
    
    def on_register():
        print("Navigate to registration.")
    
    root = tk.Tk()
    root.title("Churn Project")
    root.geometry("900x600")
    app = LoginApp(root, on_login_success=on_login_success, on_register=on_register)
    root.mainloop()

