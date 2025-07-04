

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
        try:
            with open("assets/style.qss", "r") as f:
                app.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet 'assets/style.qss' not found.")

        while True: 
            # Reset user state for a fresh login
            self.current_username = None
            self.current_user_id = None
            self.enc_handler = None
            
            state = "login"
            if not self.db_handler.get_first_user_id():
                state = "register"

            # Inner loop for handling login/register attempts
            while not self.current_username:
                if state == "register":
                    if not self.show_registration_dialog():
                        sys.exit() # Exit if user cancels initial registration
                    state = "login" # After registration, proceed to login
                
                elif state == "login":
                    login_success, wants_register, was_cancelled = self.show_login_dialog()

                    if login_success:
                        break # Success, exit the loop and launch the main app
                    
                    if wants_register:
                        state = "register" # Switch to registration mode and loop again
                        continue
                    
                    if was_cancelled:
                        sys.exit() # User explicitly cancelled, so exit
                
                # If we reach here, it was just a failed login attempt.
                # The loop will automatically repeat, showing the dialog again.

            # If we get here, login was successful
            self.main_window = MainWindow(username=self.current_username)
            self._connect_signals()
            self.main_window.show()
            
            # Load today's entry by default
            self._load_entry_for_date()

            # Start the Qt event loop. This blocks until the main window is closed.
            app.exec_()
            
            # When app.exec_() finishes (i.e., window is closed), the code continues.
            # If the closure was NOT initiated by the logout button, we should exit.
            if not hasattr(self, '_logout_initiated') or not self._logout_initiated:
                break # Exit the outer while loop, terminating the app.
            
            # If it was a logout, the loop will continue, showing the login screen.
    
    def _logout(self):
        """Handles the user logout process."""
        # Set a flag to indicate logout was intentional
        self._logout_initiated = True
        # Close the main window, which will allow the run loop to continue
        self.main_window.close()

    def show_registration_dialog(self):
        """Shows the registration dialog and handles user creation."""
        dialog = RegisterDialog()
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            success, message = self.auth_handler.register_user(username, password)
            QMessageBox.information(None, "Registration", message)
            # We no longer auto-login here. User must now log in.
            return True # Just signal that registration was attempted
        return False # User cancelled

    def show_login_dialog(self):
        """
        Shows the login dialog and handles authentication.
        Returns:
            tuple[bool, bool, bool]: A tuple of (login_success, wants_to_register, was_cancelled)
        """
        dialog = LoginDialog()
        result = dialog.exec_()

        if result == QDialog.Accepted:
            # User clicked "Unlock"
            username, password = dialog.get_credentials()
            success, message = self.auth_handler.login_user(username, password)
            if success:
                self.current_username = username
                self._post_login_setup(password)
                return True, False, False # (login_success=True, wants_register=False, was_cancelled=False)
            else:
                QMessageBox.warning(None, "Login Failed", message)
                return False, False, False # (login_success=False, ...)
        
        # User closed dialog or clicked a button that calls reject()
        if dialog.wants_to_register:
            return False, True, False # (..., wants_to_register=True, ...)
        
        # If we get here, the user must have cancelled (e.g., hit 'Exit' or closed the window)
        return False, False, True # (..., ..., was_cancelled=True)

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
        self.main_window.stats_action.triggered.connect(self._show_stats_placeholder) 
        self.main_window.logout_action.triggered.connect(self._logout)

 
    def _load_entry_for_date(self):
        """Loads and decrypts a diary entry for the selected date."""
        selected_date = self.main_window.calendar.selectedDate().toPyDate()
        encrypted_entry, mood_label = self.db_handler.get_entry_by_date(self.current_user_id, selected_date)

        if encrypted_entry:
            decrypted_text = self.enc_handler.decrypt(encrypted_entry)
            self.main_window.entry_editor.setText(decrypted_text)
            self.main_window.mood_label.setText(f"Saved Mood: {mood_label}")
            self._update_editor_style(mood_label) 
        else:
            self.main_window.entry_editor.clear()
            self.main_window.mood_label.setText("Mood: Not Analyzed")
            self._update_editor_style("Neutral") 

    
    def _analyze_mood(self):
        """Analyzes the current text in the editor and updates the UI."""
        text = self.main_window.entry_editor.toPlainText()
        if not text.strip():
            self.main_window.mood_label.setText("Mood: Cannot analyze empty entry.")
            self._update_editor_style("Neutral") # Reset to neutral style
            return

        mood_label, score = self.sentiment_analyzer.analyze(text)
        self.main_window.mood_label.setText(f"Detected Mood: {mood_label} (Score: {score:.2f})")
        self._update_editor_style(mood_label) 
        
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
    
    def _show_stats_placeholder(self):
        """A placeholder for the mood statistics feature."""
        QMessageBox.information(
            self.main_window, 
            "Coming Soon!", 
            "The 'View Stats' feature, with beautiful charts of your mood history, is currently under development."
        )
    
    def _update_editor_style(self, mood="Neutral"):
        """
        Sets a dynamic property on the text editor to change its style based on the mood.
        """
        editor = self.main_window.entry_editor
        
        # Set the custom 'mood' property
        editor.setProperty("mood", mood)
        
        # Force PyQt to re-evaluate the stylesheet for this widget
        editor.style().unpolish(editor)
        editor.style().polish(editor)


if __name__ == '__main__':
    main_app = MoodVaultApp()
    main_app.run()