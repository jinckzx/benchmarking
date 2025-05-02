# import sqlite3
# import threading
# from datetime import datetime
# from typing import Optional, List, Dict
# import pandas as pd
# import json

# class DatabaseHandlerClass:
#     def __init__(self, db_path: str = 'classification_logs.db'):
#         self.db_path = db_path
#         self.thread_local = threading.local()
#         self._init_db()

#     def _get_connection(self) -> sqlite3.Connection:
#         """Get or create a thread-local database connection"""
#         if not hasattr(self.thread_local, "conn") or not self.thread_local.conn:
#             self.thread_local.conn = sqlite3.connect(
#                 self.db_path,
#                 check_same_thread=False,
#                 detect_types=sqlite3.PARSE_DECLTYPES
#             )
#             self.thread_local.conn.row_factory = sqlite3.Row
#         return self.thread_local.conn
#     def _init_db(self):
#         """Initialize database schema for classification task"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS classification_interactions (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     timestamp DATETIME,
#                     question TEXT,
#                     model TEXT,
#                     predicted_class TEXT,
#                     confidence REAL,
#                     latency REAL,
#                     iteration INTEGER,
#                     reasoning TEXT,
#                     raw_response TEXT
#                 )''')
#             conn.commit()
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Database initialization failed: {str(e)}")

#     def log_interaction(self, entry):
#         """Log a classification interaction to the database"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 INSERT INTO classification_interactions 
#                 (timestamp, question, model, predicted_class, confidence, latency, iteration, reasoning, raw_response)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
#                 (
#                     entry.timestamp,
#                     entry.question,
#                     entry.model,
#                     entry.predicted_class,
#                     entry.confidence,
#                     entry.latency,
#                     entry.iteration,
#                     entry.reasoning,
#                     entry.raw_response
#                 )
#             )
#             conn.commit()
#         except sqlite3.Error as e:
#             conn.rollback()
#             raise RuntimeError(f"Failed to log classification interaction: {str(e)}")


#     def get_interactions_by_question(self, question: str) -> List[Dict]:
#         """Retrieve all interactions for a specific question"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.execute(
#                 '''SELECT * FROM classification_interactions WHERE question = ? ORDER BY timestamp DESC''',
#                 (question,)
#             )
#             return [dict(row) for row in cursor.fetchall()]
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Failed to fetch interactions: {str(e)}")

#     def get_interactions_by_model(self, model: str) -> pd.DataFrame:
#         """Get all interactions for a specific model as a pandas DataFrame"""
#         try:
#             conn = self._get_connection()
#             query = '''SELECT * FROM classification_interactions WHERE model = ? ORDER BY timestamp DESC'''
#             return pd.read_sql(query, conn, params=(model,))
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Failed to fetch model interactions: {str(e)}")

#     def close(self):
#         """Close the database connection"""
#         if hasattr(self.thread_local, "conn"):
#             self.thread_local.conn.close()
#             del self.thread_local.conn
import sqlite3
import threading
from datetime import datetime
from typing import Optional, List, Dict
import pandas as pd

class DatabaseHandlerClass:
    def __init__(self, db_path: str = 'classification_logs.db'):
        self.db_path = db_path
        self.thread_local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a thread-local SQLite connection."""
        if not hasattr(self.thread_local, "conn") or self.thread_local.conn is None:
            self.thread_local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self.thread_local.conn.row_factory = sqlite3.Row
        return self.thread_local.conn

    def _init_db(self):
        """Create the classification_interactions table if it doesn't exist."""
        try:
            conn = self._get_connection()
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS classification_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        question TEXT,
                        model TEXT,
                        predicted_class TEXT,
                        confidence REAL,
                        latency REAL,
                        iteration INTEGER,
                        reasoning TEXT,
                        raw_response TEXT
                    )
                ''')
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {e}")

    def log_interaction(self, entry):
        """Log a classification interaction to the database."""
        try:
            conn = self._get_connection()
            with conn:
                conn.execute('''
                    INSERT INTO classification_interactions (
                        timestamp, question, model, predicted_class,
                        confidence, latency, iteration, reasoning, raw_response
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.timestamp.isoformat() if isinstance(entry.timestamp, datetime) else entry.timestamp,
                    entry.question,
                    entry.model,
                    entry.predicted_class,
                    entry.confidence,
                    entry.latency,
                    entry.iteration,
                    entry.reasoning,
                    entry.raw_response
                ))
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to log interaction: {e}")

    def get_interactions_by_question(self, question: str) -> List[Dict]:
        """Retrieve all interactions for a specific question."""
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                '''SELECT * FROM classification_interactions WHERE question = ? ORDER BY timestamp DESC''',
                (question,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch interactions: {e}")

    def get_interactions_by_model(self, model: str) -> pd.DataFrame:
        """Retrieve all interactions for a specific model as a DataFrame."""
        try:
            conn = self._get_connection()
            query = '''SELECT * FROM classification_interactions WHERE model = ? ORDER BY timestamp DESC'''
            return pd.read_sql(query, conn, params=(model,))
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch model interactions: {e}")

    def close(self):
        """Close the database connection."""
        if hasattr(self.thread_local, "conn") and self.thread_local.conn:
            self.thread_local.conn.close()
            del self.thread_local.conn
