# column_accuracy_metric.py
from .judge_base import JudgeBaseMetric

class ColumnAccuracyMetric(JudgeBaseMetric):
    """Evaluates column name accuracy in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="column_accuracy",
            criteria="""Evaluate the generated SQL query's column name accuracy by comparing it to the reference SQL:
            1. Column name correctness - Are the exact column names used correctly?
            2. Column selection completeness - Are all necessary columns included?
            3. Column aliasing appropriateness - Are aliases used correctly and meaningfully?
            4. Case sensitivity handling - Are column names properly cased?
            5. Column reference accuracy - Are column references (table.column) correct?""",
            evaluation_steps=[
                "Extract all column names from both generated and reference SQL",
                "Compare column names for exact matches and semantic equivalence",
                "Check if all required columns are present in the generated query",
                "Evaluate column aliasing for correctness and clarity",
                "Assess proper table.column reference format",
                "Score based on accuracy, completeness, and proper usage (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )