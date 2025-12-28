"""
Profile management window for user profile information.
"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QFormLayout, QMessageBox,
                            QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from database.db_manager import DatabaseManager
from src.utils.validators import validate_phone, sanitize_input

logger = logging.getLogger(__name__)


class ProfileWindow(QWidget):
    """
    Profile management window for viewing and editing user profile.
    """
    
    def __init__(self, user_id: int):
        """
        Initialize profile window.
        
        Args:
            user_id: Current user's ID
        """
        super().__init__()
        self.user_id = user_id
        self.db = DatabaseManager()
        self.photo_path = None
        self.init_ui()
        self.load_profile()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel('My Profile')
        title_label.setProperty('class', 'title')
        layout.addWidget(title_label)
        
        # Photo section
        photo_group = QGroupBox('Profile Photo')
        photo_layout = QVBoxLayout()
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px solid #E0E0E0;
                border-radius: 75px;
                background-color: #F5F5F5;
            }
        """)
        self.photo_label.setText('No Photo')
        photo_layout.addWidget(self.photo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        upload_button = QPushButton('Upload Photo')
        upload_button.setMaximumWidth(150)
        upload_button.clicked.connect(self.upload_photo)
        photo_layout.addWidget(upload_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        photo_group.setLayout(photo_layout)
        layout.addWidget(photo_group)
        
        # Profile information form
        info_group = QGroupBox('Personal Information')
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText('Enter full name')
        form_layout.addRow('Full Name:', self.full_name_input)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Enter phone number')
        form_layout.addRow('Phone:', self.phone_input)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText('Enter street address')
        form_layout.addRow('Address:', self.address_input)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText('Enter city')
        form_layout.addRow('City:', self.city_input)
        
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText('Enter state/province')
        form_layout.addRow('State/Province:', self.state_input)
        
        self.zip_input = QLineEdit()
        self.zip_input.setPlaceholderText('Enter ZIP/postal code')
        form_layout.addRow('ZIP/Postal Code:', self.zip_input)
        
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText('Enter country')
        form_layout.addRow('Country:', self.country_input)
        
        info_group.setLayout(form_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton('Save Changes')
        save_button.setMinimumWidth(120)
        save_button.clicked.connect(self.save_profile)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_profile(self):
        """Load profile data from database."""
        try:
            query = """
                SELECT full_name, phone, address, city, state, zip, country, photo_path
                FROM profiles
                WHERE user_id = %s
            """
            result = self.db.execute_query(query, (self.user_id,), fetch=True)
            
            if result:
                profile = result[0]
                self.full_name_input.setText(profile['full_name'] or '')
                self.phone_input.setText(profile['phone'] or '')
                self.address_input.setText(profile['address'] or '')
                self.city_input.setText(profile['city'] or '')
                self.state_input.setText(profile['state'] or '')
                self.zip_input.setText(profile['zip'] or '')
                self.country_input.setText(profile['country'] or '')
                
                # Load photo if exists
                if profile['photo_path']:
                    self.photo_path = profile['photo_path']
                    self.display_photo(profile['photo_path'])
            
            logger.info(f"Profile loaded for user ID: {self.user_id}")
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            QMessageBox.warning(self, 'Error', f'Failed to load profile: {str(e)}')
    
    def save_profile(self):
        """Save profile data to database."""
        try:
            # Validate phone number
            phone = self.phone_input.text().strip()
            if phone:
                valid, error = validate_phone(phone)
                if not valid:
                    QMessageBox.warning(self, 'Validation Error', error)
                    return
            
            # Sanitize inputs
            full_name = sanitize_input(self.full_name_input.text())
            phone = sanitize_input(phone)
            address = sanitize_input(self.address_input.text())
            city = sanitize_input(self.city_input.text())
            state = sanitize_input(self.state_input.text())
            zip_code = sanitize_input(self.zip_input.text())
            country = sanitize_input(self.country_input.text())
            
            # Update profile
            query = """
                UPDATE profiles
                SET full_name = %s, phone = %s, address = %s, city = %s,
                    state = %s, zip = %s, country = %s, photo_path = %s
                WHERE user_id = %s
            """
            self.db.execute_query(
                query,
                (full_name, phone, address, city, state, zip_code, country,
                 self.photo_path, self.user_id)
            )
            
            QMessageBox.information(self, 'Success', 'Profile updated successfully!')
            logger.info(f"Profile saved for user ID: {self.user_id}")
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to save profile: {str(e)}')
    
    def upload_photo(self):
        """Upload profile photo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Profile Photo',
            '',
            'Image Files (*.png *.jpg *.jpeg *.bmp)'
        )
        
        if file_path:
            self.photo_path = file_path
            self.display_photo(file_path)
            logger.info(f"Photo selected: {file_path}")
    
    def display_photo(self, file_path: str):
        """
        Display the profile photo.
        
        Args:
            file_path: Path to the photo file
        """
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    150, 150,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.photo_label.setPixmap(scaled_pixmap)
                self.photo_label.setScaledContents(True)
        except Exception as e:
            logger.error(f"Error displaying photo: {e}")
