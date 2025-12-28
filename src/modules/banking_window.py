"""
Banking accounts management window.
"""
import logging
import shutil
from pathlib import Path
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
    QDoubleSpinBox,
    QTextEdit,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


CURRENCY_CHOICES = [
    'USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD', 'JPY', 'CHF', 'CNY', 'SGD', 'HKD', 'AED', 'ZAR', 'Other'
]

ACCOUNT_TYPES = ['Checking', 'Savings', 'Current', 'Brokerage', 'Cash Management', 'Other']


class BankingWindow(QWidget):
    """Banking accounts management window."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_accounts()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel('Banking Accounts')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)

        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Account')
        add_button.clicked.connect(self.add_account)
        button_layout.addWidget(add_button)

        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_account)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_account)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'Account Name', 'Type', 'Institution', 'Country', 'Currency', 'Balance', 'Available', 'Interest %'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_accounts(self):
        """Load banking accounts from database."""
        try:
            query = (
                """
                SELECT id, account_name, account_type, institution, country, currency,
                       balance, available_balance, interest_rate
                FROM banking_accounts
                WHERE user_id = %s
                ORDER BY account_name
                """
            )
            results = self.db.execute_query(query, (self.user_id,), fetch=True)

            self.table.setRowCount(0)
            if results:
                for row in results:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)

                    self.table.setItem(row_pos, 0, QTableWidgetItem(row['account_name'] or ''))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(row['account_type'] or ''))
                    self.table.setItem(row_pos, 2, QTableWidgetItem(row['institution'] or ''))
                    self.table.setItem(row_pos, 3, QTableWidgetItem(row['country'] or ''))
                    self.table.setItem(row_pos, 4, QTableWidgetItem(row['currency'] or ''))
                    self.table.setItem(
                        row_pos, 5,
                        QTableWidgetItem(f"{row['balance']:.2f}" if row['balance'] is not None else '')
                    )
                    self.table.setItem(
                        row_pos, 6,
                        QTableWidgetItem(
                            f"{row['available_balance']:.2f}" if row['available_balance'] is not None else ''
                        )
                    )
                    self.table.setItem(
                        row_pos, 7,
                        QTableWidgetItem(f"{row['interest_rate']:.2f}" if row['interest_rate'] is not None else '')
                    )

                    self.table.item(row_pos, 0).setData(Qt.ItemDataRole.UserRole, row['id'])
        except Exception as e:
            logger.error(f"Error loading banking accounts: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load banking accounts: {str(e)}')

    def add_account(self):
        dialog = BankingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = (
                    """
                    INSERT INTO banking_accounts
                    (user_id, account_name, account_type, institution, account_number, iban, country,
                     currency, balance, available_balance, interest_rate, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )
                self.db.execute_insert(
                    query,
                    (
                        self.user_id,
                        data['account_name'],
                        data['account_type'],
                        data['institution'],
                        data['account_number'],
                        data['iban'],
                        data['country'],
                        data['currency'],
                        data['balance'],
                        data['available_balance'],
                        data['interest_rate'],
                        data['notes'],
                    ),
                )
                self.load_accounts()
                QMessageBox.information(self, 'Success', 'Account added successfully!')
            except Exception as e:
                logger.error(f"Error adding account: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add account: {str(e)}')

    def edit_account(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an account to edit')
            return

        account_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            result = self.db.execute_query(
                "SELECT * FROM banking_accounts WHERE id = %s", (account_id,), fetch=True
            )
            if result:
                dialog = BankingDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = (
                        """
                        UPDATE banking_accounts
                        SET account_name = %s, account_type = %s, institution = %s,
                            account_number = %s, iban = %s, country = %s, currency = %s,
                            balance = %s, available_balance = %s, interest_rate = %s, notes = %s
                        WHERE id = %s
                        """
                    )
                    self.db.execute_query(
                        update_query,
                        (
                            data['account_name'],
                            data['account_type'],
                            data['institution'],
                            data['account_number'],
                            data['iban'],
                            data['country'],
                            data['currency'],
                            data['balance'],
                            data['available_balance'],
                            data['interest_rate'],
                            data['notes'],
                            account_id,
                        ),
                    )
                    self.load_accounts()
                    QMessageBox.information(self, 'Success', 'Account updated successfully!')
        except Exception as e:
            logger.error(f"Error editing account: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit account: {str(e)}')

    def delete_account(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an account to delete')
            return

        account_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this account?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM banking_accounts WHERE id = %s", (account_id,))
                self.load_accounts()
                QMessageBox.information(self, 'Success', 'Account deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting account: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete account: {str(e)}')


class BankingDialog(QDialog):
    """Dialog for adding/editing banking accounts."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Banking Account Entry')
        self.setModal(True)
        self.setMinimumWidth(520)
        self.data = data or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.account_name_input = QLineEdit(self.data.get('account_name', ''))
        form_layout.addRow('Account Name*:', self.account_name_input)

        self.account_type_input = QComboBox()
        self.account_type_input.addItems(ACCOUNT_TYPES)
        self.account_type_input.setCurrentText(self.data.get('account_type', ACCOUNT_TYPES[0]))
        form_layout.addRow('Account Type*:', self.account_type_input)

        self.institution_input = QLineEdit(self.data.get('institution', ''))
        form_layout.addRow('Institution:', self.institution_input)

        self.account_number_input = QLineEdit(self.data.get('account_number', ''))
        form_layout.addRow('Account Number:', self.account_number_input)

        self.iban_input = QLineEdit(self.data.get('iban', ''))
        form_layout.addRow('IBAN:', self.iban_input)

        self.country_input = QLineEdit(self.data.get('country', ''))
        form_layout.addRow('Country:', self.country_input)

        self.currency_input = QComboBox()
        self.currency_input.addItems(CURRENCY_CHOICES)
        self.currency_input.setCurrentText(self.data.get('currency', 'USD'))
        form_layout.addRow('Currency*:', self.currency_input)

        self.balance_input = QDoubleSpinBox()
        self.balance_input.setMaximum(999999999.99)
        self.balance_input.setDecimals(2)
        self.balance_input.setValue(float(self.data.get('balance', 0)))
        form_layout.addRow('Balance:', self.balance_input)

        self.available_balance_input = QDoubleSpinBox()
        self.available_balance_input.setMaximum(999999999.99)
        self.available_balance_input.setDecimals(2)
        self.available_balance_input.setValue(float(self.data.get('available_balance', 0)))
        form_layout.addRow('Available Balance:', self.available_balance_input)

        self.interest_rate_input = QDoubleSpinBox()
        self.interest_rate_input.setMaximum(100.00)
        self.interest_rate_input.setDecimals(2)
        self.interest_rate_input.setValue(float(self.data.get('interest_rate', 0)))
        form_layout.addRow('Interest Rate (%):', self.interest_rate_input)

        self.notes_input = QTextEdit(self.data.get('notes', ''))
        self.notes_input.setMaximumHeight(90)
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
            'account_name': self.account_name_input.text().strip(),
            'account_type': self.account_type_input.currentText(),
            'institution': self.institution_input.text().strip(),
            'account_number': self.account_number_input.text().strip(),
            'iban': self.iban_input.text().strip(),
            'country': self.country_input.text().strip(),
            'currency': self.currency_input.currentText(),
            'balance': self.balance_input.value(),
            'available_balance': self.available_balance_input.value(),
            'interest_rate': self.interest_rate_input.value(),
            'notes': self.notes_input.toPlainText().strip(),
        }
