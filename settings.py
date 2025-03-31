import tkinter as tk
from tkinter import ttk, messagebox
from db import Database
from utils import handle_error
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
        
        self.translations = {
            "English": {
                "Application Settings": "Application Settings",
                "Theme": "Theme",
                "Light": "Light",
                "Dark": "Dark",
                "Language": "Language",
                "Save Application Settings": "Save Application Settings",
                "Success": "Success",
                "Theme changed to": "Theme changed to",
                "Language set to": "Language set to",
            },
            "Spanish": {
                "Application Settings": "Configuración de la aplicación",
                "Theme": "Tema",
                "Light": "Claro",
                "Dark": "Oscuro",
                "Language": "Idioma",
                "Save Application Settings": "Guardar configuración de la aplicación",
                "Success": "Éxito",
                "Theme changed to": "Tema cambiado a",
                "Language set to": "Idioma establecido en",
            },
            "Hindi": {
                "Application Settings": "एप्लिकेशन सेटिंग्स",
                "Theme": "थीम",
                "Light": "हल्का",
                "Dark": "गहरा",
                "Language": "भाषा",
                "Save Application Settings": "एप्लिकेशन सेटिंग्स सहेजें",
                "Success": "सफलता",
                "Theme changed to": "थीम बदलकर",
                "Language set to": "भाषा सेट की गई",
            },
            "Gujarati": {
                "Application Settings": "એપ્લિકેશન સેટિંગ્સ",
                "Theme": "થીમ",
                "Light": "હળવું",
                "Dark": "ઘાટું",
                "Language": "ભાષા",
                "Save Application Settings": "એપ્લિકેશન સેટિંગ્સ સાચવો",
                "Success": "સફળતા",
                "Theme changed to": "થીમ બદલાઈ",
                "Language set to": "ભાષા સેટ કરી",
            }
        }
        
        self.theme_var = tk.StringVar(value="light")
        self.lang_var = tk.StringVar(value="English")
        self.create_widgets()

    def create_widgets(self):
        """Create application settings widgets"""
        current_lang = self.lang_var.get()

        # Application Settings LabelFrame
        app_frame = ttk.LabelFrame(self.frame, text=self.translations[current_lang]["Application Settings"])
        app_frame.pack(fill='x', pady=10)

        # Theme selection
        theme_row = ttk.Frame(app_frame)
        theme_row.pack(fill='x', padx=5, pady=2)
        ttk.Label(theme_row, text=self.translations[current_lang]["Theme"] + ":").pack(side='left')
        ttk.Radiobutton(theme_row, text=self.translations[current_lang]["Light"], variable=self.theme_var, value="light").pack(side='left', padx=5)
        ttk.Radiobutton(theme_row, text=self.translations[current_lang]["Dark"], variable=self.theme_var, value="dark").pack(side='left', padx=5)

        # Language selection
        lang_row = ttk.Frame(app_frame)
        lang_row.pack(fill='x', padx=5, pady=2)
        ttk.Label(lang_row, text=self.translations[current_lang]["Language"] + ":").pack(side='left')
        lang_options = ["English", "Spanish", "Hindi", "Gujarati"]
        lang_menu = ttk.Combobox(lang_row, textvariable=self.lang_var, values=lang_options, state="readonly")
        lang_menu.pack(side='left', padx=5)
        lang_menu.set(current_lang)  # Show current language in menu box

        # Save button for application settings
        save_app_btn = ttk.Button(app_frame, text=self.translations[current_lang]["Save Application Settings"], command=self.save_app_settings)
        save_app_btn.pack(pady=10)

    def save_app_settings(self):
        """Save application settings (theme and language)"""
        theme = self.theme_var.get()
        language = self.lang_var.get()
        try:
            self.apply_theme(theme)
            self.update_language(language)
            msg = f"{self.translations[language]['Theme changed to']}: {theme}\n{self.translations[language]['Language set to']}: {language}"
            messagebox.showinfo(self.translations[language]["Success"], msg)
        except Exception as e:
            handle_error(e, "Failed to save application settings")
    
    def apply_theme(self, theme):
        """Apply the selected theme by updating ttk styles dynamically"""
        style = ttk.Style()
        if theme == "light":
            style.theme_use("clam")
            style.configure("TFrame", background="#f0f2f5")
            style.configure("TLabel", background="#f0f2f5", foreground="#333333")
            style.configure("TButton", background="#e4e6e9", foreground="#333333")
        elif theme == "dark":
            style.theme_use("clam")
            style.configure("TFrame", background="#333333")
            style.configure("TLabel", background="#333333", foreground="#f0f2f5")
            style.configure("TButton", background="#555555", foreground="#f0f2f5")
        self.theme_var.set(theme)  # Update theme selection
        for widget in self.parent.winfo_children():
            widget.configure(style=widget.winfo_class())

    def update_language(self, language):
        """Update all widget texts based on selected language"""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.create_widgets()

    def show(self):
        """Show settings module"""
        self.frame.pack(fill='both', expand=True)
        
    def hide(self):
        """Hide settings module"""
        self.frame.lower()  # Simplified hiding by lowering stacking order
