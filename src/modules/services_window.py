"""
Services and billing management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)


class ServicesWindow(QWidget):
    """Services and billing management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_services()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Services & Billing')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Service')
        add_button.clicked.connect(self.add_service)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_service)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_service)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Service Name', 'Provider', 'Amount', 'Billing Cycle', 'Due Date', 'Auto-Pay'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_services(self):
        """Load services from database."""
        try:
            query = """
                SELECT id, service_name, provider, amount, billing_cycle, due_date, auto_pay
                FROM services_billing WHERE user_id = %s ORDER BY due_date
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['service_name'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['provider'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(f"${row_data['amount']:.2f}" if row_data['amount'] else ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(row_data['billing_cycle'] or ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(str(row_data['due_date']) if row_data['due_date'] else ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem('Yes' if row_data['auto_pay'] else 'No'))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading services: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load services: {str(e)}')
    
    def add_service(self):
        """Add new service."""
        dialog = ServiceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO services_billing
                    (user_id, service_name, provider, account_number, billing_cycle, amount, due_date, auto_pay, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['service_name'], data['provider'], data['account_number'],
                    data['billing_cycle'], data['amount'], data['due_date'], data['auto_pay'], data['notes']
                ))
                self.load_services()
                QMessageBox.information(self, 'Success', 'Service added successfully!')
            except Exception as e:
                logger.error(f"Error adding service: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add service: {str(e)}')
    
    def edit_service(self):
        """Edit selected service."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a service to edit')
            return
        
        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        service_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM services_billing WHERE id = %s"
            result = self.db.execute_query(query, (service_id,), fetch=True)
            
            if result:
                dialog = ServiceDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE services_billing
                        SET service_name = %s, provider = %s, account_number = %s,
                            billing_cycle = %s, amount = %s, due_date = %s, auto_pay = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['service_name'], data['provider'], data['account_number'],
                        data['billing_cycle'], data['amount'], data['due_date'], data['auto_pay'], data['notes'], service_id
                    ))
                    self.load_services()
                    QMessageBox.information(self, 'Success', 'Service updated successfully!')
        except Exception as e:
            logger.error(f"Error editing service: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit service: {str(e)}')
    
    def delete_service(self):
        """Delete selected service."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a service to delete')
            return
        
        service_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this service?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM services_billing WHERE id = %s", (service_id,))
                self.load_services()
                QMessageBox.information(self, 'Success', 'Service deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting service: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete service: {str(e)}')


class ServiceDialog(QDialog):
    """Dialog for adding/editing services."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Service Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.service_name_input = QLineEdit(self.data.get('service_name', ''))
        form_layout.addRow('Service Name*:', self.service_name_input)
        
        self.provider_input = QLineEdit(self.data.get('provider', ''))
        form_layout.addRow('Provider:', self.provider_input)
        
        self.account_number_input = QLineEdit(self.data.get('account_number', ''))
        form_layout.addRow('Account Number:', self.account_number_input)
        
        self.billing_cycle_input = QComboBox()
        self.billing_cycle_input.addItems(['Monthly', 'Quarterly', 'Semi-Annual', 'Annual', 'One-Time', 'Other'])
        self.billing_cycle_input.setCurrentText(self.data.get('billing_cycle', 'Monthly'))
        form_layout.addRow('Billing Cycle:', self.billing_cycle_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(99999.99)
        self.amount_input.setPrefix('$')
        self.amount_input.setValue(float(self.data.get('amount', 0)))
        form_layout.addRow('Amount:', self.amount_input)
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        if self.data.get('due_date'):
            self.due_date_input.setDate(QDate.fromString(str(self.data['due_date']), 'yyyy-MM-dd'))
        else:
            self.due_date_input.setDate(QDate.currentDate())
        form_layout.addRow('Due Date:', self.due_date_input)
        
        self.auto_pay_checkbox = QCheckBox('Enabled')
        self.auto_pay_checkbox.setChecked(bool(self.data.get('auto_pay', False)))
        form_layout.addRow('Auto-Pay:', self.auto_pay_checkbox)
        
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
            'service_name': self.service_name_input.text().strip(),
            'provider': self.provider_input.text().strip(),
            'account_number': self.account_number_input.text().strip(),
            'billing_cycle': self.billing_cycle_input.currentText(),
            'amount': self.amount_input.value(),
            'due_date': self.due_date_input.date().toString('yyyy-MM-dd'),
            'auto_pay': self.auto_pay_checkbox.isChecked(),
            'notes': self.notes_input.toPlainText().strip()
        }
