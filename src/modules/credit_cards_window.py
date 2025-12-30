"""
Credit cards management window.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox,
    QDialog,
    QFormLayout,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QTextEdit,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)

CARD_TYPES = ['Visa', 'Mastercard', 'American Express', 'Discover', 'Diners Club', 'Other']


class CreditCardsWindow(QWidget):
    """Credit cards management window."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.show_sensitive = False
        self.init_ui()
        self.load_cards()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel('Credit Cards')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)

        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Card')
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

        self.toggle_sensitive_btn = QPushButton('Show Sensitive Data')
        self.toggle_sensitive_btn.setProperty('class', 'secondary')
        self.toggle_sensitive_btn.clicked.connect(self.toggle_sensitive_data)
        button_layout.addWidget(self.toggle_sensitive_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Cardholder', 'Card Type', 'Last 4 Digits', 'Issuer', 'Expiry', 'Credit Limit', 'Status'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def toggle_sensitive_data(self):
        """Toggle visibility of sensitive data."""
        self.show_sensitive = not self.show_sensitive
        if self.show_sensitive:
            self.toggle_sensitive_btn.setText('Hide Sensitive Data')
        else:
            self.toggle_sensitive_btn.setText('Show Sensitive Data')
        self.load_cards()

    def load_cards(self):
        try:
            query = (
                """
                SELECT id, cardholder_name, card_type, last_four_digits, issuer,
                       expiry_date, credit_limit, card_status
                FROM credit_cards
                WHERE user_id = %s
                ORDER BY cardholder_name
                """
            )
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            self.table.setRowCount(0)
            if results:
                for row in results:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)

                    self.table.setItem(row_pos, 0, QTableWidgetItem(row['cardholder_name'] or ''))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(row['card_type'] or ''))
                    
                    # Mask last 4 digits unless showing sensitive
                    last_four = row['last_four_digits'] or ''
                    if not self.show_sensitive and last_four:
                        last_four = '****'
                    self.table.setItem(row_pos, 2, QTableWidgetItem(last_four))
                    
                    self.table.setItem(row_pos, 3, QTableWidgetItem(row['issuer'] or ''))
                    self.table.setItem(
                        row_pos, 4, QTableWidgetItem(str(row['expiry_date']) if row['expiry_date'] else '')
                    )
                    self.table.setItem(
                        row_pos, 5,
                        QTableWidgetItem(f"{row['credit_limit']:.2f}" if row['credit_limit'] is not None else '')
                    )
                    self.table.setItem(row_pos, 6, QTableWidgetItem(row['card_status'] or ''))

                    self.table.item(row_pos, 0).setData(Qt.ItemDataRole.UserRole, row['id'])
        except Exception as e:
            logger.error(f"Error loading credit cards: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load credit cards: {str(e)}')

    def add_card(self):
        dialog = CreditCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = (
                    """
                    INSERT INTO credit_cards
                    (user_id, cardholder_name, card_type, card_number, last_four_digits, issuer,
                     expiry_date, cvv, credit_limit, current_balance, card_status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )
                self.db.execute_insert(
                    query,
                    (
                        self.user_id,
                        data['cardholder_name'],
                        data['card_type'],
                        data['card_number'],
                        data['last_four_digits'],
                        data['issuer'],
                        data['expiry_date'],
                        data['cvv'],
                        data['credit_limit'],
                        data['current_balance'],
                        data['card_status'],
                        data['notes'],
                    ),
                )
                self.load_cards()
                QMessageBox.information(self, 'Success', 'Card added successfully!')
            except Exception as e:
                logger.error(f"Error adding card: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add card: {str(e)}')

    def edit_card(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a card to edit')
            return

        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        card_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            result = self.db.execute_query("SELECT * FROM credit_cards WHERE id = %s", (card_id,), fetch=True)
            if result:
                dialog = CreditCardDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = (
                        """
                        UPDATE credit_cards
                        SET cardholder_name = %s, card_type = %s, card_number = %s,
                            last_four_digits = %s, issuer = %s, expiry_date = %s, cvv = %s,
                            credit_limit = %s, current_balance = %s, card_status = %s, notes = %s
                        WHERE id = %s
                        """
                    )
                    self.db.execute_query(
                        update_query,
                        (
                            data['cardholder_name'],
                            data['card_type'],
                            data['card_number'],
                            data['last_four_digits'],
                            data['issuer'],
                            data['expiry_date'],
                            data['cvv'],
                            data['credit_limit'],
                            data['current_balance'],
                            data['card_status'],
                            data['notes'],
                            card_id,
                        ),
                    )
                    self.load_cards()
                    QMessageBox.information(self, 'Success', 'Card updated successfully!')
        except Exception as e:
            logger.error(f"Error editing card: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit card: {str(e)}')

    def delete_card(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a card to delete')
            return

        card_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Verify password before deletion
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        dialog = ConfirmationDialog(
            'Confirm Delete',
            'Are you sure you want to permanently delete this card?\n\nThis action cannot be undone.',
            self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM credit_cards WHERE id = %s", (card_id,))
                self.load_cards()
                QMessageBox.information(self, 'Success', 'Card deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting card: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete card: {str(e)}')


class CreditCardDialog(QDialog):
    """Dialog for adding/editing credit cards."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Credit Card Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.cardholder_input = QLineEdit(self.data.get('cardholder_name', ''))
        form_layout.addRow('Cardholder Name*:', self.cardholder_input)

        self.card_type_input = QComboBox()
        self.card_type_input.addItems(CARD_TYPES)
        self.card_type_input.setCurrentText(self.data.get('card_type', CARD_TYPES[0]))
        form_layout.addRow('Card Type*:', self.card_type_input)

        self.card_number_input = QLineEdit(self.data.get('card_number', ''))
        self.card_number_input.setPlaceholderText('Full card number (stored securely)')
        form_layout.addRow('Card Number:', self.card_number_input)

        self.last_four_input = QLineEdit(self.data.get('last_four_digits', ''))
        self.last_four_input.setPlaceholderText('Last 4 digits only')
        self.last_four_input.setMaxLength(4)
        form_layout.addRow('Last 4 Digits:', self.last_four_input)

        self.issuer_input = QLineEdit(self.data.get('issuer', ''))
        form_layout.addRow('Issuer:', self.issuer_input)

        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        if self.data.get('expiry_date'):
            self.expiry_date_input.setDate(QDate.fromString(str(self.data['expiry_date']), 'yyyy-MM-dd'))
        else:
            self.expiry_date_input.setDate(QDate.currentDate().addYears(3))
        form_layout.addRow('Expiry Date:', self.expiry_date_input)

        self.cvv_input = QLineEdit(self.data.get('cvv', ''))
        self.cvv_input.setPlaceholderText('CVV (3-4 digits)')
        self.cvv_input.setMaxLength(4)
        self.cvv_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('CVV:', self.cvv_input)

        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setMaximum(999999.99)
        self.credit_limit_input.setDecimals(2)
        self.credit_limit_input.setValue(float(self.data.get('credit_limit', 0)))
        form_layout.addRow('Credit Limit:', self.credit_limit_input)

        self.current_balance_input = QDoubleSpinBox()
        self.current_balance_input.setMaximum(999999.99)
        self.current_balance_input.setDecimals(2)
        self.current_balance_input.setValue(float(self.data.get('current_balance', 0)))
        form_layout.addRow('Current Balance:', self.current_balance_input)

        self.status_input = QComboBox()
        self.status_input.addItems(['Active', 'Inactive', 'Blocked', 'Expired'])
        self.status_input.setCurrentText(self.data.get('card_status', 'Active'))
        form_layout.addRow('Status:', self.status_input)

        self.notes_input = QTextEdit(self.data.get('notes', ''))
        self.notes_input.setMaximumHeight(80)
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
        return {
            'cardholder_name': self.cardholder_input.text().strip(),
            'card_type': self.card_type_input.currentText(),
            'card_number': self.card_number_input.text().strip(),
            'last_four_digits': self.last_four_input.text().strip(),
            'issuer': self.issuer_input.text().strip(),
            'expiry_date': self.expiry_date_input.date().toString('yyyy-MM-dd'),
            'cvv': self.cvv_input.text().strip(),
            'credit_limit': self.credit_limit_input.value(),
            'current_balance': self.current_balance_input.value(),
            'card_status': self.status_input.currentText(),
            'notes': self.notes_input.toPlainText().strip(),
        }
