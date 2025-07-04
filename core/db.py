

import sqlite3
from sqlite3 import Error
import os
from pathlib import Path

# In core/db.py
def get_db_path():
    """
    Determines the path for the database file, placing it in the project's root directory.
    """
    # Get the path to the project's root directory (which is the parent of the 'core' directory)
    # __file__ is the path to the current script (db.py)
    # .parent gives the directory of the script (core/)
    # .parent again gives the parent of that directory (the project root, MoodVault/)
    project_root = Path(__file__).resolve().parent.parent
    
    db_path = project_root / 'moodvault.db'
    
    print(f"Database path set to: {db_path}")
    return db_path

class DatabaseHandler:
    """
    Handles all database connections and queries for the MoodVault application using SQLite.
    """
    def __init__(self):
        """Initializes the handler and creates tables if they don't exist."""
        self.db_path = get_db_path()
        self.create_tables()

    def _get_connection(self):
        """Establishes a new database connection."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign key support, which is off by default in SQLite
            conn.execute("PRAGMA foreign_keys = 1")
        except Error as e:
            print(f"Error connecting to SQLite Database: {e}")
        return conn

    def create_tables(self):
        """Creates the necessary tables if they do not already exist."""
        conn = self._get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            # User table with SQLite-compatible syntax
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                encryption_salt BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Entries table with SQLite-compatible syntax
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry_date DATE NOT NULL,
                encrypted_entry BLOB NOT NULL,
                sentiment_label TEXT,
                sentiment_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, entry_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            conn.commit()
            print("SQLite database tables checked/created successfully.")
        except Error as e:
            print(f"Error creating SQLite tables: {e}")
        finally:
            if conn:
                conn.close()

    def add_user(self, username, password_hash, encryption_salt):
        """Adds a new user to the database."""
        sql = "INSERT INTO users (username, password_hash, encryption_salt) VALUES (?, ?, ?)"
        conn = self._get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (username, password_hash, encryption_salt))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_user_hash(self, username):
        """Retrieves the password hash for a given username."""
        sql = "SELECT password_hash FROM users WHERE username = ?"
        conn = self._get_connection()
        if not conn: return None

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user hash: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_id(self, username):
        """Retrieves the user ID for a given username."""
        sql = "SELECT id FROM users WHERE username = ?"
        conn = self._get_connection()
        if not conn: return None

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_first_user_id(self):
        """Checks if any user exists and returns the first user's ID."""
        sql = "SELECT id FROM users ORDER BY id LIMIT 1"
        conn = self._get_connection()
        if not conn: return None

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching first user ID: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_salt(self, username):
        """Retrieves the encryption salt for a given username."""
        sql = "SELECT encryption_salt FROM users WHERE username = ?"
        conn = self._get_connection()
        if not conn: return None

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user salt: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def add_or_update_entry(self, user_id, date, encrypted_data, mood, score):
        """Adds a new entry or updates an existing one using INSERT OR REPLACE."""
        sql = """
        INSERT OR REPLACE INTO entries (user_id, entry_date, encrypted_entry, sentiment_label, sentiment_score)
        VALUES (?, ?, ?, ?, ?);
        """
        conn = self._get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id, date, encrypted_data, mood, score))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding/updating entry: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_entry_by_date(self, user_id, date):
        """Retrieves a single entry by user and date."""
        sql = "SELECT encrypted_entry, sentiment_label FROM entries WHERE user_id = ? AND entry_date = ?"
        conn = self._get_connection()
        if not conn: return None, None

        try:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id, date))
            result = cursor.fetchone()
            return result if result else (None, None)
        except Error as e:
            print(f"Error fetching entry by date: {e}")
            return None, None
        finally:
            if conn:
                conn.close()

    def get_all_entries_for_user(self, user_id):
        """Retrieves all entry metadata for a user (for visualizations)."""
        sql = "SELECT entry_date, sentiment_label, sentiment_score FROM entries WHERE user_id = ? ORDER BY entry_date ASC"
        conn = self._get_connection()
        if not conn: return []
        
        try:
            # Use sqlite3.Row to make rows behave like dictionaries
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Error as e:
            print(f"Error fetching all entries: {e}")
            return []
        finally:
            if conn:
                conn.close()

# # --- Testing Block ---
# # This code will only run when you execute this file directly.
# if __name__ == "__main__":
#     print("--- Running Standalone Test for db.py ---")
    
#     # 1. Initialize the handler. This will also create the DB file and tables.
#     db_handler = DatabaseHandler()
#     print("\n[1. Database Handler Initialized]")

#     # To ensure a clean test, we can manually delete the db file before running if needed.
    
#     # 2. Test adding a new user
#     print("\n[2. Testing User Addition]")
#     test_username = "test_user"
#     test_password_hash = "some_bcrypt_hash"
#     test_salt = b"a_random_salt_16" # In a real scenario, this would be 16 random bytes
    
#     success = db_handler.add_user(test_username, test_password_hash, test_salt)
#     if success:
#         print(f"  -> SUCCESS: User '{test_username}' added.")
#     else:
#         print(f"  -> FAILURE: Could not add user '{test_username}'. (Might already exist if you ran this before)")

#     # 3. Test fetching user data
#     print("\n[3. Testing User Data Retrieval]")
#     user_id = db_handler.get_user_id(test_username)
#     user_hash = db_handler.get_user_hash(test_username)
#     user_salt = db_handler.get_user_salt(test_username)

#     if user_id and user_hash and user_salt:
#         print(f"  -> SUCCESS: Fetched User ID: {user_id}")
#         print(f"  -> SUCCESS: Fetched Hash: {user_hash[:15]}...") # Print first 15 chars
#         print(f"  -> SUCCESS: Fetched Salt: {user_salt}")
#     else:
#         print("  -> FAILURE: Could not retrieve all user data.")
        
#     # 4. Test adding and retrieving an entry
#     if user_id:
#         print("\n[4. Testing Entry Addition and Retrieval]")
#         from datetime import date
#         today = date.today()
#         test_entry_data = b"This is an encrypted test entry."
#         test_mood = "Joy"
#         test_score = 0.95
        
#         add_success = db_handler.add_or_update_entry(user_id, today, test_entry_data, test_mood, test_score)
#         if add_success:
#             print("  -> SUCCESS: Entry for today added/updated.")
            
#             # Now retrieve it
#             retrieved_data, retrieved_mood = db_handler.get_entry_by_date(user_id, today)
#             if retrieved_data == test_entry_data and retrieved_mood == test_mood:
#                 print("  -> SUCCESS: Retrieved entry matches the data that was saved.")
#             else:
#                 print("  -> FAILURE: Retrieved entry does not match saved data.")
#         else:
#             print("  -> FAILURE: Could not add entry.")
#     else:
#         print("\n[4. Skipping Entry Test: User ID not found]")

#     # 5. Test retrieving all entries
#     if user_id:
#         print("\n[5. Testing Retrieval of All Entries]")
#         all_entries = db_handler.get_all_entries_for_user(user_id)
#         if all_entries:
#             print(f"  -> SUCCESS: Found {len(all_entries)} total entries.")
#             print(f"  -> Entry 1 Data: {all_entries[0]}")
#         else:
#             print("  -> FAILURE: Could not retrieve all entries for user.")

#     print("\n--- Test Complete ---")