"""
Syntax Accuracy Metric for evaluating SQL syntax correctness
"""

from typing import Dict, Any
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .judge_base import SQLJudgeBaseMetric


class SyntaxAccuracyMetric(SQLJudgeBaseMetric):
    """Evaluates SQL syntax correctness"""
    
    def __init__(self, threshold: float = 0.9, model: str = "gpt-4o-mini"):
        criteria = """Evaluate SQL syntax correctness across these areas (3-4 lines each):

1. VALID SQL SYNTAX: Is the SQL syntactically correct? Any parsing errors or malformed statements?
2. KEYWORD USAGE: Are SQL keywords used properly? Correct spelling and placement?
3. CLAUSE ORDERING: Are clauses in the correct order (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY)?
4. TABLE/COLUMN REFERENCES: Are all table and column names valid? Proper aliasing?
5. OPERATOR USAGE: Are operators (=, <>, LIKE, IN, etc.) used correctly?

Identify specific syntax issues and explain why they would cause query execution problems."""
        
        super().__init__(
            name="syntax_accuracy",
            criteria=criteria,
            threshold=threshold,
            model=model,
            weight=0.8,  # Less important than intent
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
        )
    
    async def evaluate_async(self, generated_sql: str, **kwargs) -> Dict[str, Any]:
        """Async evaluation of syntax accuracy"""
        test_case = LLMTestCase(
            input="Evaluate SQL syntax",
            actual_output=generated_sql,
            expected_output="Valid SQL syntax"
        )
        
        await self.geval.a_measure(test_case)
        
        rationale = self._extract_rationale(self.geval)
        
        return {
            "score": self.geval.score,
            "rationale": rationale,
            "generated_sql": generated_sql
        }