"""
Login window for user authentication.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.auth.auth_manager import AuthManager
from src.utils.styles import get_login_stylesheet
import logging

logger = logging.getLogger(__name__)


class LoginWindow(QWidget):
    """
    Login window widget for user authentication.
    """
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(dict)
    # Signal to switch to signup window
    switch_to_signup = pyqtSignal()
    
    def __init__(self):
        """Initialize the login window."""
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Personal Information Manager - Login')
        self.setFixedSize(400, 500)
        
        # Set stylesheet
        self.setStyleSheet(get_login_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Title
        title_label = QLabel('Personal Information\nManager')
        title_label.setObjectName('titleLabel')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel('Sign in to continue')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setProperty('class', 'subtitle')
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(20)
        
        # Username/Email input
        username_label = QLabel('Username or Email:')
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username or email')
        self.username_input.returnPressed.connect(self.handle_login)
        main_layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel('Password:')
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        main_layout.addWidget(self.password_input)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox('Remember me')
        main_layout.addWidget(self.remember_checkbox)
        
        # Error message label
        self.error_label = QLabel('')
        self.error_label.setProperty('class', 'error')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)
        
        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.setObjectName('loginButton')
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        main_layout.addWidget(self.login_button)
        
        # Forgot password link (placeholder)
        forgot_password_label = QLabel('<a href="#" style="color: #2E7D32;">Forgot password?</a>')
        forgot_password_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forgot_password_label.linkActivated.connect(self.show_forgot_password)
        main_layout.addWidget(forgot_password_label)
        
        main_layout.addStretch()
        
        # Signup link
        signup_layout = QHBoxLayout()
        signup_layout.addStretch()
        signup_text = QLabel("Don't have an account?")
        signup_layout.addWidget(signup_text)
        
        signup_link = QLabel('<a href="#" style="color: #2E7D32; font-weight: bold;">Sign Up</a>')
        signup_link.linkActivated.connect(self.go_to_signup)
        signup_layout.addWidget(signup_link)
        signup_layout.addStretch()
        
        main_layout.addLayout(signup_layout)
        
        self.setLayout(main_layout)
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username:
            self.show_error('Please enter username or email')
            return
        
        if not password:
            self.show_error('Please enter password')
            return
        
        # Attempt login
        self.login_button.setEnabled(False)
        self.login_button.setText('Logging in...')
        
        success, message, user_data = self.auth_manager.login(username, password)
        
        self.login_button.setEnabled(True)
        self.login_button.setText('Login')
        
        if success:
            logger.info(f"Login successful for user: {username}")
            self.login_successful.emit(user_data)
            self.close()
        else:
            self.show_error(message)
            logger.warning(f"Login failed for user: {username}")
    
    def show_error(self, message: str):
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.show()
    
    def show_forgot_password(self):
        """Show forgot password dialog (placeholder)."""
        QMessageBox.information(
            self,
            'Forgot Password',
            'Password recovery feature will be available in a future update.\n\n'
            'Please contact your administrator for password reset assistance.'
        )
    
    def go_to_signup(self):
        """Switch to signup window."""
        self.switch_to_signup.emit()
    
    def clear_form(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.password_input.clear()
        self.remember_checkbox.setChecked(False)
        self.error_label.hide()
