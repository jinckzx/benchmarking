import os
from dotenv import load_dotenv
from typing import Dict, Any
load_dotenv()
os.environ["DEEPEVAL_IGNORE_SIGNALS"] = "1"
CRITERIA_REGISTRY: Dict[str, Any] = {}
def register_criteria(name: str, metric: Any):
    """Register a new metric in the registry"""
    CRITERIA_REGISTRY[name] = metric


from .column_accuracy import ColumnAccuracyMetric  
from .query_structure import QueryStructureMetric  
from .join_quality import JoinQualityMetric  

register_criteria('column_accuracy', ColumnAccuracyMetric())
register_criteria('query_structure', QueryStructureMetric())
register_criteria('join_quality', JoinQualityMetric())