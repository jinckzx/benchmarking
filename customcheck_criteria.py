from .judge_base import JudgeBaseMetric

class CustomcheckMetric(JudgeBaseMetric):
    """Evaluates customcheck aspects in SQL queries"""
    
    def __init__(self, threshold: float = 0.6, model: str = "gpt-3.5-turbo"):
        super().__init__(
            name="customcheck",
            criteria="""1. Join type selection - Are appropriate JOIN types (INNER, LEFT, RIGHT, FULL) us
2. Join order - Are tables joined in the optimal order?
3. Join conditions - Are join conditions properly specified?
4. Index usage - Does the join structure allow for index utilization?""",
            evaluation_steps=[
                "Identify all JOIN operations in both queries",
                "Compare join types used in generated vs reference",
                "Analyze join order for optimal execution",
                "Score based on join efficiency (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )
