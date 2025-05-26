from .judge_base import JudgeBaseMetric

class ConditionCorrectnessMetric(JudgeBaseMetric):
    """Evaluates condition correctness in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="condition_correctness",
            criteria="""Evaluate the generated SQL query's condition correctness by comparing it to the reference SQL:
            1. WHERE clause accuracy - Are the WHERE conditions correct and complete?
            2. HAVING clause appropriateness - Are HAVING conditions used correctly for aggregated data?
            3. Logical operator usage - Are AND, OR, NOT operators used correctly?
            4. Comparison operator accuracy - Are =, !=, <, >, <=, >= used appropriately?
            5. NULL handling - Are NULL values handled correctly with IS NULL/IS NOT NULL?
            6. Data type consistency - Are conditions applied to appropriate data types?
            7. Condition completeness - Are all necessary filtering conditions present?""",
            evaluation_steps=[
                "Extract all WHERE and HAVING conditions from both queries",
                "Compare individual conditions for logical equivalence",
                "Evaluate proper use of logical operators (AND, OR, NOT)",
                "Check comparison operators for appropriateness",
                "Assess NULL value handling with proper SQL syntax",
                "Verify data type compatibility in conditions",
                "Determine if all necessary filtering is present",
                "Check for any unnecessary or redundant conditions",
                "Score based on accuracy, completeness, and logical correctness (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )