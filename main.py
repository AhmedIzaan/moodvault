# MoodVault/main.py

import sys
from datetime import date
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

# Import from our packages
from core.db import DatabaseHandler
from core.auth import AuthHandler
from core.encryption import EncryptionHandler, derive_key
from core.sentiment import SentimentAnalyzer
from ui.ui_auth import LoginDialog, RegisterDialog
from ui.ui import MainWindow

class MoodVaultApp:
    def __init__(self):
        # Initialize all backend handlers
        self.db_handler = DatabaseHandler()
        self.auth_handler = AuthHandler(self.db_handler)
        self.sentiment_analyzer = SentimentAnalyzer()

        # These will be initialized after successful login
        self.enc_handler = None
        self.main_window = None
        self.current_user_id = None
        self.current_username = None

    def run(self):
        """Starts the application execution flow."""
        app = QApplication(sys.argv)

        initial_user_id = self.db_handler.get_first_user_id()

        if not initial_user_id:
            if not self.show_registration_dialog():
                sys.exit()
        
        while not self.current_username:
            if not self.show_login_dialog():
                sys.exit()

        # --- If we get here, login was successful ---
        
        # Now launch the main application window
        self.main_window = MainWindow(username=self.current_username)
        self._connect_signals()
        self.main_window.show()
        
        # Load today's entry by default when the app opens
        self._load_entry_for_date()

        sys.exit(app.exec_())

    def show_registration_dialog(self):
        dialog = RegisterDialog()
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            success, message = self.auth_handler.register_user(username, password)
            QMessageBox.information(None, "Registration", message)
            if success:
                # Automatically log in after successful registration
                self.current_username = username
                self._post_login_setup(password)
            return success
        return False

    def show_login_dialog(self):
        dialog = LoginDialog()
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            success, message = self.auth_handler.login_user(username, password)
            if success:
                self.current_username = username
                self._post_login_setup(password)
                return True
            else:
                QMessageBox.warning(None, "Login Failed", message)
                return False
        return False

    def _post_login_setup(self, password):
        """Initializes user-specific handlers after a successful login."""
        self.current_user_id = self.db_handler.get_user_id(self.current_username)
        salt = self.db_handler.get_user_salt(self.current_username)
        key = derive_key(password, salt)
        self.enc_handler = EncryptionHandler(key)

    # --- Connector and Handler Methods ---

    def _connect_signals(self):
        """Connects UI element signals to the appropriate handler methods."""
        self.main_window.calendar.selectionChanged.connect(self._load_entry_for_date)
        self.main_window.save_action.triggered.connect(self._save_entry)
        self.main_window.analyze_action.triggered.connect(self._analyze_mood)
        # self.main_window.stats_action will be connected later

    def _load_entry_for_date(self):
        """Loads and decrypts a diary entry for the selected date."""
        selected_date = self.main_window.calendar.selectedDate().toPyDate()
        encrypted_entry, mood_label = self.db_handler.get_entry_by_date(self.current_user_id, selected_date)

        if encrypted_entry:
            decrypted_text = self.enc_handler.decrypt(encrypted_entry)
            self.main_window.entry_editor.setText(decrypted_text)
            self.main_window.status_bar.showMessage(f"Mood for this day: {mood_label}")
        else:
            self.main_window.entry_editor.clear()
            self.main_window.status_bar.showMessage("No entry for this date. Write something new!")

    def _analyze_mood(self):
        """Analyzes the current text in the editor and updates the status bar."""
        text = self.main_window.entry_editor.toPlainText()
        if not text:
            self.main_window.status_bar.showMessage("Cannot analyze empty entry.")
            return
        
        mood_label, score = self.sentiment_analyzer.analyze(text)
        self.main_window.status_bar.showMessage(f"Detected Mood: {mood_label} (Score: {score:.2f})")

    def _save_entry(self):
        """Encrypts and saves the current entry to the database."""
        text_to_save = self.main_window.entry_editor.toPlainText()
        if not text_to_save:
            QMessageBox.warning(self.main_window, "Empty Entry", "Cannot save an empty entry.")
            return

        # Get mood from status bar or re-analyze
        self._analyze_mood() # Ensure mood is up-to-date before saving
        mood_label, score = self.sentiment_analyzer.analyze(text_to_save)
        
        encrypted_data = self.enc_handler.encrypt(text_to_save)
        selected_date = self.main_window.calendar.selectedDate().toPyDate()

        success = self.db_handler.add_or_update_entry(
            self.current_user_id, selected_date, encrypted_data, mood_label, score
        )

        if success:
            QMessageBox.information(self.main_window, "Success", "Entry saved securely.")
        else:
            QMessageBox.critical(self.main_window, "Error", "Failed to save entry.")


if __name__ == '__main__':
    main_app = MoodVaultApp()
    main_app.run()