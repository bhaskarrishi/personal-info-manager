"""
Social Insurance Details management window.
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
    QTextEdit,
    QHeaderView,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)

INSURANCE_TYPES = ['Social Security', 'National Insurance', 'Medicare', 'Pension', 'Disability', 'Unemployment', 'Other']


class SocialInsuranceWindow(QWidget):
    """Social insurance details management window."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.show_sensitive = False
        self.init_ui()
        self.load_records()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel('Social Insurance Details')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)

        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Record')
        add_button.clicked.connect(self.add_record)
        button_layout.addWidget(add_button)

        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_record)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_record)
        button_layout.addWidget(delete_button)

        self.toggle_sensitive_btn = QPushButton('Show Sensitive Data')
        self.toggle_sensitive_btn.setProperty('class', 'secondary')
        self.toggle_sensitive_btn.clicked.connect(self.toggle_sensitive_data)
        button_layout.addWidget(self.toggle_sensitive_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Family Member', 'Insurance Type', 'Number', 'Country', 'Issued Date', 'Expiry Date'
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
        self.load_records()

    def load_records(self):
        try:
            query = (
                """
                SELECT id, family_member_name, insurance_type, insurance_number, country,
                       issue_date, expiry_date
                FROM social_insurance
                WHERE user_id = %s
                ORDER BY family_member_name
                """
            )
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            self.table.setRowCount(0)
            if results:
                for row in results:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)

                    self.table.setItem(row_pos, 0, QTableWidgetItem(row['family_member_name'] or ''))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(row['insurance_type'] or ''))
                    
                    # Mask sensitive insurance number unless showing
                    insurance_num = row['insurance_number'] or ''
                    if not self.show_sensitive and insurance_num and len(insurance_num) > 4:
                        insurance_num = '****' + insurance_num[-4:]
                    self.table.setItem(row_pos, 2, QTableWidgetItem(insurance_num))
                    
                    self.table.setItem(row_pos, 3, QTableWidgetItem(row['country'] or ''))
                    self.table.setItem(
                        row_pos, 4, QTableWidgetItem(str(row['issue_date']) if row['issue_date'] else '')
                    )
                    self.table.setItem(
                        row_pos, 5, QTableWidgetItem(str(row['expiry_date']) if row['expiry_date'] else '')
                    )

                    self.table.item(row_pos, 0).setData(Qt.ItemDataRole.UserRole, row['id'])
        except Exception as e:
            logger.error(f"Error loading social insurance records: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load records: {str(e)}')

    def add_record(self):
        dialog = SocialInsuranceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = (
                    """
                    INSERT INTO social_insurance
                    (user_id, family_member_name, relationship, insurance_type, insurance_number,
                     country, issue_date, expiry_date, issuing_authority, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )
                self.db.execute_insert(
                    query,
                    (
                        self.user_id,
                        data['family_member_name'],
                        data['relationship'],
                        data['insurance_type'],
                        data['insurance_number'],
                        data['country'],
                        data['issue_date'],
                        data['expiry_date'],
                        data['issuing_authority'],
                        data['notes'],
                    ),
                )
                self.load_records()
                QMessageBox.information(self, 'Success', 'Record added successfully!')
            except Exception as e:
                logger.error(f"Error adding record: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add record: {str(e)}')

    def edit_record(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a record to edit')
            return

        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        record_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            result = self.db.execute_query("SELECT * FROM social_insurance WHERE id = %s", (record_id,), fetch=True)
            if result:
                dialog = SocialInsuranceDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = (
                        """
                        UPDATE social_insurance
                        SET family_member_name = %s, relationship = %s, insurance_type = %s,
                            insurance_number = %s, country = %s, issue_date = %s, expiry_date = %s,
                            issuing_authority = %s, notes = %s
                        WHERE id = %s
                        """
                    )
                    self.db.execute_query(
                        update_query,
                        (
                            data['family_member_name'],
                            data['relationship'],
                            data['insurance_type'],
                            data['insurance_number'],
                            data['country'],
                            data['issue_date'],
                            data['expiry_date'],
                            data['issuing_authority'],
                            data['notes'],
                            record_id,
                        ),
                    )
                    self.load_records()
                    QMessageBox.information(self, 'Success', 'Record updated successfully!')
        except Exception as e:
            logger.error(f"Error editing record: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit record: {str(e)}')

    def delete_record(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a record to delete')
            return

        record_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Verify password before deletion
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        dialog = ConfirmationDialog(
            'Confirm Delete', 
            'Are you sure you want to permanently delete this record?\n\nThis action cannot be undone.',
            self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM social_insurance WHERE id = %s", (record_id,))
                self.load_records()
                QMessageBox.information(self, 'Success', 'Record deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting record: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete record: {str(e)}')


class SocialInsuranceDialog(QDialog):
    """Dialog for adding/editing social insurance records."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Social Insurance Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.family_member_input = QLineEdit(self.data.get('family_member_name', ''))
        form_layout.addRow('Family Member*:', self.family_member_input)

        self.relationship_input = QComboBox()
        self.relationship_input.addItems(['Self', 'Spouse', 'Child', 'Parent', 'Sibling', 'Other'])
        self.relationship_input.setCurrentText(self.data.get('relationship', 'Self'))
        form_layout.addRow('Relationship:', self.relationship_input)

        self.insurance_type_input = QComboBox()
        self.insurance_type_input.addItems(INSURANCE_TYPES)
        self.insurance_type_input.setCurrentText(self.data.get('insurance_type', INSURANCE_TYPES[0]))
        form_layout.addRow('Insurance Type*:', self.insurance_type_input)

        self.insurance_number_input = QLineEdit(self.data.get('insurance_number', ''))
        form_layout.addRow('Insurance Number*:', self.insurance_number_input)

        self.country_input = QLineEdit(self.data.get('country', ''))
        form_layout.addRow('Country:', self.country_input)

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

        self.issuing_authority_input = QLineEdit(self.data.get('issuing_authority', ''))
        form_layout.addRow('Issuing Authority:', self.issuing_authority_input)

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
            'family_member_name': self.family_member_input.text().strip(),
            'relationship': self.relationship_input.currentText(),
            'insurance_type': self.insurance_type_input.currentText(),
            'insurance_number': self.insurance_number_input.text().strip(),
            'country': self.country_input.text().strip(),
            'issue_date': self.issue_date_input.date().toString('yyyy-MM-dd'),
            'expiry_date': self.expiry_date_input.date().toString('yyyy-MM-dd'),
            'issuing_authority': self.issuing_authority_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip(),
        }
