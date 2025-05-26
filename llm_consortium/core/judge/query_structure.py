# query_structure_metric.py
from .judge_base import JudgeBaseMetric

class QueryStructureMetric(JudgeBaseMetric):
    """Evaluates overall query structure in SQL queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="query_structure",
            criteria="""Evaluate the generated SQL query's overall structure by comparing it to the reference SQL:
            1. Query organization - Is the query well-organized and logically structured?
            2. Subquery usage - Are subqueries used appropriately and efficiently?
            3. CTE (Common Table Expression) usage - Are CTEs used when beneficial?
            4. Clause ordering - Are SQL clauses in the correct order (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY)?
            5. Readability - Is the query readable and well-formatted?
            6. Complexity appropriateness - Is the query complexity appropriate for the task?
            7. Modularity - Is the query broken down into logical components effectively?""",
            evaluation_steps=[
                "Analyze the overall structure and organization of both queries",
                "Compare the use of subqueries, CTEs, and nested structures",
                "Evaluate the logical flow and clause ordering",
                "Assess query readability and formatting",
                "Determine if query complexity matches the problem requirements",
                "Check for appropriate use of advanced SQL features",
                "Evaluate modularity and logical breakdown of complex operations",
                "Score based on organization, clarity, and structural appropriateness (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )