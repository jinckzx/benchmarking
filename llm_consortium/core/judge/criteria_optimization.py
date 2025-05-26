# query_optimization_metric.py
from .judge_base import JudgeBaseMetric

class QueryOptimizationMetric(JudgeBaseMetric):
    """Evaluates query optimization aspects in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="query_optimization",
            criteria="""Evaluate the generated SQL query's optimization aspects by comparing it to the reference SQL:
            1. Index utilization - Does the query structure allow for efficient index usage?
            2. Join efficiency - Are joins structured for optimal performance?
            3. Filtering early - Are WHERE conditions applied early to reduce data processing?
            4. Aggregation efficiency - Are GROUP BY and aggregate functions used optimally?
            5. Subquery vs JOIN trade-offs - Are subqueries used appropriately vs JOINs?
            6. LIMIT/TOP usage - Is result limiting used when appropriate?
            7. Function usage - Are expensive functions avoided when simpler alternatives exist?
            8. Data type considerations - Are appropriate data types and comparisons used?""",
            evaluation_steps=[
                "Analyze query structure for index-friendly patterns",
                "Evaluate join order and type selection for performance",
                "Check if filtering conditions are applied early in the query",
                "Assess aggregation patterns for efficiency",
                "Compare subquery usage vs JOIN alternatives",
                "Verify appropriate use of LIMIT/TOP for result sets",
                "Identify potentially expensive function calls",
                "Review data type usage and casting requirements",
                "Score based on performance optimization potential (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )