from llm_consortium.metrics_deep.deep_base import CustomBaseMetric
from typing import Any, List, Dict
import os
os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from typing import Dict, Any, List, Union
class SQLJudgeBaseMetric(CustomBaseMetric):
    """Base class for SQL evaluation metrics using GEval"""
    
    def __init__(self, 
                 name: str,
                 criteria: str,
                 threshold: float = 0.8,
                 model: str = "gpt-4o-mini",
                 weight: float = 1.0,
                 evaluation_params: List = None):
        """
        Initialize SQL judge base metric
        
        Args:
            name: Name of the metric
            criteria: Evaluation criteria for GEval
            threshold: Threshold for passing/failing
            model: Model to use for evaluation
            weight: Relative importance for ranking
            evaluation_params: Parameters for GEval evaluation
        """
        super().__init__(
            name=name,
            description=f"SQL evaluation metric for {name}",
            threshold=threshold
        )
        
        self.model = model
        self.weight = weight
        self.criteria = criteria
        
        # Set default evaluation parameters if not provided
        if evaluation_params is None:
            evaluation_params = [LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT]
        
        # Initialize GEval
        self.geval = GEval(
            name=self.name,
            criteria=self.criteria,
            evaluation_params=evaluation_params,
            model=self.model
        )
    
    def _extract_rationale(self, geval_obj) -> str:
        """Enhanced rationale extraction with fallback options"""
        rationale_attrs = ['reason', 'rationale', 'explanation', 'verbose_logs', 'evaluation_cost']
        
        for attr in rationale_attrs:
            if hasattr(geval_obj, attr):
                value = getattr(geval_obj, attr)
                if value and str(value).strip():
                    return str(value)
        
        return f"Evaluation completed with score {geval_obj.score}. Detailed rationale not available from GEval object."
    
    async def evaluate_async(self, question: str = "", generated_sql: str = "", gold_sql: str = "", **kwargs) -> Dict[str, Any]:
        """
        Async evaluation method - to be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement evaluate_async()")
    
    def calculate(self, question: str = "", generated_sql: str = "", gold_sql: str = "", **kwargs) -> Dict[str, Any]:
        """
        Synchronous wrapper for async evaluation
        """
        # Run async evaluation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.evaluate_async(question=question, generated_sql=generated_sql, gold_sql=gold_sql, **kwargs)
            )
            return result
        finally:
            loop.close()