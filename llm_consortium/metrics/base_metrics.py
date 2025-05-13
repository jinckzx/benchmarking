# metrics/base_metrics.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseMetric(ABC):
    """Abstract base class for all metrics"""
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 csv_requires: List[str] = None,
                 runtime_requires: List[str] = None):
        self.name = name
        self.description = description
        self.csv_requires = csv_requires if csv_requires else []
        self.runtime_requires = runtime_requires if runtime_requires else []
        
    @abstractmethod
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """Calculate metric from required inputs"""
        pass