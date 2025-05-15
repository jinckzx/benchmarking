from .base_metrics import BaseMetric
from typing import Dict, Any
from ..utils.logging import logger

class Select_checkMetric(BaseMetric):
    """LLM Judge metric for checking if both SQL queries have SELECT clauses"""
    
    def __init__(self):
        super().__init__(
            name="select_check",
            description="Evaluates if SQL query has proper SELECT clause in both generated and gold SQL",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.client = None  # Will be initialized during runtime
    
    def _initialize_client(self):
        """Lazy initialization of client to avoid circular imports"""
        if self.client is None:
            try:
                from ..core.client_init import llm
                self.client = llm
            except ImportError as e:
                logger.error(f"Failed to import LLM client: {str(e)}")
                raise
    
    def check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Check if both SQL queries have SELECT clauses using simple string matching"""
        try:
            # Simple string-based check to avoid async calls
            has_select_generated = "select" in generated_sql.lower()
            has_select_gold = "select" in gold_sql.lower()
            
            if has_select_generated and has_select_gold:
                return "yes"
            else:
                return "no"
        except Exception as e:
            logger.error(f"Error in select_check: {str(e)}")
            return f"Error: {str(e)}"
    
    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Calculate the select_check metric score"""
        result = self.check_sql_query(generated_sql, gold_sql)
        
        # Map result to score
        response_map = {"yes": 0.9, "no": 0.2}
        score = response_map.get(result.lower(), 0.0)
        
        return {
            "select_check": score,
            "select_check_result": result
        }