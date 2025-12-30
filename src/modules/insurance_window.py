"""
Insurance policies management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)


class InsuranceWindow(QWidget):
    """Insurance policies management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_policies()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Insurance Policies')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Policy')
        add_button.clicked.connect(self.add_policy)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_policy)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_policy)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Type', 'Provider', 'Policy #', 'Premium', 'Coverage', 'End Date'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_policies(self):
        """Load policies from database."""
        try:
            query = """
                SELECT id, policy_type, provider, policy_number, premium_amount, coverage_amount, end_date
                FROM insurance_policies WHERE user_id = %s ORDER BY end_date
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['policy_type'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['provider'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(row_data['policy_number'] or ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(f"${row_data['premium_amount']:.2f}" if row_data['premium_amount'] else ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(f"${row_data['coverage_amount']:.2f}" if row_data['coverage_amount'] else ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem(str(row_data['end_date']) if row_data['end_date'] else ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading policies: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load policies: {str(e)}')
    
    def add_policy(self):
        """Add new policy."""
        dialog = InsuranceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO insurance_policies
                    (user_id, policy_type, provider, policy_number, premium_amount, coverage_amount, 
                     start_date, end_date, beneficiary, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['policy_type'], data['provider'], data['policy_number'],
                    data['premium_amount'], data['coverage_amount'], data['start_date'], 
                    data['end_date'], data['beneficiary'], data['notes']
                ))
                self.load_policies()
                QMessageBox.information(self, 'Success', 'Policy added successfully!')
            except Exception as e:
                logger.error(f"Error adding policy: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add policy: {str(e)}')
    
    def edit_policy(self):
        """Edit selected policy."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a policy to edit')
            return
        
        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        policy_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM insurance_policies WHERE id = %s"
            result = self.db.execute_query(query, (policy_id,), fetch=True)
            
            if result:
                dialog = InsuranceDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE insurance_policies
                        SET policy_type = %s, provider = %s, policy_number = %s,
                            premium_amount = %s, coverage_amount = %s, start_date = %s,
                            end_date = %s, beneficiary = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['policy_type'], data['provider'], data['policy_number'],
                        data['premium_amount'], data['coverage_amount'], data['start_date'],
                        data['end_date'], data['beneficiary'], data['notes'], policy_id
                    ))
                    self.load_policies()
                    QMessageBox.information(self, 'Success', 'Policy updated successfully!')
        except Exception as e:
            logger.error(f"Error editing policy: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit policy: {str(e)}')
    
    def delete_policy(self):
        """Delete selected policy."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a policy to delete')
            return
        
        policy_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this policy?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM insurance_policies WHERE id = %s", (policy_id,))
                self.load_policies()
                QMessageBox.information(self, 'Success', 'Policy deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting policy: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete policy: {str(e)}')


class InsuranceDialog(QDialog):
    """Dialog for adding/editing insurance policies."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Insurance Policy Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.type_input = QComboBox()
        self.type_input.addItems(['Life', 'Health', 'Auto', 'Home', 'Travel', 'Disability', 'Other'])
        self.type_input.setCurrentText(self.data.get('policy_type', 'Life'))
        form_layout.addRow('Policy Type*:', self.type_input)
        
        self.provider_input = QLineEdit(self.data.get('provider', ''))
        form_layout.addRow('Provider*:', self.provider_input)
        
        self.policy_number_input = QLineEdit(self.data.get('policy_number', ''))
        form_layout.addRow('Policy Number:', self.policy_number_input)
        
        self.premium_input = QDoubleSpinBox()
        self.premium_input.setMaximum(999999.99)
        self.premium_input.setPrefix('$')
        self.premium_input.setValue(float(self.data.get('premium_amount', 0)))
        form_layout.addRow('Premium Amount:', self.premium_input)
        
        self.coverage_input = QDoubleSpinBox()
        self.coverage_input.setMaximum(99999999.99)
        self.coverage_input.setPrefix('$')
        self.coverage_input.setValue(float(self.data.get('coverage_amount', 0)))
        form_layout.addRow('Coverage Amount:', self.coverage_input)
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        if self.data.get('start_date'):
            self.start_date_input.setDate(QDate.fromString(str(self.data['start_date']), 'yyyy-MM-dd'))
        else:
            self.start_date_input.setDate(QDate.currentDate())
        form_layout.addRow('Start Date:', self.start_date_input)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        if self.data.get('end_date'):
            self.end_date_input.setDate(QDate.fromString(str(self.data['end_date']), 'yyyy-MM-dd'))
        else:
            self.end_date_input.setDate(QDate.currentDate().addYears(1))
        form_layout.addRow('End Date:', self.end_date_input)
        
        self.beneficiary_input = QLineEdit(self.data.get('beneficiary', ''))
        form_layout.addRow('Beneficiary:', self.beneficiary_input)
        
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
            'policy_type': self.type_input.currentText(),
            'provider': self.provider_input.text().strip(),
            'policy_number': self.policy_number_input.text().strip(),
            'premium_amount': self.premium_input.value(),
            'coverage_amount': self.coverage_input.value(),
            'start_date': self.start_date_input.date().toString('yyyy-MM-dd'),
            'end_date': self.end_date_input.date().toString('yyyy-MM-dd'),
            'beneficiary': self.beneficiary_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
