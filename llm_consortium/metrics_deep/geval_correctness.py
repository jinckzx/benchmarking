# from deepeval.metrics import GEval
# from deepeval.test_case import LLMTestCase, LLMTestCaseParams
# from .deep_base import CustomBaseMetric
# from typing import Dict, Any
# import asyncio

# class GenerationUseCaseCorrectness(CustomBaseMetric):
#     """LLM-based evaluation of output correctness without ground truth"""
    
#     def __init__(self, threshold: float = 0.8):
#         CustomBaseMetric.__init__(
#             self,
#             name="use_case_correctness",
#             description="Evaluates if generated output is factually correct and contextually appropriate",
#             threshold=threshold,
#             csv_requires=["input"],  # Only needs the original input
#             runtime_requires=["input", "actual_output"]
#         )
        
#         self.geval = GEval(
#             name="UseCaseCorrectness",
#             criteria="""Evaluate the output on:
#             1. Coherence and logical flow
#             2. Relevance to input context
#             3. Factual consistency (against general knowledge)
#             4. Absence of hallucinations
#             5. Clarity of expression""",
#             evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
#             evaluation_steps=[
#                 "Analyze the input context and requirements",
#                 "Identify key claims or statements in the output",
#                 "Verify factual accuracy using internal knowledge",
#                 "Check for logical consistency and relevance",
#                 "Detect any speculative or ungrounded claims",
#                 "Evaluate and score within 0-1"
#             ],
            
#             model="gpt-4o-mini"
#         )

#     async def measure_async(self, input: str, actual_output: str) -> None:
#         test_case = LLMTestCase(
#             input=input,
#             actual_output=actual_output
#         )
        
#         try:
#             await self.geval.a_measure(test_case)
#             self._process_score()
#         except Exception as e:
#             print(f"Evaluation error: {str(e)}")
#             self._score = 0.0

#     def measure(self, input: str, actual_output: str) -> None:
#         asyncio.run(self.measure_async(input, actual_output))

#     def _process_score(self):
#         try:
#             # Handle different score formats
#             raw_score = self.geval.score
#             if isinstance(raw_score, (int, float)):
#                 self._score = max(0.0, min(1.0, float(raw_score)))
#             elif isinstance(raw_score, str):
#                 if '/' in raw_score:  # Handle "0.75/1" format
#                     self._score = float(raw_score.split('/')[0])
#                 else:
#                     self._score = float(raw_score.strip())
#             else:
#                 self._score = 0.0
#         except Exception as e:
#             print(f"Score processing error: {str(e)}")
#             self._score = 0.0

#     def calculate(self, input: str, actual_output: str) -> Dict[str, Any]:
#         self.measure(input, actual_output)
#         return {
#             "score": self._score,
#             "input": input,
#             "actual_output": actual_output,
#             "evaluation_rationale": self.geval.reason  # Capture LLM's reasoning
#         }
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .deep_base import CustomBaseMetric
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class GenerationUseCaseCorrectness(CustomBaseMetric):
    """LLM-based evaluation of output correctness without ground truth"""
    
    def __init__(self, threshold: float = 0.8):
        super().__init__(
            name="use_case_correctness",
            description="Evaluates if generated output is factually correct and contextually appropriate",
            threshold=threshold,
            csv_requires=["input"],  # Only needs the original input
            runtime_requires=["input", "actual_output"]
        )
        
        self.geval = GEval(
            name="UseCaseCorrectness",
            criteria="""Evaluate the output on:
            1. Coherence and logical flow
            2. Relevance to input context
            3. Factual consistency (against general knowledge)
            4. Absence of hallucinations
            5. Clarity of expression""",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            evaluation_steps=[
                "Analyze the input context and requirements",
                "Identify key claims or statements in the output",
                "Verify factual accuracy using internal knowledge",
                "Check for logical consistency and relevance",
                "Detect any speculative or ungrounded claims",
                "Evaluate and score within 0-1"
            ],
            model="gpt-4o-mini"
        )

    async def measure_async(self, input: str, actual_output: str) -> None:
        """Async version of measure for proper await handling"""
        test_case = LLMTestCase(
            input=input,
            actual_output=actual_output
        )
        
        try:
            # Run async evaluation
            await self.geval.a_measure(test_case)
            self._process_score()
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            self._score = 0.0

    def measure(self, input: str = None, actual_output: str = None, **kwargs) -> None:
        """
        Measure the metric and set the score - following CustomBaseMetric pattern
        This properly handles both sync and async contexts without nested event loop issues
        """
        # Handle both direct parameters and kwargs
        if input is None:
            input = kwargs.get('input')
        if actual_output is None:
            actual_output = kwargs.get('actual_output')
            
        if not input or not actual_output:
            print("Error: input and actual_output are required")
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
                        new_loop.run_until_complete(self.measure_async(input, actual_output))
                    finally:
                        new_loop.close()
                
                # Run in a separate thread to avoid nested event loop
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_in_thread)
                    future.result()  # Wait for completion
                    
            else:
                # Safe to use asyncio.run()
                asyncio.run(self.measure_async(input, actual_output))
        except RuntimeError:
            # No event loop running, safe to create one
            asyncio.run(self.measure_async(input, actual_output))

    def calculate(self, input: str = None, actual_output: str = None, **kwargs) -> Dict[str, Any]:
        """
        Calculate method following CustomBaseMetric pattern
        This calls measure() to compute the score, then returns detailed results
        """
        # Handle both direct parameters and kwargs
        if input is None:
            input = kwargs.get('input')
        if actual_output is None:
            actual_output = kwargs.get('actual_output')
            
        if not input or not actual_output:
            return {
                "score": 0.0,
                "input": input or "",
                "actual_output": actual_output or "",
                "evaluation_rationale": "Missing required parameters",
                "error": "input and actual_output are required"
            }
        
        # Call measure to compute the score
        self.measure(input=input, actual_output=actual_output)
        
        return {
            "score": self._score,
            "input": input,
            "actual_output": actual_output,
            "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available')
        }

    async def calculate_async(self, input: str, actual_output: str) -> Dict[str, Any]:
        """Async calculate method for use in async contexts"""
        if not input or not actual_output:
            return {
                "score": 0.0,
                "input": input or "",
                "actual_output": actual_output or "",
                "evaluation_rationale": "Missing required parameters",
                "error": "input and actual_output are required"
            }
            
        await self.measure_async(input, actual_output)
        return {
            "score": self._score,
            "input": input,
            "actual_output": actual_output,
            "evaluation_rationale": getattr(self.geval, 'reason', 'No evaluation rationale available')
        }

    def _process_score(self):
        """Handle score conversion consistently"""
        try:
            # Handle different score formats
            raw_score = self.geval.score
            if isinstance(raw_score, (int, float)):
                self._score = max(0.0, min(1.0, float(raw_score)))
            elif isinstance(raw_score, str):
                clean_score = raw_score.strip().lower()
                if '/' in clean_score:  # Handle "0.75/1" format
                    self._score = float(clean_score.split('/')[0])
                elif clean_score in ["yes", "true"]:
                    self._score = 1.0
                elif clean_score in ["no", "false"]:
                    self._score = 0.0
                else:
                    self._score = max(0.0, min(1.0, float(clean_score)))
            else:
                self._score = 0.0
        except Exception as e:
            print(f"Score processing error: {str(e)}")
            self._score = 0.0