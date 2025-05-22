from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from .deep_base import CustomBaseMetric
from typing import Dict, Any
import asyncio

class GenerationUseCaseCorrectness(CustomBaseMetric):
    """LLM-based evaluation of output correctness without ground truth"""
    
    def __init__(self, threshold: float = 0.8):
        CustomBaseMetric.__init__(
            self,
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
        test_case = LLMTestCase(
            input=input,
            actual_output=actual_output
        )
        
        try:
            await self.geval.a_measure(test_case)
            self._process_score()
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            self._score = 0.0

    def measure(self, input: str, actual_output: str) -> None:
        asyncio.run(self.measure_async(input, actual_output))

    def _process_score(self):
        try:
            # Handle different score formats
            raw_score = self.geval.score
            if isinstance(raw_score, (int, float)):
                self._score = max(0.0, min(1.0, float(raw_score)))
            elif isinstance(raw_score, str):
                if '/' in raw_score:  # Handle "0.75/1" format
                    self._score = float(raw_score.split('/')[0])
                else:
                    self._score = float(raw_score.strip())
            else:
                self._score = 0.0
        except Exception as e:
            print(f"Score processing error: {str(e)}")
            self._score = 0.0

    def calculate(self, input: str, actual_output: str) -> Dict[str, Any]:
        self.measure(input, actual_output)
        return {
            "score": self._score,
            "input": input,
            "actual_output": actual_output,
            "evaluation_rationale": self.geval.reason  # Capture LLM's reasoning
        }