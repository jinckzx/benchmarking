from .base_metrics import BaseMetric
from typing import Dict, Any
from ..utils.logging import logger
class Join_clauseeMetric(BaseMetric):
    """LLM Judge metric for join_clausee"""

    def __init__(self):
        super().__init__(
            name="join_clausee",
            description="Evaluates if SQL query has proper join_clausee",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """check whether {generated_sql} has join clause or not, only answer in yes or no."""
        self.client = None  # Will be initialized during runtime
        self.response_map = {
    "yes": 1,
    "no": 0,
}

    def _initialize_client(self):
        """Lazy initialization of client to avoid circular imports"""
        if self.client is None:
            try:
                from ..core.client_init import llm
                self.client = llm
            except ImportError as e:
                logger.error(f"Failed to import LLM client: {str(e)}")
                return False
        return True

    def check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Check SQL queries based on join_clausee criteria"""
        try:
            # First try simple string-based checks when applicable
            if "join_clausee" == "select_check":
                has_feature_generated = "select" in generated_sql.lower()
                has_feature_gold = "select" in gold_sql.lower()

                if has_feature_generated and has_feature_gold:
                    return "yes"
                else:
                    return "no"
            # For more complex metrics that truly need LLM
            elif self._initialize_client():
                from langchain.schema import HumanMessage

                formatted_prompt = self.prompt.format(
                    generated_sql=generated_sql,
                    gold_sql=gold_sql
                )
                message = HumanMessage(content=formatted_prompt)
                response = self.client.chat([message])
                return response.content.strip().lower()
            else:
                logger.error("Failed to initialize LLM client")
                return "error"

        except Exception as e:
            logger.error(f"Error in join_clausee: {str(e)}")
            return f"error"

    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate the join_clausee metric score"""
        # Extract required parameters from kwargs
        generated_sql = kwargs.get("generated_sql", "")
        gold_sql = kwargs.get("gold_sql", "")

        # Validate inputs
        if not generated_sql or not gold_sql:
            logger.error(f"Join_clauseeMetric: Missing required parameters")
            return {
                "join_clausee": 0.0,
                "join_clausee_result": "error: missing parameters"
            }

        # Perform the check
        result = self.check_sql_query(generated_sql, gold_sql)

        # Map result to score
        score = self.response_map.get(result, 0.0)

        return {
            "join_clausee": score,
            "join_clausee_result": result
        }