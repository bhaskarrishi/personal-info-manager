"""
Password vault window for managing encrypted passwords.
"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QMessageBox, QDialog, QFormLayout,
                            QComboBox, QTextEdit, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QClipboard
from database.db_manager import DatabaseManager
from src.utils.encryption import EncryptionManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_generator_dialog import PasswordGeneratorDialog

logger = logging.getLogger(__name__)


class PasswordVaultWindow(QWidget):
    """
    Password vault window for securely storing and managing passwords.
    """
    
    def __init__(self, user_id: int):
        """
        Initialize password vault window.
        
        Args:
            user_id: Current user's ID
        """
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.encryption = EncryptionManager()
        self.init_ui()
        self.load_passwords()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title and search bar
        title_layout = QHBoxLayout()
        title_label = QLabel('Password Vault')
        title_label.setProperty('class', 'title')
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search passwords...')
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_passwords)
        title_layout.addWidget(self.search_input)
        
        layout.addLayout(title_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton('Add Password')
        add_button.clicked.connect(self.add_password)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_password)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Service', 'Username', 'Password', 'Category', 'URL'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.copy_password)
        layout.addWidget(self.table)
        
        # Info label
        info_label = QLabel('Tip: Double-click on a row to copy the password to clipboard')
        info_label.setProperty('class', 'subtitle')
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def load_passwords(self):
        """Load passwords from database."""
        try:
            query = """
                SELECT id, service_name, username, encrypted_password, category, url
                FROM password_vault
                WHERE user_id = %s
                ORDER BY service_name
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['service_name']))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['username'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem('••••••••'))
                    self.table.setItem(row_position, 3, QTableWidgetItem(row_data['category'] or ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(row_data['url'] or ''))
                    
                    # Store encrypted password and ID in hidden column
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
                    self.table.item(row_position, 2).setData(Qt.ItemDataRole.UserRole, row_data['encrypted_password'])
            
            logger.info(f"Loaded {len(results) if results else 0} passwords")
        except Exception as e:
            logger.error(f"Error loading passwords: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load passwords: {str(e)}')
    
    def filter_passwords(self, text: str):
        """Filter passwords based on search text."""
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def add_password(self):
        """Add new password entry."""
        dialog = PasswordEntryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                # Encrypt password
                encrypted_password = self.encryption.encrypt(data['password'])
                
                query = """
                    INSERT INTO password_vault
                    (user_id, service_name, username, encrypted_password, url, notes, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(
                    query,
                    (self.user_id, data['service_name'], data['username'],
                     encrypted_password, data['url'], data['notes'], data['category'])
                )
                
                self.load_passwords()
                QMessageBox.information(self, 'Success', 'Password added successfully!')
                logger.info(f"Password added for service: {data['service_name']}")
            except Exception as e:
                logger.error(f"Error adding password: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add password: {str(e)}')
    
    def edit_password(self):
        """Edit selected password entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a password to edit')
            return
        
        password_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get current data
        try:
            query = """
                SELECT service_name, username, encrypted_password, url, notes, category
                FROM password_vault
                WHERE id = %s
            """
            result = self.db.execute_query(query, (password_id,), fetch=True)
            
            if result:
                data = result[0]
                # Decrypt password
                decrypted_password = self.encryption.decrypt(data['encrypted_password'])
                
                dialog = PasswordEntryDialog(self, {
                    'service_name': data['service_name'],
                    'username': data['username'],
                    'password': decrypted_password,
                    'url': data['url'],
                    'notes': data['notes'],
                    'category': data['category']
                })
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_data = dialog.get_data()
                    encrypted_password = self.encryption.encrypt(new_data['password'])
                    
                    update_query = """
                        UPDATE password_vault
                        SET service_name = %s, username = %s, encrypted_password = %s,
                            url = %s, notes = %s, category = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(
                        update_query,
                        (new_data['service_name'], new_data['username'], encrypted_password,
                         new_data['url'], new_data['notes'], new_data['category'], password_id)
                    )
                    
                    self.load_passwords()
                    QMessageBox.information(self, 'Success', 'Password updated successfully!')
                    logger.info(f"Password updated: {new_data['service_name']}")
        except Exception as e:
            logger.error(f"Error editing password: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit password: {str(e)}')
    
    def delete_password(self):
        """Delete selected password entry."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a password to delete')
            return
        
        service_name = self.table.item(current_row, 0).text()
        password_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog(
            'Confirm Delete',
            f'Are you sure you want to delete the password for "{service_name}"?',
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                query = "DELETE FROM password_vault WHERE id = %s"
                self.db.execute_query(query, (password_id,))
                
                self.load_passwords()
                QMessageBox.information(self, 'Success', 'Password deleted successfully!')
                logger.info(f"Password deleted: {service_name}")
            except Exception as e:
                logger.error(f"Error deleting password: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete password: {str(e)}')
    
    def copy_password(self):
        """Copy password to clipboard."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        encrypted_password = self.table.item(current_row, 2).data(Qt.ItemDataRole.UserRole)
        
        try:
            decrypted_password = self.encryption.decrypt(encrypted_password)
            
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(decrypted_password)
            
            QMessageBox.information(self, 'Copied', 'Password copied to clipboard!\n\nIt will be cleared after 30 seconds.')
            
            # Clear clipboard after 30 seconds
            QTimer.singleShot(30000, lambda: clipboard.clear())
            
            logger.info("Password copied to clipboard")
        except Exception as e:
            logger.error(f"Error copying password: {e}")
            QMessageBox.critical(self, 'Error', 'Failed to decrypt password')


class PasswordEntryDialog(QDialog):
    """Dialog for adding/editing password entries."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Password Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.service_input = QLineEdit(self.data.get('service_name', ''))
        form_layout.addRow('Service Name*:', self.service_input)
        
        self.username_input = QLineEdit(self.data.get('username', ''))
        form_layout.addRow('Username:', self.username_input)
        
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit(self.data.get('password', ''))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_input)
        
        show_button = QPushButton('Show')
        show_button.setMaximumWidth(60)
        show_button.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(show_button)
        
        generate_button = QPushButton('Generate')
        generate_button.clicked.connect(self.generate_password)
        password_layout.addWidget(generate_button)
        
        form_layout.addRow('Password*:', password_layout)
        
        self.category_input = QComboBox()
        self.category_input.addItems(['Personal', 'Work', 'Finance', 'Social', 'Other'])
        self.category_input.setCurrentText(self.data.get('category', 'Personal'))
        form_layout.addRow('Category:', self.category_input)
        
        self.url_input = QLineEdit(self.data.get('url', ''))
        form_layout.addRow('URL:', self.url_input)
        
        self.notes_input = QTextEdit(self.data.get('notes', ''))
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow('Notes:', self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.accept_and_validate)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def generate_password(self):
        """Generate a strong password."""
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.password_input.setText(dialog.get_password())
    
    def accept_and_validate(self):
        """Validate and accept dialog."""
        if not self.service_input.text().strip():
            QMessageBox.warning(self, 'Validation Error', 'Service name is required')
            return
        
        if not self.password_input.text():
            QMessageBox.warning(self, 'Validation Error', 'Password is required')
            return
        
        self.accept()
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'service_name': self.service_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'category': self.category_input.currentText(),
            'url': self.url_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
