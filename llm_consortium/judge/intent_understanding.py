"""
Intent Understanding Metric for evaluating how well SQL captures question intent
"""

from typing import Dict, Any
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .judge_base import SQLJudgeBaseMetric


class IntentUnderstandingMetric(SQLJudgeBaseMetric):
    """Evaluates how well SQL captures question intent"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        criteria = """Evaluate how well the SQL captures the question's intent across these dimensions (3-4 lines each):

1. QUESTION COMPREHENSION: Does the SQL address what's actually being asked? Missing key aspects of the question?
2. BUSINESS LOGIC ACCURACY: Are business rules correctly implemented? Any logical gaps or misinterpretations?
3. DATA REQUIREMENTS: Does the query retrieve all necessary data? Missing tables, columns, or relationships?
4. SCOPE APPROPRIATENESS: Is the query scope too broad or narrow? Filtering appropriately?
5. IMPLICIT REQUIREMENTS: Does it handle unstated but necessary requirements (like data validation, edge cases)?
6. RESULT FORMAT ALIGNMENT: Will the results be in the format expected by the question?

Specifically identify WHERE intent is missing and WHY it's problematic for answering the original question."""
        
        super().__init__(
            name="intent_understanding",
            criteria=criteria,
            threshold=threshold,
            model=model,
            weight=1.2,  # More important than basic metrics
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str, **kwargs) -> Dict[str, Any]:
        """Async evaluation of intent understanding"""
        test_case = LLMTestCase(
            input=f"Question: {question}\nGold SQL: {gold_sql}",
            actual_output=generated_sql,
            expected_output=gold_sql
        )
        
        await self.geval.a_measure(test_case)
        
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql
        }