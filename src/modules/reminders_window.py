"""
Reminders and to-do list management window.
"""
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from database.db_manager import DatabaseManager
from src.dialogs.confirmation_dialog import ConfirmationDialog

logger = logging.getLogger(__name__)


class RemindersWindow(QWidget):
    """Reminders and to-do list management window."""
    
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.init_ui()
        self.load_reminders()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel('Reminders & To-Do List')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_label = QLabel('Filter by Status:')
        filter_layout.addWidget(filter_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'Pending', 'Completed'])
        self.status_filter.currentTextChanged.connect(self.load_reminders)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton('Add Reminder')
        add_button.clicked.connect(self.add_reminder)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton('Edit')
        edit_button.setProperty('class', 'secondary')
        edit_button.clicked.connect(self.edit_reminder)
        button_layout.addWidget(edit_button)
        
        complete_button = QPushButton('Mark Complete')
        complete_button.clicked.connect(self.mark_complete)
        button_layout.addWidget(complete_button)
        
        delete_button = QPushButton('Delete')
        delete_button.setProperty('class', 'danger')
        delete_button.clicked.connect(self.delete_reminder)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Title', 'Description', 'Due Date', 'Priority', 'Status', 'Category'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_reminders(self):
        """Load reminders from database."""
        try:
            status_filter = self.status_filter.currentText()
            
            if status_filter == 'All':
                query = """
                    SELECT id, title, description, due_date, priority, status, category
                    FROM reminders_todos WHERE user_id = %s ORDER BY due_date
                """
                results = self.db.execute_query(query, (self.user_id,), fetch=True)
            else:
                query = """
                    SELECT id, title, description, due_date, priority, status, category
                    FROM reminders_todos WHERE user_id = %s AND status = %s ORDER BY due_date
                """
                results = self.db.execute_query(query, (self.user_id, status_filter), fetch=True)
            
            self.table.setRowCount(0)
            if results:
                for row_data in results:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    
                    self.table.setItem(row_position, 0, QTableWidgetItem(row_data['title'] or ''))
                    self.table.setItem(row_position, 1, QTableWidgetItem(row_data['description'] or ''))
                    self.table.setItem(row_position, 2, QTableWidgetItem(str(row_data['due_date']) if row_data['due_date'] else ''))
                    self.table.setItem(row_position, 3, QTableWidgetItem(row_data['priority'] or ''))
                    self.table.setItem(row_position, 4, QTableWidgetItem(row_data['status'] or ''))
                    self.table.setItem(row_position, 5, QTableWidgetItem(row_data['category'] or ''))
                    
                    self.table.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, row_data['id'])
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to load reminders: {str(e)}')
    
    def add_reminder(self):
        """Add new reminder."""
        dialog = ReminderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                query = """
                    INSERT INTO reminders_todos
                    (user_id, title, description, due_date, priority, status, category)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute_insert(query, (
                    self.user_id, data['title'], data['description'], data['due_date'],
                    data['priority'], data['status'], data['category']
                ))
                self.load_reminders()
                QMessageBox.information(self, 'Success', 'Reminder added successfully!')
            except Exception as e:
                logger.error(f"Error adding reminder: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to add reminder: {str(e)}')
    
    def edit_reminder(self):
        """Edit selected reminder."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a reminder to edit')
            return
        
        reminder_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            query = "SELECT * FROM reminders_todos WHERE id = %s"
            result = self.db.execute_query(query, (reminder_id,), fetch=True)
            
            if result:
                dialog = ReminderDialog(self, result[0])
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    data = dialog.get_data()
                    update_query = """
                        UPDATE reminders_todos
                        SET title = %s, description = %s, due_date = %s,
                            priority = %s, status = %s, category = %s
                        WHERE id = %s
                    """
                    self.db.execute_query(update_query, (
                        data['title'], data['description'], data['due_date'],
                        data['priority'], data['status'], data['category'], reminder_id
                    ))
                    self.load_reminders()
                    QMessageBox.information(self, 'Success', 'Reminder updated successfully!')
        except Exception as e:
            logger.error(f"Error editing reminder: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to edit reminder: {str(e)}')
    
    def mark_complete(self):
        """Mark selected reminder as complete."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a reminder to mark as complete')
            return
        
        reminder_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        try:
            from datetime import datetime
            query = """
                UPDATE reminders_todos
                SET status = 'Completed', completed_at = %s
                WHERE id = %s
            """
            self.db.execute_query(query, (datetime.now(), reminder_id))
            self.load_reminders()
            QMessageBox.information(self, 'Success', 'Reminder marked as completed!')
        except Exception as e:
            logger.error(f"Error marking reminder complete: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to mark reminder complete: {str(e)}')
    
    def delete_reminder(self):
        """Delete selected reminder."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'No Selection', 'Please select a reminder to delete')
            return
        
        reminder_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        dialog = ConfirmationDialog('Confirm Delete', 'Are you sure you want to delete this reminder?', self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.db.execute_query("DELETE FROM reminders_todos WHERE id = %s", (reminder_id,))
                self.load_reminders()
                QMessageBox.information(self, 'Success', 'Reminder deleted successfully!')
            except Exception as e:
                logger.error(f"Error deleting reminder: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to delete reminder: {str(e)}')


class ReminderDialog(QDialog):
    """Dialog for adding/editing reminders."""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('Reminder Entry')
        self.setModal(True)
        self.setMinimumWidth(500)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.title_input = QLineEdit(self.data.get('title', ''))
        form_layout.addRow('Title*:', self.title_input)
        
        self.description_input = QTextEdit(self.data.get('description', ''))
        self.description_input.setMaximumHeight(100)
        form_layout.addRow('Description:', self.description_input)
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        if self.data.get('due_date'):
            self.due_date_input.setDate(QDate.fromString(str(self.data['due_date']), 'yyyy-MM-dd'))
        else:
            self.due_date_input.setDate(QDate.currentDate())
        form_layout.addRow('Due Date:', self.due_date_input)
        
        self.priority_input = QComboBox()
        self.priority_input.addItems(['Low', 'Medium', 'High', 'Urgent'])
        self.priority_input.setCurrentText(self.data.get('priority', 'Medium'))
        form_layout.addRow('Priority:', self.priority_input)
        
        self.status_input = QComboBox()
        self.status_input.addItems(['Pending', 'In Progress', 'Completed'])
        self.status_input.setCurrentText(self.data.get('status', 'Pending'))
        form_layout.addRow('Status:', self.status_input)
        
        self.category_input = QComboBox()
        self.category_input.addItems(['Personal', 'Work', 'Home', 'Health', 'Finance', 'Other'])
        self.category_input.setEditable(True)
        self.category_input.setCurrentText(self.data.get('category', 'Personal'))
        form_layout.addRow('Category:', self.category_input)
        
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
            'title': self.title_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'due_date': self.due_date_input.date().toString('yyyy-MM-dd'),
            'priority': self.priority_input.currentText(),
            'status': self.status_input.currentText(),
            'category': self.category_input.currentText()
        }
