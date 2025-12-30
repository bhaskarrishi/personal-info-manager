"""
Dialog for password verification.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt
import bcrypt

logger = logging.getLogger(__name__)


class PasswordVerificationDialog(QDialog):
    """Dialog for verifying user password before sensitive operations."""

    def __init__(self, db_manager, user_id: int, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.user_id = user_id
        self.setWindowTitle('Verify Password')
        self.setModal(True)
        self.setFixedWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        info_label = QLabel('Please enter your password to confirm this action:')
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Enter your password')
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        verify_button = QPushButton('Verify')
        verify_button.clicked.connect(self.verify_password)
        verify_button.setDefault(True)
        button_layout.addWidget(verify_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def verify_password(self):
        """Verify the entered password against stored hash."""
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, 'Empty Password', 'Please enter your password')
            return

        try:
            query = "SELECT password_hash FROM users WHERE id = %s"
            result = self.db.execute_query(query, (self.user_id,), fetch=True)

            if result and result[0]['password_hash']:
                stored_hash = result[0]['password_hash']
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    self.accept()
                else:
                    QMessageBox.warning(self, 'Invalid Password', 'Incorrect password. Please try again.')
                    self.password_input.clear()
                    self.password_input.setFocus()
            else:
                QMessageBox.critical(self, 'Error', 'Could not verify password')
                self.reject()
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            QMessageBox.critical(self, 'Error', f'Password verification failed: {str(e)}')
            self.reject()
