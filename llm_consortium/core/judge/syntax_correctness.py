# syntax_correctness_metric.py
from .judge_base import JudgeBaseMetric

class SyntaxCorrectnessMetric(JudgeBaseMetric):
    """Evaluates SQL syntax correctness in queries"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="syntax_correctness",
            criteria="""Evaluate the generated SQL query's syntax correctness by comparing it to the reference SQL:
            1. SQL grammar compliance - Does the query follow proper SQL grammar rules?
            2. Keyword usage - Are SQL keywords used correctly (SELECT, FROM, WHERE, etc.)?
            3. Punctuation accuracy - Are commas, semicolons, and parentheses used correctly?
            4. String literal formatting - Are string literals properly quoted and escaped?
            5. Function syntax - Are SQL functions called with correct syntax?
            6. Identifier formatting - Are table and column names properly formatted/quoted when needed?
            7. Statement termination - Are statements properly terminated where required?""",
            evaluation_steps=[
                "Parse both queries for basic SQL syntax compliance",
                "Check proper usage of SQL keywords and reserved words",
                "Validate punctuation usage (commas, parentheses, semicolons)",
                "Examine string literal formatting and escaping",
                "Verify function call syntax and parameter usage",
                "Assess identifier quoting and formatting requirements",
                "Check for proper statement structure and termination",
                "Score based on syntactic correctness and SQL standard compliance (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )