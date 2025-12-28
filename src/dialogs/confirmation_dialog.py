"""
Confirmation dialog for delete operations.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from src.utils.styles import get_main_stylesheet


class ConfirmationDialog(QDialog):
    """
    Dialog for confirming destructive operations like deletion.
    """
    
    def __init__(self, title: str, message: str, parent=None):
        """
        Initialize confirmation dialog.
        
        Args:
            title: Dialog title
            message: Confirmation message
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(400)
        self.setStyleSheet(get_main_stylesheet())
        
        self.init_ui(message)
    
    def init_ui(self, message: str):
        """
        Initialize the user interface.
        
        Args:
            message: Message to display
        """
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton('Cancel')
        cancel_button.setProperty('class', 'secondary')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        confirm_button = QPushButton('Confirm')
        confirm_button.setProperty('class', 'danger')
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
