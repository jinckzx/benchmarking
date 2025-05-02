import sqlite3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from llm_consortium.config.models_classification import LogEntry, RunResult

class DatabaseHandlerClassification:
    """
    Handler for classification database operations
    """
    def __init__(self, db_path: str = "classification_benchmarks.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._setup_database()
        
    def _setup_database(self):
        """Set up database connection and create tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create classification_logs table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_logs (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                model TEXT,
                prompt TEXT,
                predicted_class TEXT,
                confidence REAL,
                latency REAL,
                iteration INTEGER,
                raw_response TEXT,
                error TEXT,
                temperature REAL
            )
            ''')
            
            # Create runs table to track benchmark runs
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_runs (
                run_id TEXT PRIMARY KEY,
                model TEXT,
                timestamp TEXT,
                config TEXT,
                accuracy REAL,
                f1_score REAL,
                precision REAL,
                recall REAL,
                sample_size INTEGER,
                temperature REAL,
                tuned INTEGER
            )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            if self.conn:
                self.conn.close()
                
    def log_interaction(self, log_entry: LogEntry, temperature: float = 0.2) -> str:
        """
        Log a classification model interaction
        
        Args:
            log_entry (LogEntry): The log entry to store
            temperature (float): The temperature used for generation
            
        Returns:
            str: ID of the created log entry
        """
        log_id = str(uuid.uuid4())