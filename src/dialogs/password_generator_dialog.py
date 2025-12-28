"""
Password generator dialog for creating strong passwords.
"""
import random
import string
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QSpinBox, QCheckBox, QLineEdit)
from PyQt6.QtCore import Qt
from src.utils.styles import get_main_stylesheet


class PasswordGeneratorDialog(QDialog):
    """
    Dialog for generating strong random passwords.
    """
    
    def __init__(self, parent=None):
        """
        Initialize password generator dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle('Password Generator')
        self.setModal(True)
        self.setFixedSize(450, 400)
        self.setStyleSheet(get_main_stylesheet())
        
        self.generated_password = ''
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel('Generate Strong Password')
        title.setProperty('class', 'title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Password display
        password_layout = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setPlaceholderText('Generated password will appear here')
        password_layout.addWidget(self.password_display)
        
        copy_button = QPushButton('Copy')
        copy_button.clicked.connect(self.copy_password)
        password_layout.addWidget(copy_button)
        
        layout.addLayout(password_layout)
        
        # Length setting
        length_layout = QHBoxLayout()
        length_label = QLabel('Password Length:')
        length_layout.addWidget(length_label)
        
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(8)
        self.length_spin.setMaximum(128)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_spin)
        length_layout.addStretch()
        
        layout.addLayout(length_layout)
        
        # Character options
        options_label = QLabel('Include:')
        options_label.setProperty('class', 'subtitle')
        layout.addWidget(options_label)
        
        self.uppercase_check = QCheckBox('Uppercase Letters (A-Z)')
        self.uppercase_check.setChecked(True)
        layout.addWidget(self.uppercase_check)
        
        self.lowercase_check = QCheckBox('Lowercase Letters (a-z)')
        self.lowercase_check.setChecked(True)
        layout.addWidget(self.lowercase_check)
        
        self.digits_check = QCheckBox('Numbers (0-9)')
        self.digits_check.setChecked(True)
        layout.addWidget(self.digits_check)
        
        self.special_check = QCheckBox('Special Characters (!@#$%^&*)')
        self.special_check.setChecked(True)
        layout.addWidget(self.special_check)
        
        self.exclude_ambiguous_check = QCheckBox('Exclude Ambiguous Characters (0OIl)')
        self.exclude_ambiguous_check.setChecked(False)
        layout.addWidget(self.exclude_ambiguous_check)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        generate_button = QPushButton('Generate Password')
        generate_button.clicked.connect(self.generate_password)
        button_layout.addWidget(generate_button)
        
        use_button = QPushButton('Use This Password')
        use_button.setProperty('class', 'secondary')
        use_button.clicked.connect(self.accept)
        button_layout.addWidget(use_button)
        
        cancel_button = QPushButton('Cancel')
        cancel_button.setProperty('class', 'secondary')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Generate initial password
        self.generate_password()
    
    def generate_password(self):
        """Generate a random password based on selected options."""
        length = self.length_spin.value()
        
        # Build character set
        characters = ''
        
        if self.uppercase_check.isChecked():
            characters += string.ascii_uppercase
        
        if self.lowercase_check.isChecked():
            characters += string.ascii_lowercase
        
        if self.digits_check.isChecked():
            characters += string.digits
        
        if self.special_check.isChecked():
            characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        # Remove ambiguous characters if requested
        if self.exclude_ambiguous_check.isChecked():
            ambiguous = '0OIl'
            characters = ''.join(c for c in characters if c not in ambiguous)
        
        # Check if at least one character set is selected
        if not characters:
            self.password_display.setText('Please select at least one character type')
            return
        
        # Generate password
        password = ''.join(random.choice(characters) for _ in range(length))
        
        self.generated_password = password
        self.password_display.setText(password)
    
    def copy_password(self):
        """Copy the generated password to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_password)
        
        # Visual feedback
        original_text = self.password_display.placeholderText()
        self.password_display.setPlaceholderText('Copied to clipboard!')
        
        # Reset placeholder after delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.password_display.setPlaceholderText(original_text))
    
    def get_password(self) -> str:
        """
        Get the generated password.
        
        Returns:
            str: Generated password
        """
        return self.generated_password
