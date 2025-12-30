"""
Mortgage management window.
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
    QMessageBox,
    QDialog,
    QFormLayout,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QTextEdit,
    QLineEdit,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)

CURRENCY_CHOICES = [
    'USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD', 'JPY', 'CHF', 'CNY', 'SGD', 'HKD', 'AED', 'ZAR', 'Other'
]

PAYMENT_FREQUENCY = ['Monthly', 'Bi-Weekly', 'Weekly', 'Quarterly', 'Annually', 'Other']


class MortgageWindow(QWidget):
    """Mortgage tracking window."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_mortgages()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel('Mortgages')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)

        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Mortgage')
        add_button.clicked.connect(self.add_mortgage)
        button_layout.addWidget(add_button)

        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_mortgage)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_mortgage)
        button_layout.addWidget(delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Lender', 'Property Ref', 'Currency', 'Outstanding', 'Payment', 'Next Due'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_mortgages(self):
        try:
            query = (
                """
                SELECT id, lender, property_reference, currency, outstanding_balance,
                       payment_amount, next_due_date
                FROM mortgages
                WHERE user_id = %s
                ORDER BY next_due_date IS NULL, next_due_date
                """
            )
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            self.table.setRowCount(0)
            if results:
                for row in results:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)

                    self.table.setItem(row_pos, 0, QTableWidgetItem(row['lender'] or ''))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(row['property_reference'] or ''))
                    self.table.setItem(row_pos, 2, QTableWidgetItem(row['currency'] or ''))
                    self.table.setItem(
                        row_pos, 3,
                        QTableWidgetItem(
                            f"{row['outstanding_balance']:.2f}" if row['outstanding_balance'] is not None else ''
                        )
                    )
                    self.table.setItem(
                        row_pos, 4,
                        QTableWidgetItem(
                            f"{row['payment_amount']:.2f}" if row['payment_amount'] is not None else ''
                        )
                    )
                    self.table.setItem(
                        row_pos, 5,
                        QTableWidgetItem(str(row['next_due_date']) if row['next_due_date'] else '')
                    )
                    self.table.item(row_pos, 0).setData(Qt.ItemDataRole.UserRole, row['id'])
        except Exception as e:
            logger.error(f"Error loading mortgages: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load mortgages: {str(e)}')

    def add_mortgage(self):
        dialog = MortgageDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = (
                    """
                    INSERT INTO mortgages
                    (user_id, lender, property_reference, currency, original_amount, outstanding_balance,
                     interest_rate, payment_amount, payment_frequency, next_due_date, start_date, maturity_date,
                     escrow_amount, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )
                self.db.execute_insert(
                    query,
                    (
                        self.user_id,
                        data['lender'],
                        data['property_reference'],
                        data['currency'],
                        data['original_amount'],
                        data['outstanding_balance'],
                        data['interest_rate'],
                        data['payment_amount'],
                        data['payment_frequency'],
                        data['next_due_date'],
                        data['start_date'],
                        data['maturity_date'],
                        data['escrow_amount'],
                        data['notes'],
                    ),
                )
                self.load_mortgages()
                QMessageBox.information(self, 'Success', 'Mortgage added successfully!')
            except Exception as e:
                logger.error(f"Error adding mortgage: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add mortgage: {str(e)}')

    def edit_mortgage(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a mortgage to edit')
            return

        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        mortgage_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            result = self.db.execute_query("SELECT * FROM mortgages WHERE id = %s", (mortgage_id,), fetch=True)
            if result:
                dialog = MortgageDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = (
                        """
                        UPDATE mortgages
                        SET lender = %s, property_reference = %s, currency = %s,
                            original_amount = %s, outstanding_balance = %s, interest_rate = %s,
                            payment_amount = %s, payment_frequency = %s, next_due_date = %s,
                            start_date = %s, maturity_date = %s, escrow_amount = %s, notes = %s
                        WHERE id = %s
                        """
                    )
                    self.db.execute_query(
                        update_query,
                        (
                            data['lender'],
                            data['property_reference'],
                            data['currency'],
                            data['original_amount'],
                            data['outstanding_balance'],
                            data['interest_rate'],
                            data['payment_amount'],
                            data['payment_frequency'],
                            data['next_due_date'],
                            data['start_date'],
                            data['maturity_date'],
                            data['escrow_amount'],
                            data['notes'],
                            mortgage_id,
                        ),
                    )
                    self.load_mortgages()
                    QMessageBox.information(self, 'Success', 'Mortgage updated successfully!')
        except Exception as e:
            logger.error(f"Error editing mortgage: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit mortgage: {str(e)}')

    def delete_mortgage(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a mortgage to delete')
            return

        mortgage_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this mortgage?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM mortgages WHERE id = %s", (mortgage_id,))
                self.load_mortgages()
                QMessageBox.information(self, 'Success', 'Mortgage deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting mortgage: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete mortgage: {str(e)}')


class MortgageDialog(QDialog):
    """Dialog for adding/editing mortgages."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Mortgage Entry')
        self.setModal(True)
        self.setMinimumWidth(900)
        self.setMinimumHeight(400)
        self.data = data or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Two-column form layout
        form_container = QWidget()
        form_layout = QHBoxLayout()
        form_layout.setSpacing(20)
        
        # Left column
        left_col = QFormLayout()
        left_col.setSpacing(12)
        
        self.lender_input = QLineEdit(self.data.get('lender', ''))
        left_col.addRow('Lender*:', self.lender_input)

        self.property_ref_input = QLineEdit(self.data.get('property_reference', ''))
        left_col.addRow('Property Ref:', self.property_ref_input)

        self.currency_input = QComboBox()
        self.currency_input.addItems(CURRENCY_CHOICES)
        self.currency_input.setCurrentText(self.data.get('currency', 'USD'))
        left_col.addRow('Currency*:', self.currency_input)

        self.original_amount_input = QDoubleSpinBox()
        self.original_amount_input.setMaximum(999999999.99)
        self.original_amount_input.setDecimals(2)
        self.original_amount_input.setValue(float(self.data.get('original_amount', 0)))
        left_col.addRow('Original Amount:', self.original_amount_input)

        self.outstanding_balance_input = QDoubleSpinBox()
        self.outstanding_balance_input.setMaximum(999999999.99)
        self.outstanding_balance_input.setDecimals(2)
        self.outstanding_balance_input.setValue(float(self.data.get('outstanding_balance', 0)))
        left_col.addRow('Outstanding:', self.outstanding_balance_input)

        self.interest_rate_input = QDoubleSpinBox()
        self.interest_rate_input.setMaximum(100.000)
        self.interest_rate_input.setDecimals(3)
        self.interest_rate_input.setValue(float(self.data.get('interest_rate', 0)))
        left_col.addRow('Interest Rate:', self.interest_rate_input)

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        if self.data.get('start_date'):
            self.start_date_input.setDate(QDate.fromString(str(self.data['start_date']), 'yyyy-MM-dd'))
        else:
            self.start_date_input.setDate(QDate.currentDate())
        left_col.addRow('Start Date:', self.start_date_input)
        
        # Right column
        right_col = QFormLayout()
        right_col.setSpacing(12)

        self.payment_amount_input = QDoubleSpinBox()
        self.payment_amount_input.setMaximum(999999999.99)
        self.payment_amount_input.setDecimals(2)
        self.payment_amount_input.setValue(float(self.data.get('payment_amount', 0)))
        right_col.addRow('Payment Amount:', self.payment_amount_input)

        self.payment_frequency_input = QComboBox()
        self.payment_frequency_input.addItems(PAYMENT_FREQUENCY)
        self.payment_frequency_input.setCurrentText(self.data.get('payment_frequency', 'Monthly'))
        right_col.addRow('Payment Freq:', self.payment_frequency_input)

        self.next_due_date_input = QDateEdit()
        self.next_due_date_input.setCalendarPopup(True)
        if self.data.get('next_due_date'):
            self.next_due_date_input.setDate(QDate.fromString(str(self.data['next_due_date']), 'yyyy-MM-dd'))
        else:
            self.next_due_date_input.setDate(QDate.currentDate())
        right_col.addRow('Next Due Date:', self.next_due_date_input)

        self.maturity_date_input = QDateEdit()
        self.maturity_date_input.setCalendarPopup(True)
        if self.data.get('maturity_date'):
            self.maturity_date_input.setDate(QDate.fromString(str(self.data['maturity_date']), 'yyyy-MM-dd'))
        else:
            self.maturity_date_input.setDate(QDate.currentDate().addYears(20))
        right_col.addRow('Maturity Date:', self.maturity_date_input)

        self.escrow_amount_input = QDoubleSpinBox()
        self.escrow_amount_input.setMaximum(999999999.99)
        self.escrow_amount_input.setDecimals(2)
        self.escrow_amount_input.setValue(float(self.data.get('escrow_amount', 0)))
        right_col.addRow('Escrow Amount:', self.escrow_amount_input)
        
        # Add columns to layout
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        
        form_layout.addWidget(left_widget)
        form_layout.addWidget(right_widget)
        form_container.setLayout(form_layout)
        
        layout.addWidget(form_container)
        
        # Notes section below
        notes_label = QLabel('Notes:')
        layout.addWidget(notes_label)
        self.notes_input = QTextEdit(self.data.get('notes', ''))
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)

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
            'lender': self.lender_input.text().strip(),
            'property_reference': self.property_ref_input.text().strip(),
            'currency': self.currency_input.currentText(),
            'original_amount': self.original_amount_input.value(),
            'outstanding_balance': self.outstanding_balance_input.value(),
            'interest_rate': self.interest_rate_input.value(),
            'payment_amount': self.payment_amount_input.value(),
            'payment_frequency': self.payment_frequency_input.currentText(),
            'next_due_date': self.next_due_date_input.date().toString('yyyy-MM-dd'),
            'start_date': self.start_date_input.date().toString('yyyy-MM-dd'),
            'maturity_date': self.maturity_date_input.date().toString('yyyy-MM-dd'),
            'escrow_amount': self.escrow_amount_input.value(),
            'notes': self.notes_input.toPlainText().strip(),
        }
