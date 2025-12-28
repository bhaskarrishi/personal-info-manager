"""
Generic add/edit dialog base class for CRUD operations.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QPushButton, QWidget)
from PyQt6.QtCore import Qt
from src.utils.styles import get_main_stylesheet


class AddEditDialog(QDialog):
    """
    Base class for add/edit dialogs.
    Provides common structure and methods for CRUD operations.
    """
    
    def __init__(self, title: str, parent=None):
        """
        Initialize the add/edit dialog.
        
        Args:
            title: Dialog title
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet(get_main_stylesheet())
        
        self.data = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the basic user interface structure."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Form layout (to be populated by subclasses)
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(self.form_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setProperty('class', 'secondary')
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        """
        Validate form data and accept dialog if valid.
        Should be overridden by subclasses to implement validation.
        """
        if self.validate():
            self.accept()
    
    def validate(self) -> bool:
        """
        Validate form data.
        Should be overridden by subclasses.
        
        Returns:
            bool: True if valid, False otherwise
        """
        return True
    
    def get_data(self) -> dict:
        """
        Get the form data as a dictionary.
        Should be overridden by subclasses.
        
        Returns:
            dict: Form data
        """
        return self.data
    
    def set_data(self, data: dict):
        """
        Set form data from a dictionary (for editing).
        Should be overridden by subclasses.
        
        Args:
            data: Data to populate form with
        """
        self.data = data
