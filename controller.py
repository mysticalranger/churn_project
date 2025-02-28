from captcha_page import CaptchaPage

class AppController:
    def __init__(self, root):
        self.root = root
        self.current_view = None
        self.views = {}  # Will store view factories or instances
        self.logged_in = False
        self.initializing = False
        # Register the CAPTCHA view
        self.register_view("captcha", CaptchaPage)

    def register_view(self, name, view_class, *args, **kwargs):
        """Store a factory that instantiates the view lazily."""
        print(f"Registering view: {name}")
        # Instead of instantiating immediately, store a lambda factory.
        self.views[name] = lambda: view_class(self.root, controller=self, *args, **kwargs)

    def get_view(self, name):
        """Return an instance of the view; instantiate it if necessary."""
        v = self.views.get(name)
        if callable(v):
            # Not yet instantiated, so call the factory to get the instance.
            instance = v()
            self.views[name] = instance  # Replace factory with actual instance.
            return instance
        return v

    def reset_all_views(self):
        """Force reset all views to ensure clean state"""
        print("Resetting all views")
        # Hide all views explicitly
        for name, view in self.views.items():
            # If the view is a factory (callable), skip it because it is not instantiated yet.
            if not callable(view) and hasattr(view, 'hide'):
                print(f"Forcing hide of {name}")
                view.hide()
        self.current_view = None
        self.logged_in = False

        if "login" in self.views:
            self.show_view("login")
        self.root.update()

    def show_view(self, name):
        """Switch to a pre-initialized view (or instantiate it lazily)."""
        # Ensure we obtain the instance.
        view_instance = self.get_view(name)
        
        # Skip showing the same view twice in a row
        if self.current_view and self.current_view.__class__.__name__ == view_instance.__class__.__name__:
            print(f"Skipping redundant navigation to {name} - already showing")
            return

        print(f"Attempting to show view: {name}")

        # Prevent showing dashboard if not logged in
        if name == "dashboard" and not self.logged_in:
            print("Blocked unauthorized access to dashboard")
            name = "login"
            view_instance = self.get_view("login")

        # Hide current view first if it exists
        if self.current_view:
            print(f"Hiding current view: {self.current_view.__class__.__name__}")
            self.current_view.hide()
            self.root.update()
        
        print(f"Showing view: {name}")
        view_instance.show()
        self.current_view = view_instance
        print(f"Current view is now: {name}")

    def login_success(self):
        """Handler for successful login"""
        print("Login success - showing dashboard")
        self.logged_in = True
        # Register the CAPTCHA view
        
        self.show_view("dashboard")

    def logout(self):
        """Handler for logout"""
        print("Logout - showing login screen")
        self.logged_in = False
        self.show_view("login")

    def go_to_register(self):
        """Navigate to register page"""
        self.show_view("register")

    def go_to_login(self):
        """Navigate to login page"""
        self.show_view("login")

    def show_view(self, name):
        """Show the specified view."""
        if self.current_view:
            self.current_view.hide()
        self.current_view = self.get_view(name)
        if self.current_view:
            self.current_view.show()

    def on_captcha_success(self):
        """Handle successful CAPTCHA verification."""
        print("CAPTCHA verified successfully!")
        # Destroy the CAPTCHA view to prevent it from being shown again
        if "captcha" in self.views:
            captcha_view = self.views["captcha"]
            if hasattr(captcha_view, 'destroy'):
                captcha_view.destroy()
            del self.views["captcha"]
        
        # Re-register the CAPTCHA view for future use
        self.register_view("captcha", CaptchaPage)
        
        # Update current_view to None before showing the next view
        self.current_view = None
        
        # Proceed to the next step, e.g., show the dashboard
        self.show_view("dashboard")

        