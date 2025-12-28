"""
Main dashboard window with navigation and module management.
"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QStackedWidget, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.utils.styles import get_main_stylesheet

# Import module windows (will be created)
from src.modules.profile_window import ProfileWindow
from src.modules.password_vault_window import PasswordVaultWindow
from src.modules.financial_window import FinancialWindow
from src.modules.banking_window import BankingWindow
from src.modules.mortgage_window import MortgageWindow
from src.modules.credit_cards_window import CreditCardsWindow
from src.modules.insurance_window import InsuranceWindow
from src.modules.real_estate_window import RealEstateWindow
from src.modules.passport_window import PassportWindow
from src.modules.health_cards_window import HealthCardsWindow
from src.modules.services_window import ServicesWindow
from src.modules.reminders_window import RemindersWindow
from src.modules.reference_documents_window import ReferenceDocumentsWindow

logger = logging.getLogger(__name__)


class MainDashboard(QWidget):
    """
    Main dashboard with sidebar navigation and content area.
    """
    
    # Signal emitted when user requests logout
    logout_requested = pyqtSignal()
    
    def __init__(self, user_data: dict):
        """
        Initialize the main dashboard.
        
        Args:
            user_data: Dictionary containing current user information
        """
        super().__init__()
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setStyleSheet(get_main_stylesheet())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Content area (sidebar + main content)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Main content area (stacked widget for modules)
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        
        # Initialize modules
        self.init_modules()
        
        logger.info("Main dashboard initialized")
    
    def create_top_bar(self) -> QWidget:
        """
        Create the top bar with user info and logout button.
        
        Returns:
            QWidget: Top bar widget
        """
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"""
            QWidget {{
                background-color: #2E7D32;
                color: white;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # App title
        title_label = QLabel('Personal Information Manager')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # User info
        user_label = QLabel(f"Welcome, {self.user_data['username']}")
        user_font = QFont()
        user_font.setPointSize(10)
        user_label.setFont(user_font)
        layout.addWidget(user_label)
        
        # Logout button
        logout_button = QPushButton('Logout')
        logout_button.setFixedWidth(100)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.clicked.connect(self.handle_logout)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #1B5E20;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D3818;
            }
        """)
        layout.addWidget(logout_button)
        
        top_bar.setLayout(layout)
        return top_bar
    
    def create_sidebar(self) -> QWidget:
        """
        Create the sidebar navigation menu.
        
        Returns:
            QWidget: Sidebar widget
        """
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-right: 1px solid #E0E0E0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(0)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 15px 20px;
                border: none;
                color: #212121;
            }
            QListWidget::item:selected {
                background-color: #2E7D32;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #E8F5E9;
            }
        """)
        
        # Add navigation items
        nav_items = [
            'Profile',
            'Password Vault',
            'Financial Investments',
            'Banking Accounts',
            'Mortgages',
            'Credit Cards',
            'Insurance Policies',
            'Real Estate',
            'Passport/Citizenship',
            'Health Cards',
            'Services/Billing',
            'Reference Documents',
            'Reminders/To-Do'
        ]
        
        for item_text in nav_items:
            item = QListWidgetItem(item_text)
            item.setFont(QFont('Segoe UI', 10))
            self.nav_list.addItem(item)
        
        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.switch_module)
        
        layout.addWidget(self.nav_list)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def init_modules(self):
        """Initialize all module windows."""
        user_id = self.user_data['id']
        
        # Create module instances
        self.profile_window = ProfileWindow(user_id)
        self.password_vault_window = PasswordVaultWindow(user_id)
        self.financial_window = FinancialWindow(user_id)
        self.banking_window = BankingWindow(user_id)
        self.mortgage_window = MortgageWindow(user_id)
        self.credit_cards_window = CreditCardsWindow(user_id)
        self.insurance_window = InsuranceWindow(user_id)
        self.real_estate_window = RealEstateWindow(user_id)
        self.passport_window = PassportWindow(user_id)
        self.health_cards_window = HealthCardsWindow(user_id)
        self.services_window = ServicesWindow(user_id)
        self.reference_docs_window = ReferenceDocumentsWindow(user_id)
        self.reminders_window = RemindersWindow(user_id)
        
        # Add to stacked widget
        self.content_stack.addWidget(self.profile_window)
        self.content_stack.addWidget(self.password_vault_window)
        self.content_stack.addWidget(self.financial_window)
        self.content_stack.addWidget(self.banking_window)
        self.content_stack.addWidget(self.mortgage_window)
        self.content_stack.addWidget(self.credit_cards_window)
        self.content_stack.addWidget(self.insurance_window)
        self.content_stack.addWidget(self.real_estate_window)
        self.content_stack.addWidget(self.passport_window)
        self.content_stack.addWidget(self.health_cards_window)
        self.content_stack.addWidget(self.services_window)
        self.content_stack.addWidget(self.reference_docs_window)
        self.content_stack.addWidget(self.reminders_window)
        
        logger.debug("All modules initialized")
    
    def switch_module(self, index: int):
        """
        Switch to a different module.
        
        Args:
            index: Index of the module to switch to
        """
        self.content_stack.setCurrentIndex(index)
        logger.debug(f"Switched to module index: {index}")
    
    def handle_logout(self):
        """Handle logout button click."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("User confirmed logout")
            self.logout_requested.emit()
