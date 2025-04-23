# import sqlite3
# import threading
# from datetime import datetime
# from typing import Optional
# from ..config.models import LogEntry
# class DatabaseHandlerSQL:
#     def __init__(self, db_path: str = 'sql_pop.db'):
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
#         """Initialize database schema"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS interactions (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     timestamp DATETIME,
#                     prompt TEXT,
#                     model TEXT,
#                     response TEXT,
#                     confidence REAL,
#                     latency REAL,
#                     iteration INTEGER,
#                     intent TEXT,  -- New column
#                     db_id TEXT    -- New column
#                 )''')
#             conn.commit()
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Database initialization failed: {str(e)}")

#     def log_interaction(self, entry: LogEntry):
#         """Log an interaction to the database"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 INSERT INTO interactions 
#                 (timestamp, prompt, model, response, confidence, latency, iteration, intent, db_id)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',  # Updated
#                 (
#                     entry.timestamp,
#                     entry.prompt,
#                     entry.model,
#                     entry.response,
#                     entry.confidence,
#                     entry.latency,
#                     entry.iteration,
#                     entry.intent,  # New field
#                     entry.db_id   # New field
#                 )
#             )
#             conn.commit()


#         except sqlite3.Error as e:
#             conn.rollback()
#             raise RuntimeError(f"Failed to log interaction: {str(e)}")

#     def close(self):
#         """Close the database connection"""
#         if hasattr(self.thread_local, "conn"):
#             self.thread_local.conn.close()
#             del self.thread_local.conn
import sqlite3
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from ..config.models import LogEntry

class DatabaseHandlerSQL:
    def __init__(self, db_path: str = 'sql_pop.db'):
        self.db_path = db_path
        self.thread_local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a thread-local database connection"""
        if not hasattr(self.thread_local, "conn") or not self.thread_local.conn:
            self.thread_local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.thread_local.conn.row_factory = sqlite3.Row
        return self.thread_local.conn

    def _init_db(self):
        """Initialize database schema with model temperature tracking"""
        try:
            conn = self._get_connection()
            conn.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    prompt TEXT,
                    model TEXT,
                    response TEXT,
                    confidence REAL,
                    latency REAL,
                    iteration INTEGER,
                    intent TEXT,
                    db_id TEXT,
                    temperature REAL
                )''')
            
            # Add model temperature trials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_temperature_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    model TEXT,
                    temperature REAL,
                    prompt TEXT,
                    response TEXT,
                    confidence REAL,
                    latency REAL,
                    iteration INTEGER,
                    intent TEXT,
                    db_id TEXT,
                    is_best BOOLEAN DEFAULT 0
                )''')
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {str(e)}")

    def log_interaction(self, entry: LogEntry, temperature: Optional[float] = None):
        """Log an interaction to the database with temperature info"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO interactions 
                (timestamp, prompt, model, response, confidence, latency, iteration, intent, db_id, temperature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    entry.timestamp,
                    entry.prompt,
                    entry.model,
                    entry.response,
                    entry.confidence,
                    entry.latency,
                    entry.iteration,
                    entry.intent,
                    entry.db_id,
                    temperature
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log interaction: {str(e)}")

    def log_model_temperature_trial(self, entry: LogEntry, temperature: float, is_best: bool = False):
        """Log a model temperature trial"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO model_temperature_trials 
                (timestamp, model, temperature, prompt, response, confidence, latency, iteration, intent, db_id, is_best)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    entry.timestamp,
                    entry.model,
                    temperature,
                    entry.prompt,
                    entry.response,
                    entry.confidence,
                    entry.latency,
                    entry.iteration,
                    entry.intent,
                    entry.db_id,
                    int(is_best)
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log model temperature trial: {str(e)}")

    def get_best_model_temperature(self, model: str, db_id: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Get the best temperature for a specific model, database and prompt"""
        try:
            conn = self._get_connection()
            cursor = conn.execute('''
                SELECT * FROM model_temperature_trials
                WHERE model = ? AND db_id = ? AND prompt = ? AND is_best = 1
                ORDER BY confidence DESC
                LIMIT 1
            ''', (model, db_id, prompt))
            
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to get best model temperature: {str(e)}")

    def close(self):
        """Close the database connection"""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn