"""
Main application class managing windows and authentication flow.
"""
import logging
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from src.auth.login_window import LoginWindow
from src.auth.signup_window import SignupWindow
from src.ui.main_dashboard import MainDashboard
from config import Config

logger = logging.getLogger(__name__)


class PersonalInfoManager(QWidget):
    """
    Main application window that manages authentication and dashboard.
    """
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Create stacked widget to switch between windows
        self.stacked_widget = QStackedWidget()
        
        # Create authentication windows
        self.login_window = LoginWindow()
        self.signup_window = SignupWindow()
        
        # Connect signals
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.switch_to_signup.connect(self.show_signup)
        self.signup_window.switch_to_login.connect(self.show_login)
        
        # Add windows to stack
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.signup_window)
        
        # Set layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
        # Show login window first
        self.show_login()
        
        logger.info("Application initialized")
    
    def show_login(self):
        """Show the login window."""
        self.signup_window.clear_form()
        self.stacked_widget.setCurrentWidget(self.login_window)
        logger.debug("Switched to login window")
    
    def show_signup(self):
        """Show the signup window."""
        self.login_window.clear_form()
        self.stacked_widget.setCurrentWidget(self.signup_window)
        logger.debug("Switched to signup window")
    
    def on_login_success(self, user_data: dict):
        """
        Handle successful login.
        
        Args:
            user_data: Dictionary containing user information
        """
        self.current_user = user_data
        logger.info(f"User logged in: {user_data['username']}")
        
        # Create and show main dashboard
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show the main dashboard."""
        # Remove authentication windows
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
        
        # Create and add dashboard
        self.dashboard = MainDashboard(self.current_user)
        self.dashboard.logout_requested.connect(self.on_logout)
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.setCurrentWidget(self.dashboard)
        
        # Resize window for dashboard
        self.setGeometry(100, 100, 1200, 700)
        
        logger.info("Dashboard displayed")
    
    def on_logout(self):
        """Handle user logout."""
        logger.info(f"User logged out: {self.current_user['username']}")
        self.current_user = None
        
        # Remove dashboard
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
        
        # Recreate authentication windows
        self.login_window = LoginWindow()
        self.signup_window = SignupWindow()
        
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.switch_to_signup.connect(self.show_signup)
        self.signup_window.switch_to_login.connect(self.show_login)
        
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.signup_window)
        
        # Show login window
        self.show_login()
        
        # Resize window back to login size
        self.setGeometry(100, 100, 400, 500)
