# MoodVault/ui_auth.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

class AuthDialog(QDialog):
    """Base class for authentication dialogs with shared styling and structure."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MoodVault Authentication")
        self.setModal(True) # Blocks interaction with other windows
        self.layout = QVBoxLayout(self)
        
        # We will add widgets in the child classes
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        # To be populated by child classes
        self.setup_ui()

    def setup_ui(self):
        """Placeholder for UI setup in child classes."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_credentials(self):
        """Returns the entered username and password."""
        return self.username_edit.text().strip(), self.password_edit.text()

class LoginDialog(AuthDialog):
    """The dialog window for user login."""
    def setup_ui(self):
        self.setWindowTitle("Login to MoodVault")
        
        # Add widgets
        self.layout.addWidget(QLabel("Username:"))
        self.layout.addWidget(self.username_edit)
        self.username_edit.setPlaceholderText("Enter your username")
        
        self.layout.addWidget(QLabel("Master Password:"))
        self.layout.addWidget(self.password_edit)
        self.password_edit.setPlaceholderText("Enter your password")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Unlock")
        self.login_button.clicked.connect(self.accept) # `accept` closes the dialog with a "success" signal
        
        self.cancel_button = QPushButton("Exit")
        self.cancel_button.clicked.connect(self.reject) # `reject` closes with a "failure" signal
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        self.layout.addLayout(button_layout)
        
        self.login_button.setDefault(True)


class RegisterDialog(AuthDialog):
    """The dialog window for first-time user registration."""
    def setup_ui(self):
        self.setWindowTitle("Create Your MoodVault Account")
        
        self.password_confirm_edit = QLineEdit()
        self.password_confirm_edit.setEchoMode(QLineEdit.Password)
        
        # Add widgets
        self.layout.addWidget(QLabel("Choose a Username:"))
        self.layout.addWidget(self.username_edit)
        self.username_edit.setPlaceholderText("e.g., 'myjournal'")
        
        self.layout.addWidget(QLabel("Create a Master Password (min. 8 characters):"))
        self.layout.addWidget(self.password_edit)
        self.password_edit.setPlaceholderText("This will encrypt all your data. Do not forget it!")

        self.layout.addWidget(QLabel("Confirm Master Password:"))
        self.layout.addWidget(self.password_confirm_edit)
        
        # Buttons
        self.register_button = QPushButton("Create Account")
        self.register_button.clicked.connect(self.validate_and_accept)
        self.layout.addWidget(self.register_button)

        self.register_button.setDefault(True)

    def validate_and_accept(self):
        """Check if passwords match before accepting."""
        user, pw1 = self.get_credentials()
        pw2 = self.password_confirm_edit.text()
        
        if len(pw1) < 8:
            QMessageBox.warning(self, "Password Too Short", "Your master password must be at least 8 characters long.")
            return

        if pw1 != pw2:
            QMessageBox.warning(self, "Passwords Mismatch", "The passwords you entered do not match. Please try again.")
            return
        
        # If all checks pass, accept the dialog
        self.accept()

