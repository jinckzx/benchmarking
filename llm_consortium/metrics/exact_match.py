#exact_match.py
from .base_metrics import BaseMetric
from typing import Dict, Any, List
class SQLExactMatch(BaseMetric):
    """Exact match comparison for SQL queries"""
    
    def __init__(self):
        super().__init__(
            name="exact_match",
            description="Exact string match between generated and reference SQL",
            csv_requires=["gold_sql"],  # From CSV
            runtime_requires=["generated_sql", "gold_sql"]  # From model + CSV
        )
        
    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        try:
            generated_norm = generated_sql.lower().strip()
            gold_norm = gold_sql.lower().strip()
            return {"exact_match": generated_norm == gold_norm}
        except AttributeError:
            return {"exact_match": False, "error": "Invalid SQL inputs"}
