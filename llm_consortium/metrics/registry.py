# metrics/registry.py
from .exact_match import SQLExactMatch
from .execution_match import SQLExecutionMatch
from typing import Dict, List
from .base_metrics import BaseMetric
from .component_match import SQLComponentMatch
from .anmol import SQLAnmol
from .abcabc import SQLabcabc
from .xyz import SQLxyz
from .ooo import SQLooo
from .ppp import SQLppp

from .ccc import SQLccc
from .select_check import Select_checkMetric




class MetricRegistry:
    """Registry for available metrics with validation"""
    
    def __init__(self):
        self.metrics = {
            "sql": {
                "exact_match": SQLExactMatch(),
                "execution_match": SQLExecutionMatch(
                    db_root_path="D:/data_sci/benchmarking_tool/dataset/spider_data/spider_data/database"
                ),
                "component_match":SQLComponentMatch(),
                "anmol": SQLAnmol(),
                
                
                "abcabc": SQLabcabc(),
                "xyz": SQLxyz(),
                "ooo": SQLooo(),
                "ppp": SQLppp(),
                
                "ccc": SQLccc(),
                "select_check": Select_checkMetric(),
            }
        }
    
    def get_metrics_for_task(self, task: str) -> Dict[str, BaseMetric]:
        return self.metrics.get(task, {})
    
    def register_metric(self, task: str, metric: BaseMetric):
        if task not in self.metrics:
            self.metrics[task] = {}
        if not isinstance(metric, BaseMetric):
            raise TypeError("Can only register BaseMetric instances")
        self.metrics[task][metric.name] = metric

    def validate_csv_columns(self, task: str, csv_columns: List[str]) -> List[str]:
        required = set()
        for metric in self.get_metrics_for_task(task).values():
            required.update(metric.csv_requires)
        return list(required - set(csv_columns))