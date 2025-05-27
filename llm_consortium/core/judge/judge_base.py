# # judge_base_metric.py
# import os
# os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"  # Add this before any deepeval imports
# from deepeval.metrics import GEval
# from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# from ...metrics_deep.deep_base import CustomBaseMetric
# from typing import Dict, Any, List
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# import threading

# class JudgeBaseMetric(CustomBaseMetric):
#     """Base class for SQL judgment metrics using GEval"""
    
#     def __init__(self, 
#                  name: str,
#                  criteria: str,
#                  evaluation_steps: List[str],
#                  threshold: float = 0.8,
#                  model: str = "gpt-4o-mini"):
#         super().__init__(
#             name=name,
#             description=f"Evaluates SQL queries based on {name}",
#             threshold=threshold,
#             csv_requires=["question", "generated_sql", "gold_sql"],
#             runtime_requires=["question", "generated_sql", "gold_sql"]
#         )
        
#         self.geval = GEval(
#             name=name,
#             criteria=criteria,
#             evaluation_params=[
#                 LLMTestCaseParams.INPUT,
#                 LLMTestCaseParams.ACTUAL_OUTPUT,
#                 LLMTestCaseParams.EXPECTED_OUTPUT
#             ],
#             evaluation_steps=evaluation_steps,
#             model=model
#         )

#     async def measure_async(self, question: str, generated_sql: str, gold_sql: str) -> None:
#         """Async version of measure for proper await handling"""
#         test_case = LLMTestCase(
#             input=question,
#             actual_output=generated_sql,
#             expected_output=gold_sql
#         )
        
#         try:
#             # Run async evaluation
#             await self.geval.a_measure(test_case)
#             self._process_score()
#         except Exception as e:
#             print(f"Evaluation error: {str(e)}")
#             self._score = 0.0

#     def measure(self, question: str = None, generated_sql: str = None, gold_sql: str = None, **kwargs) -> None:
#         """
#         Measure the metric and set the score - following CustomBaseMetric pattern
#         This properly handles both sync and async contexts without nested event loop issues
#         """
#         # Handle both direct parameters and kwargs
#         if question is None:
#             question = kwargs.get('question')
#         if generated_sql is None:
#             generated_sql = kwargs.get('generated_sql')
#         if gold_sql is None:
#             gold_sql = kwargs.get('gold_sql')
            
#         if not question or not generated_sql or not gold_sql:
#             print("Error: question, generated_sql, and gold_sql are required")
#             self._score = 0.0
#             return
            
#         # Check if we're in an async context
#         try:
#             loop = asyncio.get_event_loop()
#             if loop.is_running():
#                 # We're in an async context - run the async operation in a separate thread
#                 # This completely avoids the nested event loop issue
#                 def run_in_thread():
#                     # Create a new event loop in the thread
#                     new_loop = asyncio.new_event_loop()
#                     asyncio.set_event_loop(new_loop)
#                     try:
#                         new_loop.run_until_complete(self.measure_async(question, generated_sql, gold_sql))
#                     finally:
#                         new_loop.close()
                
#                 # Run in a separate thread to avoid nested event loop
#                 with ThreadPoolExecutor(max_workers=1) as executor:
#                     future = executor.submit(run_in_thread)
#                     future.result()  # Wait for completion
                    
#             else:
#                 # Safe to use asyncio.run()
#                 asyncio.run(self.measure_async(question, generated_sql, gold_sql))
#         except RuntimeError:
#             # No event loop running, safe to create one
#             asyncio.run(self.measure_async(question, generated_sql, gold_sql))

#     def calculate(self, question: str = None, generated_sql: str = None, gold_sql: str = None, **kwargs) -> Dict[str, Any]:
#         """
#         Calculate method following CustomBaseMetric pattern
#         This calls measure() to compute the score, then returns detailed results
#         """
#         # Handle both direct parameters and kwargs
#         if question is None:
#             question = kwargs.get('question')
#         if generated_sql is None:
#             generated_sql = kwargs.get('generated_sql')
#         if gold_sql is None:
#             gold_sql = kwargs.get('gold_sql')
            
