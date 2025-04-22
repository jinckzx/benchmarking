import sqlite3
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd
import json

class ClassificationSynthesisLogger:
    def __init__(self, db_path: str = 'classification_synthesis.db'):
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
        """Initialize database schema with temperature tracking for classification"""
        try:
            conn = self._get_connection()
            
            # Main classification results table with temperature info
            conn.execute('''
                CREATE TABLE IF NOT EXISTS classification_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    iteration INTEGER,
                    question TEXT,
                    true_class TEXT,
                    predicted_class TEXT,
                    confidence REAL,
                    temperature REAL,
                    is_best_result BOOLEAN DEFAULT 0,
                    model_responses TEXT,  -- JSON array of all model responses
                    reasoning TEXT
                )''')
            
            # Temperature trials table for classification
            conn.execute('''
                CREATE TABLE IF NOT EXISTS classification_temperature_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    iteration INTEGER,
                    question TEXT,
                    true_class TEXT,
                    predicted_class TEXT,
                    confidence REAL,
                    temperature REAL,
                    model_responses TEXT,
                    reasoning TEXT
                )''')
            
            # Create indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_class_question 
                ON classification_results(question)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_class_trials_temp 
                ON classification_temperature_trials(temperature)
            ''')
            conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database initialization failed: {str(e)}")

    def log_classification(
        self,
        question: str,
        true_class: Optional[str],
        predicted_class: str,
        confidence: float,
        model_responses: List[Dict],
        reasoning: str,
        iteration: Optional[int] = None,
        temperature: Optional[float] = None,
        is_best_result: bool = False
    ):
        """Log a complete classification result with temperature info"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO classification_results 
                (timestamp, iteration, question, true_class, predicted_class, 
                confidence, temperature, is_best_result, model_responses, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now(),
                    iteration,
                    question,
                    true_class,
                    predicted_class,
                    confidence,
                    temperature,
                    int(is_best_result),
                    json.dumps(model_responses),
                    reasoning
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log classification result: {str(e)}")

    def log_temperature_trial(
        self,
        question: str,
        true_class: Optional[str],
        predicted_class: str,
        confidence: float,
        temperature: float,
        model_responses: List[Dict],
        reasoning: str,
        iteration: Optional[int] = None
    ):
        """Log individual temperature trial for classification"""
        try:
            conn = self._get_connection()
            conn.execute('''
                INSERT INTO classification_temperature_trials 
                (timestamp, iteration, question, true_class, predicted_class,
                confidence, temperature, model_responses, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    datetime.now(),
                    iteration,
                    question,
                    true_class,
                    predicted_class,
                    confidence,
                    temperature,
                    json.dumps(model_responses),
                    reasoning
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to log temperature trial: {str(e)}")

    def get_temperature_trials(
        self, 
        question: str,
        iteration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve temperature trials for a specific classification question"""
        try:
            conn = self._get_connection()
            params = (question,)
            query = '''
                SELECT * FROM classification_temperature_trials
                WHERE question = ?
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
        class_filter: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> pd.DataFrame:
        """Retrieve best classification results filtered by class and confidence"""
        try:
            conn = self._get_connection()
            query = '''
                SELECT * FROM classification_results
                WHERE is_best_result = 1 AND confidence >= ?
            '''
            params = (min_confidence,)
            
            if class_filter:
                query += ' AND (true_class = ? OR predicted_class = ?)'
                params += (class_filter, class_filter)
                
            query += ' ORDER BY confidence DESC'
            
            return pd.read_sql(query, conn, params=params)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch best results: {str(e)}")
            
    def export_results_csv(self, output_path: str) -> None:
        """Export best classification results to CSV"""
        try:
            conn = self._get_connection()
            query = '''
                SELECT question, true_class, predicted_class, confidence, reasoning
                FROM classification_results
                WHERE is_best_result = 1
                ORDER BY confidence DESC
            '''
            df = pd.read_sql(query, conn)
            df.to_csv(output_path, index=False)
            return df
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to export results: {str(e)}")

    def close(self):
        """Close the database connection"""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn