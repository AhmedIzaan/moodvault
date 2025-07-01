# MoodVault/ui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QCalendarWidget, QToolBar, QAction, QStatusBar,QLabel,QSizePolicy)
from PyQt5.QtGui import QColor, QTextCharFormat, QFont
from PyQt5.QtCore import QDate, Qt

class MainWindow(QMainWindow):
    """
    The main window of the MoodVault application.
    This class is responsible for setting up the entire UI skeleton.
    """
    def __init__(self, username):
        """
        Initializes the main window.
        Args:
            username (str): The name of the logged-in user.
        """
        super().__init__()
        self.current_user = username
        
        # Update the window title to be personalized
        self.setWindowTitle(f"MoodVault - Journal for {self.current_user}")
        
        self._create_main_window_geom() # Renamed for clarity
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        self._style_calendar_weekends()

    def _create_main_window_geom(self): # Renamed from _create_main_window
        """Sets up the main window geometry."""
        self.setGeometry(100, 100, 1000, 600)  # x, y, width, height

    def _create_toolbar(self):
        """Creates the main toolbar with actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # We create the actions as instance attributes so we can connect them later
        self.save_action = QAction("Save Entry", self)
        self.analyze_action = QAction("Analyze Mood", self)
        self.stats_action = QAction("View Stats", self)
        
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.analyze_action)
        toolbar.addSeparator()
        toolbar.addAction(self.stats_action)
         # --- ADD THE FOLLOWING ---
        # Spacer widget to push logout to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Logout action
        self.logout_action = QAction("Logout", self)
        toolbar.addAction(self.logout_action)

    def _create_central_widget(self):
        """Creates the main layout with calendar and text editor."""
        # Main container widget and layout
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # --- Left Side (Calendar) ---
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader) # Removes week numbers
        self.calendar.setMaximumDate(QDate.currentDate())
        self.calendar.setFixedWidth(400) # Increased width slightly for better look
        
        # --- Right Side (Diary Entry) ---
        self.editor_layout = QVBoxLayout() # Create the vertical layout for the editor side
        
        self.entry_editor = QTextEdit()
        self.entry_editor.setPlaceholderText("Write your thoughts for the day...")
        
        self.mood_label = QLabel("Mood: Not Analyzed")
        self.mood_label.setObjectName("moodLabel")
        
        # Add the editor and the mood label to the right-side layout
        self.editor_layout.addWidget(self.entry_editor)
        self.editor_layout.addWidget(self.mood_label)

        # --- Assemble the Main Layout ---
        # Add the calendar widget (left side) and the editor layout (right side)
        self.main_layout.addWidget(self.calendar)
        self.main_layout.addLayout(self.editor_layout) # This line was accidentally duplicated before
    # Add this entire method inside the MainWindow class in ui/ui.py
    
    def _style_calendar_weekends(self):
        """Applies a custom text format to weekends in the calendar header."""
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#E57373")) # A nice, soft red
        font = QFont()
        font.setBold(True)
        weekend_format.setFont(font)
        
        # Apply the format to Saturday and Sunday
        self.calendar.setWeekdayTextFormat(Qt.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.Sunday, weekend_format)

    def _create_status_bar(self):
        """Creates a status bar to display mood and other info."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to MoodVault! Select a date to begin.")

# --- Testing Block ---
# This allows us to run this file directly to see and test the UI layout
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create the main window
    main_win = MainWindow()
    main_win.show()
    
    sys.exit(app.exec_())