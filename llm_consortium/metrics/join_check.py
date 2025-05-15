from .base_metrics import BaseMetric
from typing import Dict, Any


class Join_checkMetric123(BaseMetric):
    """LLM Judge metric for join_check"""

    def __init__(self):
        super().__init__(
            name="join_check",
            description="Evaluates if SQL query has proper join_check",
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        self.prompt = """check if the {generated_sql} has join clause in it or not. If generated sql has join then return "yes" or "no" Strictly"""
        self.client = None  # Will be initialized during runtime
        self.response_map = {
    "yes ": 1,
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
                raise

    def check_sql_query(self, generated_sql: str, gold_sql: str) -> str:
        """Check SQL queries based on join_check criteria"""
        try:
            # First try simple string-based checks when applicable
            if "join_check" == "select_check":
                has_feature_generated = "select" in generated_sql.lower()
                has_feature_gold = "select" in gold_sql.lower()

                if has_feature_generated and has_feature_gold:
                    return "yes"
                else:
                    return "no"
            # For more complex metrics that truly need LLM
            else:
                self._initialize_client()
                from langchain.schema import HumanMessage

                formatted_prompt = self.prompt.format(
                    generated_sql=generated_sql,
                    gold_sql=gold_sql
                )
                message = HumanMessage(content=formatted_prompt)
                response = self.client.chat([message])
                return response.content.strip()

        except Exception as e:
            logger.error(f"Error in join_check: {str(e)}")
            return f"Error: {str(e)}"

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Calculate the join_check metric score"""
        result = self.check_sql_query(generated_sql, gold_sql)

        # Map result to score
        score = self.response_map.get(result.lower(), 0.0)

        return {
            "join_check": score,
            "join_check_result": result
        }