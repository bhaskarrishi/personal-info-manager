"""
QSS stylesheets for the application UI.
"""

# Main color scheme
PRIMARY_COLOR = "#2E7D32"  # Green
SECONDARY_COLOR = "#1B5E20"  # Dark green
ACCENT_COLOR = "#4CAF50"  # Light green
BACKGROUND_COLOR = "#F5F5F5"  # Light gray
CARD_BACKGROUND = "#FFFFFF"  # White
TEXT_COLOR = "#212121"  # Dark gray
TEXT_SECONDARY = "#757575"  # Gray
BORDER_COLOR = "#E0E0E0"  # Light gray
HOVER_COLOR = "#E8F5E9"  # Very light green
ERROR_COLOR = "#D32F2F"  # Red
SUCCESS_COLOR = "#388E3C"  # Green
WARNING_COLOR = "#F57C00"  # Orange


def get_main_stylesheet() -> str:
    """
    Get the main application stylesheet.
    
    Returns:
        str: QSS stylesheet string
    """
    return f"""
    /* Main Application Style */
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
    }}
    
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
        color: {TEXT_COLOR};
    }}
    
    /* Push Buttons */
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QPushButton:pressed {{
        background-color: {ACCENT_COLOR};
    }}
    
    QPushButton:disabled {{
        background-color: {BORDER_COLOR};
        color: {TEXT_SECONDARY};
    }}
    
    /* Secondary Buttons */
    QPushButton[class="secondary"] {{
        background-color: {CARD_BACKGROUND};
        color: {PRIMARY_COLOR};
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {HOVER_COLOR};
    }}
    
    /* Danger Buttons */
    QPushButton[class="danger"] {{
        background-color: {ERROR_COLOR};
    }}
    
    QPushButton[class="danger"]:hover {{
        background-color: #B71C1C;
    }}
    
    /* Line Edits */
    QLineEdit {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 8px;
        selection-background-color: {PRIMARY_COLOR};
    }}
    
    QLineEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    QLineEdit:disabled {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_SECONDARY};
    }}
    
    /* Text Edits */
    QTextEdit, QPlainTextEdit {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 8px;
        selection-background-color: {PRIMARY_COLOR};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
        min-width: 100px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {PRIMARY_COLOR};
    }}
    
    QComboBox:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    QComboBox::drop-down {{
        border: none;
        padding-right: 10px;
    }}
    
    QComboBox::down-arrow {{
        image: url(down_arrow.png);
        width: 12px;
        height: 12px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        selection-background-color: {HOVER_COLOR};
        selection-color: {TEXT_COLOR};
    }}
    
    /* Spin Boxes */
    QSpinBox, QDoubleSpinBox {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    /* Date Edits */
    QDateEdit {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 6px;
    }}
    
    QDateEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    QDateEdit::drop-down {{
        border: none;
        padding-right: 10px;
    }}
    
    /* Check Boxes */
    QCheckBox {{
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {BORDER_COLOR};
        border-radius: 3px;
        background-color: {CARD_BACKGROUND};
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {PRIMARY_COLOR};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {PRIMARY_COLOR};
        border-color: {PRIMARY_COLOR};
    }}
    
    /* Radio Buttons */
    QRadioButton {{
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {BORDER_COLOR};
        border-radius: 9px;
        background-color: {CARD_BACKGROUND};
    }}
    
    QRadioButton::indicator:hover {{
        border-color: {PRIMARY_COLOR};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {PRIMARY_COLOR};
        border-color: {PRIMARY_COLOR};
    }}
    
    /* Tables */
    QTableWidget {{
        background-color: {CARD_BACKGROUND};
        alternate-background-color: {BACKGROUND_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        gridline-color: {BORDER_COLOR};
    }}
    
    QTableWidget::item {{
        padding: 5px;
    }}
    
    QTableWidget::item:selected {{
        background-color: {HOVER_COLOR};
        color: {TEXT_COLOR};
    }}
    
    QHeaderView::section {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background: {BACKGROUND_COLOR};
        width: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {BORDER_COLOR};
        min-height: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_SECONDARY};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background: {BACKGROUND_COLOR};
        height: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {BORDER_COLOR};
        min-width: 20px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {TEXT_SECONDARY};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Group Boxes */
    QGroupBox {{
        border: 2px solid {BORDER_COLOR};
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        color: {PRIMARY_COLOR};
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {BORDER_COLOR};
        background-color: {CARD_BACKGROUND};
        border-radius: 4px;
    }}
    
    QTabBar::tab {{
        background-color: {BACKGROUND_COLOR};
        border: 1px solid {BORDER_COLOR};
        padding: 8px 16px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {CARD_BACKGROUND};
        border-bottom-color: {CARD_BACKGROUND};
        font-weight: bold;
    }}
    
    QTabBar::tab:hover {{
        background-color: {HOVER_COLOR};
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {CARD_BACKGROUND};
        border-bottom: 1px solid {BORDER_COLOR};
    }}
    
    QMenuBar::item {{
        padding: 6px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {HOVER_COLOR};
    }}
    
    /* Menu */
    QMenu {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
    }}
    
    QMenu::item {{
        padding: 6px 24px;
    }}
    
    QMenu::item:selected {{
        background-color: {HOVER_COLOR};
    }}
    
    /* Tool Tips */
    QToolTip {{
        background-color: {TEXT_COLOR};
        color: white;
        border: 1px solid {TEXT_COLOR};
        border-radius: 3px;
        padding: 4px;
    }}
    
    /* Labels */
    QLabel {{
        color: {TEXT_COLOR};
    }}
    
    QLabel[class="title"] {{
        font-size: 14pt;
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}
    
    QLabel[class="subtitle"] {{
        font-size: 11pt;
        color: {TEXT_SECONDARY};
    }}
    
    QLabel[class="error"] {{
        color: {ERROR_COLOR};
    }}
    
    QLabel[class="success"] {{
        color: {SUCCESS_COLOR};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        text-align: center;
        background-color: {BACKGROUND_COLOR};
    }}
    
    QProgressBar::chunk {{
        background-color: {PRIMARY_COLOR};
        border-radius: 3px;
    }}
    
    /* Dialogs */
    QDialog {{
        background-color: {CARD_BACKGROUND};
    }}
    
    /* List Widget */
    QListWidget {{
        background-color: {CARD_BACKGROUND};
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 5px;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: 3px;
    }}
    
    QListWidget::item:selected {{
        background-color: {HOVER_COLOR};
        color: {TEXT_COLOR};
    }}
    
    QListWidget::item:hover {{
        background-color: {HOVER_COLOR};
    }}
    """


def get_login_stylesheet() -> str:
    """
    Get stylesheet specific to login/signup windows.
    
    Returns:
        str: QSS stylesheet string
    """
    return get_main_stylesheet() + f"""
    QWidget#loginWidget, QWidget#signupWidget {{
        background-color: {CARD_BACKGROUND};
        border-radius: 10px;
    }}
    
    QLabel#titleLabel {{
        font-size: 18pt;
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}
    
    QPushButton#loginButton, QPushButton#signupButton {{
        min-height: 40px;
        font-size: 11pt;
    }}
    """
