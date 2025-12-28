"""
Authentication manager for user registration, login, and password management.
"""
import bcrypt
import logging
from typing import Optional, Dict, Any
from database.db_manager import DatabaseManager
from src.utils.encryption import EncryptionManager
from src.utils.validators import validate_email, validate_username, validate_password

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Manages user authentication including registration, login, and password operations.
    """
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.db = DatabaseManager()
        self.encryption = EncryptionManager()
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to check against
        
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        
        Args:
            username: Desired username
            email: User's email address
            password: Plain text password
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            valid, error = validate_username(username)
            if not valid:
                return False, error
            
            valid, error = validate_email(email)
            if not valid:
                return False, error
            
            valid, error = validate_password(password)
            if not valid:
                return False, error
            
            # Check if username already exists
            query = "SELECT id FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,), fetch=True)
            if result:
                return False, "Username already exists"
            
            # Check if email already exists
            query = "SELECT id FROM users WHERE email = %s"
            result = self.db.execute_query(query, (email,), fetch=True)
            if result:
                return False, "Email already registered"
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """
            user_id = self.db.execute_insert(query, (username, email, password_hash))
            
            # Create empty profile for user
            profile_query = "INSERT INTO profiles (user_id) VALUES (%s)"
            self.db.execute_insert(profile_query, (user_id,))
            
            logger.info(f"User registered successfully: {username}")
            return True, "Registration successful"
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False, f"Registration failed: {str(e)}"
    
    def login(self, username_or_email: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate a user.
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
        
        Returns:
            Tuple of (success: bool, message: str, user_data: dict or None)
        """
        try:
            # Find user by username or email
            query = """
                SELECT id, username, email, password_hash
                FROM users
                WHERE username = %s OR email = %s
            """
            result = self.db.execute_query(
                query,
                (username_or_email, username_or_email),
                fetch=True
            )
            
            if not result:
                return False, "Invalid username or password", None
            
            user = result[0]
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return False, "Invalid username or password", None
            
            # Set current user
            self.current_user = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
            
            logger.info(f"User logged in successfully: {user['username']}")
            return True, "Login successful", self.current_user
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, f"Login failed: {str(e)}", None
    
    def logout(self):
        """Log out the current user."""
        if self.current_user:
            logger.info(f"User logged out: {self.current_user['username']}")
        self.current_user = None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently logged-in user.
        
        Returns:
            dict: Current user data or None
        """
        return self.current_user
    
    def is_logged_in(self) -> bool:
        """
        Check if a user is currently logged in.
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        return self.current_user is not None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
        """
        Change user's password.
        
        Args:
            user_id: User's ID
            old_password: Current password
            new_password: New password
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate new password
            valid, error = validate_password(new_password)
            if not valid:
                return False, error
            
            # Get current password hash
            query = "SELECT password_hash FROM users WHERE id = %s"
            result = self.db.execute_query(query, (user_id,), fetch=True)
            
            if not result:
                return False, "User not found"
            
            # Verify old password
            if not self.verify_password(old_password, result[0]['password_hash']):
                return False, "Current password is incorrect"
            
            # Update password
            new_hash = self.hash_password(new_password)
            update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
            self.db.execute_query(update_query, (new_hash, user_id))
            
            logger.info(f"Password changed for user ID: {user_id}")
            return True, "Password changed successfully"
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, f"Password change failed: {str(e)}"
