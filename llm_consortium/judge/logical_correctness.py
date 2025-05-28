"""
Logical Correctness Metric for evaluating logical correctness of SQL queries
"""

from typing import Dict, Any
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .judge_base import SQLJudgeBaseMetric


class LogicalCorrectnessMetric(SQLJudgeBaseMetric):
    """Evaluates logical correctness of SQL queries"""
    
    def __init__(self, threshold: float = 0.85, model: str = "gpt-4o-mini"):
        criteria = """Evaluate logical correctness across these dimensions (3-4 lines each):

1. QUERY LOGIC ALIGNMENT: Does the query logic match question requirements? Logical flow correct?
2. JOIN CONDITIONS: Are join conditions logically sound? Appropriate join keys and types?
3. FILTER CONDITIONS: Do WHERE clauses properly implement business rules? Logical operators correct?
4. AGGREGATION LOGIC: Are GROUP BY, HAVING, and aggregate functions applied correctly? Proper grouping levels?
5. SUBQUERY LOGIC: Are subqueries logically sound and necessary? Efficient and correct implementation?

Identify specific logical flaws and explain how they would produce incorrect results."""
        
        super().__init__(
            name="logical_correctness",
            criteria=criteria,
            threshold=threshold,
            model=model,
            weight=1.1,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str, **kwargs) -> Dict[str, Any]:
        """Async evaluation of logical correctness"""
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