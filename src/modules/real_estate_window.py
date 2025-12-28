"""
Real estate properties management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class RealEstateWindow(QWidget):
    """Real estate properties management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_properties()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Real Estate Properties')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Property')
        add_button.clicked.connect(self.add_property)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_property)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_property)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Type', 'Address', 'Purchase Price', 'Current Value', 'Purchase Date'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_properties(self):
        """Load properties from database."""
        try:
            query = """
                SELECT id, property_type, address, purchase_price, current_value, purchase_date
                FROM real_estate WHERE user_id = %s ORDER BY purchase_date DESC
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['property_type'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['address'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(f"${row_data['purchase_price']:.2f}" if row_data['purchase_price'] else ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(f"${row_data['current_value']:.2f}" if row_data['current_value'] else ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(str(row_data['purchase_date']) if row_data['purchase_date'] else ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading properties: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load properties: {str(e)}')
    
    def add_property(self):
        """Add new property."""
        dialog = RealEstateDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO real_estate
                    (user_id, property_type, address, purchase_date, purchase_price, current_value, mortgage_details, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['property_type'], data['address'], data['purchase_date'],
                    data['purchase_price'], data['current_value'], data['mortgage_details'], data['notes']
                ))
                self.load_properties()
                QMessageBox.information(self, 'Success', 'Property added successfully!')
            except Exception as e:
                logger.error(f"Error adding property: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add property: {str(e)}')
    
    def edit_property(self):
        """Edit selected property."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a property to edit')
            return
        
        property_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM real_estate WHERE id = %s"
            result = self.db.execute_query(query, (property_id,), fetch=True)
            
            if result:
                dialog = RealEstateDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE real_estate
                        SET property_type = %s, address = %s, purchase_date = %s,
                            purchase_price = %s, current_value = %s, mortgage_details = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['property_type'], data['address'], data['purchase_date'],
                        data['purchase_price'], data['current_value'], data['mortgage_details'], data['notes'], property_id
                    ))
                    self.load_properties()
                    QMessageBox.information(self, 'Success', 'Property updated successfully!')
        except Exception as e:
            logger.error(f"Error editing property: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit property: {str(e)}')
    
    def delete_property(self):
        """Delete selected property."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a property to delete')
            return
        
        property_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this property?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM real_estate WHERE id = %s", (property_id,))
                self.load_properties()
                QMessageBox.information(self, 'Success', 'Property deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting property: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete property: {str(e)}')


class RealEstateDialog(QDialog):
    """Dialog for adding/editing real estate properties."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Property Entry')
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
        self.type_input.addItems(['House', 'Apartment', 'Condo', 'Land', 'Commercial', 'Other'])
        self.type_input.setCurrentText(self.data.get('property_type', 'House'))
        form_layout.addRow('Property Type*:', self.type_input)
        
        self.address_input = QLineEdit(self.data.get('address', ''))
        form_layout.addRow('Address*:', self.address_input)
        
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setMaximum(99999999.99)
        self.purchase_price_input.setPrefix('$')
        self.purchase_price_input.setValue(float(self.data.get('purchase_price', 0)))
        form_layout.addRow('Purchase Price:', self.purchase_price_input)
        
        self.current_value_input = QDoubleSpinBox()
        self.current_value_input.setMaximum(99999999.99)
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
        
        self.mortgage_input = QTextEdit(self.data.get('mortgage_details', ''))
        self.mortgage_input.setMaximumHeight(80)
        form_layout.addRow('Mortgage Details:', self.mortgage_input)
        
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
        """Get form data."""
        return {
            'property_type': self.type_input.currentText(),
            'address': self.address_input.text().strip(),
            'purchase_price': self.purchase_price_input.value(),
            'current_value': self.current_value_input.value(),
            'purchase_date': self.purchase_date_input.date().toString('yyyy-MM-dd'),
            'mortgage_details': self.mortgage_input.toPlainText().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
