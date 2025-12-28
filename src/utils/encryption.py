"""
Encryption utilities for securing sensitive data.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import logging
from config import Config

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data using Fernet symmetric encryption.
    """
    
    def __init__(self):
        """Initialize encryption manager with key from config."""
        self._cipher_suite = None
        self._initialize_cipher()
    
    def _initialize_cipher(self):
        """
        Initialize the cipher suite using the secret key from configuration.
        """
        try:
            secret_key = Config.SECRET_KEY.encode()
            
            # Derive a valid Fernet key from the secret key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'personal_info_manager_salt',  # Fixed salt for consistency
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key))
            
            self._cipher_suite = Fernet(key)
            logger.info("Encryption cipher initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing encryption cipher: {e}")
            raise
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            str: Encrypted string (base64 encoded)
        
        Raises:
            Exception: If encryption fails
        """
        try:
            if not plaintext:
                return ""
            
            encrypted_bytes = self._cipher_suite.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted string.
        
        Args:
            encrypted_text: Encrypted string to decrypt
        
        Returns:
            str: Decrypted plaintext string
        
        Raises:
            Exception: If decryption fails
        """
        try:
            if not encrypted_text:
                return ""
            
            decrypted_bytes = self._cipher_suite.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list) -> dict:
        """
        Encrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary containing data
            keys_to_encrypt: List of keys whose values should be encrypted
        
        Returns:
            dict: Dictionary with specified values encrypted
        """
        encrypted_data = data.copy()
        for key in keys_to_encrypt:
            if key in encrypted_data and encrypted_data[key]:
                encrypted_data[key] = self.encrypt(str(encrypted_data[key]))
        return encrypted_data
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list) -> dict:
        """
        Decrypt specific keys in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            keys_to_decrypt: List of keys whose values should be decrypted
        
        Returns:
            dict: Dictionary with specified values decrypted
        """
        decrypted_data = data.copy()
        for key in keys_to_decrypt:
            if key in decrypted_data and decrypted_data[key]:
                try:
                    decrypted_data[key] = self.decrypt(str(decrypted_data[key]))
                except Exception as e:
                    logger.warning(f"Failed to decrypt key '{key}': {e}")
                    decrypted_data[key] = "[Decryption Failed]"
        return decrypted_data


def generate_key() -> str:
    """
    Generate a new Fernet encryption key.
    
    Returns:
        str: Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()
