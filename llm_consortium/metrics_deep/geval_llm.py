# from deepeval.metrics import GEval
# from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# from .deep_base import CustomBaseMetric 
# from typing import Dict, Any
# import asyncio

# class SQLClauseCountGEval(CustomBaseMetric):
#     """LLM-based clause count matching using DeepEval's GEval"""
    
#     def __init__(self, threshold: float = 1.0):
#         CustomBaseMetric.__init__(
#             self,
#             name="clause_count_match",
#             description="Checks if generated SQL has same number of clauses as reference SQL",
#             threshold=threshold,
#             csv_requires=["gold_sql"],
#             runtime_requires=["generated_sql", "gold_sql"]
#         )
        
#         # Initialize GEval with custom criteria
#         self.geval = GEval(
#             name="ClauseCountMatch",
#             criteria="Verify if the generated SQL uses the same number of clauses (SELECT, FROM, WHERE, etc.) as the reference SQL.",
#             evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
#             evaluation_steps=[
#                 "Identify all clauses in the reference SQL (input)",
#                 "Count clauses in the generated SQL (actual_output)",
#                 "Compare the counts of each clause type",
                
#             ],
#             model="gpt-4o-mini"
#         )

#     async def measure_async(self, generated_sql: str, gold_sql: str) -> None:
#         """Async version of measure for proper await handling"""
#         test_case = LLMTestCase(
#             input=gold_sql,
#             actual_output=generated_sql
#         )
        
#         try:
#             # Run async evaluation
#             await self.geval.a_measure(test_case)
#             self._process_score()
#         except Exception as e:
#             print(f"Evaluation error: {str(e)}")
#             self._score = 0.0

#     def measure(self, generated_sql: str, gold_sql: str) -> None:
#         """Sync wrapper for async measure"""
#         asyncio.run(self.measure_async(generated_sql, gold_sql))

#     def _process_score(self):
#         """Handle score conversion consistently"""
#         try:
#             raw_score = self.geval.score
#             if isinstance(raw_score, (int, float)):
#                 self._score = float(raw_score)
#             elif isinstance(raw_score, str):
#                 clean_score = raw_score.strip().lower()
#                 self._score = 1.0 if clean_score in ["1", "yes"] else 0.0
#             else:
#                 self._score = 0.0
#         except Exception as e:
#             print(f"Score processing error: {str(e)}")
#             self._score = 0.0

#     def calculate(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
#         """Calculate method now uses sync interface"""
#         self.measure(generated_sql, gold_sql)
#         return {
#             "score": self._score,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql,
#             "explanation": self.geval.reason 
#         }
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .deep_base import CustomBaseMetric 
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class SQLClauseCountGEval(CustomBaseMetric):
    """LLM-based clause count matching using DeepEval's GEval"""
    
    def __init__(self, threshold: float = 1.0):
        super().__init__(
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

    def measure(self, generated_sql: str = None, gold_sql: str = None, **kwargs) -> None:
        """
        Measure the metric and set the score - following CustomBaseMetric pattern
        This properly handles both sync and async contexts without nested event loop issues
        """
        # Handle both direct parameters and kwargs
        if generated_sql is None:
            generated_sql = kwargs.get('generated_sql')
        if gold_sql is None:
            gold_sql = kwargs.get('gold_sql')
            
        if not generated_sql or not gold_sql:
            print("Error: generated_sql and gold_sql are required")
            self._score = 0.0
            return
            
        # Check if we're in an async context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context - run the async operation in a separate thread
                # This completely avoids the nested event loop issue
                def run_in_thread():
                    # Create a new event loop in the thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        new_loop.run_until_complete(self.measure_async(generated_sql, gold_sql))
                    finally:
                        new_loop.close()
                
                # Run in a separate thread to avoid nested event loop
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_in_thread)
                    future.result()  # Wait for completion
                    
            else:
                # Safe to use asyncio.run()
                asyncio.run(self.measure_async(generated_sql, gold_sql))
        except RuntimeError:
            # No event loop running, safe to create one
            asyncio.run(self.measure_async(generated_sql, gold_sql))

    def calculate(self, generated_sql: str = None, gold_sql: str = None, **kwargs) -> Dict[str, Any]:
        """
        Calculate method following CustomBaseMetric pattern
        This calls measure() to compute the score, then returns detailed results
        """
        # Handle both direct parameters and kwargs
        if generated_sql is None:
            generated_sql = kwargs.get('generated_sql')
        if gold_sql is None:
            gold_sql = kwargs.get('gold_sql')
            
        if not generated_sql or not gold_sql:
            return {
                "score": 0.0,
                "generated_sql": generated_sql or "",
                "gold_sql": gold_sql or "",
                "explanation": "Missing required parameters",
                "error": "generated_sql and gold_sql are required"
            }
        
        # Call measure to compute the score
        self.measure(generated_sql=generated_sql, gold_sql=gold_sql)
        
        return {
            "score": self._score,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql,
            "explanation": getattr(self.geval, 'reason', 'No explanation available')
        }

    async def calculate_async(self, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Async calculate method for use in async contexts"""
        if not generated_sql or not gold_sql:
            return {
                "score": 0.0,
                "generated_sql": generated_sql or "",
                "gold_sql": gold_sql or "",
                "explanation": "Missing required parameters",
                "error": "generated_sql and gold_sql are required"
            }
            
        await self.measure_async(generated_sql, gold_sql)
        return {
            "score": self._score,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql,
            "explanation": getattr(self.geval, 'reason', 'No explanation available')
        }

    def _process_score(self):
        """Handle score conversion consistently"""
        try:
            raw_score = self.geval.score
            if isinstance(raw_score, (int, float)):
                self._score = float(raw_score)
            elif isinstance(raw_score, str):
                clean_score = raw_score.strip().lower()
                self._score = 1.0 if clean_score in ["1", "yes", "true"] else 0.0
            else:
                self._score = 0.0
        except Exception as e:
            print(f"Score processing error: {str(e)}")
            self._score = 0.0