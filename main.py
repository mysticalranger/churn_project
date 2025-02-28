import tkinter as tk
from tkinter import ttk
from utils import handle_error
from controller import AppController
from login import LoginApp
from register import RegisterApp
from dashboard import DashboardApp

class MainApp:
    def __init__(self, root):
        self.root = root
        self.controller = AppController(root)
        # Register views using lazy loading:
        self.controller.register_view("login", LoginApp)
        self.controller.register_view("register", RegisterApp)
        self.controller.register_view("dashboard", DashboardApp)
        # Force reset the views so that only login is shown.
        self.controller.reset_all_views()

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            handle_error(e, "Application error")
            self.root.destroy()

if __name__ == "__main__": 
    root = tk.Tk()
    root.title("Churn Project")
    root.geometry("900x600")
    
    print("Starting application...")
    app = MainApp(root)
    print("MainApp initialized, starting mainloop")
    app.run()
