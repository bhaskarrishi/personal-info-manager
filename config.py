"""
Configuration management for the Personal Information Manager application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration class that loads settings from environment variables.
    """
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'personal_info_manager')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Security configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    
    # Application configuration
    APP_NAME = 'Personal Information Manager'
    APP_VERSION = '0.1.0'
    
    # Session configuration
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    # UI configuration
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    
    @staticmethod
    def validate():
        """
        Validate that all required configuration values are set.
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'SECRET_KEY']
        missing = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    @staticmethod
    def get_db_config():
        """
        Get database configuration as a dictionary.
        
        Returns:
            dict: Database configuration parameters
        """
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }
