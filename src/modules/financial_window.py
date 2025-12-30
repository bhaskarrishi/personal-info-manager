"""
Financial investments tracking window.
"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QLineEdit, QMessageBox, QDialog, QFormLayout,
                            QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit,
                            QHeaderView)
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class FinancialWindow(QWidget):
    """Financial investments tracking window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_investments()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel('Financial Investments')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Investment')
        add_button.clicked.connect(self.add_investment)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_investment)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_investment)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Type', 'Institution', 'Account #', 'Amount', 'Current Value', 'Purchase Date'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_investments(self):
        """Load investments from database."""
        try:
            query = """
                SELECT id, investment_type, institution, account_number, amount, current_value, purchase_date
                FROM financial_investments WHERE user_id = %s ORDER BY purchase_date DESC
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['investment_type'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['institution'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(row_data['account_number'] or ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(f"${row_data['amount']:.2f}" if row_data['amount'] else ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(f"${row_data['current_value']:.2f}" if row_data['current_value'] else ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem(str(row_data['purchase_date']) if row_data['purchase_date'] else ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
            
            logger.info(f"Loaded {len(results) if results else 0} investments")
        except Exception as e:
            logger.error(f"Error loading investments: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load investments: {str(e)}')
    
    def add_investment(self):
        """Add new investment entry."""
        dialog = InvestmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO financial_investments
                    (user_id, investment_type, institution, account_number, amount, purchase_date, current_value, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['investment_type'], data['institution'], data['account_number'],
                    data['amount'], data['purchase_date'], data['current_value'], data['notes']
                ))
                
                self.load_investments()
                QMessageBox.information(self, 'Success', 'Investment added successfully!')
            except Exception as e:
                logger.error(f"Error adding investment: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add investment: {str(e)}')
    
    def edit_investment(self):
        """Edit selected investment."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an investment to edit')
            return
        
        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        investment_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM financial_investments WHERE id = %s"
            result = self.db.execute_query(query, (investment_id,), fetch=True)
            
            if result:
                dialog = InvestmentDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE financial_investments
                        SET investment_type = %s, institution = %s, account_number = %s,
                            amount = %s, purchase_date = %s, current_value = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['investment_type'], data['institution'], data['account_number'],
                        data['amount'], data['purchase_date'], data['current_value'], data['notes'], investment_id
                    ))
                    
                    self.load_investments()
                    QMessageBox.information(self, 'Success', 'Investment updated successfully!')
        except Exception as e:
            logger.error(f"Error editing investment: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit investment: {str(e)}')
    
    def delete_investment(self):
        """Delete selected investment."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select an investment to delete')
            return
        
        investment_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this investment?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM financial_investments WHERE id = %s", (investment_id,))
                self.load_investments()
                QMessageBox.information(self, 'Success', 'Investment deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting investment: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete investment: {str(e)}')


class InvestmentDialog(QDialog):
    """Dialog for adding/editing investments."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Investment Entry')
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
        self.type_input.addItems(['Stocks', 'Bonds', 'Mutual Funds', 'ETF', 'Real Estate', 'Crypto', 'Other'])
        self.type_input.setCurrentText(self.data.get('investment_type', 'Stocks'))
        form_layout.addRow('Investment Type*:', self.type_input)
        
        self.institution_input = QLineEdit(self.data.get('institution', ''))
        form_layout.addRow('Institution:', self.institution_input)
        
        self.account_input = QLineEdit(self.data.get('account_number', ''))
        form_layout.addRow('Account Number:', self.account_input)
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999.99)
        self.amount_input.setPrefix('$')
        self.amount_input.setValue(float(self.data.get('amount', 0)))
        form_layout.addRow('Amount*:', self.amount_input)
        
        self.current_value_input = QDoubleSpinBox()
        self.current_value_input.setMaximum(999999999.99)
        self.current_value_input.setPrefix('$')
        self.current_value_input.setValue(float(self.data.get('current_value', 0)))
        form_layout.addRow('Current Value:', self.current_value_input)
        
        self.purchase_date_input = QDateEdit()
        self.purchase_date_input.setCalendarPopup(True)
        if self.data.get('purchase_date'):
            self.purchase_date_input.setDate(QDate.fromString(str(self.data['purchase_date']), 'yyyy-MM-dd'))
        else:
            self.purchase_date_input.setDate(QDate.currentDate())
        form_layout.addRow('Purchase Date:', self.purchase_date_input)
        
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
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self) -> dict:
        """Get form data."""
        return {
            'investment_type': self.type_input.currentText(),
            'institution': self.institution_input.text().strip(),
            'account_number': self.account_input.text().strip(),
            'amount': self.amount_input.value(),
            'current_value': self.current_value_input.value(),
            'purchase_date': self.purchase_date_input.date().toString('yyyy-MM-dd'),
            'notes': self.notes_input.toPlainText().strip()
        }