#         if not question or not generated_sql or not gold_sql:
#             return {
#                 "score": 0.0,
#                 "question": question or "",
#                 "generated_sql": generated_sql or "",
#                 "gold_sql": gold_sql or "",
#                 "evaluation_rationale": "Missing required parameters",
#                 "error": "question, generated_sql, and gold_sql are required"
#             }
        
#         # Call measure to compute the score
#         self.measure(question=question, generated_sql=generated_sql, gold_sql=gold_sql)
        
#         return {
#             "score": self._score,
#             "question": question,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql,
#             "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available')
#         }

#     async def calculate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
#         """Async calculate method for use in async contexts"""
#         if not question or not generated_sql or not gold_sql:
#             return {
#                 "score": 0.0,
#                 "question": question or "",
#                 "generated_sql": generated_sql or "",
#                 "gold_sql": gold_sql or "",
#                 "evaluation_rationale": "Missing required parameters",
#                 "error": "question, generated_sql, and gold_sql are required"
#             }
            
#         await self.measure_async(question, generated_sql, gold_sql)
#         return {
#             "score": self._score,
#             "question": question,
#             "generated_sql": generated_sql,
#             "gold_sql": gold_sql,
#             "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available')
#         }

#     def _process_score(self):
#         """Handle score conversion consistently"""
#         try:
#             # Handle different score formats
#             raw_score = self.geval.score
#             if isinstance(raw_score, (int, float)):
#                 self._score = max(0.0, min(1.0, float(raw_score)))
#             elif isinstance(raw_score, str):
#                 clean_score = raw_score.strip().lower()
#                 if '/' in clean_score:  # Handle "0.75/1" format
#                     self._score = float(clean_score.split('/')[0])
#                 elif clean_score in ["yes", "true"]:
#                     self._score = 1.0
#                 elif clean_score in ["no", "false"]:
#                     self._score = 0.0
#                 else:
#                     self._score = max(0.0, min(1.0, float(clean_score)))
#             else:
#                 self._score = 0.0
#         except Exception as e:
#             print(f"Score processing error: {str(e)}")
#             self._score = 0.0
# judge_base_metric.py
import os
os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"  # Add this before any deepeval imports
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from ...metrics_deep.deep_base import CustomBaseMetric
from typing import Dict, Any, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class JudgeBaseMetric(CustomBaseMetric):
    """Base class for SQL judgment metrics using GEval"""
    
    def __init__(self, 
                 name: str,
                 criteria: str,
                 evaluation_steps: List[str],
                 threshold: float = 0.8,
                 model: str = "gpt-4o-mini"):
        super().__init__(
            name=name,
            description=f"Evaluates SQL queries based on {name}",
            threshold=threshold,
            csv_requires=["question", "generated_sql", "gold_sql"],
            runtime_requires=["question", "generated_sql", "gold_sql"]
        )
        
        self.geval = GEval(
            name=name,
            criteria=criteria,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            evaluation_steps=evaluation_steps,
            model=model,
            threshold=threshold  # Pass threshold to GEval as well
        )

    async def measure_async(self, question: str, generated_sql: str, gold_sql: str) -> None:
        """Async version of measure for proper await handling"""
        test_case = LLMTestCase(
            input=question,
            actual_output=generated_sql,
            # expected_output=gold_sql
        )
        
        try:
            # Run async evaluation
            await self.geval.a_measure(test_case)
            self._process_score()
        except Exception as e:
            print(f"Error in {self.name} evaluation: {str(e)}")
            self._score = 0.0
            # Store error info for debugging
            self._evaluation_error = str(e)

    def measure(self, question: str = None, generated_sql: str = None, gold_sql: str = None, **kwargs) -> None:
        """
        Measure the metric and set the score - following CustomBaseMetric pattern
        This properly handles both sync and async contexts without nested event loop issues
        """
        # Handle both direct parameters and kwargs
        if question is None:
            question = kwargs.get('question')
        if generated_sql is None:
            generated_sql = kwargs.get('generated_sql')
        if gold_sql is None:
            gold_sql = kwargs.get('gold_sql')
            
        if not all([question, generated_sql, gold_sql]):
            print(f"Error in {self.name}: question, generated_sql, and gold_sql are required")
            self._score = 0.0
            return
            
        # Reset any previous evaluation error
        self._evaluation_error = None
            
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
                        new_loop.run_until_complete(self.measure_async(question, generated_sql, gold_sql))
                    finally:
                        new_loop.close()
                
                # Run in a separate thread to avoid nested event loop
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_in_thread)
                    future.result()  # Wait for completion
                    
            else:
                # Safe to use asyncio.run()
                asyncio.run(self.measure_async(question, generated_sql, gold_sql))
        except RuntimeError:
            # No event loop running, safe to create one
            asyncio.run(self.measure_async(question, generated_sql, gold_sql))

    def calculate(self, question: str = None, generated_sql: str = None, gold_sql: str = None, **kwargs) -> Dict[str, Any]:
        """
        Calculate method following CustomBaseMetric pattern
        This calls measure() to compute the score, then returns detailed results
        """
        # Handle both direct parameters and kwargs
        if question is None:
            question = kwargs.get('question')
        if generated_sql is None:
            generated_sql = kwargs.get('generated_sql')
        if gold_sql is None:
            gold_sql = kwargs.get('gold_sql')
            
        if not all([question, generated_sql, gold_sql]):
            return {
                "score": 0.0,
                "question": question or "",
                "generated_sql": generated_sql or "",
                "gold_sql": gold_sql or "",
                "evaluation_rationale": "Missing required parameters",
                "error": "question, generated_sql, and gold_sql are required",
                "metric_name": self.name
            }
        
        # Call measure to compute the score
        self.measure(question=question, generated_sql=generated_sql, gold_sql=gold_sql)
        
        # Build result dictionary
        result = {
            "score": self._score,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql,
            "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available'),
            "metric_name": self.name,
            "passed": self._score >= self.threshold
        }
        
        # Add error info if there was an evaluation error
        if hasattr(self, '_evaluation_error') and self._evaluation_error:
            result["error"] = self._evaluation_error
            
        return result

    async def calculate_async(self, question: str, generated_sql: str, gold_sql: str) -> Dict[str, Any]:
        """Async calculate method for use in async contexts"""
        if not all([question, generated_sql, gold_sql]):
            return {
                "score": 0.0,
                "question": question or "",
                "generated_sql": generated_sql or "",
                "gold_sql": gold_sql or "",
                "evaluation_rationale": "Missing required parameters",
                "error": "question, generated_sql, and gold_sql are required",
                "metric_name": self.name
            }
            
        await self.measure_async(question, generated_sql, gold_sql)
        
        result = {
            "score": self._score,
            "question": question,
            "generated_sql": generated_sql,
            "gold_sql": gold_sql,
            "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available'),
            "metric_name": self.name,
            "passed": self._score >= self.threshold
        }
        
        # Add error info if there was an evaluation error
        if hasattr(self, '_evaluation_error') and self._evaluation_error:
            result["error"] = self._evaluation_error
            
        return result

    def _process_score(self):
        """Handle score conversion consistently"""
        try:
            # Handle different score formats from GEval
            raw_score = self.geval.score
            if isinstance(raw_score, (int, float)):
                self._score = max(0.0, min(1.0, float(raw_score)))
            elif isinstance(raw_score, str):
                clean_score = raw_score.strip().lower()
                if '/' in clean_score:  # Handle "0.75/1" format
                    numerator = float(clean_score.split('/')[0])
                    denominator = float(clean_score.split('/')[1]) if len(clean_score.split('/')) > 1 else 1.0
                    self._score = max(0.0, min(1.0, numerator / denominator))
                elif clean_score in ["yes", "true"]:
                    self._score = 1.0
                elif clean_score in ["no", "false"]:
                    self._score = 0.0
                else:
                    # Try to parse as float
                    self._score = max(0.0, min(1.0, float(clean_score)))
            else:
                print(f"Warning: Unexpected score type {type(raw_score)} for {self.name}")
                self._score = 0.0
        except Exception as e:
            print(f"Score processing error in {self.name}: {str(e)}")
            self._score = 0.0

    @property
    def score(self) -> float:
        """Property to access the current score"""
        return getattr(self, '_score', 0.0)
    
    @property 
    def is_successful(self) -> bool:
        """Check if the metric passed the threshold"""
        return self.score >= self.threshold