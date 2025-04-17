# import sqlite3
# import threading
# from datetime import datetime
# from typing import Optional

# class SynthesisDatabaseHandler:
#     def __init__(self, db_path: str = 'synthesized.db'):
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
#         """Initialize database schema for synthesis results"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS synthesis_results (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     timestamp DATETIME,
#                     iteration INTEGER,
#                     prompt TEXT,
#                     arbiter_model TEXT,
#                     synthesized_text TEXT,
#                     confidence REAL,
#                     analysis TEXT,
#                     dissenting_views TEXT
#                 )''')
#             conn.commit()
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Synthesis database initialization failed: {str(e)}")

#     def log_synthesis(self, iteration: int, prompt: str, arbiter: str, 
#                     synthesized_text: str, confidence: float, 
#                     analysis: str, dissent: str):
#         """Log synthesis results to the database"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 INSERT INTO synthesis_results 
#                 (timestamp, iteration, prompt, arbiter_model, 
#                 synthesized_text, confidence, analysis, dissenting_views)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
#                 (
#                     datetime.now(),
#                     iteration,
#                     prompt,
#                     arbiter,
#                     synthesized_text,
#                     confidence,
#                     analysis,
#                     dissent
#                 )
#             )
#             conn.commit()
#         except sqlite3.Error as e:
#             conn.rollback()
#             raise RuntimeError(f"Failed to log synthesis: {str(e)}")

#     def close(self):
#         """Close the database connection"""
#         if hasattr(self.thread_local, "conn"):
#             self.thread_local.conn.close()
#             del self.thread_local.conn
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional  # Added Optional import
import json

class SynthesisDatabaseHandler:
    def __init__(self, db_path: str = 'synthesized.db'):
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
        """Initialize database schema with temperature tracking"""
        try:
            conn = self._get_connection()
            
            # Main synthesis results table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS synthesis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    iteration INTEGER,
                    prompt TEXT,
                    arbiter_model TEXT,
                    synthesized_text TEXT,
                    confidence REAL,
                    temperature REAL,
                    analysis TEXT,
                    dissenting_views TEXT,
                    is_best_result BOOLEAN DEFAULT 0
                )''')
            
            # Temperature trials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS temperature_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    iteration INTEGER,
                    temperature REAL,
                    confidence REAL,
                    synthesized_text TEXT,
                    analysis TEXT,
                    dissenting_views TEXT,
                    timestamp DATETIME
                )''')
            
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {str(e)}")

    def log_synthesis(self, 
                    iteration: int, 
                    prompt: str, 
                    arbiter: str, 
                    synthesized_text: str, 
                    confidence: float,
                    temperature: float,
                    analysis: str, 
                    dissent: str,
                    is_best_result: bool = False):
        """Log final synthesis results with temperature"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO synthesis_results 
                (timestamp, iteration, prompt, arbiter_model, 
                synthesized_text, confidence, temperature, 
                analysis, dissenting_views, is_best_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now(),
                    iteration,
                    prompt,
                    arbiter,
                    synthesized_text,
                    confidence,
                    temperature,
                    analysis,
                    dissent,
                    int(is_best_result)  # Convert bool to int for SQLite
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log synthesis: {str(e)}")

    def log_temperature_trial(self,
                            iteration: int,
                            temperature: float,
                            confidence: float,
                            synthesized_text: str,
                            analysis: str,
                            dissent: str):
        """Log individual temperature trial"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO temperature_trials 
                (iteration, temperature, confidence, 
                synthesized_text, analysis, dissenting_views, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    iteration,
                    temperature,
                    confidence,
                    synthesized_text,
                    analysis,
                    dissent,
                    datetime.now()
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log temperature trial: {str(e)}")

    def get_temperature_trials(self, iteration: int) -> List[Dict[str, Any]]:
        """Retrieve all temperature trials for an iteration"""
        try:
            conn = self._get_connection()
            cursor = conn.execute('''
                SELECT * FROM temperature_trials
                WHERE iteration = ?
                ORDER BY temperature ASC
            ''', (iteration,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch temperature trials: {str(e)}")

    def get_best_synthesis(self, iteration: int) -> Optional[Dict[str, Any]]:
        """Get the best synthesis result for an iteration"""
        try:
            conn = self._get_connection()
            cursor = conn.execute('''
                SELECT * FROM synthesis_results
                WHERE iteration = ? AND is_best_result = 1
                LIMIT 1
            ''', (iteration,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch best synthesis: {str(e)}")

    def close(self):
        """Close the database connection"""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn