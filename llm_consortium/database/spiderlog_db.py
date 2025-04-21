# # spiderlog_db.py
# import sqlite3
# import threading
# from datetime import datetime
# from typing import Optional, List, Dict
# import pandas as pd

# class SpiderDatasetLogger:
#     def __init__(self, db_path: str = 'spiderdatasetqueries.db'):
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
#         """Initialize database schema for spider dataset logging"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 CREATE TABLE IF NOT EXISTS spider_queries (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     timestamp DATETIME,
#                     db_schema TEXT,
#                     natural_language_query TEXT,
#                     intent_category TEXT,
#                     generated_sql TEXT,
#                     confidence REAL,
#                     model_responses TEXT  -- JSON array of all model responses
#                 )''')
#             conn.execute('''
#                 CREATE INDEX IF NOT EXISTS idx_intent_category 
#                 ON spider_queries(intent_category)
#             ''')
#             conn.commit()
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Spider dataset DB initialization failed: {str(e)}")

#     def log_query(
#         self,
#         db_schema: str,
#         natural_language_query: str,
#         intent_category: str,
#         generated_sql: str,
#         confidence: float,
#         model_responses: List[Dict]
#     ):
#         """Log a complete spider dataset query with intent classification"""
#         try:
#             conn = self._get_connection()
#             conn.execute('''
#                 INSERT INTO spider_queries 
#                 (timestamp, db_schema, natural_language_query, 
#                 intent_category, generated_sql, confidence, model_responses)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
#                 (
#                     datetime.now(),
#                     db_schema,
#                     natural_language_query,
#                     intent_category,
#                     generated_sql,
#                     confidence,
#                     str(model_responses)  # Serialize as JSON string
#                 )
#             )
#             conn.commit()
#         except sqlite3.Error as e:
#             conn.rollback()
#             raise RuntimeError(f"Failed to log spider query: {str(e)}")

#     def get_queries_by_intent(self, intent_category: str) -> pd.DataFrame:
#         """Retrieve queries filtered by intent category"""
#         try:
#             conn = self._get_connection()
#             df = pd.read_sql(
#                 '''SELECT * FROM spider_queries 
#                     WHERE intent_category = ? 
#                     ORDER BY timestamp DESC''',
#                 conn,
#                 params=(intent_category,)
#             )
#             return df
#         except sqlite3.Error as e:
#             raise RuntimeError(f"Failed to fetch queries by intent: {str(e)}")

#     def close(self):
#         """Close the database connection"""
#         if hasattr(self.thread_local, "conn"):
#             self.thread_local.conn.close()
#             del self.thread_local.conn
import sqlite3
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import json

class SpiderDatasetLogger:
    def __init__(self, db_path: str = 'spiderdatasetqueries.db'):
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
            
            # Main queries table with temperature info
            conn.execute('''
                CREATE TABLE IF NOT EXISTS spider_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    iteration INTEGER,
                    db_schema TEXT,
                    natural_language_query TEXT,
                    intent_category TEXT,
                    generated_sql TEXT,
                    confidence REAL,
                    temperature REAL,
                    is_best_result BOOLEAN DEFAULT 0,
                    model_responses TEXT  -- JSON array of all model responses
                )''')
            
            # Temperature trials table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS spider_temperature_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    iteration INTEGER,
                    db_schema TEXT,
                    natural_language_query TEXT,
                    intent_category TEXT,
                    generated_sql TEXT,
                    confidence REAL,
                    temperature REAL,
                    model_responses TEXT
                )''')
            
            # Create indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_spider_intent 
                ON spider_queries(intent_category)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_spider_trials_temp 
                ON spider_temperature_trials(temperature)
            ''')
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {str(e)}")

    def log_query(
        self,
        db_schema: str,
        natural_language_query: str,
        intent_category: str,
        generated_sql: str,
        confidence: float,
        model_responses: List[Dict],
        iteration: Optional[int] = None,
        temperature: Optional[float] = None,
        is_best_result: bool = False
    ):
        """Log a complete spider dataset query with temperature info"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO spider_queries 
                (timestamp, iteration, db_schema, natural_language_query, 
                intent_category, generated_sql, confidence, temperature, 
                is_best_result, model_responses)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now(),
                    iteration,
                    db_schema,
                    natural_language_query,
                    intent_category,
                    generated_sql,
                    confidence,
                    temperature,
                    int(is_best_result),
                    json.dumps(model_responses)
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log spider query: {str(e)}")

    def log_temperature_trial(
        self,
        db_schema: str,
        natural_language_query: str,
        intent_category: str,
        generated_sql: str,
        confidence: float,
        temperature: float,
        model_responses: List[Dict],
        iteration: Optional[int] = None
    ):
        """Log individual temperature trial for spider dataset"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO spider_temperature_trials 
                (timestamp, iteration, db_schema, natural_language_query,
                intent_category, generated_sql, confidence, temperature,
                model_responses)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now(),
                    iteration,
                    db_schema,
                    natural_language_query,
                    intent_category,
                    generated_sql,
                    confidence,
                    temperature,
                    json.dumps(model_responses)
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log temperature trial: {str(e)}")

    def get_temperature_trials(
        self, 
        natural_language_query: str,
        iteration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve temperature trials for a specific query"""
        try:
            conn = self._get_connection()
            params = (natural_language_query,)
            query = '''
                SELECT * FROM spider_temperature_trials
                WHERE natural_language_query = ?
            '''
            
            if iteration is not None:
                query += ' AND iteration = ?'
                params += (iteration,)
                
            query += ' ORDER BY temperature ASC'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch temperature trials: {str(e)}")

    def get_best_results(
        self,
        intent_category: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> pd.DataFrame:
        """Retrieve best results filtered by intent and confidence"""
        try:
            conn = self._get_connection()
            query = '''
                SELECT * FROM spider_queries
                WHERE is_best_result = 1 AND confidence >= ?
            '''
            params = (min_confidence,)
            
            if intent_category:
                query += ' AND intent_category = ?'
                params += (intent_category,)
                
            query += ' ORDER BY confidence DESC'
            
            return pd.read_sql(query, conn, params=params)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch best results: {str(e)}")

    def close(self):
        """Close the database connection"""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn