# from deepeval.metrics import BaseMetric
# from typing import Dict, Any, List, Optional, Union, Tuple

# class CustomBaseMetric(BaseMetric):
#     """Extended base class for custom metrics compatible with DeepEval"""
    
#     def __init__(self, 
#                  name: str, 
#                  description: str, 
#                  threshold: float = None,
#                  csv_requires: List[str] = None,
#                  runtime_requires: List[str] = None):
#         """
#         Initialize a custom metric that extends DeepEval's BaseMetric
        
#         Args:
#             name: Name of the metric
#             description: Description of what the metric measures
#             threshold: Optional threshold for passing/failing
#             csv_requires: Required fields from CSV data
#             runtime_requires: Required parameters at runtime
#         """
#         # Initialize BaseMetric attributes properly without calling super().__init__
#         # as that would cause issues with the non-standard parameters
#         self.threshold = threshold
        
#         # Set our custom attributes
#         self.name = name
#         self.description = description
#         self.csv_requires = csv_requires if csv_requires else []
#         self.runtime_requires = runtime_requires if runtime_requires else []
#         self._score = None
        
#     def _is_successful(self) -> bool:
#         """
#         Returns True if the metric passes the threshold
#         Required by DeepEval's BaseMetric
#         """
#         if self.threshold is None or self._score is None:
#             return True
#         return self._score >= self.threshold
    
#     def _metric_name(self) -> str:
#         """
#         Returns the name of the metric
#         Required by DeepEval's BaseMetric
#         """
#         return self.name
    
#     def _metric_value(self) -> Union[float, int, bool, str, Dict, List, Tuple, None]:
#         """
#         Returns the metric value
#         Required by DeepEval's BaseMetric
#         """
#         return self._score
    
#     @property
#     def score(self) -> Union[float, int, bool, str, Dict, List, Tuple, None]:
#         """
#         Returns the score for easy access
#         """
#         return self._score
    
#     def is_successful(self) -> bool:
#         """
#         Returns whether the metric passed the threshold
#         """
#         return self._is_successful()
    
#     def calculate(self, **kwargs) -> Dict[str, Any]:
#         """
#         Calculate metric from required inputs
#         Must be implemented by child classes
#         """
#         raise NotImplementedError("Subclasses must implement calculate()")
    
#     def measure(self, **kwargs) -> None:
#         """
#         Measure the metric and set the score
#         Required by DeepEval's BaseMetric
#         """
#         result = self.calculate(**kwargs)
#         if isinstance(result, dict) and 'score' in result:
#             self._score = result['score']
#         elif isinstance(result, (int, float)):
#             self._score = result
#         else:
#             # Depending on your metric, you may need to adapt this logic
#             try:
#                 main_key = next(iter(result)) if result else None
#                 self._score = result[main_key] if main_key else 0.0
#             except:
#                 self._score = 0.0
"""
Base metric class for SQL evaluation criteria
Inherits from DeepEval's BaseMetric for compatibility
"""

from deepeval.metrics import BaseMetric
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio


class CustomBaseMetric(BaseMetric):
    """Extended base class for custom metrics compatible with DeepEval"""
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 threshold: float = None,
                 csv_requires: List[str] = None,
                 runtime_requires: List[str] = None):
        """
        Initialize a custom metric that extends DeepEval's BaseMetric
        
        Args:
            name: Name of the metric
            description: Description of what the metric measures
            threshold: Optional threshold for passing/failing
            csv_requires: Required fields from CSV data
            runtime_requires: Required parameters at runtime
        """
        # Initialize BaseMetric attributes properly without calling super().__init__
        # as that would cause issues with the non-standard parameters
        self.threshold = threshold
        
        # Set our custom attributes
        self.name = name
        self.description = description
        self.csv_requires = csv_requires if csv_requires else []
        self.runtime_requires = runtime_requires if runtime_requires else []
        self._score = None
        
    def _is_successful(self) -> bool:
        """
        Returns True if the metric passes the threshold
        Required by DeepEval's BaseMetric
        """
        if self.threshold is None or self._score is None:
            return True
        return self._score >= self.threshold
    
    def _metric_name(self) -> str:
        """
        Returns the name of the metric
        Required by DeepEval's BaseMetric
        """
        return self.name
    
    def _metric_value(self) -> Union[float, int, bool, str, Dict, List, Tuple, None]:
        """
        Returns the metric value
        Required by DeepEval's BaseMetric
        """
        return self._score
    
    @property
    def score(self) -> Union[float, int, bool, str, Dict, List, Tuple, None]:
        """
        Returns the score for easy access
        """
        return self._score
    
    def is_successful(self) -> bool:
        """
        Returns whether the metric passed the threshold
        """
        return self._is_successful()
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate metric from required inputs
        Must be implemented by child classes
        """
        raise NotImplementedError("Subclasses must implement calculate()")
    
    def measure(self, **kwargs) -> None:
        """
        Measure the metric and set the score
        Required by DeepEval's BaseMetric
        """
        result = self.calculate(**kwargs)
        if isinstance(result, dict) and 'score' in result:
            self._score = result['score']
        elif isinstance(result, (int, float)):
            self._score = result
        else:
            # Depending on your metric, you may need to adapt this logic
            try:
                main_key = next(iter(result)) if result else None
                self._score = result[main_key] if main_key else 0.0
            except:
                self._score = 0.0