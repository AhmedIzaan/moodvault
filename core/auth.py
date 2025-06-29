

import bcrypt
from core.db import DatabaseHandler
from core.encryption import generate_salt

class AuthHandler:
    """
    Handles user registration and login authentication.
    Works as a layer between the UI and the database for auth-related tasks.
    """
    def __init__(self, db_handler: DatabaseHandler):
        """
        Initializes the AuthHandler with a database handler instance.

        Args:
            db_handler (DatabaseHandler): An active instance of the DatabaseHandler.
        """
        self.db_handler = db_handler

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Registers a new user. Hashes the password, generates an encryption salt,
        and stores the new user in the database.

        Args:
            username (str): The desired username.
            password (str): The user's chosen password.

        Returns:
            tuple[bool, str]: A tuple containing a boolean for success
                              and a message string.
        """
        # Basic validation
        if not username or not password or len(password) < 8:
            return (False, "Username cannot be empty and password must be at least 8 characters.")

        # Check if user already exists
        if self.db_handler.get_user_hash(username):
            return (False, "Username already exists. Please choose another.")

        # 1. Hash the password with bcrypt
        password_bytes = password.encode('utf-8')
        bcrypt_salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, bcrypt_salt)

        # 2. Generate the separate salt for entry encryption
        encryption_salt = generate_salt()

        # 3. Add user to the database
        success = self.db_handler.add_user(username, password_hash, encryption_salt)

        if success:
            return (True, "Registration successful! You can now log in.")
        else:
            return (False, "An error occurred during registration. Please try again.")

    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticates a user by checking their password against the stored hash.

        Args:
            username (str): The username of the user trying to log in.
            password (str): The password provided by the user.

        Returns:
            tuple[bool, str]: A tuple containing a boolean for success
                              and a message string.
        """
        # 1. Fetch the stored hash from the database
        stored_hash = self.db_handler.get_user_hash(username)

        if not stored_hash:
            # Important: Use a generic error message to prevent username enumeration
            return (False, "Invalid username or password.")

        # 2. Check the provided password against the stored hash
        password_bytes = password.encode('utf-8')
        
        # bcrypt.checkpw handles the comparison securely
        if bcrypt.checkpw(password_bytes, stored_hash.encode('utf-8')):
            return (True, "Login successful!")
        else:
            return (False, "Invalid username or password.")