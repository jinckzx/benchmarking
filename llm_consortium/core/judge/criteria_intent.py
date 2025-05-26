# intent_understanding_metric.py
from .judge_base import JudgeBaseMetric

class IntentUnderstandingMetric(JudgeBaseMetric):
    """Evaluates how well the generated SQL captures the original question intent"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        super().__init__(
            name="intent_understanding",
            criteria="""Evaluate how well the generated SQL query captures the intent of the original question:
            1. Question comprehension - Does the SQL address what the question is asking?
            2. Business logic accuracy - Does the query implement the correct business rules?
            3. Data requirements fulfillment - Does the query retrieve the data needed to answer the question?
            4. Scope appropriateness - Is the query scope (broad/narrow) appropriate for the question?
            5. Implicit requirement handling - Are unstated but implied requirements addressed?
            6. Edge case consideration - Does the query handle relevant edge cases mentioned or implied?
            7. Result format alignment - Will the query results be in a format suitable for answering the question?""",
            evaluation_steps=[
                "Parse the original question to understand the core intent",
                "Identify key business requirements and constraints from the question",
                "Analyze what data is needed to properly answer the question",
                "Compare the generated SQL's approach to the reference SQL's approach",
                "Evaluate if the generated query addresses all aspects of the question",
                "Check for handling of implicit requirements and edge cases",
                "Assess if the query results would properly answer the original question",
                "Score based on intent capture accuracy and completeness (0-1 scale)"
            ],
            threshold=threshold,
            model=model
        )