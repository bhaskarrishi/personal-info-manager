"""
Passport and citizenship documents management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class PassportWindow(QWidget):
    """Passport and citizenship documents management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_documents()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Passport & Citizenship Documents')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Document')
        add_button.clicked.connect(self.add_document)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_document)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_document)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Family Member', 'Relationship', 'Document Type', 'Document #', 'Issue Date', 'Expiry Date'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_documents(self):
        """Load documents from database."""
        try:
            query = """
                SELECT id, family_member_name, relationship, document_type, document_number, issue_date, expiry_date
                FROM passports_citizenship WHERE user_id = %s ORDER BY expiry_date
            """
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['family_member_name'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['relationship'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(row_data['document_type'] or ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(row_data['document_number'] or ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(str(row_data['issue_date']) if row_data['issue_date'] else ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem(str(row_data['expiry_date']) if row_data['expiry_date'] else ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load documents: {str(e)}')
    
    def add_document(self):
        """Add new document."""
        dialog = PassportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO passports_citizenship
                    (user_id, family_member_name, relationship, document_type, document_number, 
                     issue_date, expiry_date, issuing_country, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['family_member_name'], data['relationship'], data['document_type'],
                    data['document_number'], data['issue_date'], data['expiry_date'], 
                    data['issuing_country'], data['notes']
                ))
                self.load_documents()
                QMessageBox.information(self, 'Success', 'Document added successfully!')
            except Exception as e:
                logger.error(f"Error adding document: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add document: {str(e)}')
    
    def edit_document(self):
        """Edit selected document."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a document to edit')
            return
        
        doc_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM passports_citizenship WHERE id = %s"
            result = self.db.execute_query(query, (doc_id,), fetch=True)
            
            if result:
                dialog = PassportDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE passports_citizenship
                        SET family_member_name = %s, relationship = %s, document_type = %s,
                            document_number = %s, issue_date = %s, expiry_date = %s,
                            issuing_country = %s, notes = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['family_member_name'], data['relationship'], data['document_type'],
                        data['document_number'], data['issue_date'], data['expiry_date'],
                        data['issuing_country'], data['notes'], doc_id
                    ))
                    self.load_documents()
                    QMessageBox.information(self, 'Success', 'Document updated successfully!')
        except Exception as e:
            logger.error(f"Error editing document: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit document: {str(e)}')
    
    def delete_document(self):
        """Delete selected document."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a document to delete')
            return
        
        doc_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this document?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM passports_citizenship WHERE id = %s", (doc_id,))
                self.load_documents()
                QMessageBox.information(self, 'Success', 'Document deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete document: {str(e)}')


class PassportDialog(QDialog):
    """Dialog for adding/editing passport/citizenship documents."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Document Entry')
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
        
        self.document_type_input = QComboBox()
        self.document_type_input.addItems(['Passport', 'Citizenship Certificate', 'Visa', 'Residence Permit', 'Other'])
        self.document_type_input.setCurrentText(self.data.get('document_type', 'Passport'))
        form_layout.addRow('Document Type*:', self.document_type_input)
        
        self.document_number_input = QLineEdit(self.data.get('document_number', ''))
        form_layout.addRow('Document Number:', self.document_number_input)
        
        self.issue_date_input = QDateEdit()
        self.issue_date_input.setCalendarPopup(True)
        if self.data.get('issue_date'):
            self.issue_date_input.setDate(QDate.fromString(str(self.data['issue_date']), 'yyyy-MM-dd'))
        else:
            self.issue_date_input.setDate(QDate.currentDate())
        form_layout.addRow('Issue Date:', self.issue_date_input)
        
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        if self.data.get('expiry_date'):
            self.expiry_date_input.setDate(QDate.fromString(str(self.data['expiry_date']), 'yyyy-MM-dd'))
        else:
            self.expiry_date_input.setDate(QDate.currentDate().addYears(10))
        form_layout.addRow('Expiry Date:', self.expiry_date_input)
        
        self.issuing_country_input = QLineEdit(self.data.get('issuing_country', ''))
        form_layout.addRow('Issuing Country:', self.issuing_country_input)
        
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
            'document_type': self.document_type_input.currentText(),
            'document_number': self.document_number_input.text().strip(),
            'issue_date': self.issue_date_input.date().toString('yyyy-MM-dd'),
            'expiry_date': self.expiry_date_input.date().toString('yyyy-MM-dd'),
            'issuing_country': self.issuing_country_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
