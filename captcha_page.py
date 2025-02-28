import tkinter as tk
from tkinter import ttk
from captcha.image import ImageCaptcha
import random
import string
from PIL import Image, ImageTk
from io import BytesIO

class CaptchaPage:
    def __init__(self, root, controller=None):
        print("CaptchaPage: Initialized")
        self.root = root
        self.controller = controller
        self.frame = tk.Frame(self.root, 
                bg="white", 
                bd=2, 
                relief="groove", 
                highlightthickness=2, 
                highlightbackground="grey",
                width=600,  # Set the width to match LoginApp
                height=300)  # Set the height to match LoginApp
        
        # Center the frame
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Force the frame to maintain its size
        self.frame.grid_propagate(False)
        self.frame.pack_propagate(False)

        self.captcha_text = ""
        self.captcha_image = None

        self.create_widgets()

    def create_widgets(self):
        font_family = "Helvetica"

        # Title Label
        title_label = tk.Label(
            self.frame,
            text="Please Verify CAPTCHA",
            font=(font_family, 16, "bold"),
            bg="white"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10), sticky="ew")

        # CAPTCHA Label
        self.captcha_label = tk.Label(self.frame, bg="white")
        self.captcha_label.grid(row=1, column=0, columnspan=2, padx=40, pady=(5, 5), sticky="ew")

        # CAPTCHA Entry
        self.captcha_entry = ttk.Entry(self.frame, width=20, font=(font_family, 12))
        self.captcha_entry.grid(row=2, column=0, columnspan=2, padx=40, pady=(5, 10), sticky="ew")

        # Verify CAPTCHA Button
        verify_captcha_btn = tk.Button(
            self.frame,
            text="Verify CAPTCHA",
            command=self.verify_captcha,
            font=(font_family, 12, "bold"),
            bg="black",
            fg="white",
            bd=0,
            padx=10,
            pady=2,
            activebackground="grey",
            activeforeground="white"
        )
        verify_captcha_btn.grid(row=3, column=0, columnspan=2, padx=40, pady=(10, 20), sticky="ew")

        # Generate initial CAPTCHA
        self.generate_captcha()

        # Configure column weights to ensure centering
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def generate_captcha(self):
        """Generate a new CAPTCHA image and text."""
        self.captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        image = ImageCaptcha(width=280, height=90)
        data = image.generate(self.captcha_text)
        image_data = data.read()  # Read the data from BytesIO
        self.captcha_image = ImageTk.PhotoImage(data=image_data)
        self.captcha_label.config(image=self.captcha_image)

    def verify_captcha(self):
        """Verify the CAPTCHA input."""
        if self.captcha_entry.get().strip().upper() == self.captcha_text:
            if self.controller:
                self.controller.on_captcha_success()
        else:
            self.captcha_label.config(text="Incorrect CAPTCHA. Please try again.")
            self.generate_captcha()

    def show(self):
        print("CaptchaPage: Show called")
        self.frame.tkraise()

    def hide(self):
        self.frame.grid_forget() 

    def destroy(self):
        """Destroy the CAPTCHA view."""
        print("CaptchaPage: Destroy called")
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()