"""
Query Metrics Analyzer for evaluating basic SQL query metrics
"""

from typing import Dict, Any
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .judge_base import SQLJudgeBaseMetric


class QueryMetricsAnalyzer(SQLJudgeBaseMetric):
    """Analyzes basic SQL query metrics"""
    
    def __init__(self, threshold: float = 0.8, model: str = "gpt-4o-mini"):
        criteria = """Evaluate the SQL query across these specific dimensions, providing 3-4 lines for each:

1. COLUMN ACCURACY: Are the correct columns selected? Missing or extra columns? Column aliases appropriate?
2. QUERY STRUCTURE: Is the SQL structure proper? Correct syntax and organization? Readable formatting?
3. JOIN QUALITY: Are join conditions appropriate and efficient? Missing joins or incorrect join types?
4. CLAUSE ACCURACY: Are WHERE, GROUP BY, HAVING, ORDER BY clauses correctly implemented?

For each dimension, explain what's correct, what's missing, and why it matters for the query's correctness."""
        
        super().__init__(
            name="query_metrics",
            criteria=criteria,
            threshold=threshold,
            model=model,
            weight=1.0,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        )
    
    async def evaluate_async(self, question: str, generated_sql: str, gold_sql: str, **kwargs) -> Dict[str, Any]:
        """Async evaluation of a single query"""
        test_case = LLMTestCase(
            input=f"Question: {question}\nGold SQL: {gold_sql}",
            actual_output=generated_sql,
            expected_output=gold_sql
        )
        
        await self.geval.a_measure(test_case)
        
        # Enhanced rationale extraction
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql
        }