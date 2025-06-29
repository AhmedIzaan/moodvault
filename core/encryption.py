

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# It is recommended to use a high number of iterations.
# OWASP recommends at least 100,000 for PBKDF2-HMAC-SHA256.
# We use a higher value for better security.
PBKDF2_ITERATIONS = 390000

def generate_salt():
    """Generates a cryptographically secure random salt."""
    return os.urandom(16)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a secure encryption key from a password and salt using PBKDF2.
    The key is returned in a URL-safe base64 encoded format suitable for Fernet.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

class EncryptionHandler:
    """
    Handles the encryption and decryption of diary entries using a derived key.
    An instance of this class should be created after user login and held
    for the duration of the session.
    """
    def __init__(self, key: bytes):
        """
        Initializes the handler with a Fernet instance using the provided key.
        
        Args:
            key (bytes): The URL-safe base64 encoded key derived from the user's password.
        """
        self.fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypts a plaintext string.
        
        Args:
            plaintext (str): The diary entry text to encrypt.
            
        Returns:
            bytes: The encrypted data.
        """
        return self.fernet.encrypt(plaintext.encode('utf-8'))

    def decrypt(self, encrypted_data: bytes) -> str | None:
        """
        Decrypts data.
        
        Args:
            encrypted_data (bytes): The data to decrypt.
            
        Returns:
            str: The decrypted plaintext string, or None if decryption fails
                 (e.g., wrong key, corrupted data).
        """
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            # This error occurs if the key is incorrect or the data is tampered with.
            print("Decryption failed: Invalid token. Key may be wrong or data corrupted.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during decryption: {e}")
            return None