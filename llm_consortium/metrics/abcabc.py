from .base_metrics import BaseMetric
from typing import Dict, Any

class SQLabcabc(BaseMetric):
    """Exact match comparison for SQL queries"""
    def __init__(self):
        super().__init__(
            name="abcabc",
            description="Exact string match between generated and reference SQL",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        try:
            generated_norm = generated_sql.lower().strip()
            gold_norm = gold_sql.lower().strip()
            return {"abcabc": generated_norm == gold_norm}
        except AttributeError:
            return {"abcabc": False, "error": "Invalid SQL inputs"}