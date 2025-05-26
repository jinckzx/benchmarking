# join_quality_metric.py
from .judge_base import JudgeBaseMetric

class JoinQualityMetric(JudgeBaseMetric):
    """Evaluates join quality in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="join_quality",
            criteria="""Evaluate the generated SQL query's join quality by comparing it to the reference SQL:
            1. Join type correctness - Are the correct JOIN types used (INNER, LEFT, RIGHT, FULL)?
            2. Join condition accuracy - Are the join conditions correct and complete?
            3. Join order optimization - Is the join order logical and efficient?
            4. Foreign key relationships - Are proper foreign key relationships maintained?
            5. Join completeness - Are all necessary joins present and no unnecessary ones included?
            6. Performance considerations - Would the joins execute efficiently?""",
            evaluation_steps=[
                "Identify all JOIN operations in both generated and reference SQL",
                "Compare JOIN types (INNER, LEFT, RIGHT, FULL OUTER) for correctness",
                "Analyze join conditions for accuracy and completeness",
                "Evaluate join order for logical flow and performance",
                "Check if foreign key relationships are properly maintained",
                "Assess whether all necessary joins are present",
                "Identify any unnecessary or redundant joins",
                "Score based on correctness, completeness, and efficiency (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )