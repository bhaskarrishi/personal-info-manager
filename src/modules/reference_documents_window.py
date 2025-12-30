"""
Reference documents management window (upload, view, download).
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
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QFileDialog,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QDate, QUrl
from PyQt6.QtGui import QDesktopServices
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog
from src.dialogs.password_verification_dialog import PasswordVerificationDialog

logger = logging.getLogger(__name__)
UPLOAD_ROOT = Path('storage/uploads')


class ReferenceDocumentsWindow(QWidget):
    """Reference documents management window."""

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_documents()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel('Reference Documents')
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

        open_button = QPushButton('Open')
        open_button.setProperty('class', 'secondary')
        open_button.clicked.connect(self.open_document)
        button_layout.addWidget(open_button)

        download_button = QPushButton('Save Copy')
        download_button.setProperty('class', 'secondary')
        download_button.clicked.connect(self.save_copy)
        button_layout.addWidget(download_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Title', 'Type', 'Country', 'Issue Date', 'Expiry Date', 'File'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_documents(self):
        try:
            query = (
                """
                SELECT id, title, document_type, country, issue_date, expiry_date, file_path
                FROM reference_documents
                WHERE user_id = %s
                ORDER BY title
                """
            )
            results = self.db.execute_query(query, (self.user_id,), fetch=True)
            self.table.setRowCount(0)
            if results:
                for row in results:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)

                    self.table.setItem(row_pos, 0, QTableWidgetItem(row['title'] or ''))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(row['document_type'] or ''))
                    self.table.setItem(row_pos, 2, QTableWidgetItem(row['country'] or ''))
                    self.table.setItem(
                        row_pos, 3, QTableWidgetItem(str(row['issue_date']) if row['issue_date'] else '')
                    )
                    self.table.setItem(
                        row_pos, 4, QTableWidgetItem(str(row['expiry_date']) if row['expiry_date'] else '')
                    )
                    file_name = Path(row['file_path']).name if row['file_path'] else ''
                    self.table.setItem(row_pos, 5, QTableWidgetItem(file_name))

                    self.table.item(row_pos, 0).setData(Qt.ItemDataRole.UserRole, row['id'])
                    self.table.item(row_pos, 5).setData(Qt.ItemDataRole.UserRole, row['file_path'])
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load documents: {str(e)}')

    def add_document(self):
        dialog = DocumentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['title'] or not data['file_path']:
                QMessageBox.warning(self, 'Missing Data', 'Title and file are required')
                return
            try:
                stored_path = self._store_file(data['file_path'])
                query = (
                    """
                    INSERT INTO reference_documents
                    (user_id, title, document_type, description, file_path, country, issued_by,
                     issue_date, expiry_date, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                )
                self.db.execute_insert(
                    query,
                    (
                        self.user_id,
                        data['title'],
                        data['document_type'],
                        data['description'],
                        stored_path,
                        data['country'],
                        data['issued_by'],
                        data['issue_date'],
                        data['expiry_date'],
                        data['tags'],
                    ),
                )
                self.load_documents()
                QMessageBox.information(self, 'Success', 'Document added successfully!')
            except Exception as e:
                logger.error(f"Error adding document: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add document: {str(e)}')

    def edit_document(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a document to edit')
            return

        # Verify password before editing
        pwd_dialog = PasswordVerificationDialog(self.db, self.user_id, self)
        if pwd_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        doc_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            result = self.db.execute_query("SELECT * FROM reference_documents WHERE id = %s", (doc_id,), fetch=True)
            if result:
                dialog = DocumentDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    if not data['title']:
                        QMessageBox.warning(self, 'Missing Data', 'Title is required')
                        return
                    stored_path = result[0]['file_path']
                    if data['file_path']:
                        stored_path = self._store_file(data['file_path'])

                    update_query = (
                        """
                        UPDATE reference_documents
                        SET title = %s, document_type = %s, description = %s, file_path = %s,
                            country = %s, issued_by = %s, issue_date = %s, expiry_date = %s, tags = %s
                        WHERE id = %s
                        """
                    )
                    self.db.execute_query(
                        update_query,
                        (
                            data['title'],
                            data['document_type'],
                            data['description'],
                            stored_path,
                            data['country'],
                            data['issued_by'],
                            data['issue_date'],
                            data['expiry_date'],
                            data['tags'],
                            doc_id,
                        ),
                    )
                    self.load_documents()
                    QMessageBox.information(self, 'Success', 'Document updated successfully!')
        except Exception as e:
            logger.error(f"Error editing document: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit document: {str(e)}')

    def delete_document(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a document to delete')
            return

        doc_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = ConfirmationDialog('Confirm Delete', 'Delete this document record?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM reference_documents WHERE id = %s", (doc_id,))
                self.load_documents()
                QMessageBox.information(self, 'Success', 'Document deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting document: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete document: {str(e)}')

    def open_document(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Select a document to open')
            return

        file_path = self.table.item(current_row, 5).data(Qt.ItemDataRole.UserRole)
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, 'File Missing', 'Stored file path is not accessible')
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(file_path).resolve())))

    def save_copy(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Select a document to save a copy')
            return

        file_path = self.table.item(current_row, 5).data(Qt.ItemDataRole.UserRole)
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, 'File Missing', 'Stored file path is not accessible')
            return

        dest_path, _ = QFileDialog.getSaveFileName(self, 'Save a Copy', Path(file_path).name)
        if dest_path:
            try:
                shutil.copy2(file_path, dest_path)
                QMessageBox.information(self, 'Saved', 'Copy saved successfully')
            except Exception as e:
                logger.error(f"Error saving copy: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to save copy: {str(e)}')

    def _store_file(self, source_path: str) -> str:
        """Copy file into storage/uploads/user_x and return stored path."""
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError('Selected file no longer exists')

        user_dir = UPLOAD_ROOT / f'user_{self.user_id}'
        user_dir.mkdir(parents=True, exist_ok=True)

        dest = user_dir / src.name
        counter = 1
        while dest.exists():
            dest = user_dir / f"{dest.stem}_{counter}{dest.suffix}"
            counter += 1

        shutil.copy2(src, dest)
        return str(dest)


class DocumentDialog(QDialog):
    """Dialog for adding/editing reference documents."""

    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Reference Document')
        self.setModal(True)
        self.setMinimumWidth(520)
        self.data = data or {}
        self.selected_file_path = ''
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.title_input = QLineEdit(self.data.get('title', ''))
        form_layout.addRow('Title*:', self.title_input)

        self.type_input = QLineEdit(self.data.get('document_type', ''))
        form_layout.addRow('Document Type:', self.type_input)

        self.country_input = QLineEdit(self.data.get('country', ''))
        form_layout.addRow('Country:', self.country_input)

        self.issued_by_input = QLineEdit(self.data.get('issued_by', ''))
        form_layout.addRow('Issued By:', self.issued_by_input)

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
            self.expiry_date_input.setDate(QDate.currentDate().addYears(5))
        form_layout.addRow('Expiry Date:', self.expiry_date_input)

        self.tags_input = QLineEdit(self.data.get('tags', ''))
        form_layout.addRow('Tags:', self.tags_input)

        self.description_input = QTextEdit(self.data.get('description', ''))
        self.description_input.setMaximumHeight(100)
        form_layout.addRow('Description:', self.description_input)

        file_select_layout = QHBoxLayout()
        self.file_label = QLabel(self.data.get('file_path', 'No file selected'))
        file_button = QPushButton('Select File')
        file_button.clicked.connect(self.pick_file)
        file_select_layout.addWidget(self.file_label)
        file_select_layout.addWidget(file_button)
        form_layout.addRow('File*:', file_select_layout)

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

    def pick_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Document',
            '',
            'Documents (*.pdf *.doc *.docx *.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*.*)'
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(Path(file_path).name)

    def get_data(self) -> dict:
        file_path = self.selected_file_path or self.data.get('file_path', '')
        return {
            'title': self.title_input.text().strip(),
            'document_type': self.type_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'file_path': file_path,
            'country': self.country_input.text().strip(),
            'issued_by': self.issued_by_input.text().strip(),
            'issue_date': self.issue_date_input.date().toString('yyyy-MM-dd'),
            'expiry_date': self.expiry_date_input.date().toString('yyyy-MM-dd'),
            'tags': self.tags_input.text().strip(),
        }
