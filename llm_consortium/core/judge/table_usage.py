# table_usage_metric.py
from .judge_base import JudgeBaseMetric

class TableUsageMetric(JudgeBaseMetric):
    """Evaluates table usage correctness in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="table_usage_correctness",
            criteria="""Evaluate the generated SQL query's table usage correctness by comparing it to the reference SQL:
            1. Table selection accuracy - Are the correct tables being used?
            2. Table aliasing consistency - Are table aliases used correctly and consistently?
            3. Schema qualification - Are tables properly qualified with schema names when needed?
            4. Table reference completeness - Are all necessary tables included?
            5. Unnecessary table usage - Are there any redundant or unnecessary table references?""",
            evaluation_steps=[
                "Identify all tables referenced in both generated and reference SQL",
                "Compare table names and aliases for accuracy",
                "Check if all necessary tables are included in the generated query",
                "Evaluate proper schema qualification where applicable",
                "Assess consistency of table aliasing throughout the query",
                "Identify any unnecessary or redundant table references",
                "Score based on correctness, completeness, and efficiency (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )