"""
Health cards management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)


class HealthCardsWindow(QWidget):
    """Health cards management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.show_sensitive = False
        self.init_ui()
        self.load_cards()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Health Cards')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Health Card')
        add_button.clicked.connect(self.add_card)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_card)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_card)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        
        self.toggle_sensitive_btn = QPushButton('Show Sensitive Data')
        self.toggle_sensitive_btn.setProperty('class', 'secondary')
        self.toggle_sensitive_btn.clicked.connect(self.toggle_sensitive_data)
        button_layout.addWidget(self.toggle_sensitive_btn)
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Family Member', 'Relationship', 'Card Type', 'Card Number', 'Provider', 'Expiry Date'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_cards(self):
        """Load health cards from database."""
        try:
            query = """
                SELECT id, family_member_name, relationship, card_type, card_number, provider, expiry_date
                FROM health_cards WHERE user_id = %s ORDER BY expiry_date
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['family_member_name'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['relationship'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(row_data['card_type'] or ''))
                    
                    # Mask card number if sensitive data is hidden
                    card_number = row_data['card_number'] or ''
                    if not self.show_sensitive and card_number:
                        masked_number = '****' + card_number[-4:] if len(card_number) > 4 else '****'
                        self.table.setItem(row_position, 3, QTableWidgetItem(masked_number))
                    else:
                        self.table.setItem(row_position, 3, QTableWidgetItem(card_number))
                    
                    self.table.setItem(row_position, 4, QTableWidgetItem(row_data['provider'] or ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem(str(row_data['expiry_date']) if row_data['expiry_date'] else ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading health cards: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load health cards: {str(e)}')
    
    def toggle_sensitive_data(self):
        """Toggle between showing and hiding sensitive data."""
        self.show_sensitive = not self.show_sensitive
        if self.show_sensitive:
            self.toggle_sensitive_btn.setText('Hide Sensitive Data')
        else:
            self.toggle_sensitive_btn.setText('Show Sensitive Data')
        self.load_cards()
    
    def add_card(self):
        """Add new health card."""
        dialog = HealthCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO health_cards
                    (user_id, family_member_name, relationship, card_type, card_number, provider, expiry_date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['family_member_name'], data['relationship'], data['card_type'],
                    data['card_number'], data['provider'], data['expiry_date'], data['notes']
                ))
                self.load_cards()
                QMessageBox.information(self, 'Success', 'Health card added successfully!')
            except Exception as e:
                logger.error(f"Error adding health card: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add health card: {str(e)}')
    
    def edit_card(self):
        """Edit selected health card."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a health card to edit')
            return
        
        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        card_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM health_cards WHERE id = %s"
            result = self.db.execute_query(query, (card_id,), fetch=True)
            
            if result:
                dialog = HealthCardDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE health_cards
                        SET family_member_name = %s, relationship = %s, card_type = %s,
                            card_number = %s, provider = %s, expiry_date = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['family_member_name'], data['relationship'], data['card_type'],
                        data['card_number'], data['provider'], data['expiry_date'], data['notes'], card_id
                    ))
                    self.load_cards()
                    QMessageBox.information(self, 'Success', 'Health card updated successfully!')
        except Exception as e:
            logger.error(f"Error editing health card: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit health card: {str(e)}')
    
    def delete_card(self):
        """Delete selected health card."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a health card to delete')
            return
        
        card_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this health card?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM health_cards WHERE id = %s", (card_id,))
                self.load_cards()
                QMessageBox.information(self, 'Success', 'Health card deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting health card: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete health card: {str(e)}')


class HealthCardDialog(QDialog):
    """Dialog for adding/editing health cards."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Health Card Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.family_member_input = QLineEdit(self.data.get('family_member_name', ''))
        form_layout.addRow('Family Member*:', self.family_member_input)
        
        self.relationship_input = QComboBox()
        self.relationship_input.addItems(['Self', 'Spouse', 'Child', 'Parent', 'Sibling', 'Other'])
        self.relationship_input.setCurrentText(self.data.get('relationship', 'Self'))
        form_layout.addRow('Relationship:', self.relationship_input)
        
        self.card_type_input = QComboBox()
        self.card_type_input.addItems(['Health Insurance', 'Medicare', 'Medicaid', 'Dental', 'Vision', 'Other'])
        self.card_type_input.setCurrentText(self.data.get('card_type', 'Health Insurance'))
        form_layout.addRow('Card Type*:', self.card_type_input)
        
        self.card_number_input = QLineEdit(self.data.get('card_number', ''))
        form_layout.addRow('Card Number:', self.card_number_input)
        
        self.provider_input = QLineEdit(self.data.get('provider', ''))
        form_layout.addRow('Provider:', self.provider_input)
        
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        if self.data.get('expiry_date'):
            self.expiry_date_input.setDate(QDate.fromString(str(self.data['expiry_date']), 'yyyy-MM-dd'))
        else:
            self.expiry_date_input.setDate(QDate.currentDate().addYears(1))
        form_layout.addRow('Expiry Date:', self.expiry_date_input)
        
        self.notes_input = QTextEdit(self.data.get('notes', ''))
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow('Notes:', self.notes_input)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'family_member_name': self.family_member_input.text().strip(),
            'relationship': self.relationship_input.currentText(),
            'card_type': self.card_type_input.currentText(),
            'card_number': self.card_number_input.text().strip(),
            'provider': self.provider_input.text().strip(),
            'expiry_date': self.expiry_date_input.date().toString('yyyy-MM-dd'),
            'notes': self.notes_input.toPlainText().strip()
        }
