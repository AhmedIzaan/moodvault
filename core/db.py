

import mysql.connector
from mysql.connector import Error
import json

def get_db_config():
    """Loads database configuration from a JSON file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config['mysql']
    except FileNotFoundError:
        print("Error: 'config.json' not found. Please create it with your DB credentials.")
        return None
    except KeyError:
        print("Error: 'mysql' key not found in 'config.json'.")
        return None

class DatabaseHandler:
    """
    Handles all database connections and queries for the MoodVault application.
    """
    def __init__(self):
        """Initializes the handler by loading the configuration."""
        self.config = get_db_config()
        if self.config:
            self.create_tables()

    def _get_connection(self):
        """Establishes a new database connection."""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"Error connecting to MySQL Database: {e}")
            return None

    def create_tables(self):
        """Creates the necessary tables if they do not already exist."""
        conn = self._get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            # User table stores login information
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                encryption_salt BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """)

            # Entries table stores diary content and sentiment analysis results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                entry_date DATE NOT NULL,
                encrypted_entry BLOB NOT NULL,
                sentiment_label VARCHAR(20),
                sentiment_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY (user_id, entry_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """)
            conn.commit()
            print("Database tables checked/created successfully.")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            conn.close()
            
    def add_user(self, username, password_hash, encryption_salt):
        """Adds a new user to the database."""
        sql = "INSERT INTO users (username, password_hash, encryption_salt) VALUES (%s, %s, %s)"
        conn = self._get_connection()
        if not conn: return False
        
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (username, password_hash, encryption_salt))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    def get_first_user_id(self):
        """Checks if any user exists and returns the first user's ID."""
        sql = "SELECT id FROM users ORDER BY id LIMIT 1"
        conn = self._get_connection()
        if not conn: return None

        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching first user ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
            
    def get_user_salt(self, username):
        """Retrieves the encryption salt for a given username."""
        sql = "SELECT encryption_salt FROM users WHERE username = %s"
        conn = self._get_connection()
        if not conn: return None

        cursor = conn.cursor()
        try:
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user salt: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_hash(self, username):
        """Retrieves the password hash for a given username."""
        sql = "SELECT password_hash FROM users WHERE username = %s"
        conn = self._get_connection()
        if not conn: return None

        cursor = conn.cursor()
        try:
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user hash: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
            
    def get_user_id(self, username):
        """Retrieves the user ID for a given username."""
        sql = "SELECT id FROM users WHERE username = %s"
        conn = self._get_connection()
        if not conn: return None

        cursor = conn.cursor()
        try:
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error fetching user ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


    def add_or_update_entry(self, user_id, date, encrypted_data, mood, score):
        """Adds a new entry or updates an existing one for a given date."""
        # This query uses a neat MySQL feature to update if a unique key (user_id, entry_date) exists
        sql = """
        INSERT INTO entries (user_id, entry_date, encrypted_entry, sentiment_label, sentiment_score)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        encrypted_entry = VALUES(encrypted_entry),
        sentiment_label = VALUES(sentiment_label),
        sentiment_score = VALUES(sentiment_score);
        """
        conn = self._get_connection()
        if not conn: return False

        cursor = conn.cursor()
        try:
            cursor.execute(sql, (user_id, date, encrypted_data, mood, score))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding/updating entry: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_entry_by_date(self, user_id, date):
        """Retrieves a single entry by user and date."""
        sql = "SELECT encrypted_entry, sentiment_label FROM entries WHERE user_id = %s AND entry_date = %s"
        conn = self._get_connection()
        if not conn: return None

        cursor = conn.cursor()
        try:
            cursor.execute(sql, (user_id, date))
            result = cursor.fetchone()
            return result if result else (None, None)
        except Error as e:
            print(f"Error fetching entry by date: {e}")
            return None, None
        finally:
            cursor.close()
            conn.close()

    def get_all_entries_for_user(self, user_id):
        """Retrieves all entry metadata for a user (for visualizations)."""
        sql = "SELECT entry_date, sentiment_label, sentiment_score FROM entries WHERE user_id = %s ORDER BY entry_date ASC"
        conn = self._get_connection()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True) # Fetch as dictionaries for easy access
        try:
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error fetching all entries: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
            
