import sqlite3
import pickle
import json
import os
from datetime import datetime, timedelta

class StorageModule:
    """
    StorageModule handles persistence for the Smart Surveillance System.
    It manages a SQLite database for detection history and facial embeddings.
    """
    def __init__(self, db_path="surveillance_history.db", config_path=None):
        # Default config path to root directory relative to this file
        if config_path is None:
            self.config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
        else:
            self.config_path = config_path
            
        # Ensure db_path is absolute or clearly defined to avoid multiple DBs
        if not os.path.isabs(db_path):
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', db_path))
        else:
            self.db_path = db_path
            
        self.insertion_count = 0
        self._init_db()

    def _init_db(self):
        """Initializes the detections table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    track_id INTEGER,
                    embedding BLOB,
                    frame_path TEXT,
                    confidence REAL
                )
            ''')
            conn.commit()

    def _get_retention_hours(self):
        """Reads retention policy from config.json."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("RETENTION_HOURS", 24)
        except Exception as e:
            print(f"StorageModule: Error reading config: {e}")
        return 24

    def insert_detection(self, track_id, embedding, frame_path, confidence):
        """
        Inserts a detection event into the database.
        Serializes the embedding using pickle for version cross-compatibility.
        """
        embedding_blob = pickle.dumps(embedding)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO detections (track_id, embedding, frame_path, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (track_id, embedding_blob, frame_path, confidence))
                conn.commit()
            
            # Auto-pruning logic to prevent I/O lag
            self.insertion_count += 1
            if self.insertion_count >= 100:
                self.prune_data()
                self.insertion_count = 0
        except sqlite3.Error as e:
            print(f"StorageModule: Database error during insertion: {e}")

    def prune_data(self):
        """Deletes records older than the configured retention threshold."""
        retention_hours = self._get_retention_hours()
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        # SQLite uses UTC for CURRENT_TIMESTAMP by default, 
        # but here we'll use a relative comparison.
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM detections WHERE timestamp < ?
                ''', (cutoff_str,))
                conn.commit()
                print(f"StorageModule: Pruned data older than {retention_hours} hours (before {cutoff_str}).")
        except sqlite3.Error as e:
            print(f"StorageModule: Database error during pruning: {e}")

    def get_recent_detections(self, limit=10):
        """Retrieves the most recent detection events."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?', (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"StorageModule: Database error during retrieval: {e}")
            return []
