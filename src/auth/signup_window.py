"""
Signup window for user registration.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QCheckBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.auth.auth_manager import AuthManager
from src.utils.validators import validate_email, validate_username, validate_password, get_password_strength
from src.utils.styles import get_login_stylesheet
import logging

logger = logging.getLogger(__name__)


class SignupWindow(QWidget):
    """
    Signup window widget for user registration.
    """
    
    # Signal emitted when signup is successful
    signup_successful = pyqtSignal()
    # Signal to switch back to login window
    switch_to_login = pyqtSignal()
    
    def __init__(self):
        """Initialize the signup window."""
        super().__init__()
        self.auth_manager = AuthManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Personal Information Manager - Sign Up')
        self.setFixedSize(400, 650)
        
        # Set stylesheet
        self.setStyleSheet(get_login_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel('Create Account')
        title_label.setObjectName('titleLabel')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel('Sign up to get started')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setProperty('class', 'subtitle')
        main_layout.addWidget(subtitle_label)
        
        main_layout.addSpacing(10)
        
        # Username input
        username_label = QLabel('Username:')
        main_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Choose a username')
        self.username_input.textChanged.connect(self.validate_form)
        main_layout.addWidget(self.username_input)
        
        self.username_error = QLabel('')
        self.username_error.setProperty('class', 'error')
        self.username_error.setWordWrap(True)
        self.username_error.hide()
        main_layout.addWidget(self.username_error)
        
        # Email input
        email_label = QLabel('Email:')
        main_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Enter your email')
        self.email_input.textChanged.connect(self.validate_form)
        main_layout.addWidget(self.email_input)
        
        self.email_error = QLabel('')
        self.email_error.setProperty('class', 'error')
        self.email_error.setWordWrap(True)
        self.email_error.hide()
        main_layout.addWidget(self.email_error)
        
        # Password input
        password_label = QLabel('Password:')
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Choose a strong password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.update_password_strength)
        main_layout.addWidget(self.password_input)
        
        # Password strength indicator
        self.password_strength_label = QLabel('')
        self.password_strength_label.hide()
        main_layout.addWidget(self.password_strength_label)
        
        self.password_strength_bar = QProgressBar()
        self.password_strength_bar.setMaximum(100)
        self.password_strength_bar.setValue(0)
        self.password_strength_bar.setTextVisible(False)
        self.password_strength_bar.setMaximumHeight(5)
        self.password_strength_bar.hide()
        main_layout.addWidget(self.password_strength_bar)
        
        self.password_error = QLabel('')
        self.password_error.setProperty('class', 'error')
        self.password_error.setWordWrap(True)
        self.password_error.hide()
        main_layout.addWidget(self.password_error)
        
        # Confirm password input
        confirm_password_label = QLabel('Confirm Password:')
        main_layout.addWidget(confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Re-enter your password')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.textChanged.connect(self.validate_form)
        main_layout.addWidget(self.confirm_password_input)
        
        self.confirm_password_error = QLabel('')
        self.confirm_password_error.setProperty('class', 'error')
        self.confirm_password_error.hide()
        main_layout.addWidget(self.confirm_password_error)
        
        # Terms acceptance checkbox
        self.terms_checkbox = QCheckBox(
            'I agree to the Terms of Service and Privacy Policy'
        )
        self.terms_checkbox.stateChanged.connect(self.validate_form)
        main_layout.addWidget(self.terms_checkbox)
        
        # General error message label
        self.error_label = QLabel('')
        self.error_label.setProperty('class', 'error')
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)
        
        # Signup button
        self.signup_button = QPushButton('Sign Up')
        self.signup_button.setObjectName('signupButton')
        self.signup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signup_button.clicked.connect(self.handle_signup)
        self.signup_button.setEnabled(False)
        main_layout.addWidget(self.signup_button)
        
        main_layout.addStretch()
        
        # Login link
        login_layout = QHBoxLayout()
        login_layout.addStretch()
        login_text = QLabel('Already have an account?')
        login_layout.addWidget(login_text)
        
        login_link = QLabel('<a href="#" style="color: #2E7D32; font-weight: bold;">Login</a>')
        login_link.linkActivated.connect(self.go_to_login)
        login_layout.addWidget(login_link)
        login_layout.addStretch()
        
        main_layout.addLayout(login_layout)
        
        self.setLayout(main_layout)
    
    def update_password_strength(self):
        """Update the password strength indicator."""
        password = self.password_input.text()
        
        if not password:
            self.password_strength_label.hide()
            self.password_strength_bar.hide()
            return
        
        strength = get_password_strength(password)
        self.password_strength_label.setText(f'Password Strength: {strength}')
        self.password_strength_label.show()
        self.password_strength_bar.show()
        
        # Set progress bar value and color based on strength
        strength_values = {
            'Weak': (25, '#D32F2F'),
            'Medium': (50, '#F57C00'),
            'Strong': (75, '#388E3C'),
            'Very Strong': (100, '#2E7D32')
        }
        
        value, color = strength_values.get(strength, (0, '#D32F2F'))
        self.password_strength_bar.setValue(value)
        self.password_strength_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        self.validate_form()
    
    def validate_form(self):
        """Validate all form fields and enable/disable signup button."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        terms_accepted = self.terms_checkbox.isChecked()
        
        # Reset error messages
        self.username_error.hide()
        self.email_error.hide()
        self.password_error.hide()
        self.confirm_password_error.hide()
        
        is_valid = True
        
        # Validate username
        if username:
            valid, error = validate_username(username)
            if not valid:
                self.username_error.setText(error)
                self.username_error.show()
                is_valid = False
        
        # Validate email
        if email:
            valid, error = validate_email(email)
            if not valid:
                self.email_error.setText(error)
                self.email_error.show()
                is_valid = False
        
        # Validate password
        if password:
            valid, error = validate_password(password)
            if not valid:
                self.password_error.setText(error)
                self.password_error.show()
                is_valid = False
        
        # Validate confirm password
        if confirm_password and password != confirm_password:
            self.confirm_password_error.setText('Passwords do not match')
            self.confirm_password_error.show()
            is_valid = False
        
        # Check all fields are filled and terms accepted
        # Force boolean; string chaining returns last truthy string otherwise
        all_filled = bool(username and email and password and confirm_password and terms_accepted)
        
        self.signup_button.setEnabled(is_valid and all_filled)
    
    def handle_signup(self):
        """Handle signup button click."""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Attempt registration
        self.signup_button.setEnabled(False)
        self.signup_button.setText('Creating account...')
        
        success, message = self.auth_manager.register_user(username, email, password)
        
        self.signup_button.setEnabled(True)
        self.signup_button.setText('Sign Up')
        
        if success:
            logger.info(f"Registration successful for user: {username}")
            self.show_success(message)
            # Switch to login window after short delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self.go_to_login)
        else:
            self.show_error(message)
            logger.warning(f"Registration failed for user: {username}")
    
    def show_error(self, message: str):
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.setProperty('class', 'error')
        self.error_label.setStyleSheet('color: #D32F2F;')
        self.error_label.show()
    
    def show_success(self, message: str):
        """
        Display a success message.
        
        Args:
            message: Success message to display
        """
        self.error_label.setText(message)
        self.error_label.setProperty('class', 'success')
        self.error_label.setStyleSheet('color: #388E3C;')
        self.error_label.show()
    
    def go_to_login(self):
        """Switch to login window."""
        self.switch_to_login.emit()
    
    def clear_form(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.terms_checkbox.setChecked(False)
        self.error_label.hide()
        self.username_error.hide()
        self.email_error.hide()
        self.password_error.hide()
        self.confirm_password_error.hide()
        self.password_strength_label.hide()
        self.password_strength_bar.hide()
