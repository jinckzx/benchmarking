from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .deep_base import CustomBaseMetric 
from typing import Dict, Any
import asyncio

class SQLClauseCountGEval(CustomBaseMetric):
    """LLM-based clause count matching using DeepEval's GEval"""
    
    def __init__(self, threshold: float = 1.0):
        CustomBaseMetric.__init__(
            self,
            name="clause_count_match",
            description="Checks if generated SQL has same number of clauses as reference SQL",
            threshold=threshold,
            csv_requires=["gold_sql"],
            runtime_requires=["generated_sql", "gold_sql"]
        )
        
        # Initialize GEval with custom criteria
        self.geval = GEval(
            name="ClauseCountMatch",
            criteria="Verify if the generated SQL uses the same number of clauses (SELECT, FROM, WHERE, etc.) as the reference SQL.",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            evaluation_steps=[
                "Identify all clauses in the reference SQL (input)",
                "Count clauses in the generated SQL (actual_output)",
                "Compare the counts of each clause type",
                
            ],
            model="gpt-4o-mini"
        )

    async def measure_async(self, generated_sql: str, gold_sql: str) -> None:
        """Async version of measure for proper await handling"""
        test_case = LLMTestCase(
            input=gold_sql,
            actual_output=generated_sql
        )
        
        try:
            # Run async evaluation
            await self.geval.a_measure(test_case)
            self._process_score()
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            self._score = 0.0

    def measure(self, generated_sql: str, gold_sql: str) -> None:
        """Sync wrapper for async measure"""
        asyncio.run(self.measure_async(generated_sql, gold_sql))

    def _process_score(self):
        """Handle score conversion consistently"""
        try:
            raw_score = self.geval.score
            if isinstance(raw_score, (int, float)):
                self._score = float(raw_score)
            elif isinstance(raw_score, str):
                clean_score = raw_score.strip().lower()
                self._score = 1.0 if clean_score in ["1", "yes"] else 0.0
            else:
                self._score = 0.0
        except Exception as e:
            print(f"Score processing error: {str(e)}")
            self._score = 0.0

    def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Calculate method now uses sync interface"""
        self.measure(generated_sql, gold_sql)
        return {
            "score": self._score,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql,
            "explanation": self.geval.reason 
        }