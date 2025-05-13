# metrics/execution_match.py
from .base_metrics import BaseMetric
import sqlite3
import os
from typing import Dict, Any

class SQLExecutionMatch(BaseMetric):
    """Execution-based match for SQL queries"""
    
    def __init__(self, db_root_path: str):
        super().__init__(
            name="execution_match",
            description="Result set match between generated and reference SQL",
            csv_requires=["gold_sql", "db_id"],
            runtime_requires=["generated_sql", "gold_sql", "db_id"]
        )
        self.db_root_path = db_root_path
        
    def get_db_path(self, db_id: str) -> str:
        path = os.path.join(self.db_root_path, db_id, f"{db_id}.sqlite")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database {db_id} not found at {path}")
        return path
        
    def calculate(self, generated_sql: str, gold_sql: str, db_id: str) -> Dict[str, Any]:
        try:
            db_path = self.get_db_path(db_id)
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(generated_sql)
                generated_res = cursor.fetchall()
                cursor.execute(gold_sql)
                gold_res = cursor.fetchall()
                return {
                    "execution_match": generated_res == gold_res,
                    "generated_result": generated_res,
                    "gold_result": gold_res
                }
        except Exception as e:
            return {
                "execution_match": False,
                "error": str(e),
                "generated_sql": generated_sql,
                "gold_sql": gold_sql
            }